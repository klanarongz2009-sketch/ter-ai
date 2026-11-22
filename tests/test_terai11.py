# SPDX-License-Identifier: LicenseRef-TER-AI-2.0
"""TERAI1.1 pipeline tests with a fake client (no model weights; they test code, not model quality)."""
import hashlib
import json
from pathlib import Path

from terai_router import terai11 as t11
from terai_router.terai11.cli import main as cli_main
from terai_router.versions import MODEL_ID, MODELS

ROOT = Path(__file__).resolve().parents[1]


class FakeLM:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def chat(self, messages, **kw):
        self.calls.append((messages, kw))
        return self.replies.pop(0) if self.replies else ""


def test_pack_has_sources_and_license():
    p = t11.load_pack()
    assert p["license"].startswith("CC BY-SA 4.0")
    assert p["count"] == len(p["entries"]) > 500
    assert all(e["pageid"] and e["revid"] and e["meanings"] for e in p["entries"])


def test_explain_known_and_unknown():
    r = t11.explain("กบในกะลา")
    assert r["found"] and "wiktionary.org/?curid=" in r["text"]
    r = t11.explain("มะม่วงหล่นไม่ไกลจากดาวอังคาร")
    assert not r["found"] and "ไม่เดา" in r["text"]


def test_lookup_ignores_spaces():
    e = t11.load_pack()["entries"][0]
    assert t11.lookup(e["title"].replace(" ", "")) is e


def test_parse_choice():
    assert t11.parse_choice("คำตอบ: ค", 4) == 2
    assert t11.parse_choice("ข", 4) == 1
    assert t11.parse_choice("ไม่ทราบ", 4) is None
    assert t11.parse_choice("คำตอบคือ ก", 4) == 0
    assert t11.parse_choice("คำตอบคือ ข.", 4) == 1
    # Devin findings on 16cb1bf: "ข้อ" prefix and polite particles
    assert t11.parse_choice("คำตอบคือ ข้อ ค", 4) == 2
    assert t11.parse_choice("ข้อ ง", 4) == 3
    assert t11.parse_choice("คำตอบ: ขครับ", 4) == 1
    assert t11.parse_choice("ขครับ", 4) == 1
    assert t11.parse_choice("คำตอบ: กค่ะ", 4) == 0
    assert t11.parse_choice("คะแนนดี", 4) is None
    assert t11.parse_choice("ขอโทษ ไม่ทราบ", 4) is None


def test_answer_choice_puts_pack_in_prompt():
    lm = FakeLM(["คำตอบ: ข"])
    got = t11.Terai11(lm).answer_choice("สำนวน «กบในกะลา» หมายถึงข้อใด", ["ก", "ข", "ค", "ง"])
    assert got == 1
    prompt = lm.calls[0][0][1]["content"]
    assert "กบในกะลา" in prompt and "คลังสำนวน" in prompt
    assert lm.calls[0][0][0]["role"] == "system"


GOOD = ("การอ่านหนังสือเป็นกิจกรรมที่ช่วยเปิดโลกทัศน์ของเราให้กว้างขึ้น ทำให้เราไม่เป็นคนที่รู้จักแต่เรื่องใกล้ตัวเท่านั้น\n\n"
        "คนที่ไม่อ่านหนังสือเลยอาจเป็นเหมือนกบในกะลา คือผู้ที่มีความรู้ความคิดคับแคบ เพราะไม่เคยเห็นสิ่งอื่นนอกจากสิ่งที่อยู่รอบตัว "
        "หนังสือจึงเป็นเหมือนหน้าต่างที่พาเราออกไปรู้จักความคิดของคนอื่นและโลกภายนอกที่กว้างใหญ่\n\n"
        "ดังนั้น เราควรแบ่งเวลาอ่านหนังสือทุกวัน แม้เพียงวันละไม่กี่หน้า เพื่อให้ความรู้ค่อยๆ สะสมจนกลายเป็นพื้นฐานของชีวิตที่มั่นคงในอนาคต")


def test_rubric_good_and_bad():
    r = t11.rubric(GOOD, "กบในกะลา")
    assert r["structure_3plus_paragraphs"] and r["proverb_present"] and r["thai_script"] and r["no_markdown"]
    assert t11.rubric(GOOD)["proverb_present"]  # auto-detected from the pack
    bad = t11.rubric("# Title\n- point one in English", "กบในกะลา")
    assert not bad["no_markdown"] and not bad["proverb_present"] and not bad["thai_script"]


def test_essay_pipeline_revises_once():
    outline = "คำนำ: ก\nเนื้อเรื่อง1: ข\nเนื้อเรื่อง2: ค\nเนื้อเรื่อง3: ง\nสรุป: จ"
    lm = FakeLM([outline, "# bad draft", GOOD])
    r = t11.Terai11(lm).essay("การอ่านหนังสือ", proverb="กบในกะลา")
    assert r["model"] == "TERAI1.1" and r["revised"] and r["proverb"] == "กบในกะลา"
    assert len(lm.calls) == 3 and r["citations"]


def test_cli_proverb_offline(capsys):
    assert cli_main(["proverb", "กบในกะลา"]) == 0
    assert "wiktionary" in capsys.readouterr().out
    assert cli_main(["proverb", "ไม่มีสำนวนนี้แน่นอน"]) == 1


def test_registry_terai1_stays_default():
    assert MODEL_ID == "TERAI1" and MODELS[0]["id"] == "TERAI1"
    row = next(m for m in MODELS if m["id"] == "TERAI1.1")
    assert "opt-in" in row["status"]


def test_heldout_frozen():
    sums = (ROOT / "eval" / "SHA256SUMS").read_text()
    data = (ROOT / "eval" / "terai11_heldout_v1.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() in sums
    d = json.loads(data)
    assert len(d["proverb_items"]) == 100 and len(d["essays"]) == 40


def test_unknown_required_proverb_is_refused():
    import pytest
    with pytest.raises(ValueError):
        t11.Terai11(FakeLM([])).essay("หัวข้อ", proverb="ไม่มีสำนวนนี้แน่นอน")
    assert cli_main(["essay", "หัวข้อ", "--proverb", "ไม่มีสำนวนนี้แน่นอน"]) == 1


def test_find_in_text_keeps_shorter_title_used_separately():
    long_ = next(e for e in t11.load_pack()["entries"]
                 if any(t11.norm(o["title"]) in t11.norm(e["title"]) and o is not e and len(t11.norm(o["title"])) >= 4
                        for o in t11.load_pack()["entries"]))
    short = next(o for o in t11.load_pack()["entries"] if o is not long_ and len(t11.norm(o["title"])) >= 4
                 and t11.norm(o["title"]) in t11.norm(long_["title"]))
    titles = [e["title"] for e in t11.find_in_text(long_["title"] + " และ " + short["title"])]
    assert long_["title"] in titles and short["title"] in titles
    assert [e["title"] for e in t11.find_in_text(long_["title"])][0] == long_["title"]


def test_cli_json_search_and_info(capsys):
    assert cli_main(["info", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["model"] == "TERAI1.1"
    assert cli_main(["search", "กบในกะลา", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["citation"]
