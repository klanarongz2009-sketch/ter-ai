# TER-AI 2.9 model roadmap

Status: proposal for investigation, not an implementation commitment or release schedule.

This roadmap explores a small, locally runnable Qwen-based model for a future TER-AI model version. “TER-AI 2.9” is a working name from the request, not a confirmed model ID or package version. TER-AI keeps model IDs separate from the repository's `0.X.Y` package versions; confirm the final name and role before implementation.

The [Qwen LoRA tutorial](https://youtube.com/watch?v=m5juRyGmhU4&si=tjGbXIHCGpiV8Qhc) is a workflow reference: it demonstrates fine-tuning Qwen3 1.7B on a Mac. It is not a TER-AI implementation, does not establish that the requested Qwen 2.5/3.5 1.5B variants fit an unknown Mac, and does not show that fine-tuning improves factual accuracy. Treat the existing [TERAI1SML Qwen2.5-0.5B prototype](../README.md#terai1sml-prototype-small-storage-text-model-not-yet-released) as a nearby project baseline, not as proof of readiness.

## Design intent

- Test whether a fine-tuned small Qwen model improves one explicitly chosen TER-AI task, especially Thai interaction or instruction-following, while preserving TER-AI's local-first and evidence-grounded behavior.
- Keep deterministic tools, project rules, source data and safety checks outside the model. A fine-tuned model should not become the authority for calculations, memory changes, or unsupported facts.
- Compare a fine-tuned adapter with the same base model and the current TER-AI behavior. If it does not provide a measurable improvement within the chosen resource budget, do not ship it.

## Sequence and exit gates

These are ordered gates, not dated milestones. The Mac model, chip, unified memory and available storage are not yet specified.

1. **Define the target.** Choose the exact user task, supported input/output format, language scope, and what the model must refuse or leave to TER-AI tools. Write success criteria before training; do not assume this is a replacement for the intent router or TERAI1.
2. **Select a candidate and verify feasibility.** Compare the requested Qwen 2.5/3.5 1.5B candidates with the tutorial's Qwen3 1.7B reference and the existing TERAI1SML prototype. Record exact model IDs/revisions, weight format, license, runtime support, download/storage size and measured memory needs. Select a training stack only after checking support on the actual Mac. Stop here until hardware and model details are known.
3. **Build a clean dataset and baseline.** Use only project-owned or clearly licensed examples; exclude private user data. Split train, development and held-out test data, deduplicate and run the project's leakage checks. Include representative Thai, Thai-English, typo, correct abstention and “no tool needed” cases where they fit the target. Freeze the held-out set and its hash. Evaluate the base Qwen and current TER-AI behavior first, following the [evaluation guide](AI_EVALUATION.md).
4. **Run a small LoRA feasibility experiment.** Start with a smoke test, then a small reproducible run on the selected Mac. Keep base weights unchanged and save the adapter separately. Record software versions, configuration, seed, data/model revisions, elapsed time, peak memory, failures and artifact hashes. Do not assume QLoRA or a particular Mac backend is supported; verify the chosen method for the selected stack.
5. **Evaluate before integrating.** Compare base, fine-tuned and current TER-AI outputs on the same frozen cases. Report raw counts and denominators for task correctness, Thai quality, appropriate abstention, unsupported claims, tool/format correctness and regressions. Also report p50/p95 latency, peak memory, download size and offline behavior. Set numeric acceptance thresholds before the run; do not tune against the held-out set.
6. **Integrate only if the gate passes.** Keep the candidate opt-in under a distinct model ID, pin the base revision and adapter hash, and preserve the existing rules/tools, grounding checks and safe fallback. Make initial model acquisition explicit; verify that inference works offline after setup. Document limits and licensing beside the model entry and test clean setup, missing/corrupt weights, fallback and existing behavior.
7. **Release decision.** Run real-model tests plus the existing test suite and relevant Python/browser parity checks. Publish results, resource requirements, license/attribution and known failures. Keep the model experimental until the maintainer explicitly decides whether to release it; this roadmap itself does not authorize a release or change the project's version policy.

## Decisions still open

- The target task and whether this is a chat model, tool-call model, or another component.
- Exact Qwen family, model revision and weight format; “Qwen 2.5/3.5 1.5B” is not yet a single selected model.
- Mac model/chip, unified memory, free disk space and acceptable training/inference time.
- Dataset sources, license review, evaluation thresholds and supported use cases.
- The eventual model ID and how it relates to TERAI1 / TERAI1SML.

No dates are assigned until the target and hardware gates are settled.
