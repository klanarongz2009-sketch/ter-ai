"""Local TERAI1 chat backends: Gemma 4 for text and vision, or TERAI1SML for compact text-only chat.

Weights are downloaded on first use into ``$TERAI_MODELS_DIR`` (default ``~/.cache/terai/models``) and
SHA-256 checked. Gemma 4 is Apache-2.0 (NOTICE item 4); TERAI1SML uses Qwen2.5 under Apache-2.0.
"""
from __future__ import annotations

import base64
import mimetypes
import os
import re
import sys
import time
from pathlib import Path

from ..sankpup import gemma as G

DEFAULT_MODEL = "e2b"
SML_MODEL = "sml"
SML_MODEL_ID = "TERAI1SML"
# Official Qwen2.5 0.5B Instruct Q2_K GGUF (Apache-2.0). This is the smallest official
# quant in the repository: 415 MB on disk, text-only, with no image projector.
SML_SPEC = G.ModelSpec(
    "terai1sml", "Qwen/Qwen2.5-0.5B-Instruct-GGUF", "qwen2.5-0.5b-instruct-q2_k.gguf",
    415182688, "9ee36184e616dfc76df4f5dd66f908dbde6979524ae36e6cefb67f532f798cb8",
    "TERAI1SML; Qwen2.5-0.5B-Instruct Q2_K; text-only, smallest official quant",
    "9217f5db79a29953eb74d5343926648285ec7e67",
)


def normalize_model(model: str | None) -> str:
    name = (model or os.environ.get("TERAI_LLM_MODEL") or DEFAULT_MODEL).lower()
    return SML_MODEL if name in ("terai1sml", "qwen2.5-0.5b-instruct", "qwen2.5-0.5b-instruct-q2_k") else name


def model_id(model: str | None) -> str:
    return SML_MODEL_ID if normalize_model(model) == SML_MODEL else "TERAI1"


def model_base(model: str | None) -> str:
    name = normalize_model(model)
    return "Qwen2.5-0.5B-Instruct Q2_K" if name == SML_MODEL else "Gemma 4 " + name.upper()


def model_spec_path(model: str | None = None):
    name = normalize_model(model)
    if name == SML_MODEL:
        return SML_SPEC, G.models_dir() / SML_SPEC.filename
    return G.resolve_model(name)


def _sml_verified(path: Path) -> bool:
    return path.is_file() and path.stat().st_size == SML_SPEC.size and G.sha256_file(path) == SML_SPEC.sha256


def _download_model(model: str, quiet: bool = False) -> Path:
    name = normalize_model(model)
    if name != SML_MODEL:
        return G.download(name, quiet=quiet)
    path = G.models_dir() / SML_SPEC.filename
    if path.exists():
        if not _sml_verified(path):
            raise LLMUnavailable(f"TERAI1SML file failed its size/SHA-256 check: {path}; remove the corrupt file and run terai chat --brain terai1sml --setup")
        return path
    return _download_spec(SML_SPEC, quiet=quiet)


# Vision projectors that go with the Gemma 4 GGUF files (same Hugging Face repositories, Apache-2.0).
MMPROJ = {
    "e2b": G.ModelSpec("e2b-mmproj", "google/gemma-4-E2B-it-qat-q4_0-gguf", "gemma-4-E2B-it-mmproj.gguf", 986833664,
                       "021059cce659fe7f9170d5599761d7bbaf644b798dab9503aca30dc43e6beb14", "vision projector for e2b"),
    "e4b": G.ModelSpec("e4b-mmproj", "google/gemma-4-E4B-it-qat-q4_0-gguf", "gemma-4-E4B-it-mmproj.gguf", 991552256,
                       "7498a37cb619e55f2fcf87eb931f56e99389ed6d432e4c5c66110694c0d65578", "vision projector for e4b"),
}

INSTALL_HINT = ("TERAI1 needs llama-cpp-python: pip install \"terai-router[llm] @ "
                "git+https://github.com/klanarongz2009-sketch/ter-ai.git\" (then terai chat --setup)")


class LLMUnavailable(RuntimeError):
    pass


def available(model: str = DEFAULT_MODEL, vision: bool = False) -> bool:
    """True when llama-cpp-python is installed and the requested weights are already on disk."""
    name = normalize_model(model)
    if vision and name == SML_MODEL:
        return False
    if not G.llama_cpp_available():
        return False
    if name == SML_MODEL:
        return _sml_verified(G.models_dir() / SML_SPEC.filename)
    if not G.is_downloaded(name):
        return False
    return not vision or mmproj_path(name).is_file()


