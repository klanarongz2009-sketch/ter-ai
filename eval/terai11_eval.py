# SPDX-License-Identifier: LicenseRef-TER-AI-2.0
"""Evaluate TERAI1 (baseline) vs TERAI1.1 on the frozen set eval/terai11_heldout_v1.json.

Both arms use the same local Gemma 4 E2B GGUF (QAT Q4_0, ``LocalLM(model=\"e2b\")``). The \"terai1\" arm is
the TERAI1 base model with a plain prompt, not the ``terai chat --brain terai1`` route (temperature 0 for questions, seed 0).
Results are appended to a JSONL file so an interrupted run resumes. Summary: ``--summary``.

  python eval/terai11_eval.py --arm terai1 --part proverbs --out eval/results/my_run.jsonl
  python eval/terai11_eval.py --arm terai11 --part essays --limit 10 --out ...
  python eval/terai11_eval.py --summary eval/results/terai11_v1.jsonl
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from terai_router.terai11 import Terai11, check_essay, mcq_prompt, parse_choice, rubric  # noqa: E402

SET = ROOT / "eval" / "terai11_heldout_v1.json"


def real_fake_prompt(phrase: str) -> str:
    return f"วลี «{phrase}» เป็นสำนวนหรือสุภาษิตไทยที่มีอยู่จริงหรือไม่ ตอบคำเดียว: จริง หรือ ไม่จริง"


def essay_prompt(item: dict) -> str:
    return (f"เขียนเรียงความภาษาไทยหัวข้อ «{item['topic']}» {item['instruction']} "
            "ความยาวประมาณ 200-300 คำ")


def set_sha256(path: Path) -> str:
    """Hash of the set with line endings normalised, so a CRLF checkout resumes."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_done(out: Path, sha: str):
    """(arm, part, idx) rows already in ``out``; None if any row is from another set."""
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("set_sha256") != sha:
                return None
            done.add((r["arm"], r["part"], r["idx"]))
    return done


def run(args) -> int:
    from terai_router.brain.local import LocalLM

    SET = Path(args.set)
    data = json.loads(SET.read_text(encoding="utf-8"))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sha = set_sha256(SET)
    done = load_done(out, sha)  # resume only rows produced from this exact set
    if done is None:
        print(f"{out} has rows from another evaluation set; use a new --out", file=sys.stderr)
        return 2
    lm = LocalLM(model="e2b", auto_download=False)
    t11 = Terai11(lm)
    items = data["proverb_items"] if args.part == "proverbs" else data["essays"]
    if args.limit:
        items = items[:args.limit]
    for idx, it in enumerate(items):
        if (args.arm, args.part, idx) in done:
            continue
        t0 = time.time()
        rec = {"arm": args.arm, "part": args.part, "idx": idx, "set_sha256": sha}
        if args.part == "proverbs":
            rec["kind"] = it["kind"]
            if it["kind"] == "real_or_fake":
                if args.arm == "terai11":
                    pred = "real" if t11.is_known(it["phrase"]) else "fake"
                    rec["reply"] = "(pack lookup)"
                else:
                    reply = lm.chat([{"role": "user", "content": real_fake_prompt(it["phrase"])}], max_tokens=6,
                                    temperature=0.0, seed=0)
                    pred = "fake" if "ไม่" in reply else ("real" if "จริง" in reply else None)
                    rec["reply"] = reply
                rec["pred"], rec["correct"] = pred, pred == it["answer"]
            else:
                if args.arm == "terai11":
                    pred = t11.answer_choice(it["question"], it["options"])
                else:
                    reply = lm.chat([{"role": "user", "content": mcq_prompt(it["question"], it["options"])}],
                                    max_tokens=8, temperature=0.0, seed=0)
                    pred = parse_choice(reply, len(it["options"]))
                    rec["reply"] = reply
                rec["pred"], rec["correct"] = pred, pred == it["answer"]
        else:
            if args.arm == "terai11":
                res = t11.essay(it["topic"])
                text, rec["proverb"], rec["revised"] = res["text"], res["proverb"], res["revised"]
            else:
                text = lm.chat([{"role": "user", "content": essay_prompt(it)}], max_tokens=650, temperature=0.3,
                               seed=0)
            rec["text"] = text
            rec["rubric"] = rubric(text, None)
            rec["score"] = sum(rec["rubric"].values())
        rec["seconds"] = round(time.time() - t0, 1)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(args.arm, args.part, idx, rec.get("correct", rec.get("score")), rec["seconds"], flush=True)
    return 0


def summary(path: str, rescore: bool = False) -> int:
    rows = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines()]
    if rescore:
        for r in rows:
            if r["part"] == "essays":
                r["rubric"] = rubric(r["text"], None)
                r["score"] = sum(r["rubric"].values())
    agg = collections.defaultdict(lambda: [0, 0])
    crit = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r["part"] == "proverbs":
            for key in ((r["arm"], "proverbs_all"), (r["arm"], r["kind"])):
                agg[key][0] += int(bool(r["correct"]))
                agg[key][1] += 1
        else:
            agg[(r["arm"], "essay_points")][0] += r["score"]
            agg[(r["arm"], "essay_points")][1] += len(r["rubric"])
            for k, v in r["rubric"].items():
                crit[(r["arm"], k)][0] += int(v)
                crit[(r["arm"], k)][1] += 1
    for (arm, k), (a, n) in sorted(agg.items(), key=lambda x: (x[0][1], x[0][0])):
        print(f"{k:22s} {arm:8s} {a}/{n}")
    for (arm, k), (a, n) in sorted(crit.items(), key=lambda x: (x[0][1], x[0][0])):
        print(f"  essay:{k:28s} {arm:8s} {a}/{n}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["terai1", "terai11"])
    ap.add_argument("--part", choices=["proverbs", "essays"])
    ap.add_argument("--set", default=str(SET), help="evaluation set (default: frozen terai11_heldout_v1.json). TERAI1 gets each essay item's instruction; TERAI1.1 gets only the topic (its pipeline sets the structure), so a set with non-standard instructions is not a like-for-like comparison")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(ROOT / "eval" / "results" / "terai11_run.jsonl"),
                    help="new results file (eval/results/terai11_v1.jsonl is the committed reference run)")
    ap.add_argument("--rescore", action="store_true", help="with --summary: recompute the essay rubric from stored texts")
    ap.add_argument("--summary")
    a = ap.parse_args()
    if not a.summary and not (a.arm and a.part):
        ap.error("--arm and --part are required for an evaluation run (or use --summary)")
    sys.exit(summary(a.summary, a.rescore) if a.summary else run(a))
