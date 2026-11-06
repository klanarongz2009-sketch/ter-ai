# SPDX-License-Identifier: LicenseRef-TER-AI-1.0
"""Tagentic1 shared knowledge (Knowledge-inbox.md -> fact check -> Knowledge.md) and the public-chat mode.
The model is a mock: no weights."""
import io
import json

import pytest

from terai_router.tagentic import agent as A
from terai_router.tagentic import cli as C
from terai_router.tagentic import knowledge as K
from terai_router.tagentic import memory as M
from terai_router.tagentic.tools import PUBLIC_TOOLS, Toolbox
from terai_router.tagentic.workspace import Workspace


class FakeLM:
    model = 'e2b'

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []

    def chat(self, messages, **kw):
        self.calls.append({'messages': [dict(m) for m in messages], **kw})
        return self.replies.pop(0) if self.replies else json.dumps({'think': 'ok', 'tool': 'final', 'answer': '-'})


def step(tool, args):
    return json.dumps({'think': 'step', 'tool': tool, 'args': args}, ensure_ascii=False)


@pytest.fixture
def env(tmp_path):
    ws, pub = tmp_path / 'ws', tmp_path / 'pubws'
    ws.mkdir(); pub.mkdir()
    (ws / 'secret-plan.txt').write_text('owner workspace file', encoding='utf-8')
    home = tmp_path / 'home'
    M.init_home(home)
    (home / 'User.md').write_text('# User.md\n\n## Profile\n- ชื่อ: OWNER-NAME-123\n', encoding='utf-8')
    (home / 'Memory.md').write_text('# Memory.md\n- OWNER-MEMORY-456\n', encoding='utf-8')
    return ws, pub, home


# ------------------------------------------------------------------------------------------- inbox
def test_add_writes_one_verbatim_pending_line(env):
    _, _, home = env
    e = K.add(home, 'telegram:111 @someone', '  Google.com คือ search engine ของ Google | "quote"\nบรรทัดสอง ')
    assert e['id'] == 'K0001' and e['status'] == 'pending' and not e['duplicate']
    lines = [l for l in (home / K.INBOX).read_text(encoding='utf-8').splitlines() if l.startswith('- K')]
    assert len(lines) == 1
    got = K.parse(lines[0])
    assert got['text'] == 'Google.com คือ search engine ของ Google | "quote"\nบรรทัดสอง'
    assert got['from'] == 'telegram:111 @someone' and got['time'].endswith('+07')
    assert K.add(home, 'Sesame', got['text'])['duplicate'] is True


@pytest.mark.parametrize('bad', ['token: abc123', 'call 0812345678', 'mail me a@b.co', 'sk-' + 'x' * 30, '', 'x' * 1001])
def test_add_refuses_secrets_phones_emails(env, bad):
    _, _, home = env
    with pytest.raises(K.Refused):
        K.add(home, 'telegram:1', bad)
    assert K.entries(home) == []


def test_verify_moves_fact_with_source_and_reject_keeps_reason(env):
    _, _, home = env
    a = K.add(home, 'GET IDEAS', 'fact a')['id']
    b = K.add(home, 'Wabi', 'fact b')['id']
    K.verify(home, a, 'Fact A checked', 'https://example.org/a', today='2026-11-07')
    K.reject(home, b, 'no source supports it')
    kn = (home / K.KNOWLEDGE).read_text(encoding='utf-8')
    assert 'Fact A checked (ที่มา: https://example.org/a · K0001 ตรวจ 2026-11-07)' in kn and 'fact b' not in kn
    st = {e['id']: e for e in K.entries(home)}
    assert st[a]['status'] == 'verified' and st[a]['source'] == 'https://example.org/a'
    assert st[b]['status'] == 'rejected' and st[b]['reason'] == 'no source supports it'
    assert K.pending(home) == []
    with pytest.raises(K.Refused):
        K.reject(home, a, 'again')


def test_cli_add_and_pending(env, capsys):
    _, _, home = env
    assert K.main(['--home', str(home), 'add', '--sender', 'Bogus', 'TER-AI is on GitHub']) == 0
    assert json.loads(capsys.readouterr().out)['id'] == 'K0001'
    assert K.main(['--home', str(home), 'add', '--sender', 'Bogus', 'password: hunter2']) == 3
    capsys.readouterr()
    K.main(['--home', str(home), 'pending', '--json'])
    assert [e['text'] for e in json.loads(capsys.readouterr().out)] == ['TER-AI is on GitHub']


