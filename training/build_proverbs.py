# SPDX-License-Identifier: LicenseRef-TER-AI-2.0
"""Build the TERAI1.1 Thai proverb/idiom pack from Thai Wiktionary (CC BY-SA 4.0).

Fetches the members of the Thai Wiktionary categories for Thai idioms and proverbs, keeps the
Thai-language definitions (``# `` lines) and usage examples, strips wiki markup and stores the page id
and revision id of every entry so each meaning can be traced to its page history.

Usage: python training/build_proverbs.py [out.json]
Output default: src/terai_router/data/proverbs_th.json (CC BY-SA 4.0, see DATA_LICENSE).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://th.wiktionary.org/w/api.php"
CATEGORIES = ["หมวดหมู่:สำนวนภาษาไทย", "หมวดหมู่:สุภาษิตภาษาไทย"]
UA = "TER-AI proverb pack builder (https://github.com/klanarongz2009-sketch/ter-ai)"
OUT = Path(__file__).resolve().parents[1] / "src" / "terai_router" / "data" / "proverbs_th.json"


def get(params: dict) -> dict:
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:  # network hiccup: retry with backoff
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("Wiktionary API failed: " + url)


def members(cat: str) -> list:
    out, cont = [], {}
    while True:
        d = get(dict({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmlimit": "500",
                      "cmnamespace": "0"}, **cont))
        out += [m["title"] for m in d["query"]["categorymembers"]]
        if "continue" not in d:
            return out
        cont = {"cmcontinue": d["continue"]["cmcontinue"]}


_LINK = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")
_TPL = re.compile(r"\{\{[^{}]*\}\}")
_REF = re.compile(r"<ref[^>/]*/>|<ref[^>]*>.*?</ref>", re.S)
_TAG = re.compile(r"<[^>]+>")


def _keep_template(m: re.Match) -> str:
    body = m.group(0)[2:-2].split("|")
    name = body[0].strip()
    if name in ("l", "m", "ล") and len(body) >= 3:
        return body[2]
    if name in ("ux", "uxi") and len(body) >= 3:
        return body[2]
    return ""


def clean(text: str) -> str:
    text = _REF.sub("", text)
    for _ in range(3):
        text = _TPL.sub(_keep_template, text)
    text = _LINK.sub(r"\1", text)
    text = _TAG.sub("", text).replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", text).strip(" .;:,")


def thai_section(wikitext: str) -> str:
    m = re.search(r"^==\s*ภาษาไทย\s*==\s*$", wikitext, re.M)
    if not m:
        return ""
    rest = wikitext[m.end():]
    n = re.search(r"^==[^=].*==\s*$", rest, re.M)
    return rest[:n.start()] if n else rest


def parse(wikitext: str) -> tuple:
    sec = thai_section(wikitext)
    meanings, examples, kind = [], [], ""
    for line in sec.splitlines():
        h = re.match(r"^===+\s*(.*?)\s*===+\s*$", line)
        if h and h.group(1) in ("สุภาษิต", "คำนาม", "คำกริยา", "คำวิเศษณ์", "วลี", "คำพังเพย", "สำนวน"):
            kind = kind or h.group(1)
        if re.match(r"^#\s", line) or (line.startswith("#") and not line[1:2] in (":", "*")):
            t = clean(line.lstrip("#"))
            if t:
                meanings.append(t)
        elif line.startswith("#:"):
            t = clean(line[2:])
            if t:
                examples.append(t)
    return meanings, examples, kind


def main(argv: list) -> int:
    out = Path(argv[1]) if len(argv) > 1 else OUT
    cats = {}
    for c in CATEGORIES:
        for t in members(c):
            cats.setdefault(t, []).append(c.split(":", 1)[1])
    titles = sorted(cats)
    entries = []
    for i in range(0, len(titles), 50):
        d = get({"action": "query", "prop": "revisions", "rvprop": "content|ids", "rvslots": "main",
                 "titles": "|".join(titles[i:i + 50])})
        for p in d["query"]["pages"]:
            if "revisions" not in p:
                continue
            rev = p["revisions"][0]
            meanings, examples, kind = parse(rev["slots"]["main"]["content"])
            if not meanings:
                continue
            entries.append({"title": p["title"], "pageid": p["pageid"], "revid": rev["revid"],
                            "categories": cats[p["title"]], "kind": kind,
                            "meanings": meanings[:4], "examples": examples[:2]})
        time.sleep(0.5)
    entries.sort(key=lambda e: e["title"])
    pack = {
        "name": "TERAI1.1 Thai proverb and idiom pack",
        "source": "Thai Wiktionary (https://th.wiktionary.org), categories " + ", ".join(CATEGORIES),
        "license": "CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)",
        "authors": "Wiktionary contributors; history of each entry: https://th.wiktionary.org/?curid=<pageid>",
        "changes": "wiki markup, templates and references removed; Thai definitions and up to two examples kept",
        "retrieved": dt.date.today().isoformat(),
        "count": len(entries),
        "entries": entries,
    }
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"{len(titles)} titles, {len(entries)} entries with a Thai meaning -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
