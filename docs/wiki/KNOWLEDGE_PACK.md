# Knowledge Pack

> **Migration note (2026-11-22):** This preserves the Wiki snapshot’s knowledge-pack description. Counts, size, retrieval date, and license details are historical metadata; use the current source files and license notices to confirm present contents and terms.
> This page is maintained in the repository; see the [documentation index](INDEX.md).


`src/terai_router/data/knowledge_th.json` is the offline knowledge behind Chat's answers. It is installed with the package. The browser demo uses a copy at `docs/knowledge_th.json`.

| | |
|---|---|
| Name | TER-AI Thai knowledge pack |
| Version | 0.8.0 |
| Articles | 8,192 |
| Size | 11,937,726 bytes; 2,782,344 bytes (about 2.8 MB) over the network with GitHub Pages gzip |
| Source | Thai Wikipedia (th.wikipedia.org), lead sections of articles, plain text, shortened |
| Retrieved | 2026-10-16 |
| License | CC BY-SA 4.0 |
| Built by | `training/build_knowledge.py` |

## License and attribution

The text is by Wikipedia contributors. The authors of each article are listed in its page history at `https://th.wikipedia.org/?curid=<id>`; the id of every entry is stored in the file.

Changes made: wiki markup, tables, references and templates removed; text converted to plain text and shortened to the lead section; a search index added.

As an adaptation of Wikipedia text, the file is distributed under the Creative Commons Attribution-ShareAlike 4.0 International license (https://creativecommons.org/licenses/by-sa/4.0/). If you share it or a modified version, keep the attribution and the same license.

Every answer Chat gives from this file ends with the article title and "CC BY-SA 4.0", so the source stays visible to the reader.

The full notice is in [`DATA_LICENSE`](https://github.com/klanarongz2009-sketch/ter-ai/blob/main/DATA_LICENSE). All other files in `src/terai_router/data/` (`model.json`, `typo_pairs.json`, `chitchat_th.json`) were written or trained for this project and are MIT licensed like the code.

## Limits

- No live data: prices, news and today's results get an honest "no data" reply. Questions that ask for something current can use [Web Search](WEB_SEARCH.md) when it is on.
- Only the lead section of each article is included.

## Rebuild

```
python training/build_knowledge.py
```
