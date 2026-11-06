# SPDX-License-Identifier: LicenseRef-TER-AI-1.0
"""Tagentic1 Telegram bridge: offline tests (fake Telegram API, fake model runner, no network)."""
import json

import pytest

from terai_router.tagentic import telegram as tg

OWNER = 111
OTHER = 222
BOT = {'id': 999, 'username': 'example_tagentic_bot', 'is_bot': True}
ADD_PROMPT = '[System] Send the information in your next message. /cancel to stop.'


class FakeTG:
    def __init__(self, updates=None):
        self.calls = []
        self.updates = list(updates or [])

    def call(self, method, http_timeout=30, **params):
        self.calls.append((method, params))
        if method == 'getMe':
            return dict(BOT)
        if method == 'getUpdates':
            ups, self.updates = self.updates, []
            return ups
        return True

    def sent(self, chat_id=None):
        return [p for m, p in self.calls if m == 'sendMessage' and (chat_id is None or p['chat_id'] == chat_id)]

    def texts(self, chat_id=None):
        return [p['text'] for p in self.sent(chat_id)]


class FakeRunner:
    def __init__(self, reply=None, error=None):
        self.calls = []
        self.reply = reply or {'answer': 'model says hi', 'trace': [], 'pending_action': None, 'timing_s': 1.0}
        self.error = error

    def __call__(self, cmd, session, text=None, public=False, sender=''):
        self.calls.append({'cmd': cmd, 'session': session, 'text': text, 'public': public, 'sender': sender})
        if self.error:
            raise RuntimeError(self.error)
        return dict(self.reply)


@pytest.fixture
def cfg(tmp_path):
    return tg.Config.load(None, owners=[OWNER], memory_dir=str(tmp_path / 'mem'), state_dir=str(tmp_path / 'st'))


def make(cfg, runner=None, adder=None, now=None):
    clock = now or (lambda: 1000.0)
    b = tg.Bridge(cfg, FakeTG(), runner or FakeRunner(), adder=adder, clock=clock)
    b.me = dict(BOT)
    return b


def msg(chat_id, text, ctype='private', from_id=None, **extra):
    m = {'message_id': 5, 'chat': {'id': chat_id, 'type': ctype}, 'from': {'id': from_id or chat_id}, 'text': text}
    m.update(extra)
    return m


def drain(b):
    while b.process_one(block=False):
        pass


def test_owner_vs_public_mode(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OWNER, 'hello'))
    drain(b)
    b.handle_message(msg(OTHER, 'hello'))
    drain(b)
    assert [c['public'] for c in r.calls] == [False, True]
    assert r.calls[0]['session'] == f'tg-{OWNER}' and r.calls[1]['session'] == f'tgp-{OTHER}'
    assert b.tg.texts(OWNER) == ['model says hi'] and b.tg.texts(OTHER) == ['model says hi']


def test_groups_are_always_public_and_need_address(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(-5, 'just chatting', ctype='group', from_id=OWNER))
    assert r.calls == [] and b.tg.sent() == []
    b.handle_message(msg(-5, '@example_tagentic_bot what is 2+2', ctype='group', from_id=OWNER))
    drain(b)
    assert r.calls[0]['public'] is True and r.calls[0]['text'] == 'what is 2+2'
    assert b.tg.sent(-5)[0]['reply_to_message_id'] == 5


def test_model_output_has_no_header_or_timing(cfg):
    b = make(cfg, FakeRunner({'answer': 'สวัสดีครับ', 'trace': [], 'timing_s': 3.2}))
    b.handle_message(msg(OWNER, 'hi'))
    drain(b)
    assert b.tg.texts(OWNER) == ['สวัสดีครับ']


