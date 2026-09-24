"""Mock Google Calendar F3 (SPEC 006).

Idempotente por tool_call_id. Sin red, sin secretos en logs.
"""

from __future__ import annotations

import threading
import uuid

_EVENTOS_BY_CALL: dict[str, dict] = {}
_lock = threading.Lock()

DEFAULT_SLOTS = ["Mar 29 10:00", "Mié 30 15:00 Lima"]


def crear_evento(
    titulo: str,
    fecha_inicio: str,
    duracion_minutos: int = 60,
    asistentes: list[str] | None = None,
    zona_horaria: str = "America/Lima",
    descripcion: str | None = None,
    tool_call_id: str | None = None,
    **kwargs,
) -> dict:
    """Crea un evento simulado con slots fijos de fallback."""
    cache_key = tool_call_id or f"{titulo}|{fecha_inicio}"
    with _lock:
        if cache_key in _EVENTOS_BY_CALL:
            return dict(_EVENTOS_BY_CALL[cache_key])
    event_id = "evt_" + uuid.uuid4().hex[:8]
    result = {
        "event_id": event_id,
        "titulo": titulo,
        "fecha_inicio": fecha_inicio,
        "duracion_minutos": duracion_minutos,
        "asistentes": list(asistentes or []),
        "zona_horaria": zona_horaria,
        "descripcion": descripcion,
        "link": f"https://calendar.google.com/calendar/event?eid={event_id}",
        "slots": list(DEFAULT_SLOTS),
    }
    with _lock:
        # Si otro hilo ya lo guardó, devuelve el existente (idempotencia).
        existing = _EVENTOS_BY_CALL.setdefault(cache_key, dict(result))
    return dict(existing)


def clear_cache() -> None:
    with _lock:
        _EVENTOS_BY_CALL.clear()