# ------------------------------------------------------------------------------------------- prompt
def test_knowledge_md_is_loaded_for_owner_and_public(env):
    ws, pub, home = env
    (home / K.KNOWLEDGE).write_text('# Knowledge.md\n- KNOWN-FACT-789\n', encoding='utf-8')
    owner = A.Tagentic(FakeLM(), Toolbox(Workspace(ws), home=home), home=home).system_prompt()
    public = A.Tagentic(FakeLM(), Toolbox(Workspace(pub), home=home, public=True), home=home).system_prompt()
    assert 'KNOWN-FACT-789' in owner and 'OWNER-NAME-123' in owner and 'OWNER-MEMORY-456' in owner
    assert 'KNOWN-FACT-789' in public
    for private in ('OWNER-NAME-123', 'OWNER-MEMORY-456', str(ws)):
        assert private not in public
    assert [f.name for f in M.load_memory(home, public=True)] == ['Systemprompt.md', 'Knowledge.md', 'Systemskill.md']


def test_knowledge_md_is_cut_to_its_newest_lines(env):
    _, _, home = env
    (home / K.KNOWLEDGE).write_text('OLD-LINE\n' + 'x' * 5000 + '\nNEW-LINE', encoding='utf-8')
    kn = [f for f in M.load_memory(home) if f.name == 'Knowledge.md'][0].text
    assert 'NEW-LINE' in kn and 'OLD-LINE' not in kn and len(kn) <= M.LIMITS['Knowledge.md'] + 30


# ------------------------------------------------------------------------------------------- public tools
@pytest.mark.parametrize('tool,args', [('write_file', {'path': 'x.txt', 'content': 'x'}), ('run_shell', {'command': 'id'}),
                                       ('run_python', {'code': 'print(1)'}), ('remember', {'fact': 'a'}),
                                       ('read_file', {'path': 'secret-plan.txt'}), ('list_files', {}),
                                       ('edit_file', {'path': 'x', 'old': 'a', 'new': 'b'})])
def test_public_toolbox_blocks_write_run_remember_and_files_in_code(env, tool, args):
    ws, pub, home = env
    box = Toolbox(Workspace(ws), home=home, public=True, yes=True)
    r = box.call(tool, args, allow=True)
    assert not r.ok and 'off in this public chat' in r.output
    assert not (ws / 'x.txt').exists()
    assert 'OWNER-MEMORY-456' in (home / 'Memory.md').read_text(encoding='utf-8')
    assert (home / 'Memory.md').read_text(encoding='utf-8').count('\n') == 2
    assert set(box.names) == set(PUBLIC_TOOLS)


def test_public_add_knowledge_records_the_sender(env):
    ws, pub, home = env
    box = Toolbox(Workspace(pub), home=home, public=True, sender='telegram:999 @stranger')
    assert box.call('add_knowledge', {'text': 'TER-AI เป็นชุด AI ภาษาไทย'}).ok
    assert K.entries(home)[0]['from'] == 'telegram:999 @stranger'
    assert not box.call('add_knowledge', {'text': 'เบอร์ฉัน 0898765432'}).ok


def test_public_relay_session_lives_outside_memory_and_cannot_approve(env, tmp_path):
    ws, pub, home = env
    sdir = tmp_path / 'public-sessions'
    lm = FakeLM(step('write_file', {'path': 'x.txt', 'content': 'x'}),
                json.dumps({'think': 'ok', 'tool': 'final', 'answer': 'hi'}))
    out = io.StringIO()
    rc = C.main(['-w', str(pub), '--memory-dir', str(home), '--public', '--sender', 'telegram:5',
                 '--sessions-dir', str(sdir), '--session', 'tgp-5', '--message', 'hello', '--json'], lm=lm, stdout=out)
    j = json.loads(out.getvalue().strip().splitlines()[-1])
    assert rc == 0 and j['answer'] == 'hi' and j['pending_action'] is None
    assert (sdir / 'tgp-5.json').exists() and not (home / 'sessions' / 'tgp-5.json').exists()
    assert not (pub / 'x.txt').exists()
    sysmsg = lm.calls[0]['messages'][0]['content']
    assert 'OWNER-NAME-123' not in sysmsg and 'public chat' in sysmsg
    # the schema itself offers only the public tools
    enum = json.dumps(lm.calls[0].get('json_schema'))
    assert 'write_file' not in enum and 'add_knowledge' in enum
    out = io.StringIO()
    assert C.main(['-w', str(pub), '--memory-dir', str(home), '--public', '--sessions-dir', str(sdir),
                   '--session', 'tgp-5', '--approve', '--json'], lm=FakeLM(), stdout=out) == 2


def test_public_needs_a_sessions_dir(env):
    ws, pub, home = env
    assert C.main(['-w', str(pub), '--memory-dir', str(home), '--public', '--session', 'tgp-5',
                   '--message', 'hi', '--json'], lm=FakeLM(), stdout=io.StringIO()) == 2


def test_owner_read_file_of_a_memory_file_returns_it(env):
    ws, _, home = env
    r = Toolbox(Workspace(ws), home=home).call('read_file', {'path': 'User.md'})
    assert r.ok and 'OWNER-NAME-123' in r.output


def test_public_prompt_has_no_owner_annotations(env):
    _, pub, home = env
    t = A.Tagentic(FakeLM(), Toolbox(Workspace(pub), home=home, public=True), home=home).system_prompt()
    assert '(Bogus 20' not in t