def test_permission_request_is_english_with_buttons(cfg):
    reply = {'answer': None, 'trace': [{'think': 'need a file', 'tool': 'write_file', 'args': {'path': 'a.txt'},
                                        'result_short': ''}],
             'pending_action': {'tool': 'write_file', 'summary': 'write file a.txt (3 bytes)'}}
    b = make(cfg, FakeRunner(reply))
    b.handle_message(msg(OWNER, 'make a file'))
    drain(b)
    sent = b.tg.sent(OWNER)[-1]
    assert '[System] Permission needed: write file a.txt (3 bytes)' in sent['text']
    assert sent['reply_markup'] == tg.APPROVE_MARKUP
    labels = [btn['text'] for btn in tg.APPROVE_MARKUP['inline_keyboard'][0]]
    assert labels == ['Allow', 'Deny']


def test_public_cannot_approve_and_callbacks_ignored(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OTHER, '/approve'))
    b.handle_callback({'id': 'x', 'data': 'approve', 'message': {'chat': {'id': OTHER, 'type': 'private'}}})
    drain(b)
    assert r.calls == []
    assert b.tg.texts(OTHER)[0].startswith('[System] Nothing to approve')
    b.handle_callback({'id': 'y', 'data': 'deny', 'message': {'chat': {'id': OWNER, 'type': 'private'}}})
    drain(b)
    assert r.calls[-1]['cmd'] == 'deny' and r.calls[-1]['public'] is False


def test_start_help_english_with_community_link(cfg):
    b = make(cfg)
    b.handle_message(msg(OTHER, '/start'))
    b.handle_message(msg(OWNER, '/help'))
    pub, own = b.tg.texts(OTHER)[0], b.tg.texts(OWNER)[0]
    for t in (pub, own):
        assert t.startswith('[System] ')
        assert tg.COMMUNITY_URL in t and tg.DOCS_URL in t
        assert all(ord(ch) < 0x0E00 or ord(ch) > 0x0E7F for ch in t)   # no Thai in bot-written text
    assert 'owner mode' in own and 'owner mode' not in pub


def test_rate_limit_public_only(cfg):
    t = [1000.0]
    r = FakeRunner()
    b = make(cfg, r, now=lambda: t[0])
    for i in range(7):
        b.handle_message(msg(OTHER, f'q{i}'))
        drain(b)
    assert len(r.calls) == 6
    assert 'limit of messages per hour' in b.tg.texts(OTHER)[-1]
    t[0] += 3601
    b.handle_message(msg(OTHER, 'later'))
    drain(b)
    assert len(r.calls) == 7
    for i in range(8):
        b.handle_message(msg(OWNER, f'o{i}'))
        drain(b)
    assert len([c for c in r.calls if not c['public']]) == 8


def test_public_one_message_at_a_time(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OTHER, 'one'))
    b.handle_message(msg(OTHER, 'two'))
    assert b.tg.texts(OTHER) == ['[System] Please wait for my answer to your last message first.']


def test_owner_goes_first(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OTHER, 'public first'))
    b.handle_message(msg(OWNER, 'owner second'))
    assert b.tg.texts(OWNER) == ['[System] Queued. Owner chats go before public chats.']
    drain(b)
    assert [c['text'] for c in r.calls] == ['owner second', 'public first']


def test_add_knowledge_messages(cfg):
    results = iter([{'ok': True, 'id': 'K0001', 'duplicate': False},
                    {'ok': True, 'id': 'K0001', 'duplicate': True},
                    {'ok': False, 'refused': 'looks like a phone number'}])
    seen = []
    b = make(cfg, adder=lambda s, i: (seen.append((s, i)), next(results))[1])
    for _ in range(3):
        b.handle_message(msg(OTHER, '/add The sky is blue'))
    b.handle_message(msg(OTHER, '/add'))
    assert b.tg.texts(OTHER) == [
        '[System] Thanks. Saved as K0001. A fact checker will verify it against a real source before Tagentic1 uses it.',
        '[System] Already in the knowledge inbox as K0001.',
        '[System] Not stored: looks like a phone number',
        ADD_PROMPT]
    assert b.tg.sent(OTHER)[-1]['reply_markup'] == tg.ADD_PROMPT_MARKUP
    assert seen[0] == (f'telegram:{OTHER}', 'The sky is blue') and len(seen) == 3   # bare /add stores nothing


