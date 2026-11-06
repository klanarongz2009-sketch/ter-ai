# SPDX-License-Identifier: LicenseRef-TER-AI-1.0
"""Shared knowledge for Tagentic1: Knowledge-inbox.md (submitted, waiting for a fact check) and Knowledge.md
(verified only, loaded into the prompt).

Anyone may submit (Telegram /add, other AIs and sub-agents, Bogus) - decision 1b + 1c, 2026-11-07.
Nothing reaches Knowledge.md until the Fact checker verified it against a real source - decision 2a.

Inbox line (one entry per line, string fields are JSON strings so the text stays verbatim):
    - K0001 · 2026-11-07 01:10 +07 · from="telegram:123 @name" · status=pending · text="..." · reason="" · source=""

CLI (python -m terai_router.tagentic.knowledge --home DIR ...):
    add --sender NAME (TEXT | -)          submit; prints the id, or the reason it was refused (exit 3)
    pending [--json]                      entries that wait for the fact check
    verify ID --fact TEXT --source URL [--reason TEXT]   move into Knowledge.md
    reject ID --reason TEXT [--source URL]
    list [--json]
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import fcntl
import json
import os
import re
import sys
from pathlib import Path

from . import memory as M

INBOX = 'Knowledge-inbox.md'
KNOWLEDGE = 'Knowledge.md'
LOCK = '.knowledge.lock'
TEXT_MAX = 1000
STATUSES = ('pending', 'verified', 'rejected')
ICT = _dt.timezone(_dt.timedelta(hours=7))
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

INBOX_HEAD = (
    '# Knowledge-inbox.md\n\n'
    'ไฟล์เพิ่มข้อมูลของ Tagentic1 ทุกคนส่งได้ (Telegram /add, AI และ sub-agent ตัวอื่น, Bogus) '
    'ข้อมูลในไฟล์นี้ยังไม่ถูกใช้ตอบ จนกว่า Fact checker จะตรวจกับแหล่งอ้างอิงจริงแล้วย้ายเข้า Knowledge.md\n'
    'หนึ่งบรรทัดต่อหนึ่งรายการ: id · วันที่เวลา · from (ผู้ส่ง) · status (pending/verified/rejected) · '
    'text (ข้อความ verbatim) · reason · source\n'
    'ไม่รับ secret, เบอร์โทร, เลขบัตร, อีเมล หรือข้อมูลส่วนตัวของคนอื่น\n\n'
    '## Entries\n')
KNOWLEDGE_HEAD = (
    '# Knowledge.md\n\n'
    'ความรู้กลางของ Tagentic1 ที่ตรวจกับแหล่งอ้างอิงจริงแล้วเท่านั้น (ย้ายมาจาก Knowledge-inbox.md โดย Fact checker) '
    'ใช้ตอบคำถามความรู้ทั่วไปก่อนความรู้ของโมเดลเอง\n\n'
    '## Facts\n')

QS = r'"(?:[^"\\]|\\.)*"'
LINE = re.compile(r'^- (K\d{4,}) · ([^·]+?) · from=(' + QS + r') · status=(\w+) · text=(' + QS + r') · reason=('
                  + QS + r') · source=(' + QS + r')\s*$')


class Refused(ValueError):
    """The submission was not stored; the message says why."""


def _home(home) -> Path:
    h = Path(home).expanduser() if home else M.default_home()
    h.mkdir(parents=True, exist_ok=True)
    return h


@contextlib.contextmanager
def _locked(h: Path):
    with open(h / LOCK, 'a') as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def init(home=None) -> Path:
    h = _home(home)
    for name, head in ((INBOX, INBOX_HEAD), (KNOWLEDGE, KNOWLEDGE_HEAD)):
        p = h / name
        if not p.exists():
            p.write_text(head, encoding='utf-8')
    return h


def check_text(text: str) -> str:
    """Return the text as sent (only outer whitespace removed), or raise Refused."""
    t = (text or '').strip()
    if not t:
        raise Refused('empty: write the information after /add')
    if len(t) > TEXT_MAX:
        raise Refused(f'too long ({len(t)} characters, max {TEXT_MAX}); send one fact at a time')
    if M.SECRET.search(t):
        raise Refused('looks like a secret (password, key or token); secrets are never stored')
    if M.PHONE.search(t) or M.CARD.search(t):
        raise Refused('looks like a phone, card or ID number; personal numbers are never stored')
    if EMAIL.search(t):
        raise Refused('contains an email address; personal contact data is never stored')
    return t


def _clean_sender(sender: str) -> str:
    s = ' '.join(str(sender or '').split())[:120]
    if not s:
        raise Refused('sender is required (telegram:<chat id> or the AI name)')
    return s


def parse(line: str):
    m = LINE.match(line.rstrip('\n'))
    if not m:
        return None
    i, ts, frm, st, text, reason, source = m.groups()
    return {'id': i, 'time': ts.strip(), 'from': json.loads(frm), 'status': st, 'text': json.loads(text),
            'reason': json.loads(reason), 'source': json.loads(source)}


def render(e: dict) -> str:
    q = lambda s: json.dumps(s or '', ensure_ascii=False)
    return (f"- {e['id']} · {e['time']} · from={q(e['from'])} · status={e['status']} · text={q(e['text'])} · "
            f"reason={q(e['reason'])} · source={q(e['source'])}")


def _read(h: Path):
    lines = (h / INBOX).read_text(encoding='utf-8').splitlines()
    return lines, [(n, parse(l)) for n, l in enumerate(lines) if parse(l)]


def entries(home=None) -> list:
    h = init(home)
    return [e for _, e in _read(h)[1]]


def pending(home=None) -> list:
    return [e for e in entries(home) if e['status'] == 'pending']


def add(home, sender: str, text: str, now: _dt.datetime | None = None) -> dict:
    """Store one submission as pending. Raises Refused (nothing is written) for secrets, phones, emails..."""
    t = check_text(text)
    s = _clean_sender(sender)
    h = init(home)
    with _locked(h):
        lines, es = _read(h)
        for _, e in es:
            if e['text'] == t and e['status'] in ('pending', 'verified'):
                return dict(e, duplicate=True)
        n = max([int(e['id'][1:]) for _, e in es] or [0]) + 1
        ts = (now or _dt.datetime.now(ICT)).astimezone(ICT).strftime('%Y-%m-%d %H:%M +07')
        e = {'id': f'K{n:04d}', 'time': ts, 'from': s, 'status': 'pending', 'text': t, 'reason': '', 'source': ''}
        with open(h / INBOX, 'a', encoding='utf-8') as fh:
            fh.write(render(e) + '\n')
    return dict(e, duplicate=False)


def _set(home, kid: str, status: str, reason: str, source: str) -> dict:
    h = init(home)
    with _locked(h):
        lines, es = _read(h)
        for n, e in es:
            if e['id'] == kid:
                if e['status'] != 'pending':
                    raise Refused(f"{kid} is already {e['status']}")
                e.update(status=status, reason=reason, source=source)
                lines[n] = render(e)
                (h / INBOX).write_text('\n'.join(lines) + '\n', encoding='utf-8')
                return e
    raise Refused(f'no entry {kid}')


def verify(home, kid: str, fact: str, source: str, reason: str = '', today: str | None = None) -> dict:
    """Mark verified and add the checked fact (with its source) to Knowledge.md."""
    fact = ' '.join((fact or '').split())
    if not fact or not (source or '').strip():
        raise Refused('verify needs --fact and --source')
    check_text(fact)
    e = _set(home, kid, 'verified', reason or 'ตรงกับแหล่งอ้างอิง', source.strip())
    h = _home(home)
    day = today or _dt.datetime.now(ICT).strftime('%Y-%m-%d')
    with _locked(h):
        with open(h / KNOWLEDGE, 'a', encoding='utf-8') as fh:
            fh.write(f'- {fact} (ที่มา: {source.strip()} · {kid} ตรวจ {day})\n')
    return e


def reject(home, kid: str, reason: str, source: str = '') -> dict:
    if not (reason or '').strip():
        raise Refused('reject needs --reason')
    return _set(home, kid, 'rejected', reason.strip(), (source or '').strip())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='tagentic-knowledge')
    ap.add_argument('--home', default=None, help='memory folder (default $TERAI_TAGENTIC_HOME)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add'); a.add_argument('--sender', required=True); a.add_argument('text')
    for name in ('pending', 'list'):
        sub.add_parser(name).add_argument('--json', action='store_true')
    v = sub.add_parser('verify'); v.add_argument('id'); v.add_argument('--fact', required=True)
    v.add_argument('--source', required=True); v.add_argument('--reason', default='')
    r = sub.add_parser('reject'); r.add_argument('id'); r.add_argument('--reason', required=True)
    r.add_argument('--source', default='')
    args = ap.parse_args(argv)
    try:
        if args.cmd == 'add':
            text = sys.stdin.read() if args.text == '-' else args.text
            e = add(args.home, args.sender, text)
            print(json.dumps({'ok': True, 'id': e['id'], 'duplicate': e['duplicate'], 'status': e['status']},
                             ensure_ascii=False))
        elif args.cmd in ('pending', 'list'):
            es = pending(args.home) if args.cmd == 'pending' else entries(args.home)
            print(json.dumps(es, ensure_ascii=False, indent=1) if args.json else
                  '\n'.join(render(e) for e in es) or '(none)')
        elif args.cmd == 'verify':
            e = verify(args.home, args.id, args.fact, args.source, args.reason)
            print(json.dumps({'ok': True, 'id': e['id'], 'status': e['status']}, ensure_ascii=False))
        else:
            e = reject(args.home, args.id, args.reason, args.source)
            print(json.dumps({'ok': True, 'id': e['id'], 'status': e['status']}, ensure_ascii=False))
    except Refused as ex:
        print(json.dumps({'ok': False, 'refused': str(ex)}, ensure_ascii=False))
        return 3
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
