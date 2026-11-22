# SPDX-License-Identifier: LicenseRef-TER-AI-2.0
"""TERAI1.1: opt-in Thai essay and proverb profile on TERAI1's local Gemma 4 E2B base.

TERAI1.1 is not a newly trained model. It is the same open-weight base as TERAI1 (Gemma 4 E2B,
Apache-2.0, not trained by TER-AI) plus:

- a cited Thai proverb/idiom pack built from Thai Wiktionary (CC BY-SA 4.0, ``data/proverbs_th.json``);
- retrieval that puts matching pack entries in the prompt and answers "not in the pack" instead of guessing;
- an essay pipeline: outline -> draft -> rule self-check -> at most one revision;
- a Thai system prompt for essays and proverbs.

TERAI1 stays the default model; nothing here changes TERAI1's behaviour.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib import resources
from typing import Any, Dict, List, Optional

MODEL_ID = "TERAI1.1"
PACK_LICENSE = "CC BY-SA 4.0"
PACK_SOURCE = "Thai Wiktionary"

SYSTEM_PROMPT = (
    "คุณคือ TERAI1.1 โหมดเฉพาะด้านเรียงความและสำนวนไทยของโปรเจกต์ TER-AI รันในเครื่องบน Gemma 4 "
    "ซึ่งเป็น open model ที่ใช้เป็นฐาน (TER-AI ไม่ได้ฝึกโมเดลฐานเอง) "
    "เขียนภาษาไทยที่ถูกต้อง เป็นธรรมชาติ ใช้คำเชื่อมระหว่างย่อหน้า ไม่ใช้หัวข้อ markdown หรือ bullet ในเรียงความ "
    "เมื่อพูดถึงสำนวน สุภาษิต หรือคำพังเพย ให้ใช้ความหมายจาก «คลังสำนวน» ที่ให้มาเท่านั้น "
    "ถ้าสำนวนไม่อยู่ในคลัง ให้บอกตรงๆ ว่าไม่พบในคลัง อย่าเดาความหมาย และอย่าแต่งสำนวนขึ้นเอง"
)

_SPACE = re.compile(r"\s+")
_THAI = re.compile(r"[\u0e00-\u0e7f]")
_LATIN = re.compile(r"[A-Za-z]")


def norm(text: str) -> str:
    """Normalise for matching: drop spaces and the common joiners ``,`` ``ฯ`` so "น้ำขึ้น ให้รีบตัก" == "น้ำขึ้นให้รีบตัก"."""
    return re.sub(r"[\s,ฯ'\"“”‘’().]", "", text or "")


def trigrams(text: str) -> set:
    t = norm(text)
    return {t[i:i + 3] for i in range(max(0, len(t) - 2))}


def similarity(a: str, b: str) -> float:
    x, y = trigrams(a), trigrams(b)
    return len(x & y) / len(x | y) if x and y else 0.0


@lru_cache(maxsize=1)
def load_pack() -> Dict[str, Any]:
    raw = resources.files("terai_router").joinpath("data/proverbs_th.json").read_text(encoding="utf-8")
    pack = json.loads(raw)
    pack["_index"] = {norm(e["title"]): e for e in pack["entries"]}
    return pack


def cite(entry: Dict[str, Any]) -> str:
    return f"ที่มา: {PACK_SOURCE} «{entry['title']}» https://th.wiktionary.org/?curid={entry['pageid']} ({PACK_LICENSE})"


def lookup(phrase: str) -> Optional[Dict[str, Any]]:
    """Exact (space-insensitive) lookup of a proverb/idiom in the pack, or None."""
    return load_pack()["_index"].get(norm(phrase))


def find_in_text(text: str, limit: int = 5, min_len: int = 4) -> List[Dict[str, Any]]:
    """Pack entries whose title occurs in ``text``, longest first.

    A shorter title is kept when it also occurs outside the spans of the longer titles already kept
    (so "กบในกะลา" and "กบในกะลาครอบ" asked side by side both come back).
    """
    t = norm(text)
    hits = [e for k, e in load_pack()["_index"].items() if len(k) >= min_len and k in t]
    hits.sort(key=lambda e: -len(norm(e["title"])))
    out: List[Dict[str, Any]] = []
    rest = t
    for e in hits:
        k = norm(e["title"])
        if k not in rest:
            continue
        out.append(e)
        rest = rest.replace(k, "\x00")
        if len(out) >= limit:
            break
    return out


def search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Titles found in the query first, then the closest meanings by character trigrams."""
    found = find_in_text(query, limit)
    if len(found) >= limit:
        return found
    q = trigrams(query)
    scored = []
    for e in load_pack()["entries"]:
        if e in found:
            continue
        s = trigrams(e["title"] + " " + " ".join(e["meanings"]))
        j = len(q & s) / len(q | s) if q and s else 0.0
        if j > 0.02:
            scored.append((j, e))
    scored.sort(key=lambda x: -x[0])
    return found + [e for _, e in scored[:limit - len(found)]]