def test_add_knowledge_real_inbox_refuses_phone(cfg):
    b = make(cfg)
    b.handle_message(msg(OTHER, '/add call me at 0812345678'))
    b.handle_message(msg(OTHER, '/add Python was first released in 1991'))
    texts = b.tg.texts(OTHER)
    assert texts[0].startswith('[System] Not stored:')
    assert texts[1].startswith('[System] Thanks. Saved as K0001.')
    assert 'Python was first released in 1991' in (cfg.memory_dir / 'Knowledge-inbox.md').read_text()


def test_errors_public_hides_detail(cfg):
    b = make(cfg, FakeRunner(error='/secret/path failed'))
    b.handle_message(msg(OTHER, 'x'))
    drain(b)
    b.handle_message(msg(OWNER, 'x'))
    drain(b)
    assert b.tg.texts(OTHER) == ['[System] Sorry, Tagentic1 hit an error. Try again later.']
    assert b.tg.texts(OWNER) == ['[System] Tagentic1 error: /secret/path failed']


def test_reset_and_unknown_and_non_text(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OTHER, '/reset'))
    drain(b)
    b.handle_message(msg(OTHER, '/foo'))
    b.handle_message({'message_id': 1, 'chat': {'id': OTHER, 'type': 'private'}, 'from': {'id': OTHER}})
    assert r.calls[0]['cmd'] == 'reset'
    assert b.tg.texts(OTHER) == ['[System] Conversation cleared. Send a new message.',
                                 '[System] Unknown command. Use /help.', '[System] Text messages only.']


def test_public_closed_and_allowlist(cfg, tmp_path):
    cfgfile = tmp_path / 'c.json'
    cfgfile.write_text(json.dumps({'owners': [OWNER], 'memory_dir': str(tmp_path / 'mem'),
                                   'state_dir': str(tmp_path / 'st'), 'public': {'open': False}}))
    c = tg.Config.load(str(cfgfile))
    r = FakeRunner()
    b = make(c, r)
    b.handle_message(msg(OTHER, 'hello'))
    assert b.tg.texts(OTHER) == ['[System] This bot is not open to the public right now.']
    assert str(OTHER) in json.loads(c.pending_file.read_text())
    tg.save_json(c.allow_file, {'chat_ids': [OTHER]})
    b.handle_message(msg(OTHER, 'hello again'))
    drain(b)
    assert r.calls[0]['public'] is False


def test_poll_once_saves_offset(cfg):
    b = make(cfg)
    b.tg.updates = [{'update_id': 41, 'message': msg(OTHER, '/help')}]
    assert b.poll_once(timeout=0) == 1
    assert json.loads(cfg.state_file.read_text())['offset'] == 42


def test_split_text():
    parts = tg.split_text('a' * 9000)
    assert [len(p) for p in parts] == [4000, 4000, 1000]


def test_runner_argv_builds_public_restrictions(cfg):
    run = tg.Runner(cfg)
    argv, stdin = run.argv('message', 'tgp-1', 'hi', True, 'telegram:1')
    assert '--public' in argv and '--sessions-dir' in argv and argv[argv.index('--message') + 1] == 'hi'
    assert stdin is None
    argv, _ = run.argv('approve', 'tg-1', None, False, '')
    assert '--public' not in argv and '--approve' in argv
    cfg.relay_command = 'my-relay.sh'
    argv, stdin = run.argv('message', 'tgp-1', 'hi', True, 'telegram:1')
    assert argv == ['my-relay.sh', 'pmessage', 'tgp-1', '-'] and stdin == 'hi'