def mmproj_path(model: str = DEFAULT_MODEL) -> Path:
    spec = MMPROJ.get((model or DEFAULT_MODEL).lower())
    if spec is None:
        env = os.environ.get("TERAI_MMPROJ")
        if env:
            return Path(env).expanduser()
        raise LLMUnavailable(f"no vision projector known for model '{model}'; set TERAI_MMPROJ to a mmproj .gguf")
    return G.models_dir() / spec.filename


def _download_spec(spec, quiet=False) -> Path:
    """Download one ModelSpec with the SANKPUP downloader (resumable, SHA-256 checked)."""
    saved = dict(G.MODELS)
    try:
        G.MODELS[spec.key] = spec
        return G.download(spec.key, quiet=quiet)
    finally:
        G.MODELS.clear()
        G.MODELS.update(saved)


def setup(model: str = DEFAULT_MODEL, vision: bool = True, quiet: bool = False) -> list:
    """Download a TER-AI chat model. TERAI1SML is text-only and has no projector."""
    name = normalize_model(model)
    if name == SML_MODEL:
        if vision:
            raise LLMUnavailable("TERAI1SML is text-only and cannot read images; omit vision setup")
        return [_download_model(name, quiet=quiet)]
    paths = [_download_model(name, quiet=quiet)]
    if vision and name in MMPROJ:
        paths.append(_download_spec(MMPROJ[name], quiet=quiet))
    return paths


def image_data_uri(path: str) -> str:
    p = Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"image not found: {p}")
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    if not mime.startswith("image/"):
        raise ValueError(f"not an image file: {p}")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def _perf_reset(llm):
    """Reset llama.cpp's perf counters; returns a reader for prefill/generation tokens and seconds."""
    try:
        import llama_cpp
        llama_cpp.llama_perf_context_reset(llm.ctx)
    except Exception:
        return lambda _llm: {}

    def read(_llm):
        try:
            p = llama_cpp.llama_perf_context(_llm.ctx)
            return {"prefill_tokens": int(p.n_p_eval), "prefill_s": round(p.t_p_eval_ms / 1000, 2),
                    "gen_tokens": int(p.n_eval), "gen_s": round(p.t_eval_ms / 1000, 2)}
        except Exception:
            return {}
    return read


def json_complete(text: str) -> bool:
    """True once ``text`` holds one complete top-level JSON object (string-aware brace count)."""
    depth, in_str, esc, seen = 0, False, False, False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
            seen = True
        elif ch == "}":
            depth -= 1
            if seen and depth == 0:
                return True
    return False


def _stream_until_json(chunks) -> tuple:
    """Read a streamed chat completion; stop once one JSON object is complete. Returns (text, chunks, stopped_early)."""
    text, n, early = "", 0, False
    try:
        for ch in chunks:
            delta = ((ch.get("choices") or [{}])[0].get("delta") or {}).get("content") or ""
            if not delta:
                continue
            n += 1
            text += delta
            if "}" in delta and json_complete(text):
                early = True
                break
    finally:
        close = getattr(chunks, "close", None)
        if close:
            close()
    return text, n, early


_THOUGHT = re.compile(r"<\|channel\>.*?<channel\|>|<think>.*?</think>", re.S)


def clean_reply(text: str) -> str:
    text = _THOUGHT.sub("", text or "")
    text = text.replace("<end_of_turn>", "").replace("<turn|>", "")
    return text.strip()


