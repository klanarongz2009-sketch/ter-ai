"""End-of-service notices: TTH (2026-11-30); MuML, Temmo and SANKPUP (2027-01-10)."""
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from terai_router import deprecations

SRC = str(Path(__file__).resolve().parents[1] / "src")


def _import_stderr(module: str) -> str:
    env = dict(os.environ, PYTHONPATH=SRC + os.pathsep + os.environ.get("PYTHONPATH", ""))
    out = subprocess.run([sys.executable, "-W", "always::DeprecationWarning", "-c", f"import {module}"],
                         capture_output=True, text=True, env=env, timeout=120)
    assert out.returncode == 0, out.stderr
    return out.stderr


@pytest.mark.parametrize("module,name", [
    ("terai_router.muml_wa", "MuML"),
    ("terai_router.muml_hiq", "MuML"),
    ("terai_router.temmo", "Temmo 1.0"),
])
def test_import_warns_once(module, name):
    err = _import_stderr(module)
    assert err.count("DeprecationWarning") == 1
    assert name in err and "2027-01-10" in err


def test_both_muml_modules_warn_once_together():
    err = _import_stderr("terai_router.muml_wa, terai_router.muml_hiq")
    assert err.count("end of service on 2027-01-10") == 1


def test_shared_gemma_loader_and_chat_backend_do_not_warn():
    # TERAI1 chat and Tagentic use terai_router.sankpup.gemma; they are not deprecated.
    err = _import_stderr("terai_router.brain.local, terai_router.sankpup.gemma")
    assert "2027-01-10" not in err


def test_sankpup_generate_warns_once(monkeypatch):
    from terai_router import sankpup
    monkeypatch.setattr(deprecations, "_warned", set())
    with pytest.warns(DeprecationWarning, match="SANKPUP .*2027-01-10"):
        art = sankpup.generate("cat on the moon", engine="offline")
    assert art.svg.startswith("<svg")
    import warnings
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        sankpup.generate("cat on the moon", engine="offline")
    assert not [w for w in rec if "2027-01-10" in str(w.message)]


@pytest.mark.parametrize("component", sorted(deprecations.COMPONENTS))
def test_cli_notice_once(monkeypatch, component):
    monkeypatch.setattr(deprecations, "_noticed", set())
    buf = io.StringIO()
    deprecations.cli_notice(component, stream=buf)
    deprecations.cli_notice(component, stream=buf)
    text = buf.getvalue()
    assert text.count("\n") == 1
    assert text.startswith("note: ") and deprecations.EOS_DATES[component] in text and "Tagentic" in text


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_sankpup_cli_prints_notice(monkeypatch, capsys, tmp_path):
    from terai_router.sankpup import cli
    monkeypatch.setattr(deprecations, "_noticed", set())
    assert cli.main(["a red boat", "--engine", "offline", "-o", str(tmp_path / "boat.svg")]) == 0
    assert "SANKPUP is deprecated" in capsys.readouterr().err


def test_tth_date_and_import_does_not_warn():
    assert deprecations.EOS_DATES["tth"] == "2026-11-30"
    # terai chat imports terai_router.tth for option help even without --speak: importing must stay silent.
    assert "end of service" not in _import_stderr("terai_router.tth, terai_router.cli")


def test_tth_object_warns_once(monkeypatch):
    from terai_router import tth
    monkeypatch.setattr(deprecations, "_warned", set())
    with pytest.warns(DeprecationWarning, match="TTH .*2026-11-30"):
        tth.TTH(engine="edge")
    import warnings
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        tth.TTH(engine="edge")
        tth.prepare("12 ครับ")
    assert not [w for w in rec if "end of service" in str(w.message)]


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_terai_tth_cli_prints_notice(monkeypatch, capsys):
    from terai_router import cli
    monkeypatch.setattr(deprecations, "_noticed", set())
    try:
        cli.tth_main(["--dry-run", "สวัสดี"])
    except SystemExit:
        pass
    assert "TTH (all versions" in capsys.readouterr().err


def test_tth_message_allows_forks_and_others_do_not():
    assert "may continue or fine-tune it" in deprecations.message("tth")
    assert "fine-tune" not in deprecations.message("muml")