def test_main_needs_token_and_never_prints_it(cfg, tmp_path, monkeypatch, capsys):
    monkeypatch.delenv(tg.TOKEN_ENV, raising=False)
    assert tg.main(['--state-dir', str(tmp_path / 's')]) == 2
    assert 'no bot token' in capsys.readouterr().err
    tok = tmp_path / 'tok'
    tok.write_text('123:SECRET-TOKEN\n')
    assert tg.main(['--token-file', str(tok), '--check'], tg_factory=lambda t: FakeTG()) == 0
    out = capsys.readouterr()
    assert 'ok: @example_tagentic_bot' in out.out and 'SECRET' not in out.out + out.err
    assert 'hidden' in repr(tg.TelegramAPI('123:SECRET'))


def test_cli_dispatch_and_example_config(capsys):
    from terai_router.tagentic.cli import main
    assert main(['telegram', '--example-config']) == 0
    ex = json.loads(capsys.readouterr().out)
    assert ex['owners'] == [123456789] and ':' not in ex['token_file']


def inbox(cfg):
    p = cfg.memory_dir / 'Knowledge-inbox.md'
    return p.read_text() if p.exists() else ''


def test_bare_add_then_next_message_goes_to_inbox(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OTHER, '/add'))
    assert b.tg.texts(OTHER) == [ADD_PROMPT]
    assert b.tg.sent(OTHER)[0]['reply_markup'] == {'force_reply': True, 'selective': True,
                                                   'input_field_placeholder': 'One fact'}
    assert inbox(cfg).count('status=') == 0                       # nothing stored for the bare /add
    b.handle_message(msg(OTHER, 'Python was first released in 1991', from_id=OTHER))
    drain(b)
    assert r.calls == []                                          # the model never sees it
    assert b.tg.texts(OTHER)[-1].startswith('[System] Thanks. Saved as K0001.')
    text = inbox(cfg)
    assert 'Python was first released in 1991' in text and f'telegram:{OTHER}' in text and 'status=pending' in text
    b.handle_message(msg(OTHER, 'and now a normal chat'))          # the wait is over after one message
    drain(b)
    assert [c['text'] for c in r.calls] == ['and now a normal chat']


def test_add_with_bot_name_is_a_bare_add(cfg):
    b = make(cfg)
    b.handle_message(msg(OTHER, '/add@example_tagentic_bot'))
    assert b.tg.texts(OTHER) == [ADD_PROMPT]
    b.handle_message(msg(OTHER, 'Bangkok is the capital of Thailand'))
    assert 'Bangkok is the capital of Thailand' in inbox(cfg)


def test_waiting_add_keeps_the_filters(cfg):
    b = make(cfg)
    for bad in ('mail me at someone@example.com', 'call me at 0812345678'):
        b.handle_message(msg(OTHER, '/add'))
        b.handle_message(msg(OTHER, bad))
        assert b.tg.texts(OTHER)[-1].startswith('[System] Not stored:')
    assert inbox(cfg).count('status=') == 0
    b.handle_message(msg(OTHER, 'a normal message after a refusal'))   # refused also ends the wait
    assert b.tg.texts(OTHER)[-1] != ADD_PROMPT and inbox(cfg).count('status=') == 0


def test_waiting_add_counts_against_adds_not_messages(cfg):
    added = []
    r = FakeRunner()
    b = make(cfg, r, adder=lambda s, i: (added.append(i), {'ok': True, 'id': f'K{len(added):04d}',
                                                             'duplicate': False})[1])
    for i in range(10):
        b.handle_message(msg(OTHER, '/add'))
        b.handle_message(msg(OTHER, f'fact {i}'))
    assert len(added) == 10 and r.calls == []
    b.handle_message(msg(OTHER, '/add'))
    b.handle_message(msg(OTHER, 'fact 10'))
    assert len(added) == 10
    assert b.tg.texts(OTHER)[-1] == '[System] Too many /add messages this hour. Try again later.'
    for i in range(6):                                            # messages per hour are untouched
        b.handle_message(msg(OTHER, f'q{i}'))
        drain(b)
    assert len(r.calls) == 6


