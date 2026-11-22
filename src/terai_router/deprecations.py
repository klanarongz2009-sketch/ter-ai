"""End-of-service notices for the components that leave TER-AI (TTH on 2026-11-30; MuML, Temmo, SANKPUP on 2027-01-10).

TER-AI is a Thai-language AI suite built around the Terai models and Tagentic. MuML (MuML 1.0 WA and
MUML 1.0 HIQ), Temmo, SANKPUP and every TTH engine (Wayu, edge-tts fallback, TTH-MTL) are outside that scope.
They stay in the repository and keep working until their end-of-service date (``EOS_DATES``), then they may be
removed from ``main``. Releases tagged before that date keep them.

Each component warns once per process: a ``DeprecationWarning`` (on import, or on the first ``generate`` call
for SANKPUP, whose Gemma 4 downloader in ``terai_router.sankpup.gemma`` is shared with TERAI1 chat and
Tagentic and is not part of this notice; for TTH, when a ``TTH`` or an engine object is created, because
``terai chat`` imports ``terai_router.tth`` for its option help even without ``--speak``), and a one-line notice
on stderr when its ``terai`` subcommand (or ``terai chat --speak``) starts.
"""
from __future__ import annotations

import sys
import warnings

EOS_DATE = "2027-01-10"
EOS_DATES = {"muml": EOS_DATE, "temmo": EOS_DATE, "sankpup": EOS_DATE, "tth": "2026-11-30"}
REASON = ("TER-AI is a Thai-language AI suite built around the Terai models and Tagentic, "
          "and this component is outside that scope")
COMPONENTS = {
    "muml": "MuML (MuML 1.0 WA and MUML 1.0 HIQ)",
    "temmo": "Temmo 1.0",
    "sankpup": "SANKPUP",
    "tth": "TTH (all versions: Wayu-Paxa-TTS-Edge, the edge-tts fallback and TTH-MTL)",
}

_warned: set[str] = set()
_noticed: set[str] = set()


def message(component: str) -> str:
    name = COMPONENTS[component]
    date = EOS_DATES[component]
    extra = (" Other repositories may continue or fine-tune it (code MIT; model weights keep their own licenses)."
             if component == "tth" else "")
    return (f"{name} is deprecated and reaches end of service on {date}: {REASON}.{extra} "
            f"It may be removed from main on or after that date; pin a TER-AI release tagged before "
            f"{date} to keep using it.")


def warn(component: str, stacklevel: int = 3) -> None:
    """Emit the DeprecationWarning for ``component`` once per process."""
    if component in _warned:
        return
    _warned.add(component)
    warnings.warn(message(component), DeprecationWarning, stacklevel=stacklevel)


def cli_notice(component: str, stream=None) -> None:
    """Print the end-of-service notice for a ``terai`` subcommand once per process (stderr by default)."""
    if component in _noticed:
        return
    _noticed.add(component)
    print("note: " + message(component), file=stream or sys.stderr)
