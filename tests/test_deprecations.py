"""End-of-service notices for MuML, Temmo and SANKPUP (2027-01-10)."""
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
    assert text.startswith("note: ") and "2027-01-10" in text and "Tagentic" in text


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_sankpup_cli_prints_notice(monkeypatch, capsys, tmp_path):
    from terai_router.sankpup import cli
    monkeypatch.setattr(deprecations, "_noticed", set())
    assert cli.main(["a red boat", "--engine", "offline", "-o", str(tmp_path / "boat.svg")]) == 0
    assert "SANKPUP is deprecated" in capsys.readouterr().err
