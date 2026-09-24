"""Mock CRM F3 (SPEC 006).

Idempotente por tool_call_id. Sin red, sin secretos en logs.
"""

from __future__ import annotations

import threading

_CONTACTOS_BY_CALL: dict[str, dict] = {}
_lock = threading.Lock()


def actualizar(
    empresa: str,
    nombre: str | None = None,
    email: str = "",
    etapa: str = "",
    nombre_contacto: str | None = None,
    notas: str | None = None,
    tool_call_id: str | None = None,
    **kwargs,
) -> dict:
    """Actualiza un contacto simulado. Siempre ok:true, idempotente."""
    contacto = nombre_contacto or nombre or ""
    cache_key = tool_call_id or f"{empresa}|{email}|{etapa}"
    with _lock:
        if cache_key in _CONTACTOS_BY_CALL:
            return dict(_CONTACTOS_BY_CALL[cache_key])
    result = {
        "ok": True,
        "empresa": empresa,
        "nombre_contacto": contacto,
        "email": email,
        "etapa": etapa,
        "notas": notas,
    }
    with _lock:
        existing = _CONTACTOS_BY_CALL.setdefault(cache_key, dict(result))
    return dict(existing)


def clear_cache() -> None:
    with _lock:
        _CONTACTOS_BY_CALL.clear()
