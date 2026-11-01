"""TERAI1SML: the compact, text-only Qwen chat variant. No model weights are loaded."""
from pathlib import Path

import pytest

from terai_router.brain import local
from terai_router.brain.agent import Brain, identity_answer, system_prompt
from terai_router.brain.cli import make_brain, vision_main
from terai_router.chat import Chat
from terai_router.cli import chat_main
from terai_router.versions import MODELS


def test_small_model_metadata_is_pinned_and_explicit():
    spec = local.SML_SPEC
    assert spec.repo == "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    assert spec.filename == "qwen2.5-0.5b-instruct-q2_k.gguf"
    assert spec.size == 415182688
    assert spec.revision == "6dd44a1fb35d11b5d1b28902876ce3cc9e882d0e"
    assert spec.sha256 == "9ee36184e616dfc76df4f5dd66f908dbde6979524ae36e6cefb67f532f798cb8"
    assert spec.url.endswith(f"{spec.revision}/{spec.filename}")
    row = next(m for m in MODELS if m["id"] == "TERAI1SML")
    assert row["since"] == "-"
    assert row["status"] == "prototype, not released"


@pytest.mark.parametrize("alias", ["sml", "TERAI1SML", "qwen2.5-0.5b-instruct", "qwen2.5-0.5b-instruct-q2_k"])
def test_model_aliases_normalize_to_sml(alias):
    assert local.normalize_model(alias) == local.SML_MODEL
    assert local.model_id(alias) == "TERAI1SML"


def test_model_path_is_text_model_and_no_projector(tmp_path, monkeypatch):
    monkeypatch.setattr(local.G, "models_dir", lambda: tmp_path)
    spec, path = local.model_spec_path("terai1sml")
    assert spec == local.SML_SPEC
    assert path == tmp_path / local.SML_SPEC.filename
    with pytest.raises(local.LLMUnavailable, match="no vision projector"):
        local.mmproj_path("sml")


def test_setup_refuses_vision_for_small_model():
    with pytest.raises(local.LLMUnavailable, match="text-only"):
        local.setup("TERAI1SML", vision=True)


def test_sml_disk_size_and_default_model_sizes_are_distinct():
    from terai_router.sankpup.gemma import MODELS as GEMMA_MODELS
    assert local.SML_SPEC.size == 415182688
    assert GEMMA_MODELS["e2b"].size == 3349516256
    assert local.MMPROJ["e2b"].size == 986833664
    assert GEMMA_MODELS["e2b"].size + local.MMPROJ["e2b"].size == 4336349920


def test_sml_file_verification_checks_size_and_published_hash(tmp_path, monkeypatch):
    path = tmp_path / local.SML_SPEC.filename
    with path.open("wb") as f:
        f.truncate(local.SML_SPEC.size)
    monkeypatch.setattr(local.G, "sha256_file", lambda p: local.SML_SPEC.sha256)
    assert local._sml_verified(path)
    monkeypatch.setattr(local.G, "sha256_file", lambda p: "wrong")
    assert not local._sml_verified(path)
    path.write_bytes(b"too small")
    monkeypatch.setattr(local.G, "sha256_file", lambda p: local.SML_SPEC.sha256)
    assert not local._sml_verified(path)


def test_setup_small_model_downloads_only_the_text_weights(tmp_path, monkeypatch):
    target = tmp_path / "qwen.gguf"
    calls = []
    monkeypatch.setattr(local, "_download_model", lambda model, quiet=False: calls.append((model, quiet)) or target)
    assert local.setup("TERAI1SML", vision=False) == [target]
    assert calls == [("sml", False)]


def test_small_model_identity_names_qwen_and_no_vision():
    assert "TERAI1SML" in identity_answer("who are you", "sml")
    assert "Qwen2.5-0.5B-Instruct Q2_K" in identity_answer("what model do you use", "sml")
    prompt = system_prompt("sml")
    assert "TERAI1SML" in prompt and "Qwen2.5-0.5B-Instruct Q2_K" in prompt
    assert "และอ่านภาพ" not in prompt


def test_brain_engine_selects_sml_without_loading_weights():
    brain = make_brain(Chat(now="2026-10-28T09:30:00", seed=1), "terai1sml", None, 1, quiet=True)
    assert isinstance(brain, Brain)
    assert brain.lm.model == local.SML_MODEL


@pytest.mark.parametrize("args", [["--brain", "terai1sml", "--setup"], ["--model", "TERAI1SML", "--setup"]])
def test_chat_setup_selects_small_weights_without_projector(args, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(local, "setup", lambda model, vision=True: calls.append((model, vision)) or [])
    assert chat_main(args) == 0
    assert calls == [("sml", False)]
    assert capsys.readouterr().err == ""


def test_vision_setup_normalizes_model_alias_and_stays_text_only(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(local, "setup", lambda model, vision=True: calls.append((model, vision)) or [])
    assert vision_main(["--model", "TERAI1SML", "--setup"]) == 0
    assert calls == [("terai1sml", False)]
    assert capsys.readouterr().err == ""
