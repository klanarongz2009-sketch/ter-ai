# FAQ

> **Migration note (2026-11-22):** This replaces the outdated Wiki FAQ with current repository guidance. See the [documentation index](INDEX.md).

### What is TER-AI?

TER-AI is an open-source Thai-language AI toolkit. The current package is v0.18.3. Its primary component is a small, offline Thai intent router; the repository also contains separate chat, speech, graphics, and music tools. See the [README](../../README.md) for component scope and limitations.

### Does the intent router use a generative language model or need the network?

No. The intent router is a compact local classifier and runs on CPU without network access. Other optional components have different requirements: some use local model weights, and some explicitly offer online services. Check each component's current setup and data flow before use.

### What are TERAI1 and TERAI1SML?

The README describes TERAI1 as a beta chat model using local Gemma 4 E2B; TERAI1SML is an unreleased, text-only Qwen2.5-0.5B-Instruct prototype. Neither is the intent router, and TERAI1SML is not the proposed TER-AI 2.9 Qwen fine-tuning work. See [Versions: repository and models](../../README.md#versions-repository-and-models).

### Where are evaluation results?

The README's frozen-set scores are internal project evaluations, not an independent benchmark. See the [evaluation guide](../AI_EVALUATION.md) for what was measured and its limitations.

### Where is the current roadmap?

The README holds current project direction. The [TER-AI 2.9 roadmap](../TERAI2.9_ROADMAP.md) is a proposal, not a merged implementation plan; its Mac and model-variant details remain gates.