class LocalLM:
    """One loaded Gemma 4 model. ``vision=True`` also loads the image projector (about 1 GB more RAM).

    ``client`` is a test hook: callable(messages, max_tokens=, temperature=, seed=) -> str.
    """

    def __init__(self, model: str | None = None, vision: bool = False, threads: int | None = None,
                 n_ctx: int = 4096, auto_download: bool = True, client=None, threads_batch: int | None = None,
                 flash_attn: bool | None = None, n_batch: int | None = None) -> None:
        self.model = normalize_model(model)
        self.vision = vision
        self.threads = threads or int(os.environ.get('TERAI_THREADS') or 0) or max(1, os.cpu_count() or 1)
        self.n_ctx = n_ctx
        self.auto_download = auto_download
        self._client = client
        self.threads_batch = threads_batch   # None: llama.cpp default (same as threads)
        self.flash_attn = flash_attn         # None: llama.cpp default (off)
        self.n_batch = n_batch               # None: llama.cpp default (512)
        self._llm = None
        self.load_seconds = 0.0
        self.calls = []  # (seconds, prompt_tokens, completion_tokens) per call
        self.perf = []   # per call: {seconds, prefill_tokens, prefill_s, gen_tokens, gen_s, early_stop}

    @property
    def label(self) -> str:
        if self._client:
            return "test client"
        if self.model == SML_MODEL:
            return "Qwen2.5-0.5B-Instruct Q2_K (TERAI1SML)"
        return f"gemma-4-{self.model} q4_0" + (" + mmproj" if self.vision else "")

    def load(self):
        if self._client is not None or self._llm is not None:
            return self._llm
        if self.vision and self.model == SML_MODEL:
            raise LLMUnavailable("TERAI1SML is text-only; use TERAI1 (Gemma 4) for image reading")
        try:
            from llama_cpp import Llama
        except Exception as exc:
            raise LLMUnavailable(INSTALL_HINT) from exc
        _spec, path = model_spec_path(self.model)
        if not path.is_file():
            if not self.auto_download:
                raise LLMUnavailable(f"model weights not found at {path}; run terai chat --brain terai1sml --setup")
            label = "TERAI1SML Qwen2.5 0.5B" if self.model == SML_MODEL else "TERAI1 Gemma 4"
            print(f"{label}: downloading model weights (first use)", file=sys.stderr)
            path = _download_model(self.model)
        elif self.model == SML_MODEL and not _sml_verified(path):
            raise LLMUnavailable(f"TERAI1SML file failed its size/SHA-256 check: {path}")
        kw = {}
        if self.vision:
            mp = mmproj_path(self.model)
            if not mp.is_file():
                if not self.auto_download:
                    raise LLMUnavailable(f"vision projector not found at {mp}; run: terai vision --setup")
                mp = _download_spec(MMPROJ[self.model])
            try:
                from llama_cpp.llama_chat_format import Gemma4ChatHandler
            except Exception as exc:
                raise LLMUnavailable("this llama-cpp-python has no Gemma4ChatHandler; need >= 0.3.36") from exc
            kw["chat_handler"] = Gemma4ChatHandler(clip_model_path=str(mp), verbose=False)
        if self.threads_batch:
            kw["n_threads_batch"] = self.threads_batch
        if self.flash_attn is not None:
            kw["flash_attn"] = bool(self.flash_attn)
        if self.n_batch:
            kw["n_batch"] = self.n_batch
        t0 = time.time()
        self._llm = Llama(model_path=str(path), n_ctx=self.n_ctx, n_threads=self.threads, verbose=False, **kw)
        self.load_seconds = round(time.time() - t0, 2)
        return self._llm

    def chat(self, messages: list, max_tokens: int = 300, temperature: float = 0.3, seed: int | None = 0,
             stop: list | None = None, json_schema: dict | None = None, stop_on_json: bool = False) -> str:
        """``stop_on_json``: stream the reply and stop as soon as one complete JSON object has come out."""
        if self._client is not None:
            return self._client(messages, max_tokens=max_tokens, temperature=temperature, seed=seed)
        llm = self.load()
        kw = {"messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        if seed is not None:
            kw["seed"] = seed
        if stop:
            kw["stop"] = stop
        if json_schema is not None:
            kw["response_format"] = {"type": "json_object", "schema": json_schema}
        perf = _perf_reset(llm)
        t0 = time.time()
        early = False
        if stop_on_json:
            text, n_out, early = _stream_until_json(llm.create_chat_completion(stream=True, **kw))
            n_in = 0
        else:
            r = llm.create_chat_completion(**kw)
            u = r.get("usage") or {}
            text = r["choices"][0]["message"].get("content") or ""
            n_in, n_out = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
        secs = round(time.time() - t0, 2)
        self.calls.append((secs, n_in, n_out))
        self.perf.append(dict(perf(llm), seconds=secs, early_stop=early))
        return clean_reply(text)

    def look(self, image: str, question: str, max_tokens: int = 400, temperature: float = 0.0,
             system: str | None = None) -> str:
        """Ask about one image file."""
        if not self.vision:
            raise LLMUnavailable("this LocalLM was loaded without vision; use LocalLM(vision=True)")
        content = [{"type": "image_url", "image_url": {"url": image_data_uri(image)}},
                   {"type": "text", "text": question}]
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": content}]
        return self.chat(msgs, max_tokens=max_tokens, temperature=temperature)
