"""End-of-service notices for the components that leave TER-AI on 2027-01-10.

TER-AI is a Thai-language AI suite built around the Terai models and Tagentic. MuML (MuML 1.0 WA and
MUML 1.0 HIQ), Temmo and SANKPUP are outside that scope: they stay in the repository and keep working until
2027-01-10, then they may be removed from ``main``. Releases tagged before that date keep them.

Each component warns once per process: a ``DeprecationWarning`` (on import, or on the first ``generate`` call
for SANKPUP, whose Gemma 4 downloader in ``terai_router.sankpup.gemma`` is shared with TERAI1 chat and
Tagentic and is not part of this notice), and a one-line notice on stderr when its ``terai`` subcommand starts.
"""
from __future__ import annotations

import sys
import warnings

EOS_DATE = "2027-01-10"
REASON = ("TER-AI is a Thai-language AI suite built around the Terai models and Tagentic, "
          "and this component is outside that scope")
COMPONENTS = {
    "muml": "MuML (MuML 1.0 WA and MUML 1.0 HIQ)",
    "temmo": "Temmo 1.0",
    "sankpup": "SANKPUP",
}

_warned: set[str] = set()
_noticed: set[str] = set()


def message(component: str) -> str:
    name = COMPONENTS[component]
    return (f"{name} is deprecated and reaches end of service on {EOS_DATE}: {REASON}. "
            f"It may be removed from main on or after that date; pin a TER-AI release tagged before "
            f"{EOS_DATE} to keep using it.")


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
