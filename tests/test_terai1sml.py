"""TERAI1SML: the compact, text-only Qwen chat variant. No model weights are loaded."""
from pathlib import Path

import pytest

from terai_router.brain import local
from terai_router.brain.agent import Brain, identity_answer, system_prompt
from terai_router.brain.cli import make_brain, vision_main
from terai_router.chat import Chat
from terai_router.versions import MODELS


def test_small_model_metadata_is_pinned_and_explicit():
    spec = local.SML_SPEC
    assert spec.repo == "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
    assert spec.filename == "qwen2.5-0.5b-instruct-q2_k.gguf"
    assert spec.size == 415182688
    assert spec.revision == "9217f5db79a29953eb74d5343926648285ec7e67"
    assert spec.sha256 == "9ee36184e616dfc76df4f5dd66f908dbde6979524ae36e6cefb67f532f798cb8"
    assert spec.url.endswith(f"{spec.revision}/{spec.filename}")
    assert next(m for m in MODELS if m["id"] == "TERAI1SML")["status"] == "beta"


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
    assert "แต่ไม่อ่านภาพ" in prompt
    assert "และอ่านภาพ" not in prompt


def test_brain_engine_selects_sml_without_loading_weights():
    brain = make_brain(Chat(now="2026-10-28T09:30:00", seed=1), "terai1sml", None, 1, quiet=True)
    assert isinstance(brain, Brain)
    assert brain.lm.model == local.SML_MODEL


def test_vision_setup_normalizes_model_alias_and_stays_text_only(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(local, "setup", lambda model, vision=True: calls.append((model, vision)) or [])
    assert vision_main(["--model", "TERAI1SML", "--setup"]) == 0
    assert calls == [("terai1sml", False)]
    assert capsys.readouterr().err == ""