def pack_context(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return "คลังสำนวน: (ไม่พบรายการที่ตรง)"
    lines = ["คลังสำนวน (" + PACK_SOURCE + ", " + PACK_LICENSE + "):"]
    for e in entries:
        lines.append(f"- {e['title']}: " + "; ".join(e["meanings"]))
    return "\n".join(lines)


def explain(phrase: str) -> Dict[str, Any]:
    """Meaning of a proverb from the pack only. Not in the pack -> found=False, no guess."""
    e = lookup(phrase)
    if e is None:
        near = [x["title"] for x in find_in_text(phrase, 3)]
        return {"found": False, "phrase": phrase, "near": near,
                "text": f"ไม่พบ «{phrase}» ในคลังสำนวนของ TERAI1.1 จึงไม่ให้ความหมาย (ไม่เดา)"
                        + (" ใกล้เคียง: " + ", ".join(near) if near else "")}
    body = f"{e['title']}: " + "; ".join(e["meanings"])
    if e["examples"]:
        body += "\nตัวอย่าง: " + e["examples"][0]
    return {"found": True, "phrase": e["title"], "entry": e, "text": body + "\n" + cite(e)}


# ---------------------------------------------------------------- multiple choice (used by the eval)
_LETTER = re.compile(r"[กขคง]|\b[ABCD]\b")
LETTERS = ["ก", "ข", "ค", "ง"]


def parse_choice(reply: str, n: int) -> Optional[int]:
    """Option index from a reply such as "คำตอบ: ข", "คำตอบคือ ข", "ตอบ ข" or a bare "ข"."""
    text = reply or ""
    m = re.search(r"(?:คำตอบ|ตอบ)\s*(?:คือ|ได้แก่)?\s*[:：]?\s*([กขคง])(?![\u0e01-\u0e2e])", text)
    if not m:
        m = re.search(r"(?<![\u0e00-\u0e7f])([กขคง])(?![\u0e00-\u0e7f])", text)
    if not m:
        return None
    i = LETTERS.index(m.group(1))
    return i if i < n else None


def mcq_prompt(question: str, options: List[str]) -> str:
    opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(options))
    return f"{question}\n{opts}\nตอบเพียงตัวอักษรเดียว (ก ข ค หรือ ง) ในรูปแบบ คำตอบ: <ตัวอักษร>"


