# SPDX-License-Identifier: LicenseRef-TER-AI-2.0
"""Build the frozen TERAI1.1 Thai essay + proverb eval set (deterministic, seed 1101).

Proverb items are generated from the pack (src/terai_router/data/proverbs_th.json, Thai Wiktionary,
CC BY-SA 4.0), so the proverb part measures in-pack knowledge, not coverage of all Thai proverbs.
Essay prompts are written for this project (TER-AI License 2.0). Output: eval/terai11_heldout_v1.json
(100 proverb items + 40 essay prompts) and eval/terai11_dev_v1.json (20 proverb items + 5 essays,
used for prompt checks; the held-out file is never used for tuning). SHA-256 goes into eval/SHA256SUMS.

Note on v1: terai11_heldout_v1.json is the frozen artifact checked by its hash. It was generated before two
builder fixes (sorted pool for "complete" distractors, figurative meaning as the answer), so re-running this
script does not reproduce v1 byte for byte; a future v2 must be written under a new name.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from terai_router.terai11 import load_pack, norm  # noqa: E402

TOPICS = [
    "ความสำคัญของการอ่านหนังสือ", "การใช้เวลาให้เกิดประโยชน์", "ความกตัญญูต่อพ่อแม่", "เทคโนโลยีกับชีวิตประจำวัน",
    "การอนุรักษ์สิ่งแวดล้อม", "มิตรภาพในโรงเรียน", "ความซื่อสัตย์สุจริต", "การออกกำลังกายเพื่อสุขภาพ",
    "การประหยัดและการออมเงิน", "ความสามัคคีในชุมชน", "การเรียนรู้ตลอดชีวิต", "บทเรียนจากความล้มเหลว",
    "การใช้สื่อสังคมอย่างรู้เท่าทัน", "ความอดทนและความพยายาม", "การเคารพผู้อาวุโส", "ภาษาไทยในยุคดิจิทัล",
    "การทำงานเป็นทีม", "การคิดก่อนพูด", "ความรับผิดชอบต่อหน้าที่", "การเลือกคบเพื่อน",
    "ความพอเพียงในชีวิต", "การรักษาสุขภาพจิต", "การเตรียมตัวสอบ", "ประโยชน์ของการเป็นจิตอาสา",
    "ปัญหาขยะในเมือง", "การฟังความคิดเห็นที่ต่างจากเรา", "ความกล้าหาญในการยอมรับความผิด", "การอ่านข่าวอย่างมีวิจารณญาณ",
    "ความสำคัญของครู", "ชีวิตในหอพัก", "การตั้งเป้าหมายในชีวิต", "ประเพณีท้องถิ่นของฉัน",
    "การประหยัดพลังงาน", "ความมีน้ำใจ", "การฝึกฝนทักษะใหม่", "ผลกระทบของข่าวลือ",
    "การแบ่งปันความรู้ให้ผู้อื่น", "ความสำคัญของน้ำ", "การวางแผนก่อนลงมือทำ", "ความภูมิใจในความเป็นไทย",
]


IDIOMATIC = re.compile(r"โดยปริยาย|เปรียบ|หมายถึง|สำนวน")
NOT_IDIOM = re.compile(r"^ชื่อ")


def idiom_meaning(e: dict) -> str:
    """The meaning used as the answer: skip names (songs, plants ...), prefer figurative senses."""
    ms = [m for m in e["meanings"] if not NOT_IDIOM.match(m)] or e["meanings"]
    return next((m for m in ms if IDIOMATIC.search(m)), ms[0]) if len(ms) > 1 and not IDIOMATIC.search(ms[0]) else ms[0]


def main() -> int:
    if (ROOT / "eval" / "terai11_heldout_v1.json").exists() and "--force" not in sys.argv:
        print("eval/terai11_heldout_v1.json is frozen; pass --force and write a new version instead")
        return 1
    rng = random.Random(1101)
    entries = [e for e in load_pack()["entries"] if 4 <= len(norm(e["title"])) <= 30 and e["meanings"]]
    rng.shuffle(entries)
    used = set()

    def take(pred, n):
        out = []
        for e in entries:
            if e["title"] not in used and pred(e):
                used.add(e["title"])
                out.append(e)
                if len(out) == n:
                    break
        return out

    def distractors(e, field, k=3):
        pool = [x for x in entries if x["title"] != e["title"]]
        picks = rng.sample(pool, k)
        return [idiom_meaning(p) if field == "meaning" else p["title"] for p in picks]

    def mcq(kind, question, right, wrong, e):
        opts = wrong + [right]
        rng.shuffle(opts)
        return {"kind": kind, "question": question, "options": opts, "answer": opts.index(right),
                "source_title": e["title"], "pageid": e["pageid"]}

    def items(n_meaning, n_complete, n_usage, n_real):
        out = []
        for e in take(lambda e: True, n_meaning):
            out.append(mcq("meaning", f"สำนวน «{e['title']}» มีความหมายตรงกับข้อใด",
                           idiom_meaning(e), distractors(e, "meaning"), e))
        for e in take(lambda e: " " in e["title"].strip(), n_complete):
            head, tail = e["title"].strip().rsplit(" ", 1)
            pool = [x["title"].strip().rsplit(" ", 1)[-1] for x in entries if " " in x["title"].strip()]
            wrong = rng.sample(sorted({t for t in pool if t != tail}), 3)
            out.append(mcq("complete", f"เติมสำนวนให้ครบ: «{head} ...»", tail, wrong, e))
        for e in take(lambda e: any(norm(e["title"]) in norm(x) for x in e["examples"]), n_usage):
            ex = next(x for x in e["examples"] if norm(e["title"]) in norm(x))
            blank = ex.replace(e["title"], "____") if e["title"] in ex else None
            if blank is None or "____" not in blank:
                used.discard(e["title"])
                continue
            out.append(mcq("usage", f"เลือกสำนวนที่เติมลงในช่องว่างได้ถูกต้อง: «{blank}»",
                           e["title"], distractors(e, "title"), e))
        reals = take(lambda e: " " in e["title"].strip(), n_real)
        for e in reals:  # real idiom, and a fake made by swapping its last word with another idiom's
            out.append({"kind": "real_or_fake", "phrase": e["title"], "answer": "real",
                        "source_title": e["title"], "pageid": e["pageid"]})
            for _ in range(50):
                other = rng.choice(entries)
                if " " in other["title"].strip() and other["title"] != e["title"]:
                    fake = e["title"].strip().rsplit(" ", 1)[0] + " " + other["title"].strip().rsplit(" ", 1)[1]
                    if norm(fake) not in load_pack()["_index"]:
                        break
            out.append({"kind": "real_or_fake", "phrase": fake, "answer": "fake",
                        "source_title": None, "pageid": None})
        return out

    def essays(topics):
        out = []
        for t in topics:
            out.append({"topic": t, "instruction": "เขียนเรียงความ 5 ย่อหน้า และใช้สำนวนไทยที่เหมาะกับหัวข้ออย่างน้อย 1 สำนวน"})
        return out

    held = {"version": "terai11_heldout_v1", "seed": 1101,
            "note": "frozen; never use for tuning. Proverb items come from the TERAI1.1 pack (in-pack knowledge).",
            "pack_license": "items quote Thai Wiktionary text: CC BY-SA 4.0",
            "proverb_items": items(40, 20, 20, 10), "essays": essays(TOPICS[:40])}
    dev = {"version": "terai11_dev_v1", "seed": 1101, "proverb_items": items(8, 4, 4, 2),
           "essays": essays(["ความสุขในชีวิตประจำวัน", "การเดินทาง", "อาหารไทยในสายตาโลก", "กีฬาสี", "ห้องสมุด"])}
    for name, obj in (("terai11_heldout_v1.json", held), ("terai11_dev_v1.json", dev)):
        (ROOT / "eval" / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(held["proverb_items"]), "held-out proverb items,", len(held["essays"]), "essays;",
          len(dev["proverb_items"]), "dev items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