def test_waiting_add_times_out(cfg):
    t = [1000.0]
    r = FakeRunner()
    b = make(cfg, r, now=lambda: t[0])
    b.handle_message(msg(OTHER, '/add'))
    t[0] += tg.ADD_WAIT_S + 1
    b.handle_message(msg(OTHER, 'too late for the inbox'))
    drain(b)
    assert [c['text'] for c in r.calls] == ['too late for the inbox']
    assert inbox(cfg).count('status=') == 0


def test_cancel(cfg):
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(OTHER, '/cancel'))
    b.handle_message(msg(OWNER, '/add'))
    b.handle_message(msg(OWNER, '/cancel'))
    b.handle_message(msg(OWNER, 'just chat'))
    drain(b)
    assert b.tg.texts(OTHER) == ['[System] Nothing to cancel.']
    assert b.tg.texts(OWNER)[:2] == [ADD_PROMPT, '[System] Cancelled.']
    assert [c['text'] for c in r.calls] == ['just chat'] and inbox(cfg).count('status=') == 0


def test_other_command_ends_waiting_add(cfg):
    b = make(cfg)
    b.handle_message(msg(OTHER, '/add'))
    b.handle_message(msg(OTHER, '/add The sky is blue'))           # stored directly, as before
    b.handle_message(msg(OTHER, 'not for the inbox'))
    drain(b)
    text = inbox(cfg)
    assert 'The sky is blue' in text and 'not for the inbox' not in text
    b.handle_message(msg(OTHER, '/add'))
    b.handle_message(msg(OTHER, '/help'))
    b.handle_message(msg(OTHER, '/cancel'))
    assert b.tg.texts(OTHER)[-1] == '[System] Nothing to cancel.'


def test_group_waiting_add_only_from_the_same_user(cfg):
    A, B = 301, 302
    r = FakeRunner()
    b = make(cfg, r)
    b.handle_message(msg(-7, '/add@example_tagentic_bot', ctype='group', from_id=A, message_id=40))
    prompt = b.tg.sent(-7)[0]
    assert prompt['text'] == ADD_PROMPT and prompt['reply_to_message_id'] == 40
    assert prompt['reply_markup']['selective'] is True
    reply_to_bot = {'from': dict(BOT), 'message_id': 41}
    b.handle_message(msg(-7, 'B wants this stored', ctype='group', from_id=B, reply_to_message=reply_to_bot))
    drain(b)
    assert 'B wants this stored' not in inbox(cfg)
    assert [c['text'] for c in r.calls] == ['B wants this stored']   # handled as a normal public message
    b.handle_message(msg(-7, '/cancel', ctype='group', from_id=B))
    assert b.tg.texts(-7)[-1] == '[System] Nothing to cancel.'
    b.handle_message(msg(-7, 'Water boils at 100 C at sea level', ctype='group', from_id=A,
                         reply_to_message=reply_to_bot))
    text = inbox(cfg)
    assert 'Water boils at 100 C at sea level' in text and f'telegram:{A}' in text and 'in chat -7' in text
    assert len(r.calls) == 1


def test_help_mentions_both_ways_and_cancel_in_menu(cfg):
    b = make(cfg)
    b.handle_message(msg(OTHER, '/help'))
    b.handle_message(msg(OWNER, '/start'))
    for t in (b.tg.texts(OTHER)[0], b.tg.texts(OWNER)[0]):
        assert '/add <information>' in t and 'tap /add' in t and '/cancel' in t
        assert all(ord(ch) < 0x0E00 or ord(ch) > 0x0E7F for ch in t)
    b.set_commands()
    menus = [p['commands'] for m, p in b.tg.calls if m == 'setMyCommands']
    assert len(menus) == 2 and all('cancel' in [c['command'] for c in cmds] for cmds in menus)
