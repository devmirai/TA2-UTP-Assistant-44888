"""Mock Jira F3 (SPEC 006).

Idempotente por tool_call_id. Sin red, sin secretos en logs.
"""

from __future__ import annotations

import threading

_ISSUES_BY_CALL: dict[str, dict] = {}
_lock = threading.Lock()

BASE_URL = "https://utp.atlassian.net/browse"
FIXED_NUMBER = 142


def crear_issue(
    proyecto: str,
    titulo: str,
    descripcion: str,
    prioridad: str,
    email: str | None = None,
    email_reporter: str | None = None,
    etiquetas: list[str] | None = None,
    tool_call_id: str | None = None,
    **kwargs,
) -> dict:
    """Crea un issue simulado. Reutiliza el resultado si tool_call_id repite."""
    reporter = email_reporter or email or ""
    cache_key = tool_call_id or f"{proyecto}|{titulo}|{reporter}"
    with _lock:
        if cache_key in _ISSUES_BY_CALL:
            return dict(_ISSUES_BY_CALL[cache_key])
    prefix = (proyecto or "UTPC").strip().upper() or "UTPC"
    key = f"{prefix}-{FIXED_NUMBER}"
    result = {
        "key": key,
        "url": f"{BASE_URL}/{key}",
        "proyecto": prefix,
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "email_reporter": reporter,
        "etiquetas": list(etiquetas or []),
        "status": "To Do",
    }
    with _lock:
        _ISSUES_BY_CALL[cache_key] = dict(result)
    return result


def clear_cache() -> None:
    with _lock:
        _ISSUES_BY_CALL.clear()