class Terai11:
    """TERAI1.1 over a TERAI1-compatible client ``lm`` with ``chat(messages, **kw) -> str``.

    A fake client can be injected for offline tests; that tests the pipeline, not model quality.
    """

    def __init__(self, lm: Any, seed: int = 0) -> None:
        self.lm = lm
        self.seed = seed

    def _chat(self, user: str, max_tokens: int, system: str = SYSTEM_PROMPT, temperature: float = 0.0) -> str:
        return self.lm.chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
                            max_tokens=max_tokens, temperature=temperature, seed=self.seed)

    # -- proverbs
    def answer_choice(self, question: str, options: List[str]) -> Optional[int]:
        ctx = search(question + "\n" + "\n".join(options), limit=6)
        reply = self._chat(pack_context(ctx) + "\n\n" + mcq_prompt(question, options), max_tokens=8)
        return parse_choice(reply, len(options))

    def is_known(self, phrase: str) -> bool:
        """True only when the phrase is in the pack; the model is not asked to guess."""
        return lookup(phrase) is not None

    def ask(self, question: str) -> str:
        """Free-form proverb question: pack entries in context, citations appended by code."""
        ctx = search(question, limit=5)
        direct = find_in_text(question, 3)
        reply = self._chat(pack_context(ctx) + "\n\nคำถาม: " + question
                           + "\nตอบจากคลังสำนวนข้างบนเท่านั้น ถ้าไม่มีในคลังให้ตอบว่าไม่พบในคลัง", max_tokens=300)
        cites = [cite(e) for e in (direct or ctx[:2])]
        return reply.strip() + ("\n" + "\n".join(cites) if cites else "")

    # -- essays
    def outline(self, topic: str, proverb: Optional[str] = None) -> Dict[str, Any]:
        if proverb and lookup(proverb) is None:
            raise ValueError(f"ไม่พบ «{proverb}» ในคลังสำนวนของ TERAI1.1 (ไม่เดา และไม่เปลี่ยนเป็นสำนวนอื่นเอง)")
        entries = [lookup(proverb)] if proverb and lookup(proverb) else search(topic, limit=4)
        need = f"ต้องใช้สำนวน «{entries[0]['title']}»" if proverb and entries else "เลือกสำนวนจากคลังที่เข้ากับหัวข้อ 1 สำนวน (ถ้าไม่มีที่เข้า ไม่ต้องใช้)"
        reply = self._chat(
            pack_context(entries) + f"\n\nวางโครงเรื่องเรียงความหัวข้อ «{topic}» {need}\n"
            "ตอบเป็น 5 บรรทัด ขึ้นต้นด้วย คำนำ: / เนื้อเรื่อง1: / เนื้อเรื่อง2: / เนื้อเรื่อง3: / สรุป: บรรทัดละประโยคเดียว",
            max_tokens=260)
        chosen = entries[0] if (proverb and entries) else None
        if chosen is None:
            picked = find_in_text(reply, 1, min_len=4)
            chosen = picked[0] if picked else (entries[0] if entries else None)
        parts: Dict[str, str] = {}
        for line in reply.splitlines():
            m = re.match(r"\s*[-*]?\s*(คำนำ|เนื้อเรื่อง\s*\d|สรุป)\s*[:：]\s*(.+)", line)
            if m:
                parts[m.group(1).replace(" ", "")] = m.group(2).strip()
        if chosen is not None:
            entries = [chosen] + [e for e in entries if e is not chosen]
        return {"topic": topic, "proverb": chosen["title"] if chosen else None,
                "entries": entries, "parts": parts, "raw": reply}

    def draft(self, plan: Dict[str, Any], issues: Optional[List[str]] = None, previous: str = "") -> str:
        lines = "\n".join(f"{k}: {v}" for k, v in plan["parts"].items()) or plan["raw"]
        must = f" ต้องมีสำนวน «{plan['proverb']}» ตามตัวอักษร และใช้ตามความหมายในคลัง" if plan["proverb"] else ""
        fix = ""
        if issues:
            fix = "\nแก้เรียงความเดิมให้หายปัญหาเหล่านี้: " + "; ".join(issues) + "\nเรียงความเดิม:\n" + previous[:2500]
        return self._chat(
            pack_context(plan["entries"][:2]) + f"\n\nเขียนเรียงความภาษาไทยหัวข้อ «{plan['topic']}» ตามโครงเรื่องนี้\n{lines}\n"
            "เขียน 5 ย่อหน้า (คำนำ 1 เนื้อเรื่อง 3 สรุป 1) คั่นย่อหน้าด้วยบรรทัดว่าง ไม่ใส่หัวข้อย่อย ไม่ใช้ bullet "
            "ความยาวรวมประมาณ 200-300 คำ" + must + fix,
            max_tokens=650, temperature=0.3)

    def essay(self, topic: str, proverb: Optional[str] = None) -> Dict[str, Any]:
        plan = self.outline(topic, proverb)
        text = self.draft(plan)
        issues = check_essay(text, plan["proverb"])
        revised = False
        if issues:
            text2 = self.draft(plan, issues, text)
            if len(check_essay(text2, plan["proverb"])) < len(issues):
                text, revised = text2, True
                issues = check_essay(text, plan["proverb"])
        return {"model": MODEL_ID, "text": text.strip(), "proverb": plan["proverb"], "issues": issues,
                "revised": revised, "citations": [cite(e) for e in plan["entries"][:1]] if plan["proverb"] else []}


