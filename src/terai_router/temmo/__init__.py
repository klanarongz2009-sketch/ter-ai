"""Temmo 1.0 (TER-AI): an AI pipeline that builds a complete small indie game, not a mockup.

idea -> game design doc -> tasks -> code -> assets (SANKPUP / Nano Banana, TTH, MuML WA)
-> assembled HTML5 game -> headless Chromium test with a bot -> fix loop.
Providers are BYOK (bring your own key); with no key Temmo uses Gemma 4 on this machine.
"""
from ..deprecations import warn as _eos_warn
from .gdd import check, repair  # noqa: F401
from .providers import DEFAULT_MODELS, DEFAULT_ROLES, make, resolve_roles  # noqa: F401

_eos_warn("temmo")

VERSION = "1.0.0-dev"


def build(*args, **kwargs):
    from .pipeline import build as _build
    return _build(*args, **kwargs)
