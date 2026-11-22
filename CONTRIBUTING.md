# Contributing to TER-AI

Thanks for looking. The easiest place to start is the intent router: typo pairs, test cases and docs.
Open tasks are labelled [good first issue](https://github.com/klanarongz2009-sketch/ter-ai/labels/good%20first%20issue)
and [help wanted](https://github.com/klanarongz2009-sketch/ter-ai/labels/help%20wanted).

## Before you start: response times

The maintainer is a boarding-school student and cannot use a phone or computer during school terms.
Replies to issues and pull requests can take days or weeks. Read the [project notice](PROJECT_NOTICE.md).

Two AI helpers run by the maintainer may reply before a human does:

- **GET IDEAS** answers new issues with a list of ideas.
- **Teemate** answers posts in the Tagentic Telegram bot community on GitHub Discussions.

Their replies are suggestions and can be wrong. They do not merge pull requests, publish releases or make
project decisions; the maintainer does.

## Set up

Python 3.11 or newer. The core package has no runtime dependencies.

```bash
git clone https://github.com/klanarongz2009-sketch/ter-ai.git
cd ter-ai
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run the tests

```bash
pytest -q                         # real speech and real model runs are opt-in and show as skipped
python training/evaluate.py       # router accuracy on the frozen test and held-out sets
python eval/parity.py             # needs Node.js: checks the browser (JS) and Python versions agree
```

A pull request should keep `pytest` green and should not lower the numbers from `training/evaluate.py`.

## Add a typo pair

Typo fixes live in `src/terai_router/data/typo_pairs.json`.

1. Add `["typed", "intended", "HIGH"]` to `safe_pairs` (use `"MED"` if you are less sure). Only add a pair when
   the typed form is not itself a correct Thai word; otherwise it needs a context rule in `ctx_rules`.
2. Add a test to `tests/test_normalizer.py`, for example
   `assert normalize('เส็ดหรือยัง') == 'เสร็จหรือยัง'`, and one that shows a correct word is left alone.
3. Rebuild the browser demo, which embeds the same table: `python docs/build_demo.py`.
4. Run `pytest -q` and `python eval/parity.py`.

## Add a test case

- New router examples go into a test under `tests/`, for example a `route('...')['intent'] == '...'` assertion.
- Do **not** edit `eval/test_set.json` or `eval/heldout_v07.json`. They are frozen so results stay comparable
  across versions; `eval/router_report.py` prints their hashes.

## Pull request flow

1. Fork the repository and create a branch from `main`.
2. Keep one change per pull request, with a test when you change behaviour.
3. Write public text (code comments, docs, commit messages) in English by default. Translated versions of project documentation (for example, `README.th.md`) may use their target language; the English version remains canonical unless the project says otherwise. Thai examples are welcome in tests.
4. Open the pull request against `main` and say what you changed and how you tested it.
5. Releases and version numbers are handled by the maintainer.

## Licenses

Code is MIT. Some data and optional model weights use other licenses; see the license table in the
[README](README.md#license) and [NOTICE](NOTICE). By contributing you agree that your contribution is
released under the license of the file you change. Do not add files you do not have the right to share.
