# Roadmap

> **Migration note (2026-11-22):** Archived Wiki roadmap snapshot. Its completed/forward-looking statements reflect the original page date and are not current commitments. The current repository roadmap is in the [README](../../README.md#roadmap) and the proposed [TER-AI 2.9 roadmap](../TERAI2.9_ROADMAP.md).
> This page is maintained in the repository; see the [documentation index](INDEX.md).


## Done

### v0.7.0: intent router

- Offline Thai intent router that tolerates typos and speech-to-text errors: 15 intents, 1.1 MB, CPU only, no dependencies.
- 97.6% (121/124) on the frozen test set, 99.1% (111/112) held out.
- Benchmark against Typhoon2 1B instruct (accuracy, speed, size).
- Browser demo on GitHub Pages; `pip install` from GitHub.

### v0.8.0: offline chat

- `Chat` and `terai chat`: tools (calculator, date and time, unit conversion, random, text tools), memory saved to a session file, follow-ups.
- Thai Wikipedia knowledge pack (8,192 articles, CC BY-SA 4.0) with the source named in every answer, and "I don't know" instead of guessing.
- Chat mode in the browser demo (`docs/chat.js`), with JavaScript/Python parity.

### v0.9.0: opt-in web search

- `terai chat --web`, `Chat(web=True)`: Thai Wikipedia, then English Wikipedia, then an optional SearXNG instance.
- Our own ranking and passage choice, citation on every web answer, 5-second timeout, cache, fallback to the pack when offline.
- Web search switch in the browser demo, off by default.
- Mocked-web parity between JavaScript and Python (24/24 turns).

### v0.10.0: TTH, Thai speech

- `terai tth`, `TTH(...).synthesize(...)`: local Wayu-Paxa-TTS-Edge (weights downloaded from Hugging Face at runtime, CC-BY-NC-4.0) with edge-tts fallback, as optional extras `tth` and `tth-edge`.
- Thai text frontend (numbers, times, versions, maths, abbreviations, acronyms, ครับ/ค่ะ) and 90-character chunking, the same in Python and JavaScript.
- `terai chat --speak` and the Speak replies (TTH) switch in the browser demo (Web Speech API th-TH, off by default).
- Frontend parity between JavaScript and Python (1,700/1,700); 108 tests. See [TTH](TTH.md).

### v0.11.0: SANKPUP, pictures from code

- `terai sankpup`, `sankpup.generate(...)`: a local Gemma 4 model (default E2B, QAT Q4_0 GGUF) or the offline generator writes SVG, which is sanitized and rendered to PNG/JPG. Optional extras `sankpup` and `sankpup-gemma`. No cloud API.
- Gemma 4 E2B bench on 8 CPU cores: 11/12 valid pictures, p50 24.2 s per picture.
- SANKPUP tab in the browser demo (offline generator, byte-identical to Python, 688/688); 138 tests. See [SANKPUP](SANKPUP.md).

### v0.12.0: MuML 1.0 WA, music in the browser

- `terai_router.muml_wa` and the MuML tab: a Thai or English prompt and a seed become a Folk or Rock song, synthesized by the Web Audio API, downloadable as .wav and .mid. No server, no cloud API.
- Note writer: Markov v1 (seeded Markov chain from the Nottingham tunes); same interface so the model can replace it. Replaced in v0.15.0: the trained MuML 1.0 network (`muml-1.0-net`) now writes the notes, and Markov v1 is only the fallback.
- License: code MIT; the note table is GPL-3.0 data in its own files (Nottingham dataset). JavaScript vs Python 330/330; 169 tests. See [MuML](MUML.md).

### v0.13.0: MUML 1.0 HIQ, text-to-music audio on CPU

- `terai muml --hiq`: a Thai or English prompt (and optional lyrics) becomes an .mp3 or .wav, offline after `--setup`. Built on other open models; weights not fine-tuned and not stored in the repo.
- Engines: ACE-Step 1.5 for instrumentals and English songs; YuE2-3B for Thai lyrics (default); `split` = ACE-Step instrumental + TTH Wayu speech.
- `--fade-out` for songs cut at the requested length, song length sized from the lyrics for yue2, and a `--setup` that checks git, cmake and a C++ compiler before downloading.
- Thai song on yue2: 24:53, peak RSS 2.93 GB, CER 0.8598, 14/30 lyric words. Songs from yue2 or split are non-commercial only (CC-BY-NC-4.0). 293 tests. See [MuML](MUML.md) and [Evaluation](EVALUATION.md).

### v0.14.0: TERM AI, limited-time trial

- `terai term`: the original Terminal AI of 2026-10-10 (rules plus the TER-AI-0.5 intent model), shipped as it was. Offline, no dependencies.
- Limited-time trial: works until 2027-01-01 00:00:00 Asia/Bangkok (UTC+7); at and after that it prints that the trial ended and exits with code 3. 347 tests. See [TERM AI](TERM_AI.md).

## Ending: TERM AI on 2027-01-01 00:00:00 (UTC+7)

- TERM AI is removed from `main` at the end of the trial. The file list is on [TERM AI](TERM_AI.md) (Removal). Old tags and releases stay.

## Next: v1.0, more languages

- Languages other than Thai, starting with English.
- Each language gets its own training data, typo and speech-to-text augmentation, its own frozen test set, and must pass 90% accuracy.
- Automatic language detection before the intent model, including mixed Thai-English messages.
- It must stay small and run offline on CPU.

## Done early: optional language model backend (TERAI1BETA, v0.16.0)

Shipped in v0.16.0 as the optional chat model TERAI1BETA (Gemma 4 E2B), at the maintainer's request, ahead of the plan below. The repository's 1.0 criteria are unchanged. Original plan, kept for the record:

- TER-AI keeps doing routing, tools, memory, retrieval and web search (the facts). An optional small model only rewrites those facts into more natural Thai, grounded in them.
- Candidates: Gemma 3 (270M, 1B), small Qwen models, Typhoon2 (1B, 3B), compared on the same Thai chat eval for naturalness, hallucination, latency and RAM.
- Optional install, offline on CPU (quantized), with plain TER-AI as the fallback. Each backend's license will be added to the repo, and the README will say which parts are ours.
- ~~The 0.x line stays TER-AI only. Backend work happens only in 1.x.~~ Changed in v0.16.0: the backend is optional, so the rule chat stays the default without it.

## Web chat

A web chat using TER-AI is planned together with v1.0, at [terai.eu.org](DOMAIN.md) once the domain is approved.

Have an idea? Open an issue and [GET IDEAS](GET_IDEAS.md) will reply.
