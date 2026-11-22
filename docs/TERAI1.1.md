# TERAI1.1: Thai essay and proverb mode (opt-in)

TERAI1.1 is an opt-in model profile in TER-AI for writing Thai essays (เรียงความ) and for Thai
idioms and proverbs (สำนวน, สุภาษิต, คำพังเพย). TERAI1 stays the default model and is unchanged.

## What it is, and what it is not

- **Base model:** the same local Gemma 4 E2B GGUF that TERAI1 uses (open weights, Apache-2.0).
  TER-AI did not train this foundation model.
- **No fine-tuning.** TERAI1.1 v1 changes nothing in the weights. A LoRA fine-tune is a later gate
  (see below); it has not been done.
- **What TERAI1.1 adds on top of the base:**
  1. A Thai proverb and idiom pack, `src/terai_router/data/proverbs_th.json`, built from Thai
     Wiktionary by `training/build_proverbs.py`. Each entry keeps its page id and revision id.
  2. Retrieval: matching pack entries go into the prompt. `terai terai11 proverb` answers from the
     pack only, adds the source link, and says "not in the pack" instead of guessing.
  3. An essay pipeline: outline (intro, three body points, conclusion; one idiom chosen from the
     pack) -> draft -> automatic self-check -> at most one revision, kept only if it fixes more.
  4. A Thai system prompt for essays and idioms.

## Use

```bash
terai terai11 info                                   # pack size, source, license
terai terai11 proverb "กบในกะลา"                     # pack only, no model needed
terai terai11 search "ความอดทน"                       # pack entries close to a meaning
terai terai11 ask "สำนวนไหนหมายถึงคนที่รู้น้อย"      # needs the local Gemma 4 GGUF
terai terai11 essay "ความสำคัญของการอ่านหนังสือ"  # outline -> draft -> self-check
```

`ask` and `essay` need the same optional local setup as TERAI1 (`llama-cpp-python` and the Gemma 4
E2B GGUF; see the TERAI1 section of the README). An essay takes about 31 seconds on the CPU test VM (median of 40;
TERAI1 plain prompt: about 22 seconds).

## Evaluation

Frozen held-out set: `eval/terai11_heldout_v1.json` (SHA-256 in `eval/SHA256SUMS`), built by
`eval/terai11_build.py` with seed 1101. A separate dev file was used for prompt checks; the held-out
file was not used for tuning. Both arms ran the same Gemma 4 E2B QAT Q4_0 GGUF on CPU through
`LocalLM`, temperature 0 for questions, 0.3 for essays, seed 0. Raw outputs:
`eval/results/terai11_v1.jsonl` (essay rubric fields recomputed with the current `rubric()`; re-check with
`eval/terai11_eval.py --summary eval/results/terai11_v1.jsonl --rescore`). Reproduce with `eval/terai11_eval.py`.

| Part (held-out) | TERAI1 (base) | TERAI1.1 |
|---|---|---|
| Proverb items, all | 57/100 | 88/100 |
| - meaning (4-way choice) | 24/40 | 40/40 |
| - complete the idiom (4-way) | 11/20 | 18/20 |
| - fill the blank in an example sentence (4-way) | 9/20 | 10/20 |
| - real or made-up idiom | 13/20 | 20/20 |
| Essays: automatic rubric points | 180/280 | 269/280 |

Essay rubric, essays passing each check (40 prompts):

| Check | TERAI1 | TERAI1.1 |
|---|---|---|
| Three or more paragraphs | 40/40 | 40/40 |
| Uses an idiom from the pack (title of 4+ characters) | 17/40 | 40/40 |
| Idiom paragraph overlaps the idiom's meaning (trigram proxy) | 3/40 | 29/40 |
| Thai script (>= 95% of letters) | 40/40 | 40/40 |
| Length 400-4000 characters | 40/40 | 40/40 |
| No markdown headings or bullets | 0/40 | 40/40 |
| No repeated sentences | 40/40 | 40/40 |

### Read these numbers with their limits

- **The proverb items are generated from the pack itself.** They measure whether the model gets
  in-pack idioms right, not coverage of all Thai idioms. "Real or made-up" is answered by TERAI1.1
  with a pack lookup, so 20/20 there is by construction; a real idiom that is missing from the pack
  would be called made-up.
- **The essay rubric is automatic.** It checks form (paragraphs, Thai script, no markdown, length,
  repeated sentences), whether an idiom from the pack appears, and a character-trigram overlap between
  that paragraph and the idiom's meaning. It is a proxy. It does not grade argument quality, style or
  grammar, and no human grading was done. TERAI1's markdown headings in essays count against it.
- **Two answer keys are weak.** Items 17 and 18 (meaning) use the first Wiktionary sense, which is the
  literal sense / a song title rather than the idiom's figurative meaning. Both arms got both right;
  without them: TERAI1 55/98, TERAI1.1 86/98. The frozen v1 file is kept as is (its hash is the
  contract); the builder now picks the figurative sense, for a future v2.
- **The "terai1" arm is the TERAI1 base model with a plain prompt** (`LocalLM(model="e2b")`, the
  QAT Q4_0 GGUF), not the full `terai chat --brain terai1` route with its system prompt.
- **One run, one seed, CPU only.** No confidence intervals.
- The idiom TERAI1.1 picks is not always a good fit for the topic; the overlap check does not catch that.
- "Fill the blank" moved by one item (9 -> 10/20): treat that as no measurable change.

## Limits

- Knows only the idioms in the pack (Thai Wiktionary categories สำนวนภาษาไทย and
  สุภาษิตภาษาไทย, retrieved 2026-11-22). Wiktionary definitions can be short or incomplete.
- `ask` and `essay` are generated by a 2B-class model: they can still contain wrong Thai or a wrongly
  used idiom. Only `proverb` and `search` output come straight from the pack.
- No fine-tuning, no new training data beyond the pack.

## Licenses

- TERAI1.1 code (`src/terai_router/terai11/`, the build and eval scripts, the tests): TER-AI License 2.0.
- Pack and eval files that quote it: CC BY-SA 4.0, Wiktionary contributors (see `DATA_LICENSE`).
  Pack answers end with the entry title, a link to its page and "CC BY-SA 4.0".
- Gemma 4 E2B weights: Apache-2.0, by Google DeepMind, downloaded separately, not shipped here.
- Essay topics in the eval set: written for this project, TER-AI License 2.0.

## Later gate: LoRA fine-tune

Not done. Allowed only on free compute without billing or new sign-ins, trained on licensed data
(the pack and project-written essays), and shipped only if it beats TERAI1.1 v1 on this same frozen
set without regressions. Until then TERAI1.1 is the base model plus retrieval and a pipeline.
