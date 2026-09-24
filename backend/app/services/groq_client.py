"""Wrapper Groq F2 (SPEC 006). Sin llamada real aún (F3).

- api_key sale de config/settings (.env), nunca se logea.
- get_model() retorna GROQ_MODEL.
- TOOLS carga tools/*.json (function-calling definitions).
"""

from __future__ import annotations

import glob
import json
import os

from app.core.config import settings

TOOLS: list[dict] = []


def _tools_dir() -> str:
    # backend/app/services/groq_client.py -> repo root TA2/tools
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "..", "tools"))


def _load_tools() -> list[dict]:
    pattern = os.path.join(_tools_dir(), "*.json")
    loaded: list[dict] = []
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, encoding="utf-8") as fh:
                loaded.append(json.load(fh))
        except (OSError, json.JSONDecodeError):
            continue
    return loaded


TOOLS = _load_tools()

_client = None


def get_model() -> str:
    return settings.GROQ_MODEL


def get_client():
    """Retorna cliente Groq singleton sin exponer la key en logs."""
    global _client
    if _client is None:
        from groq import Groq

        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client
