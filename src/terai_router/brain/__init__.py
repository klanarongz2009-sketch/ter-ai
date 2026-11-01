"""TERAI1 (beta; named TERAI1BETA in 0.16.0): the TER-AI model with a local language model.

A small local Gemma 4 (E2B, quantized, CPU) writes the chat replies and reads images. The rule-based parts of TER-AI
(calculator, date and time, unit conversion, memory, the Thai Wikipedia pack, web search) are its tools: their
results ground tool-backed replies. A grounding check keeps those replies tied to their evidence and falls back
to the rule answer when they add unsupported numbers or facts. When no source is found, the language model may answer
stable general-knowledge questions, but should acknowledge uncertainty and must not invent current, personal or
project-specific facts that require verification.

The weights are downloaded on first use (or with ``terai chat --setup``) and are never stored in this repository.
"""
from .local import LocalLM, LLMUnavailable, setup  # noqa: F401
from .agent import Brain  # noqa: F401
