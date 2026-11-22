# TERM AI

> **Migration note (2026-11-22):** The original Wiki page is represented by this source-controlled guide so its history and future sunset links remain stable.

The maintained feature guide is [docs/TERM-AI.md](../TERM-AI.md). The trial/removal plan in [`trial.py` in preserved v0.14.0](https://github.com/klanarongz2009-sketch/ter-ai/blob/v0.14.0/src/terai_router/term_ai/trial.py) sets the planned end at **2027-01-01 00:00:00 Asia/Bangkok (UTC+7)**. That is a plan in the source, not confirmation that removal has happened.

## Sunset sequence

The source plan in [`trial.py` in preserved v0.14.0](https://github.com/klanarongz2009-sketch/ter-ai/blob/v0.14.0/src/terai_router/term_ai/trial.py) lists the feature directory, its test file, and the main `docs/TERM-AI.md` guide for removal; it names `cli.py`, `pyproject.toml`, both READMEs, and `CHANGELOG.md` for mention edits. It does not specify Wiki pages, navigation, the History page, or issue #6.

As separate maintainer follow-up, publish an end-of-trial notice before removal and review the current body and comments on [announcement issue #6](https://github.com/klanarongz2009-sketch/ter-ai/issues/6), then decide whether to update, unpin, or close it. Keep stable landing content at the old entry points: replace the detailed [`docs/TERM-AI.md`](../TERM-AI.md) guide with a short notice that `terai term` has ended and points to `terai chat`; retain this Wiki page, its index/Home/navigation links, and the History entry as pointers or historical records linked to that notice. GitHub does not provide automatic redirects for these Markdown paths. Revise the source removal list before implementation if needed to preserve these landing pages. This recommendation changes no code and does not mean the planned removal or issue #6 update has happened.
