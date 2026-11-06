# SPDX-License-Identifier: LicenseRef-TER-AI-1.0
"""Tagentic1 on Telegram: a long-polling bot bridge (beta, release candidate).

Run it with your own bot::

    export TAGENTIC_TG_TOKEN=123456:ABC...        # or --token-file / "token_file" in the config
    terai tagentic telegram --config telegram.json

Two modes, decided in code (not in the prompt):

* owner chats (private chats whose id is in ``owners`` or in the allowlist file): full Tagentic1 with
  User.md, Memory.md, the workspace and every tool; writes and runs wait for Allow / Deny.
* every other chat and every group: public mode. No User.md or Memory.md, read-only tools only
  (calculator, datetime, units, add_knowledge), sessions in their own folder, per-chat rate limits.
  Groups only get an answer to commands, mentions, or replies to the bot.

Every text the bot writes itself is English and starts with ``[System]``. Text the model writes
(its answer and its trace) is sent as the model wrote it, with no header and no timing line.

The token is read from the ``TAGENTIC_TG_TOKEN`` environment variable or from a file you name; it is
never printed or logged. The log keeps chat ids, sizes and timings, never the text of other people's
messages.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import shlex
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

SYSTEM = '[System]'
COMMUNITY_URL = 'https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-telegram-bot-community'
DOCS_URL = 'https://github.com/klanarongz2009-sketch/ter-ai/blob/main/docs/TAGENTIC_TELEGRAM.md'
TG_LIMIT = 4000          # Telegram allows 4096 characters per message; keep a margin
OWNER_PRIORITY, PUBLIC_PRIORITY = 0, 10
PUBLIC_DEFAULTS = {'open': True, 'msgs_per_hour': 6, 'adds_per_hour': 10, 'max_public_queue': 2}
TOKEN_ENV = 'TAGENTIC_TG_TOKEN'

EXAMPLE_CONFIG = {
    'token_file': '~/.config/tagentic/telegram_token',
    'owners': [123456789],
    'memory_dir': '~/.terai/tagentic',
    'workspace': '~/tagentic-workspace',
    'state_dir': '~/.terai/tagentic/telegram',
    'relay_command': '',
    'max_queue': 3,
    'turn_timeout': 900,
    'public': dict(PUBLIC_DEFAULTS),
}


def sys_msg(text: str) -> str:
    return f'{SYSTEM} {text}'


def welcome_public(community: str = COMMUNITY_URL, docs: str = DOCS_URL) -> str:
    return sys_msg(
        'Tagentic1 (beta, release candidate) from the TER-AI project.\n\n'
        'It runs on one small machine: it answers one message at a time, a reply can take 1 to 3 minutes, '
        'and you may wait in a queue. Answers can be wrong.\n\n'
        'Type a message to chat. In a group, mention me or reply to my message.\n'
        '/add <information> - send a fact to the shared knowledge inbox. A fact checker verifies it against a '
        'real source before Tagentic1 uses it. Do not send passwords, phone numbers or anyone\'s personal data.\n'
        '/reset - start a new conversation (deletes this chat\'s history on the server).\n'
        '/help - show this message.\n\n'
        'Each chat has its own history. In a public chat Tagentic1 cannot read or write files or run code.\n\n'
        f'Questions, bug reports and ideas: {community}\nSet up your own bot: {docs}')


def welcome_owner(community: str = COMMUNITY_URL, docs: str = DOCS_URL) -> str:
    return sys_msg(
        'Tagentic1 (beta, release candidate), owner mode.\n'
        'You get the full model: User.md, Memory.md, the workspace and every tool. Writes, edits and runs '
        'wait for your Allow or Deny.\n'
        'One message at a time; a reply can take from tens of seconds to a few minutes. '
        'Owner chats go to the front of the queue.\n'
        '/add <information> - send a fact to the knowledge inbox (checked before use)\n'
        '/reset - start a new session\n/approve /deny - answer a permission request\n/help - this message\n\n'
        f'Community: {community}\nDocs: {docs}')


def log(msg: str) -> None:
    print(f"{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')} {msg}", flush=True)


def load_json(p: Path, default):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return default


def save_json(p: Path, obj) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1))
    os.chmod(tmp, 0o600)
    tmp.replace(p)


def _path(v, default: Path) -> Path:
    return Path(os.path.expanduser(str(v))) if v else default


@dataclass
class Config:
    token_file: Path | None = None
    owners: list = field(default_factory=list)
    memory_dir: Path = Path('~/.terai/tagentic')
    workspace: Path | None = None
    state_dir: Path | None = None
    relay_command: str = ''
    max_queue: int = 3
    turn_timeout: float = 900.0
    public: dict = field(default_factory=lambda: dict(PUBLIC_DEFAULTS))
    config_file: Path | None = None
    community_url: str = COMMUNITY_URL
    docs_url: str = DOCS_URL

    @property
    def allow_file(self) -> Path:
        return self.state_dir / 'allowlist.json'

    @property
    def pending_file(self) -> Path:
        return self.state_dir / 'pending.json'

    @property
    def state_file(self) -> Path:
        return self.state_dir / 'state.json'

    @property
    def public_dir(self) -> Path:
        return self.state_dir / 'public'

    @classmethod
    def load(cls, path=None, **over) -> 'Config':
        raw = load_json(_path(path, Path()), {}) if path else {}
        if path and not raw and not Path(os.path.expanduser(str(path))).exists():
            raise FileNotFoundError(f'config file not found: {path}')
        raw.update({k: v for k, v in over.items() if v not in (None, [], '')})
        home = os.environ.get('TERAI_TAGENTIC_HOME') or '~/.terai/tagentic'
        mem = _path(raw.get('memory_dir'), _path(home, Path()))
        state = _path(raw.get('state_dir'), mem / 'telegram')
        cfg = cls(token_file=_path(raw.get('token_file'), None) if raw.get('token_file') else None,
                  owners=[int(x) for x in raw.get('owners') or []],
                  memory_dir=mem, workspace=_path(raw.get('workspace'), state / 'workspace'), state_dir=state,
                  relay_command=raw.get('relay_command') or '', max_queue=int(raw.get('max_queue', 3)),
                  turn_timeout=float(raw.get('turn_timeout', 900)),
                  public={**PUBLIC_DEFAULTS, **(raw.get('public') or {})},
                  config_file=_path(path, None) if path else None,
                  community_url=raw.get('community_url') or COMMUNITY_URL, docs_url=raw.get('docs_url') or DOCS_URL)
        return cfg

    def public_cfg(self) -> dict:
        """Public limits, re-read from the config file on every call so edits apply without a restart."""
        if self.config_file:
            raw = load_json(self.config_file, None)
            if isinstance(raw, dict) and isinstance(raw.get('public'), dict):
                return {**PUBLIC_DEFAULTS, **raw['public']}
        return {**PUBLIC_DEFAULTS, **self.public}

    def read_token(self) -> str:
        t = os.environ.get(TOKEN_ENV, '').strip()
        if not t and self.token_file and self.token_file.exists():
            t = self.token_file.read_text().strip()
        return t


class TelegramAPI:
    def __init__(self, token: str):
        self._base = f'https://api.telegram.org/bot{token}/'

    def __repr__(self) -> str:          # never show the token
        return 'TelegramAPI(<token hidden>)'

    def call(self, method: str, http_timeout: float = 30, **params):
        data = urllib.parse.urlencode({k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                                       for k, v in params.items() if v is not None}).encode()
        req = urllib.request.Request(self._base + method, data=data)
        try:
            with urllib.request.urlopen(req, timeout=http_timeout) as r:
                body = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode())
            except Exception:
                body = {'ok': False, 'description': f'HTTP {e.code}'}
        except urllib.error.URLError as e:
            raise RuntimeError(f'{method}: network error {e.reason}') from None
        if not body.get('ok'):
            raise RuntimeError(f"{method}: {body.get('error_code', '')} {body.get('description', '')}")
        return body['result']


def split_text(text: str, limit: int = TG_LIMIT) -> list:
    parts = []
    while len(text) > limit:
        cut = text.rfind('\n', 0, limit)
        if cut < limit // 2:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].lstrip('\n')
    if text:
        parts.append(text)
    return parts or ['']


def format_reply(j: dict) -> str:
    """Model output only: the trace and the answer as the model wrote them, no header, no timing."""
    lines = []
    for st in j.get('trace') or []:
        args = st.get('args')
        if isinstance(args, (dict, list)):
            args = json.dumps(args, ensure_ascii=False)
        args = args or ''
        if len(args) > 120:
            args = args[:117] + '...'
        seg = f"• {st.get('think') or ''}"
        if st.get('tool'):
            seg += f" → {st['tool']}({args}) → {st.get('result_short') or ''}"
        lines.append(seg)
    out = '\n'.join(lines) + '\n\n' if lines else ''
    if j.get('answer') is not None:
        out += str(j['answer'])
    pa = j.get('pending_action')
    if pa:
        out += '\n\n' + sys_msg(f"Permission needed: {pa.get('summary') or pa.get('tool')}")
    return out.strip() or sys_msg('The model returned an empty answer.')


APPROVE_MARKUP = {'inline_keyboard': [[{'text': 'Allow', 'callback_data': 'approve'},
                                       {'text': 'Deny', 'callback_data': 'deny'}]]}


class Runner:
    """Runs one Tagentic1 relay turn and returns its JSON. ``cmd``: message, approve, deny or reset."""

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def argv(self, cmd: str, session: str, text, public: bool, sender: str) -> tuple:
        cfg = self.cfg
        if cfg.relay_command:
            name = ('p' + cmd if cmd in ('message', 'reset') else cmd) if public else cmd
            base = shlex.split(os.path.expanduser(cfg.relay_command))
            return base + [name, session] + (['-'] if text is not None else []), text
        base = [sys.executable, '-m', 'terai_router.tagentic.server', 'call', '--',
                '--memory-dir', str(cfg.memory_dir), '--session', session, '--json']
        if public:
            base += ['-w', str(cfg.public_dir / 'workspace'), '--public',
                     '--sessions-dir', str(cfg.public_dir / 'sessions'), '--sender', sender or 'public']
        else:
            base += ['-w', str(cfg.workspace)]
            if sender:
                base += ['--sender', sender]
        if cmd == 'message':
            base += ['--message', text or '']
        else:
            base += ['--' + cmd]
        return base, None

    def __call__(self, cmd: str, session: str, text=None, public: bool = False, sender: str = '') -> dict:
        args, stdin = self.argv(cmd, session, text, public, sender)
        env = dict(os.environ, TAGENTIC_SENDER=sender) if sender else None
        p = subprocess.run(args, input=stdin, capture_output=True, text=True, timeout=self.cfg.turn_timeout, env=env)
        out = (p.stdout or '').strip().splitlines()
        j = None
        if out:
            try:
                j = json.loads(out[-1])
            except Exception:
                j = None
        if p.returncode != 0 or j is None or 'error' in (j or {}):
            msg = (j or {}).get('error') or ' | '.join(((p.stderr or '').strip().splitlines() or ['no output'])[-2:])
            raise RuntimeError(str(msg)[:500])
        return j


def add_knowledge(cfg: Config, sender: str, info: str) -> dict:
    from . import knowledge
    try:
        e = knowledge.add(cfg.memory_dir, sender, info)
    except knowledge.Refused as ex:
        return {'ok': False, 'refused': str(ex)}
    return {'ok': True, 'id': e['id'], 'duplicate': e['duplicate'], 'status': e['status']}


class Bridge:
    def __init__(self, cfg: Config, tg, runner=None, adder=None, clock=time.time):
        self.cfg = cfg
        self.tg = tg
        self.runner = runner or Runner(cfg)
        self.adder = adder or (lambda sender, info: add_knowledge(cfg, sender, info))
        self.clock = clock
        self.q = queue.PriorityQueue()
        self.seq = 0
        self.lock = threading.Lock()
        self.queued = {}          # chat_id -> items waiting or running
        self.hits = {}            # (chat_id, kind) -> [timestamps]
        self.state = load_json(cfg.state_file, {'offset': 0})
        self.me = None

    # ---- who is who -----------------------------------------------------
    def owner_ids(self) -> set:
        allow = load_json(self.cfg.allow_file, {'chat_ids': []})
        return set(self.cfg.owners) | set(int(x) for x in allow.get('chat_ids', []))

    def is_owner_chat(self, chat: dict) -> bool:
        # owner mode only in a private chat; groups are always public
        return chat.get('type') == 'private' and chat.get('id') in self.owner_ids()

    def sender_of(self, frm: dict, chat: dict) -> str:
        s = f"telegram:{frm.get('id')}"
        if frm.get('username'):
            s += f" @{frm['username']}"
        if chat.get('type') != 'private':
            s += f" in chat {chat.get('id')}"
        if frm.get('id') in self.cfg.owners:
            s = 'owner (' + s + ')'
        return s

    def rate_ok(self, chat_id: int, kind: str, per_hour: int) -> bool:
        now = self.clock()
        with self.lock:
            h = [t for t in self.hits.get((chat_id, kind), []) if now - t < 3600]
            ok = len(h) < per_hour
            if ok:
                h.append(now)
            self.hits[(chat_id, kind)] = h
            return ok

    def send(self, chat_id: int, text: str, markup=None, reply_to=None) -> None:
        parts = split_text(text)
        for i, part in enumerate(parts):
            try:
                self.tg.call('sendMessage', chat_id=chat_id, text=part,
                             reply_markup=markup if i == len(parts) - 1 else None,
                             reply_to_message_id=reply_to if i == 0 else None,
                             allow_sending_without_reply='true' if reply_to else None)
            except Exception as e:
                log(f'send error chat={chat_id}: {e}')

    def record_pending(self, chat: dict, frm: dict) -> None:
        pend = load_json(self.cfg.pending_file, {})
        pend[str(chat['id'])] = {'chat_id': chat['id'], 'type': chat.get('type'), 'username': frm.get('username'),
                                 'first_name': frm.get('first_name'), 'time': datetime.now().astimezone().isoformat()}
        save_json(self.cfg.pending_file, pend)

    # ---- model worker -------------------------------------------------
    def typing_loop(self, chat_id: int, stop: threading.Event) -> None:
        while not stop.is_set():
            try:
                self.tg.call('sendChatAction', chat_id=chat_id, action='typing', http_timeout=10)
            except Exception:
                pass
            stop.wait(4.5)

    def run_turn(self, item: dict) -> None:
        chat_id, cmd, text, public = item['chat_id'], item['cmd'], item.get('text'), item['public']
        session = f'tgp-{chat_id}' if public else f'tg-{chat_id}'
        stop = threading.Event()
        if item.get('typing', True):
            threading.Thread(target=self.typing_loop, args=(chat_id, stop), daemon=True).start()
        t0 = self.clock()
        mode = 'public' if public else 'owner'
        try:
            log(f'turn start chat={chat_id} mode={mode} cmd={cmd} chars={len(text or "")}')
            j = self.runner(cmd, session, text if cmd == 'message' else None, public=public,
                            sender=item.get('sender', ''))
            if cmd == 'reset':
                self.send(chat_id, sys_msg('Conversation cleared. Send a new message.'))
            else:
                markup = APPROVE_MARKUP if j.get('pending_action') and not public else None
                self.send(chat_id, format_reply(j), markup, reply_to=item.get('reply_to'))
            log(f"turn done chat={chat_id} mode={mode} cmd={cmd} model_timing_s={j.get('timing_s')} "
                f"wall_s={self.clock() - t0:.1f} answer_chars={len(str(j.get('answer') or ''))} "
                f"pending={'yes' if j.get('pending_action') else 'no'}")
        except Exception as e:
            log(f'turn error chat={chat_id} mode={mode} cmd={cmd}: {e}')
            self.send(chat_id, sys_msg('Sorry, Tagentic1 hit an error. Try again later.') if public
                      else sys_msg(f'Tagentic1 error: {e}'))
        finally:
            stop.set()

    def _done(self, item: dict) -> None:
        with self.lock:
            n = self.queued.get(item['chat_id'], 1) - 1
            if n <= 0:
                self.queued.pop(item['chat_id'], None)
            else:
                self.queued[item['chat_id']] = n

    def process_one(self, block: bool = True) -> bool:
        try:
            _, _, item = self.q.get(block=block)
        except queue.Empty:
            return False
        try:
            self.run_turn(item)
        finally:
            self._done(item)
            self.q.task_done()
        return True

    def worker(self) -> None:
        while True:
            self.process_one()

    def enqueue(self, chat_id: int, cmd: str, text=None, public: bool = False, sender: str = '',
                reply_to=None) -> bool:
        cfg = self.cfg.public_cfg()
        with self.lock:
            waiting = self.q.unfinished_tasks
            if public:
                public_waiting = sum(1 for _, _, it in list(self.q.queue) if it['public'])
                if self.queued.get(chat_id):
                    msg = 'Please wait for my answer to your last message first.'
                elif public_waiting >= cfg['max_public_queue'] or waiting >= self.cfg.max_queue + 2:
                    msg = 'The queue is full (one message at a time on a small machine). Try again in a few minutes.'
                else:
                    msg = None
            else:
                msg = ('Your queue is full (Tagentic1 answers one message at a time). '
                       'Send again after you get an answer.') if self.queued.get(chat_id, 0) >= self.cfg.max_queue else None
            if msg is None:
                self.seq += 1
                self.queued[chat_id] = self.queued.get(chat_id, 0) + 1
                item = {'chat_id': chat_id, 'cmd': cmd, 'text': text, 'public': public, 'sender': sender,
                        'reply_to': reply_to}
                self.q.put((PUBLIC_PRIORITY if public else OWNER_PRIORITY, self.seq, item))
        if msg:
            self.send(chat_id, sys_msg(msg))
            return False
        if waiting > 0:
            self.send(chat_id, sys_msg(f'In the queue (position {waiting + 1}). Replies can take a few minutes.'
                                       if public else 'Queued. Owner chats go before public chats.'))
        return True

    # ---- /add -----------------------------------------------------------
    def handle_add(self, chat_id: int, sender: str, info: str, public: bool) -> None:
        if not info.strip():
            self.send(chat_id, sys_msg('Usage: /add <information>, one fact per message.'))
            return
        if public and not self.rate_ok(chat_id, 'add', self.cfg.public_cfg()['adds_per_hour']):
            self.send(chat_id, sys_msg('Too many /add messages this hour. Try again later.'))
            return
        try:
            j = self.adder(sender, info)
        except Exception as e:
            log(f'add error chat={chat_id}: {e}')
            self.send(chat_id, sys_msg('Sorry, /add failed. Try again later.') if public
                      else sys_msg(f'/add error: {e}'))
            return
        log(f"add chat={chat_id} mode={'public' if public else 'owner'} chars={len(info)} "
            f"result={j.get('id') or 'refused'}{' dup' if j.get('duplicate') else ''}")
        if not j.get('ok'):
            self.send(chat_id, sys_msg(f"Not stored: {j.get('refused')}"))
        elif j.get('duplicate'):
            self.send(chat_id, sys_msg(f"Already in the knowledge inbox as {j['id']}."))
        else:
            self.send(chat_id, sys_msg(f"Thanks. Saved as {j['id']}. A fact checker will verify it against a real "
                                       'source before Tagentic1 uses it.'))

    # ---- updates ------------------------------------------------------
    def addressed_text(self, m: dict, chat: dict):
        """Text meant for the bot, or None. Private chats: everything. Groups: commands, mentions, replies."""
        text = (m.get('text') or '').strip()
        if chat.get('type') == 'private':
            return text
        uname = '@' + (self.me or {}).get('username', '')
        if text.startswith('/'):
            head = text.split()[0]
            if '@' in head and head.split('@', 1)[1].lower() != uname[1:].lower():
                return None
            return text
        if uname != '@' and uname.lower() in text.lower():
            i = text.lower().index(uname.lower())
            return (text[:i] + text[i + len(uname):]).strip()
        rep = (m.get('reply_to_message') or {}).get('from') or {}
        if rep.get('id') and rep.get('id') == (self.me or {}).get('id'):
            return text
        return None

    def handle_message(self, m: dict) -> None:
        chat = m.get('chat') or {}
        frm = m.get('from') or {}
        chat_id = chat.get('id')
        if chat_id is None or chat.get('type') == 'channel':
            return
        public = not self.is_owner_chat(chat)
        if public and not self.cfg.public_cfg()['open']:
            log(f"denied chat={chat_id} type={chat.get('type')} (public closed)")
            if chat.get('type') == 'private':
                self.record_pending(chat, frm)
                self.send(chat_id, sys_msg('This bot is not open to the public right now.'))
            return
        text = self.addressed_text(m, chat)
        if text is None:
            return          # group message not meant for the bot: ignored, not logged
        if not text:
            if chat.get('type') == 'private' or m.get('text'):
                self.send(chat_id, sys_msg('Text messages only.'))
            return
        sender = self.sender_of(frm, chat)
        cmd = text.split()[0].split('@')[0].lower() if text.startswith('/') else ''
        if cmd in ('/start', '/help'):
            log(f"start chat={chat_id} mode={'public' if public else 'owner'} type={chat.get('type')}")
            self.send(chat_id, welcome_public(self.cfg.community_url, self.cfg.docs_url) if public
                      else welcome_owner(self.cfg.community_url, self.cfg.docs_url))
            return
        if cmd == '/add':
            rest = text.split(None, 1)
            self.handle_add(chat_id, sender, rest[1] if len(rest) > 1 else '', public)
            return
        if cmd == '/reset':
            self.enqueue(chat_id, 'reset', public=public, sender=sender)
            return
        if cmd in ('/approve', '/deny'):
            if public:
                self.send(chat_id, sys_msg('Nothing to approve: in a public chat Tagentic1 has no tools that '
                                           'need approval.'))
            else:
                self.enqueue(chat_id, cmd[1:])
            return
        if cmd:
            self.send(chat_id, sys_msg('Unknown command. Use /help.'))
            return
        if public and not self.rate_ok(chat_id, 'msg', self.cfg.public_cfg()['msgs_per_hour']):
            log(f'rate limited chat={chat_id}')
            self.send(chat_id, sys_msg('You reached the limit of messages per hour for this beta. Try again later.'))
            return
        self.enqueue(chat_id, 'message', text, public=public, sender=sender,
                     reply_to=m.get('message_id') if chat.get('type') != 'private' else None)

    def handle_callback(self, cq: dict) -> None:
        chat = (cq.get('message') or {}).get('chat') or {}
        try:
            self.tg.call('answerCallbackQuery', callback_query_id=cq['id'])
        except Exception:
            pass
        if chat.get('id') is None or not self.is_owner_chat(chat):
            return
        if cq.get('data') in ('approve', 'deny'):
            self.enqueue(chat['id'], cq['data'])

    def handle_update(self, u: dict) -> None:
        if u.get('message'):
            self.handle_message(u['message'])
        elif u.get('callback_query'):
            self.handle_callback(u['callback_query'])

    def set_commands(self) -> None:
        self.tg.call('setMyCommands', commands=[
            {'command': 'help', 'description': 'How to use this bot'},
            {'command': 'add', 'description': 'Send a fact to the knowledge inbox (checked before use)'},
            {'command': 'reset', 'description': 'Start a new conversation'}])
        for oid in self.cfg.owners:
            self.tg.call('setMyCommands', scope={'type': 'chat', 'chat_id': oid}, commands=[
                {'command': 'help', 'description': 'How to use this bot'},
                {'command': 'add', 'description': 'Send a fact to the knowledge inbox'},
                {'command': 'reset', 'description': 'Start a new Tagentic1 session'},
                {'command': 'approve', 'description': 'Allow the action the model asked for'},
                {'command': 'deny', 'description': 'Refuse the action the model asked for'}])

    def start(self) -> None:
        self.me = self.tg.call('getMe')
        log(f"bridge up as @{self.me.get('username')} (id {self.me.get('id')}); owners={len(self.owner_ids())}; "
            f"public={self.cfg.public_cfg()}")
        (self.cfg.public_dir / 'sessions').mkdir(parents=True, exist_ok=True)
        (self.cfg.public_dir / 'workspace').mkdir(parents=True, exist_ok=True)
        self.cfg.workspace.mkdir(parents=True, exist_ok=True)
        for method in ('deleteWebhook', 'set_commands'):
            try:
                self.set_commands() if method == 'set_commands' else self.tg.call(method)
            except Exception as e:
                log(f'{method} (not fatal): {e}')

    def poll_once(self, timeout: int = 50) -> int:
        ups = self.tg.call('getUpdates', http_timeout=timeout + 20, timeout=timeout,
                           offset=self.state.get('offset', 0), allowed_updates=['message', 'callback_query'])
        for u in ups:
            self.state['offset'] = u['update_id'] + 1
            save_json(self.cfg.state_file, self.state)
            try:
                self.handle_update(u)
            except Exception as e:
                log(f'update error: {e}')
        return len(ups)

    def run(self) -> None:
        self.start()
        threading.Thread(target=self.worker, daemon=True).start()
        backoff = 2
        while True:
            try:
                self.poll_once()
                backoff = 2
            except Exception as e:
                log(f'getUpdates error: {e}')
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog='terai tagentic telegram',
                                 description='Run Tagentic1 (beta) as a Telegram bot with your own bot token.')
    ap.add_argument('--config', '-c', default=None, help='JSON config file (see --example-config)')
    ap.add_argument('--token-file', default=None, help=f'file with the bot token (default: ${TOKEN_ENV})')
    ap.add_argument('--owner', type=int, action='append', default=[], help='owner chat id (repeatable)')
    ap.add_argument('--memory-dir', default=None, help='Tagentic1 memory folder')
    ap.add_argument('--workspace', '-w', default=None, help='owner workspace folder')
    ap.add_argument('--state-dir', default=None, help='bridge state folder (offset, allowlist, public sessions)')
    ap.add_argument('--relay-command', default=None,
                    help='advanced: run turns through this command instead of terai_router.tagentic.server')
    ap.add_argument('--check', action='store_true', help='call getMe with the token, print the bot name, exit')
    ap.add_argument('--example-config', action='store_true', help='print an example config file and exit')
    return ap


def main(argv=None, tg_factory=TelegramAPI) -> int:
    args = build_parser().parse_args(argv)
    if args.example_config:
        print(json.dumps(EXAMPLE_CONFIG, indent=2))
        return 0
    try:
        cfg = Config.load(args.config, token_file=args.token_file, owners=args.owner or None,
                          memory_dir=args.memory_dir, workspace=args.workspace, state_dir=args.state_dir,
                          relay_command=args.relay_command)
    except FileNotFoundError as e:
        print(f'terai tagentic telegram: {e}', file=sys.stderr)
        return 2
    token = cfg.read_token()
    if not token:
        print(f'terai tagentic telegram: no bot token. Set ${TOKEN_ENV} or pass --token-file '
              '(create a bot with @BotFather first).', file=sys.stderr)
        return 2
    tg = tg_factory(token)
    if args.check:
        try:
            me = tg.call('getMe')
        except Exception as e:
            print(f'terai tagentic telegram: {e}', file=sys.stderr)
            return 1
        print(f"ok: @{me.get('username')} (id {me.get('id')})")
        return 0
    Bridge(cfg, tg).run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
