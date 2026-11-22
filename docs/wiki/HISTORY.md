# History of TER-AI

> **Migration note (2026-11-22):** Historical timeline copied from the GitHub Wiki. It records events only through its stated coverage and is not a current project-status page; consult the [README](../../README.md) and [changelog](../../CHANGELOG.md) for current state.
> This page is maintained in the repository; see the [documentation index](INDEX.md).


This page is the full history of TER-AI (`terai-router`), from the first terminal chatbot through v0.16.0 and the project notice; v0.16.0 is the last release covered by this historical snapshot. Every date, hash and number below comes from the repository, its GitHub Releases, the wiki, or the build logs kept on the development VM. Where a date or number is not recorded, the page says so.

TER-AI is maintained by klanarongz2009 ([klanarongz2009-sketch](https://github.com/klanarongz2009-sketch) on GitHub). Made with Sesame: the code, tests, benchmarks and docs were written by a Sesame AI agent working on the maintainer's instructions.

**Times.** Times are Bangkok time (ICT, UTC+7) unless marked `Z` (UTC). Git commit times are stored in UTC.

**Evidence levels.** Following the project's own rule, this page keeps four things apart: a *proposal* (an idea or plan), a *decision* (the maintainer chose it), an *implementation* (code exists, with a commit), and a *validation* (tests or measurements were run). A plan, a roadmap line or an AI-written issue is not proof that something shipped.

**Commit hashes.** On 2026-10-21 the repository history was rewritten to remove personal data (see [2026-10-21: privacy rewrite](#2026-10-21-privacy-rewrite)). Every hash on this page is the current one, as seen on `origin`. Older notes, issues #4 and #5, and some logs still quote the pre-rewrite hashes; the mapping is given in that section.

## Contents

- [Timeline at a glance](#timeline-at-a-glance)
- [Phase 0: Terminal AI on the VM (2026-10-10 to 2026-10-11)](#phase-0-terminal-ai-on-the-vm-2026-10-10-to-2026-10-11)
- [Phase 1: the public repository (2026-10-16)](#phase-1-the-public-repository-2026-10-16)
- [Pause: credits ran out (2026-10-17 to 2026-10-21)](#pause-credits-ran-out-2026-10-17-to-2026-10-21)
- [Phase 2: speech, pictures and music (2026-10-21)](#phase-2-speech-pictures-and-music-2026-10-21)
- [Phase 3: project notice (2026-10-22)](#phase-3-project-notice-2026-10-22)
- [Phase 4: TERM AI comes back as a limited-time trial (2026-10-22)](#phase-4-term-ai-comes-back-as-a-limited-time-trial-2026-10-22)
- [Phase 5: TERAI1BETA, the chat model (2026-10-22)](#phase-5-terai1beta-the-chat-model-2026-10-22)
- [Side projects around the repository](#side-projects-around-the-repository)
- [Planned, not shipped](#planned-not-shipped)
- [Version and test numbers over time](#version-and-test-numbers-over-time)
- [Known gaps and conflicts between sources](#known-gaps-and-conflicts-between-sources)
- [Sources](#sources)

## Timeline at a glance

| Date (ICT) | Version / event | What changed | Evidence |
|---|---|---|---|
| 2026-10-10 | TERM_AI | Rule-based Python chatbot in a terminal on the VM | `term_ai.py` (VM only until v0.14.0 published it as the TERM AI limited-time trial) |
| 2026-10-10 | TER-AI-0.5 | First own model: intent classifier, 149 samples, 11 intents | VM build log: leave-one-out accuracy 67.8% |
| 2026-10-10 ~21:00 | TER-AI-0.6 | Typo normalizer, 15 intents, own Naive Bayes | 78/124 on the new test set (VM only) |
| 2026-10-11 06:46 | TER-AI-0.6.1 | Router: new-intent model plus the v0.5 model as expert; became the active model on the VM | 81/124 (VM only) |
| 2026-10-16 08:02 | v0.7.0 | First public commit: offline Thai intent router as a pip package | commit `27e9287`; 97.6% (121/124) |
| 2026-10-16 15:00 | Demo and links | GitHub Pages demo and repository links | commit `3f24229` |
| 2026-10-16 16:15 | v0.8.0 | Offline Thai Chat with tools, knowledge pack and memory | commits `4e24fd3`, `a06c752`, `eb5bc0d` |
| 2026-10-16 16:37 | v0.9.0 | Opt-in web search (Wikipedia th/en, SearXNG) | commits `33e9eb2`, `3b6821b` |
| 2026-10-16 17:47 | terai.eu.org | Domain requested at nic.eu.org | Status: still pending |
| 2026-10-16 17:59 | GET IDEAS | Ideas bot on GitHub Issues, first test issue #1 | [issue #1](https://github.com/klanarongz2009-sketch/ter-ai/issues/1) |
| 2026-10-16 18:19 | Wiki | 12-page wiki with sidebar and footer | wiki commit `a8d450a` |
| 2026-10-17 to 2026-10-21 | Pause | Agent credits ran out; TTH and SANKPUP were built but not released | build logs |
| 2026-10-21 08:36 | v0.10.0 | TTH, Thai text-to-speech | tag `v0.10.0` -> `3d2e9be`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.10.0) |
| 2026-10-21 08:57 | v0.11.0 | SANKPUP, pictures from code | tag `v0.11.0` -> `a03b86c`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.11.0) |
| 2026-10-21 10:43 | v0.12.0 | MuML 1.0 WA, music in the browser | tag `v0.12.0` -> `9ce492d`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.12.0) |
| 2026-10-21 12:24 to 13:26 | Docs, privacy, English-only | README rewrite, history rewrite, README.th.md, English-only demo | commits `71cf7df`, `ff63e12`, `40fe086`, `676e390` |
| 2026-10-21 12:38 | Temmo prototype | Game tab in the web demo, not released | commit `ff00b99` |
| 2026-10-21 20:30 | v0.13.0 | MUML 1.0 HIQ, text-to-music audio on CPU | tag `v0.13.0` -> `c2cac26`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.13.0) |
| 2026-10-22 03:15 to 03:44 | Project notice | PROJECT_NOTICE.md and .th.md | commits `59239cf`, `f73b7cf`, `7a1f7e5`, `372cb32` |
| 2026-10-22 04:53 | v0.14.0 | TERM AI, the original Terminal AI, back as a limited-time trial until 2027-01-01 00:00:00 (UTC+7) | tag `v0.14.0` -> `0e2a5e5`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.14.0), pinned [issue #6](https://github.com/klanarongz2009-sketch/ter-ai/issues/6) |
| 2026-10-22 05:57 | v0.15.0 | MuML 1.0 WA writes notes with the trained MuML 1.0 network (Markov v1 only as fallback); model id separate from the repository version | tag `v0.15.0` -> `c416ad2`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.15.0) |
| 2026-10-22 06:26 | v0.16.0 | Model TERAI1BETA: local Gemma 4 writes chat replies with the rules as tools, grounding check, image reading; model ids separate from the repository version, written down in `versions.py` | tag `v0.16.0` -> `36ff01d`, [release](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.16.0) |
| 2027-01-01 00:00 (UTC+7) | TERM AI trial end (planned in `trial.py`) | The source plan lists the feature directory, tests and main guide for removal, plus CLI/package metadata/README/CHANGELOG mention edits. It does not specify Wiki, navigation, History or issue #6 follow-up; see the separate maintainer recommendation. | [TERM AI sunset sequence](TERM_AI.md#sunset-sequence) |

22 milestones in total: 4 before the public repository, 18 from the first public commit on (v0.16.0 included), plus the planned TERM AI removal on 2027-01-01.

## Phase 0: Terminal AI on the VM (2026-10-10 to 2026-10-11)

Nothing from this phase is in the public repository. It lived in `/root/work/terminal-ai/` on the Sesame VM and is known from the build logs and the files kept there.

### 2026-10-10: TERM_AI, a rule-based chatbot

- **Proposal and decision.** The maintainer asked for "an AI of our own in the terminal" and picked a rule-based Python chatbot.
- **Implementation.** `term_ai.py` with a bot named `TERM_AI` and a small `memory.json`. Settings were later moved to `config.json` (`bot_name`, confidence threshold 0.9).
- **Validation.** Manual terminal runs only: greeting, "remember my name", and recall of the name. Example: `python3 term_ai.py "สวัสดี"` answered with a greeting.

### 2026-10-10: TER-AI-0.5, the first own model

- **Decision.** The maintainer said that "make a model" means building and training a model of our own, not wrapping someone else's model (an Ollama + Qwen wrapper was rejected). He named it **TER-AI-0.5**, with the tagline "made with Sesame". This is the first recorded use of the name TER-AI.
- **Implementation.** `intent_model.py`: an intent classifier trained on `train_data.json`, saved as `model.json`.
- **Validation.** 149 samples, 11 intents, leave-one-out accuracy **67.8%** (build log).

### 2026-10-10 ~21:00: TER-AI-0.6

- **Implementation.** Folder `v0.6/` (files written 21:09 to 21:16): a typo normalizer built from a profile of how the maintainer actually types Thai (`build_typo_pairs.py`), 15 intents, and a Naive Bayes classifier written from scratch. Dataset: 28 of 188 real message segments labeled, the 149 v0.5 samples and 80 seed samples; 239 training sentences (111 real, 60 from v0.5, 15 seed, 53 augmented) and 124 test sentences (36 real, 20 new-intent, 13 real messages from the maintainer, 11 seed, 44 from v0.5). Model: multinomial Naive Bayes on character 1 to 4-grams plus 2 to 4-grams of a consonant skeleton, alpha 0.3, chosen by cross-validation (`select_model.py`). A vowel-folding step in the normalizer was added after a first evaluation (`eval_report_before_vowelfold.md`).
- **Validation** (124-sentence test set, build log): v0.6 **78/124**; v0.5 retrained on the same data 45/124; the shipped v0.5 model 72/124, which is almost all from the old-intent sentences (72/73) because it cannot output the 4 new intents. On the maintainer's real messages the shipped v0.5 scored 2/13 and v0.6 10/13. On the 73 test sentences that use the old intents, v0.6 scored 41/73 against 45/73 for retrained v0.5.

### 2026-10-11: TER-AI-0.6.1

- **Implementation.** Folder `v0.6.1/` (files written 2026-10-11 04:02 to 04:09). Two experiment rounds (`exp_report.md`, `exp_report_round2.md`) picked a router (`router.py`): the main Naive Bayes model (character 1 to 4-grams, skeleton weight 1, alpha 0.3) decides first, and messages it routes to the old intents go to the v0.5 model as an expert. The config was chosen by a cross-validation rule, not by the test set.
- **Validation.** 81/124 overall (v0.5: 45, v0.6: 78) and 44/73 on the old intents (v0.5: 45, v0.6: 41).
- **Decision.** At 06:46 it became the active model of the terminal launcher, with rollback kept.

The log has no recorded TER-AI work between 2026-10-11 and 2026-10-16.

## Phase 1: the public repository (2026-10-16)

### Why the name

On 2026-10-16 the maintainer explained the name: TER comes from the Thai word "เธอ" (you), and it works both ways: TER-AI calls the user เธอ, and the user calls TER-AI เธอ. The README has said this since.

### Rules set the same day

These decisions from 2026-10-16 shaped every later release:

- The repository is English only (README, docs, comments, CLI messages, commit messages). Thai is allowed only in data, example inputs and demo text.
- 0.x work and 1.x work are never mixed in one task, commit or release. This is why a model called "MuML 1.0" or "MUML 1.0 HIQ" still ships inside a 0.x repository version.
- From v1.0 on, TER-AI may combine its own model with other open-weight models (Gemma, Qwen, Typhoon); TER-AI stays the core (routing, tools, memory, retrieval, web). This is an exception to the "our own model" rule, made by the maintainer.
- v1.0 must support languages other than Thai (not yet named; English first).
- Pushes go through a repository deploy key added by the maintainer on the web, because keys created through an OAuth app were deleted when that OAuth grant was revoked.

### v0.7.0: offline Thai intent router (2026-10-16 08:02)

- **Commit.** [`27e9287`](https://github.com/klanarongz2009-sketch/ter-ai/commit/27e9287) "TER-AI v0.7.0: offline Thai intent router that tolerates typos" (01:02Z). No git tag and no GitHub Release exist for v0.7.0.
- **What it is.** A pip-installable package `terai-router`, pure Python, no runtime dependencies, no language model inside. It reads one Thai or Thai-English message, fixes common typos and speech-to-text errors, and returns one of 15 intents with a confidence score. The model file is 1.1 MB.
- **Validation** (`eval/results_v07.json`, `bench/typhoon_results.json`):

| | TER-AI v0.7.0 | Typhoon2 1B instruct (zero-shot) |
|---|---|---|
| Accuracy, frozen test set (124 sentences) | 97.6% (121/124) | 44.4% (55/124, 14 unparsed) |
| Accuracy, held-out set (112 sentences) | 99.1% (111/112) | 55.4% (62/112, 14 unparsed) |
| Mean latency per message, CPU | 0.24 ms (1 thread) | 2,325.1 ms test, 2,445.8 ms held-out (8 threads) |
| Model size | 1.1 MB | 2.49 GB download (1.24B params, float32) |

  Baseline: `typhoon-ai/llama3.2-typhoon2-1b-instruct`, revision `7513a054`, greedy decoding, at most 6 new tokens, system prompt listing the 15 intents, AMD EPYC with 8 threads, run on 2026-10-16 before the first commit (`bench/typhoon_run2.log`; a first, partial run logged 2,418.0 ms on the test set and was replaced). The intent model has not changed since v0.7.0; the 2026-10-21 re-run of `training/evaluate.py` published in the README still gives 121/124 (0.167 ms) and 111/112 (0.213 ms).

- **Follow-ups the same day.** [`3f24229`](https://github.com/klanarongz2009-sketch/ter-ai/commit/3f24229) (15:00) added the repository and demo links; the GitHub Pages demo went live at https://klanarongz2009-sketch.github.io/ter-ai/. [`c091cbe`](https://github.com/klanarongz2009-sketch/ter-ai/commit/c091cbe) (15:12) documented install from GitHub and mobile-friendly CLI examples.

### v0.8.0: offline Thai Chat (2026-10-16 16:15 to 16:32)

- **Commits.** [`4e24fd3`](https://github.com/klanarongz2009-sketch/ter-ai/commit/4e24fd3) part 1 (Python chat), [`a06c752`](https://github.com/klanarongz2009-sketch/ter-ai/commit/a06c752) part 2 (chat in the browser, `docs/chat.js`, lazy-loaded knowledge pack, JS/Python parity), [`eb5bc0d`](https://github.com/klanarongz2009-sketch/ter-ai/commit/eb5bc0d) README. No tag, no GitHub Release.
- **What changed.** `terai chat`: an offline Thai chat that answers with real tools (calculator, date and time, unit conversion, random), answers knowledge questions from a bundled Thai Wikipedia pack of 8,192 articles with the source named, and remembers facts the user tells it. `DATA_LICENSE` was added because the knowledge pack is adapted from Thai Wikipedia under CC BY-SA 4.0. The wheel grew to 2.73 MB, of which `knowledge_th.json` is 11,937,726 bytes uncompressed (2,782,344 bytes over GitHub Pages gzip, as measured for the wiki).
- **Validation.** pytest 42 passed after part 1 and 45 after part 2; chat parity JS vs Python 790/790 identical; router parity 607 sentences, no diff; `chat_eval_v08` 81/81, held-out 37/37, regression 16/16.
- **Incidents.** One build task falsely reported that nothing ran, and part 2 failed once at 16:30 and was finished by hand at 16:32. Both are recorded in the logs; neither reached the published code.

### v0.9.0: opt-in web search (2026-10-16 16:37 to 16:47)

- **Commits.** [`33e9eb2`](https://github.com/klanarongz2009-sketch/ter-ai/commit/33e9eb2) part 1 (`websearch.py`, `terai chat --web`, optional `--searx URL`), [`3b6821b`](https://github.com/klanarongz2009-sketch/ter-ai/commit/3b6821b) part 2 (web search switch in the browser demo, mocked-web parity). No tag, no GitHub Release.
- **What changed.** Chat stays offline by default. With web search on, only the question (minus question words) is sent to th.wikipedia.org and en.wikipedia.org, and to a SearXNG instance if one is set.
- **Validation.** pytest 59 then 63 passed (14 new web-search tests with the network mocked); web-mock parity 24/24 (8 conversations, 24 turns, fixtures recorded from real Wikipedia on 2026-10-16); chat 790/790; intent 97.6% / 99.1% unchanged. A live browser test on GitHub Pages showed no request to Wikipedia with the switch off, and 1 to 2 requests (HTTP 200) with it on; 0 console errors.

### Wiki (2026-10-16 18:19)

Wiki commit `a8d450a` "Wiki: TER-AI v0.9.0 documentation (12 pages, sidebar, footer)": Home, Getting-Started, Chat, Router, Web-Demo, Web-Search, Knowledge-Pack, Evaluation, GET-IDEAS, Roadmap, Domain, FAQ, plus `_Sidebar` and a "Made with Sesame" footer. Commit `a4543ac` (18:19) linked the README to the wiki. At 18:21 commit `b006ae4` corrected the knowledge-pack transfer size on the wiki to 2.8 MB. Later pages: TTH, SANKPUP and MuML (with v0.10.0 to v0.13.0) and this page.

## Pause: credits ran out (2026-10-17 to 2026-10-21)

On 2026-10-17 the agent's credits ran out, and all running tasks stopped until the reset on 2026-10-21 at 08:00. Work done before the stop:

- **TTH (2026-10-17).** The maintainer asked for the project's own Thai TTS, named TTH after "TTS". A first run of the in-progress code produced a 9.70 s test file with the local Wayu engine; numbers, dates and times were read correctly, and the maintainer decided that TER-AI is read as "เธอเอไอ". He also asked for 9 named voices (6 male, 3 female); a spec was written.
- **SANKPUP (2026-10-17).** The maintainer asked for a picture model that draws only through code, named after the Thai word for "make a picture", and then specified a **local** model, Gemma 4. A first task using a cloud API was cancelled before it changed anything.

Neither was released during the pause. Both shipped right after the reset.

## Phase 2: speech, pictures and music (2026-10-21)

The CHANGELOG starts here: v0.10.0 is the first version with a git tag, a GitHub Release and a CHANGELOG entry.

### v0.10.0: TTH, Thai text-to-speech (08:36)

- **Evidence.** Tag `v0.10.0` -> [`3d2e9be`](https://github.com/klanarongz2009-sketch/ter-ai/commit/3d2e9be); release ["TER-AI v0.10.0: TTH, Thai text-to-speech"](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.10.0), published 2026-10-21 01:37Z. Wiki page [TTH](TTH.md).
- **What changed.** `terai tth "ข้อความ" -o out.wav`, `terai chat --speak`, and a Speak replies switch in the web demo. A Thai text frontend shared by Python and JavaScript reads numbers, times, versions, maths symbols, units, abbreviations and acronyms in Thai, and drops links and emoji.
- **Engines.** `wayu` (default): Wayu-Paxa-TTS-Edge, 82M open weights by Paxa Labs / Wayu Research, run locally on CPU, weights (about 315 MB) downloaded from Hugging Face on first use and never stored in the repository; weights CC-BY-NC-4.0 (non-commercial, attribution), inference code Apache-2.0. `edge` (fallback): edge-tts, online, LGPL-3.0 plus Microsoft service terms. Install with the `[tth]` or `[tth-edge]` extra; the core install still has no dependencies.
- **Why not the Paxa cloud API.** It was evaluated on 2026-10-17 (free tier: a one-time 100 credits per account) and not used; the open-weight local model runs free and without limits on the VM.
- **Validation.** pytest 108 passed (45 new); the real Wayu synthesis test (`TERAI_TTH_REAL=1`) passed on the build machine; TTH frontend parity 1,700/1,700 (850 texts x ครับ/ค่ะ); router, chat and web parity unchanged.

### v0.11.0: SANKPUP, pictures from code (08:57)

- **Evidence.** Tag `v0.11.0` -> [`a03b86c`](https://github.com/klanarongz2009-sketch/ter-ai/commit/a03b86c); release ["v0.11.0: SANKPUP, pictures from code"](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.11.0), published 01:57Z. Wiki page [SANKPUP](SANKPUP.md).
- **What changed.** `terai sankpup`: a local model writes SVG, which is sanitized (no scripts, no external links) and rendered to PNG or JPG. It is a workflow, not an image model. Engines: `gemma` (Gemma 4 through llama-cpp-python or a local OpenAI-compatible server such as Ollama or llama-server), `offline` (deterministic, no download) and `auto` (default). Gemma 4 sizes `e2b` (default, fits 8 GB RAM on CPU), `e4b`, `12b`, `26b-a4b`, `31b`, official QAT Q4_0 GGUF, SHA-256 checked, downloaded with `--pull`.
- **Validation.** Gemma 4 E2B on 8 CPU cores, 8 GB RAM, no GPU, 12 prompts: 11/12 valid pictures (Thai 5/6, English 6/6); time per picture p50 24.2 s, p95 49.1 s; model load 38 to 125 s. pytest 138 passed, 1 skipped; SANKPUP parity 688/688.
- **Decisions after release.** On 2026-10-21 the maintainer settled the scope recorded in [issue #5](https://github.com/klanarongz2009-sketch/ter-ai/issues/5): simple flat-vector scenes, freeform prompts, local-only, lenient thresholds. Two items are still open there: a prompt-match rubric and a blank-render guard.

### v0.12.0: MuML 1.0 WA, music in the browser (10:43)

- **Evidence.** Prototype commit [`b1b9e18`](https://github.com/klanarongz2009-sketch/ter-ai/commit/b1b9e18) (10:28), release commit tag `v0.12.0` -> [`9ce492d`](https://github.com/klanarongz2009-sketch/ter-ai/commit/9ce492d); release ["v0.12.0: MuML 1.0 WA, music in the browser (Markov v1)"](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.12.0), published 03:43Z. Wiki page [MuML](MUML.md).
- **The MuML family.** The maintainer planned three music models: MuML 1.0 (his own model, trained from scratch), MUML 1.0 HIQ (fine-tuned from another model) and MuML 1.0 WA (runs in the browser with the Web Audio API).
- **What changed.** A Thai or English prompt (mood, BPM, key, meter, length), a style (Auto, Folk or Rock) and a seed become a short song played with the Web Audio API and downloadable as `.wav` and `.mid`. The note writer is Markov v1, not the trained MuML 1.0 model, because MuML 1.0 was still training when WA was built.
- **License decision.** The maintainer chose option A: code MIT; the note table, built from the Nottingham Music Database as cleaned by jukedeck/nottingham-dataset (commit `0992bb6c`), is GPL-3.0 and kept in its own files with the GPL text next to them (NOTICE item 7, DATA_LICENSE).
- **Validation.** pytest 169 passed, 1 skipped; MuML WA parity 330/330, and the demo's table file equals `markov.json`.

### 2026-10-21: README rewrite

Commit [`71cf7df`](https://github.com/klanarongz2009-sketch/ter-ai/commit/71cf7df) (12:24): README rewrite with a table of released parts, benchmarks re-measured on 2026-10-21, and a license table with a commercial-use column. Docs only, no tag.

### 2026-10-21: privacy rewrite

- **What happened.** Personal test values had been committed in test data since v0.8.0 and v0.10.0. Commit [`ff63e12`](https://github.com/klanarongz2009-sketch/ter-ai/commit/ff63e12) (12:35) "privacy: replace real phone number and persona details with fictional values; add handle to author" fixed the current tree. The history was then rewritten with `git filter-repo --replace-text` in a separate mirror (12 of 15 commits changed), checked (grep for the personal values found 0, the main tree was identical to `c3b56f5`, pytest on main and v0.12.0 gave 169 passed, 1 skipped, and `SHA256SUMS` matched), and force-pushed at 12:47 after the maintainer approved it.
- **Hash mapping.** main `c3b56f5` -> `ff63e12`; v0.10.0 `765cd85` -> `3d2e9be`; v0.11.0 `b1fb40d` -> `a03b86c`; v0.12.0 `4867fa4` -> `9ce492d`; README rewrite `2ead5d5` -> `71cf7df`. Commits before v0.8.0 (`27e9287`, `3f24229`, `c091cbe`) kept their hashes. The three GitHub Releases were kept and point at the new tags.
- **Still open.** Old commits stay reachable by their SHA until GitHub Support purges them. A personal value was also found later on the wiki TTH page; it was removed from the page (wiki commit `c44af7b`), but it is still in the wiki's git history. Rewriting the wiki history needs the maintainer's decision.

### 2026-10-21: English-only surfaces

Commits [`40fe086`](https://github.com/klanarongz2009-sketch/ter-ai/commit/40fe086) and [`ec2d4c0`](https://github.com/klanarongz2009-sketch/ter-ai/commit/ec2d4c0) (12:54 to 12:55) moved Thai text out of README into `README.th.md`; [`676e390`](https://github.com/klanarongz2009-sketch/ter-ai/commit/676e390) (13:08) made the web demo UI English only (no Thai page, no language switch). Thai stays only where it is functional: engine output, data, example prompts.

### 2026-10-21: Temmo prototype (not released)

- **Proposal.** Temmo 1.0 is the maintainer's idea for an AI that builds complete, playable indie games, not mockups.
- **Implementation.** Commit [`ff00b99`](https://github.com/klanarongz2009-sketch/ter-ai/commit/ff00b99) (12:38) "Temmo 1.0 prototype (not released)": a game pipeline with local Gemma 4 by default and bring-your-own-key as an option, shown as a Temmo tab in the web demo. Remix commits [`f14294d`](https://github.com/klanarongz2009-sketch/ter-ai/commit/f14294d), [`308449f`](https://github.com/klanarongz2009-sketch/ter-ai/commit/308449f) and [`92b903a`](https://github.com/klanarongz2009-sketch/ter-ai/commit/92b903a) (13:13 to 13:26) taught the remix rules English word order (for example "pink background, blue walls, faster enemies, more levels").
- **Validation.** Temmo remix parity 42/42 (reported with v0.13.0). The README shows one sample game built locally with Gemma 4 E2B.
- **Status.** Not tagged, not released, no Temmo server. A second Temmo task (community features and a free-tier queue) stopped when its budget ran out; its full-repo test run and commit are still to do.

### v0.13.0: MUML 1.0 HIQ, text-to-music audio on CPU (20:30)

- **Evidence.** Tag `v0.13.0` -> [`c2cac26`](https://github.com/klanarongz2009-sketch/ter-ai/commit/c2cac269e42bce2c3d391513c88d225c5bf011bb); release ["v0.13.0: MUML 1.0 HIQ, text-to-music audio on CPU"](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.13.0), published 13:31Z. main was fast-forwarded from `92b903a` to `c2cac26`, no force push. Details: [docs/MUML-HIQ.md](https://github.com/klanarongz2009-sketch/ter-ai/blob/v0.13.0/docs/MUML-HIQ.md).
- **How it got there** (all 2026-10-21, branch `muml-hiq`):
  1. ACE-Step 1.5 through acestep.cpp was the first engine. Early Thai lyric tests were not intelligible: CER 0.8411 (best), with an English-song floor of 0.8131.
  2. [`9a91f10`](https://github.com/klanarongz2009-sketch/ter-ai/commit/9a91f10): lyrics run through `ace-lm` then `ace-synth`; the vocal language follows the lyrics; a smaller LM with romanised lyrics became the Thai default.
  3. A search for open-weight models that sing Thai found none that document Thai lyrics besides ACE-Step 1.5. YuE2-3B (zh/en, CC-BY-NC-4.0) with Thai script measured CER 0.9065, 4/30 words.
  4. [`741f7a6`](https://github.com/klanarongz2009-sketch/ter-ai/commit/741f7a6): `--thai-vocal split`, an ACE-Step instrumental plus the local TTH Wayu voice per lyric line, pitched with pyworld and sidechain ducked. CLI result CER 0.2430.
  5. Decision: the maintainer chose YuE2-3B as the main engine for Thai lyrics. [`c80a620`](https://github.com/klanarongz2009-sketch/ter-ai/commit/c80a620): yue2.cpp (pinned `8af0174`, Q5_K_M, 32 steps) is the default for Thai lyrics, with `--vocal-engine yue2|ace|split`; ACE-Step stays for English and instrumentals.
  6. [`9db0658`](https://github.com/klanarongz2009-sketch/ter-ai/commit/9db0658): songs were cut mid-phrase because yue-synth stops at duration x 25 frames. Added `--fade-out` (default 2.5 s, quadratic, only when the last 0.25 s is louder than -40 dB) and a yue2 duration taken from the lyrics.
  7. [`a1e4913`](https://github.com/klanarongz2009-sketch/ter-ai/commit/a1e4913): `--setup` checks git, cmake and a C++ compiler before any weights download. [`77221c0`](https://github.com/klanarongz2009-sketch/ter-ai/commit/77221c0): the reach report no longer claims that lyric sections outside the plan go unsung.
- **Benchmarks** (measured 2026-10-21, 8 vCPU, 8 GB RAM, no GPU; Thai test song of 4 lyric lines, seed 42; CER from `airesearch/wav2vec2-large-xlsr-53-th` on the mixed song):

| Run | Time | Peak RAM | CER | Lyric words heard |
|---|---|---|---|---|
| yue2, no `--duration` (90 s planned, ended on its own at 50.6 s, 2.5 s fade-out) | 24:53 | 2.93 GB | 0.8598 | 14/30, from all 4 lines |
| yue2, `--duration 30` (before the fix, cut mid-phrase) | 14:03 | 2.93 GB | 0.9065 | 4/30 |
| split (ACE-Step + TTH Wayu speech) | 5:44 | 3.33 GB | 0.2430 | 20/30 |
| English song on ACE-Step (floor: no Thai) | - | - | 0.8131 | 3/30 |

  After the fade fix the song tail dropped from -23.8 dB to -73.1 dB.
- **Licenses.** No weights are in the repository; `--setup` downloads them. ACE-Step 1.5, acestep.cpp and yue2.cpp are MIT; YuE2-3B and its VAE are CC-BY-NC-4.0; Qwen3-Embedding-0.6B is Apache-2.0. Songs made with yue2 (the Thai default) or split are non-commercial only; the CLI warns before each such render. NOTICE item 13 added PyThaiNLP (Apache-2.0).
- **Validation.** pytest 293 passed, 4 skipped. Parity: router 607 no diff, chat 790/790, web 24/24, TTH 1,700/1,700, SANKPUP 688/688, MuML WA 330/330, Temmo remix 42/42. `training/evaluate.py`: 121/124 and 111/112. A fresh venv installed from `@v0.13.0` reported `__version__` 0.13.0.
- **Known limits.** CPU only and slow: the release notes say about 15 minutes per 30 s of Thai song, and README.th.md says a 90 s Thai request takes about 25 minutes (the measured run was 24:53). Thai lyrics are only partly intelligible.
- **Plan versus implementation.** The MuML family plan described HIQ as fine-tuned from another model. The shipped v0.13.0 does not fine-tune anything: docs/MUML-HIQ.md says the weights are not fine-tuned and HIQ is tuned only at the conditioning level (the prompt and lyrics adapter). A LoRA on the ACE-Step DiT was not run: the turbo DiT has 2,394M parameters (9.58 GB in fp32, more than the 8 GB VM), and this CPU has AVX2 only, so bf16 training would be emulated. acestep.cpp can load a PEFT LoRA trained elsewhere later. NOTICE states HIQ does not fine-tune or redistribute the weights.

## Phase 3: project notice (2026-10-22)

Commits [`59239cf`](https://github.com/klanarongz2009-sketch/ter-ai/commit/59239cf), [`f73b7cf`](https://github.com/klanarongz2009-sketch/ter-ai/commit/f73b7cf), [`7a1f7e5`](https://github.com/klanarongz2009-sketch/ter-ai/commit/7a1f7e5) and [`372cb32`](https://github.com/klanarongz2009-sketch/ter-ai/commit/372cb32) (2026-10-22 03:15 to 03:44; 2026-10-21 20:15Z to 20:44Z) added [PROJECT_NOTICE.md](https://github.com/klanarongz2009-sketch/ter-ai/blob/main/PROJECT_NOTICE.md) and its Thai copy, linked from both READMEs. The notice says TER-AI is an indie project that may pause, may close without a reason, may close over a legal claim about a model or its output (including music that sounds like real songs), or may close for good, and it explains which free services the project depends on (the Sesame agent and its credits, GitHub, Hugging Face). These are docs commits with no tag.

## Phase 4: TERM AI comes back as a limited-time trial (2026-10-22)

- **Request.** The maintainer asked to launch TERM AI in the repository for people to try for a limited time, and to remove it on 2027-01-01 at 00:00:00.
- **What "TERM AI" is.** The Phase 0 program: `term_ai.py` with its regex rules and the TER-AI-0.5 intent model (character 1-3-gram Naive Bayes, 149 training sentences, 11 intents, leave-one-out 101/149). The later VM versions (TER-AI-0.6 and 0.6.1) were not shipped: 0.6.1 was trained partly on real chat messages, while the 0.5 data was written for the project, so 0.5 is the version that can be published.
- **Implementation.** `src/terai_router/term_ai/` (bot, intent model, trial clock, data) and `terai term`. Rules, replies and thresholds are the original ones; `model.json` is byte-identical to the 2026-10-10 file and the tests rebuild it exactly from `train_data.json`. Output on the same 14 test messages was compared with the original program: identical apart from the display name.
- **Time limit.** Fixed end `2027-01-01 00:00:00` at UTC+7. Before it a one-line notice; at and after it a clear message and exit code 3, nothing written; the Python API raises `TrialEnded`. Not added to the web demo (Thai-only replies, English-only demo UI). See [TERM AI](TERM_AI.md).
- **Validation.** 54 new tests with an injected clock (one microsecond before, exactly at, after, the same instants in UTC and UTC-5, a session crossing midnight). pytest 347 passed, 4 skipped; parity unchanged; frozen 121/124, held-out 111/112. Installed from the tag in a fresh venv: version 0.14.0, `terai term "คำนวณ (12+8)*3"` answered `(12+8)*3 = 60`.
- **Release.** v0.14.0 on 2026-10-22 04:53 (UTC+7), tag -> `0e2a5e5`; README banner and pinned announcement [issue #6](https://github.com/klanarongz2009-sketch/ter-ai/issues/6) in `147a410` on `main`.
- **Planned removal.** `trial.py` sets 2027-01-01 00:00:00 (UTC+7). Its actual removal list names the feature directory, tests, and main guide; its mention-edit list names the CLI, package metadata, both READMEs, and changelog. It does not specify Wiki/navigation/History changes or an action on issue #6. The [sunset sequence](TERM_AI.md#sunset-sequence) records those as separate maintainer follow-up recommendations: publish a notice, review issue #6, and preserve useful landing links. Old tags stay.

### v0.15.0: MuML 1.0 WA writes with the trained MuML 1.0 network (05:57)

- **Evidence.** Commit and tag `v0.15.0` -> [`c416ad2`](https://github.com/klanarongz2009-sketch/ter-ai/commit/c416ad2a47989cb8be9a2eb3298b70bd2dbce678); release ["v0.15.0: MuML 1.0 WA writes notes with the trained MuML 1.0 network"](https://github.com/klanarongz2009-sketch/ter-ai/releases/tag/v0.15.0), published 22:57Z, asset `muml-1.0-int8.bin`. Wiki page [MuML](MUML.md).
- **Why.** The maintainer said the models still felt like they answered from a script. MuML 1.0 WA was still writing notes with Markov v1 although MuML 1.0 had finished training.
- **What changed.** The browser and the new `terai muml-wa` command write notes with the MuML 1.0 network (decoder-only transformer, 3,332,352 parameters, int8 weights 3,421,372 bytes, val loss 1.3779). Markov v1 stays only as the fallback. The model id (MuML 1.0, note writer `muml-1.0-net`) is now named separately from the repository version, which stays 0.x.
- **Validation.** Distinct 4-grams 0.757 -> 0.927, bars repeated 22.3% -> 1.2%, notes in key 97.6% -> 98.3%, ends on tonic 100% -> 26.7%. pytest 353 passed, 4 skipped; parity Markov v1 330/330, network 30/30.
- **Release order.** Planned after TERAI1BETA; released first because the TERAI1BETA task had stopped. TERAI1BETA moves to the next version.

## Phase 5: TERAI1BETA, the chat model (2026-10-22)

- **Request.** The maintainer said TERAI, Temmo and MUML 1.0 still answered as if from a script, asked that the AI can read images, and that the TER-AI model version be separate from the repository version: the repository stays 0.X.Y with its 1.0 criteria unchanged, and the model is called TERAI1BETA.
- **What changed.** `src/terai_router/brain/`: Gemma 4 E2B (QAT Q4_0 GGUF, CPU, llama-cpp-python) writes the reply; the old rules (calculator, date and time, units, memory, Thai Wikipedia pack, optional web search) are its tools; a grounding check allows only numbers from a tool result, the user's message or memory, with one retry and then the rule answer. Image reading through the Gemma 4 vision projector: `terai chat --image`, `terai vision`. Weights (about 4.3 GB) download with `terai chat --setup`, never committed. The web demo keeps the rule chat.
- **Validation.** Fixed set of 52 cases: correct 22/30 -> 30/30, hallucination 1/52 -> 1/52, "I don't know" with no source 9/10 -> 9/10, varied small talk 6/12 -> 12/12; latency p50 15.9 s, p95 46.2 s on a busy CPU (load about 15 on 8 cores); peak RAM 4.7 GB. Vision on 12 test images: text CER 0.150 (Thai 0.165), 4/8 exact, questions 5/6. pytest 367 passed, 6 skipped; all parity suites unchanged.
- **Release.** v0.16.0 on 2026-10-22 06:26 (UTC+7), tag -> [`36ff01d`](https://github.com/klanarongz2009-sketch/ter-ai/commit/36ff01dd815a9bc3dea1d1008f0b8513205bb688). Planned as v0.15.0; MuML 1.0 WA took that number first.
- **Roadmap change.** The roadmap had said a language model backend would come only in 1.x. The maintainer asked for it now, so it shipped in 0.x as an optional model; the repository's 1.0 criteria did not change.

## Side projects around the repository

### GET IDEAS, the ideas bot

- **What it is.** A separate Sesame sub-agent that answers GitHub Issues of this repository with a numbered list of ideas (each with the idea, why, and a first step), signs "— GET IDEAS", and adds the label `get-ideas`. It checks every hour at minute 15. It reads `user.login` on every item: only the repository owner can ask it to act; everyone else gets ideas only. See [GET IDEAS](GET_IDEAS.md).
- **Started.** 2026-10-16: [issue #1](https://github.com/klanarongz2009-sketch/ter-ai/issues/1) "GET IDEAS test" (10:59Z, closed), then [#2](https://github.com/klanarongz2009-sketch/ter-ai/issues/2) and [#3](https://github.com/klanarongz2009-sketch/ter-ai/issues/3) (11:07Z and 11:08Z).
- **Rate limits** (added 2026-10-21): at most 5 replies per rolling hour, 30 per Bangkok day, 2 per author per hour; items over the limit are queued, never dropped; issues labelled `no-ai` are never answered.
- **Issues written by AI tools.** [#4](https://github.com/klanarongz2009-sketch/ter-ai/issues/4) (2026-10-19, labels `bug`, `get-ideas`) reports that web demo UI text leaks into name capture; a reply on 2026-10-21 reproduced it on v0.11.0 in both `docs/chat.js` and `chat.py`. It is still open and no fix commit exists. [#5](https://github.com/klanarongz2009-sketch/ter-ai/issues/5) (2026-10-20, marked as drafted by an AI tool) proposed SANKPUP unknowns; its body was rewritten on 2026-10-21 to record the maintainer's decisions. Both are proposals and bug reports, not proof of shipped work.
- **Paused.** Between 2026-10-17 and 2026-10-21 the bot did not run, because of the credit pause.

### terai.eu.org

- **Decision.** The maintainer wanted a domain but not a paid one, so `terai.chat` (free in RDAP on 2026-10-16, but paid) was not registered.
- **Request.** 2026-10-16 17:47 at nic.eu.org. DNS is hosted at deSEC (`ns1.desec.io`, `ns2.desec.org`) with records pointing to GitHub Pages.
- **Status.** Pending. A DNS query on 2026-10-22 at about 03:58 still returned NXDOMAIN for `terai.eu.org`. Until approval, the demo is at https://klanarongz2009-sketch.github.io/ter-ai/. See [Domain](DOMAIN.md).

## Planned, not shipped

Nothing in this section is in a release.

| Item | Stage | What exists |
|---|---|---|
| MuML 1.0, own music model | Integrated in v0.15.0 (MuML 1.0 WA note writer) | Trained from scratch on the Nottingham data: 3,332,352 parameters, 957 training and 50 validation tunes, 30 epochs, best validation loss 1.3780, 55.1 minutes on CPU. Used by MuML 1.0 WA since v0.15.0 (Markov v1 only as fallback). |
| TTH named voices (6 male, 3 female) | Prototype on the VM | Requested 2026-10-17. Recipes made in the 2026-10-21 night shift: each name is a weighted sum of Wayu base-voice style vectors, with speed as the weighted sum of the base speeds. The first hand-made set was rejected (somchai/freets timbre cosine 0.9696, closer than any two shipped voices, whose maximum is 0.8474); a search brought the worst male pair to 0.8843. With only 4 male base voices, 6 male voices stay near 0.88. Not in the repository. A 2026-10-22 check put CER at 0 for all 21 voices on a neutral sentence; Whisper misheard 4 of the English voice names. |
| TTH-MTL (multilingual TTH) | Proposal plus a measurement | The maintainer's order: fine-tune from ElevenLabs, else Gemini TTS, else k2-fsa/OmniVoice. A CPU test measured OmniVoice CER 0.0101 (RTF 53.1, 4,147 MB) and Wayu2 CER 0.0067 (RTF 7.79, 1,719 MB). No code in the repository. |
| Temmo 1.0 | Prototype in the demo | See above; no release, no server. |
| SANKPUP open items | Proposal | Prompt-match rubric and blank-render guard (issue #5). |
| v1.0: own model plus open-weight LLM backend | Decision, not started | Gemma, Qwen or Typhoon as an optional backend; TER-AI stays the core. |
| v1.0: languages other than Thai | Decision, not started | Languages not named yet; English first. |
| Web chat for v1.0 | Proposal | Email login with a waitlist; guests keep no history. A free domain only (`terai.chat` is paid). |

The next free release number is v0.17.0.

## Version and test numbers over time

| Version | pytest | Parity suites (JS vs Python) |
|---|---|---|
| v0.7.0 | not recorded in the logs | router (607 sentences) |
| v0.8.0 | 45 passed | router 607 no diff, chat 790/790 |
| v0.9.0 | 63 passed | + web (mocked) 24/24 |
| v0.10.0 | 108 passed | + TTH 1,700/1,700 |
| v0.11.0 | 138 passed, 1 skipped | + SANKPUP 688/688 |
| v0.12.0 | 169 passed, 1 skipped | + MuML WA 330/330 |
| v0.13.0 | 293 passed, 4 skipped | + Temmo remix 42/42 |
| v0.14.0 | 347 passed, 4 skipped | same as v0.13.0; + TERM AI leave-one-out 101/149 |
| v0.15.0 | 353 passed, 4 skipped | same as v0.14.0; + MuML 1.0 network 30/30 |
| v0.16.0 | 367 passed, 6 skipped | same as v0.15.0; + TERAI1BETA brain eval 30/30, vision 5/6 questions |

The intent router accuracy (97.6% frozen, 99.1% held-out) has been the same in every version from v0.7.0 to v0.16.0.

## Known gaps and conflicts between sources

- **Old hashes.** Issues #4 and #5, the build logs and older notes quote `765cd85` (v0.10.0), `b1fb40d` (v0.11.0), `4867fa4` (v0.12.0) and `2ead5d5` (README rewrite). These are the pre-rewrite hashes; use the current ones above.
- **Issue #5 dates.** The issue was opened on 2026-10-20, but its body cites the v0.11.0 release of 2026-10-21. The body was edited on 2026-10-21 (last update 02:42Z), so the text is newer than the creation date.
- **No tags before v0.10.0.** v0.7.0, v0.8.0 and v0.9.0 exist only as commit messages, README text and logs. The CHANGELOG starts at v0.10.0.
- **TTH and SANKPUP dates.** Both were first built on 2026-10-17 but released on 2026-10-21 because of the credit pause. Their release date is 2026-10-21.
- **TER-AI-0.5 accuracy.** The VM reports give two numbers for v0.5 on the 124-sentence set: 72/124 for the model as first shipped (72/73 on the old intents, 0 on the new ones) and 45/124 when retrained on the v0.6 training split. Later comparisons use 45/124.
- **NOTICE heading.** NOTICE used to title its HIQ section "MUML 1.0 HIQ (text-to-music audio, prototype, not released)" after v0.13.0 released it. Fixed on `main` before v0.14.0 (the heading no longer says prototype).
- **MUML 1.0 HIQ fine-tune.** Planned as a fine-tune, shipped without one (see v0.13.0).
- **TTH named-voice spec.** The chat log of 2026-10-17 says a spec file was written, but the 2026-10-21 night shift found no such file and recreated it.
- **v0.7.0 pytest count.** Not found in any source read for this page.

## Sources

Read in full for this page:

- Repository at `c2cac26`/`372cb32`: git log of all branches and tags, CHANGELOG.md, README.md, README.th.md, NOTICE, DATA_LICENSE, PROJECT_NOTICE.md, docs/MUML-HIQ.md, `bench/typhoon_results.json`.
- GitHub Releases v0.10.0 to v0.13.0 and issues #1 to #5 with their comments (GitHub REST API).
- All existing wiki pages and the wiki git log.
- Repository files also read in full: PROJECT_NOTICE.th.md, `bench/typhoon_run2.log`.
- Development VM: project memory items and changelog; the Terminal AI folder (`term_ai.py`, `ROADMAP.md`, `FAQ-draft.md`; in `v0.6/` and `v0.6.1/` the eval reports, experiment reports, dataset info, model-selection report, typo-robustness report, model configs and router; `v0.8/`, which holds only the Wikipedia download cache; `release/`, with the Typhoon benchmark logs and the v0.12.0 staging copy); task and chat logs from 2026-10-10 to 2026-10-22; all night-shift runs (2026-10-15, 16, 17, 21 and 22).
- A live DNS query for `terai.eu.org` on 2026-10-22.
