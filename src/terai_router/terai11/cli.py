# SPDX-License-Identifier: LicenseRef-TER-AI-2.0
"""``terai terai11``: opt-in TERAI1.1 Thai essay and proverb mode.

  terai terai11 proverb "กบในกะลา"       meaning from the cited pack (no model needed)
  terai terai11 search "ความอดทน"          pack entries close to a meaning (no model needed)
  terai terai11 ask "สำนวนไหนหมายถึง..."  model answer grounded on the pack, with citations
  terai terai11 essay "ความสำคัญของการอ่าน" [--proverb สำนวน]  outline -> draft -> self-check
"""
from __future__ import annotations

import argparse
import json
import sys

from . import MODEL_ID, PACK_LICENSE, PACK_SOURCE, Terai11, cite, explain, load_pack, search


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="terai terai11", description=f"{MODEL_ID}: opt-in Thai essay and proverb mode "
                                 "(base: local Gemma 4 E2B, same as TERAI1; TERAI1 stays the default)")
    ap.add_argument("cmd", choices=["proverb", "search", "ask", "essay", "info"])
    ap.add_argument("text", nargs="?", default="")
    ap.add_argument("--proverb", help="essay: proverb that must appear (must be in the pack)")
    ap.add_argument("--model", default="e2b", help="Gemma variant for ask/essay: e2b (default) or e4b")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "info":
        p = load_pack()
        if a.json:
            print(json.dumps({"model": MODEL_ID, "count": p["count"], "source": p["source"], "license": p["license"],
                              "retrieved": p["retrieved"]}, ensure_ascii=False))
            return 0
        print(f"{MODEL_ID}: {p['count']} entries from {PACK_SOURCE} ({PACK_LICENSE}), retrieved {p['retrieved']}")
        return 0
    if not a.text:
        ap.error("text is required")
    if a.cmd == "proverb":
        r = explain(a.text)
        print(json.dumps({k: v for k, v in r.items() if k != "entry"}, ensure_ascii=False) if a.json else r["text"])
        return 0 if r["found"] else 1
    if a.cmd == "search":
        if a.json:
            print(json.dumps([{"title": e["title"], "meanings": e["meanings"], "citation": cite(e)} for e in search(a.text)],
                             ensure_ascii=False))
            return 0
        for e in search(a.text):
            print(f"{e['title']}: {'; '.join(e['meanings'][:2])}\n  {cite(e)}")
        return 0
    if a.cmd == "essay" and a.proverb and explain(a.proverb)["found"] is False:
        print(explain(a.proverb)["text"], file=sys.stderr)
        return 1
    from ..brain.local import LocalLM

    t = Terai11(LocalLM(model=a.model))
    if a.cmd == "ask":
        ans = t.ask(a.text)
        print(json.dumps({"model": MODEL_ID, "answer": ans}, ensure_ascii=False) if a.json else ans)
        return 0
    try:
        r = t.essay(a.text, a.proverb)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print(r["text"])
        for c in r["citations"]:
            print("\n" + c)
        if r["issues"]:
            print("\n[self-check] " + "; ".join(r["issues"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
