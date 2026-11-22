# TERM AI

> **Migration note (2026-11-22):** The original Wiki page is represented by this source-controlled guide so its history and future sunset links remain stable.

The maintained feature guide is [docs/TERM-AI.md](../TERM-AI.md). The trial/removal plan in [`trial.py`](../../src/terai_router/term_ai/trial.py) sets the planned end at **2027-01-01 00:00:00 Asia/Bangkok (UTC+7)**. That is a plan in the source, not confirmation that removal has happened.

## Sunset sequence

Before carrying out the planned removal, publish a clear end-of-trial notice in the README and changelog and update the existing announcement (issue #6) before unpinning or closing it. The source plan already lists the README and changelog updates and the issue action; this sequence makes the notice available before users reach a stopped command.

Keep stable landing content at the old entry points. Replace the detailed [`docs/TERM-AI.md`](../TERM-AI.md) guide with a short sunset notice at the same path, explaining that `terai term` has ended and pointing users to `terai chat`. Keep this migrated Wiki page and its index/Home/navigation links as pointers to that notice, and keep the History entry as a historical record linked to the notice. GitHub does not provide automatic redirects for these Markdown paths, so do not delete the landing pages or their links when removing the feature.

The current `trial.py` removal list names `docs/TERM-AI.md` and the Wiki page/navigation for deletion. Before implementing that plan, revise its documentation-removal steps to preserve the landing content and links. This note changes no code and does not mark the planned removal complete.