# ---------------------------------------------------------------- essay rubric (automatic proxy)
def paragraphs(text: str) -> List[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", (text or "").strip()) if p.strip()]
    if len(parts) < 3:  # some models use single newlines between paragraphs
        parts = [p.strip() for p in (text or "").splitlines() if p.strip()]
    return parts


def rubric(text: str, proverb: Optional[str] = None) -> Dict[str, bool]:
    """Seven automatic checks. They are proxies for structure and form, not a human quality grade.

    With ``proverb=None`` the essay must contain at least one idiom from the pack (any idiom the essay
    uses that is not in the pack is not counted: the check is pack-limited, see the model card).
    """
    paras = paragraphs(text)
    thai, latin = len(_THAI.findall(text or "")), len(_LATIN.findall(text or ""))
    sentences = [s for s in re.split(r"[\n ]{2,}|(?<=[.!?])\s", text or "") if len(s.strip()) > 15]
    if proverb:
        entry = lookup(proverb)
        present = norm(proverb) in norm(text)
    else:
        found = find_in_text(text or "", limit=1, min_len=4)
        entry = found[0] if found else None
        present = entry is not None
    meaning_ok = False
    if entry is not None and present:
        host = next((p for p in paras if norm(entry["title"]) in norm(p)), "")
        meaning_ok = bool(host) and max(similarity(host, m) for m in entry["meanings"]) >= 0.03
    return {
        "structure_3plus_paragraphs": len(paras) >= 3,
        "proverb_present": present,
        "thai_script": thai > 0 and thai / (thai + latin) >= 0.95,
        "length_ok": 400 <= len(norm(text)) <= 4000,
        "no_markdown": not re.search(r"^\s*(?:#|[-*\u2022]\s|\d+\.\s)", text or "", re.M) and "**" not in (text or ""),
        "proverb_meaning_overlap": meaning_ok,
        "no_repeats": len(sentences) == len(set(s.strip() for s in sentences)),
    }


def check_essay(text: str, proverb: Optional[str] = None) -> List[str]:
    names = {
        "structure_3plus_paragraphs": "ต้องมีอย่างน้อย 3 ย่อหน้า (คำนำ เนื้อเรื่อง สรุป)",
        "proverb_present": f"ต้องมีสำนวน «{proverb}» ตามตัวอักษร" if proverb else "ต้องใช้สำนวนไทยจากคลังอย่างน้อย 1 สำนวน",
        "thai_script": "เขียนเป็นภาษาไทย ไม่ปนอังกฤษ",
        "length_ok": "ความยาวไม่เหมาะ (ประมาณ 200-300 คำ)",
        "no_markdown": "ไม่ใช้หัวข้อ markdown หรือ bullet",
        "proverb_meaning_overlap": "ย่อหน้าที่ใช้สำนวนต้องอธิบายให้ตรงความหมายในคลัง",
        "no_repeats": "อย่าเขียนประโยคซ้ำ",
    }
    return [names[k] for k, ok in rubric(text, proverb).items() if not ok]
