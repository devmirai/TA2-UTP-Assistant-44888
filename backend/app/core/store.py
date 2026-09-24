"""In-memory store F2 (SPEC 006).

Dicts simples sin persistencia. F3 añadirá Groq real, F4 SSE/files.
No se logea ningún secreto aquí.
"""

from __future__ import annotations

import threading
import time
import uuid

threads: dict[str, dict] = {}
messages: dict[str, list[dict]] = {}
runs: dict[str, dict] = {}
idem_keys: dict[str, str] = {}

_lock = threading.Lock()


def _now() -> int:
    return int(time.time())


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def create_thread(metadata: dict | None = None) -> dict:
    thread_id = _new_id("th")
    thread = {"id": thread_id, "created_at": _now(), "metadata": metadata or {}}
    with _lock:
        threads[thread_id] = thread
        messages.setdefault(thread_id, [])
    return thread


def get_thread(thread_id: str) -> dict | None:
    with _lock:
        return threads.get(thread_id)


def add_message(thread_id: str, role: str, content: str) -> dict | None:
    with _lock:
        if thread_id not in threads:
            return None
        msg = {
            "id": _new_id("msg"),
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "created_at": _now(),
        }
        messages.setdefault(thread_id, []).append(msg)
        return msg


def list_messages(thread_id: str) -> list[dict] | None:
    with _lock:
        if thread_id not in threads:
            return None
        return list(messages.get(thread_id, []))


def _simulate_status(thread_id: str) -> dict:
    """queued -> in_progress -> requires_action (simulado F2).

    Sin Groq aún (F3). Si el último mensaje de usuario contiene
    "reunión"/"reunion" (test Ana Torres) se devuelve requires_action
    con 2 tool_calls simulados; si no, queda en in_progress.
    """
    msgs = messages.get(thread_id, [])
    last_user = next(
        (m for m in reversed(msgs) if m.get("role") == "user"), None
    )
    content = (last_user or {}).get("content", "") or ""
    low = content.lower()
    if "reuni" in low:  # cubre reunión / reunion / reuniones
        return {
            "status": "requires_action",
            "required_action": {
                "type": "submit_tool_outputs",
                "submit_tool_outputs": {
                    "tool_calls": [
                        {
                            "id": _new_id("call"),
                            "type": "function",
                            "function": {
                                "name": "agendar_reunion_en_google_calendar",
                                "arguments": "{}",
                            },
                        },
                        {
                            "id": _new_id("call"),
                            "type": "function",
                            "function": {
                                "name": "actualizar_contacto_en_crm",
                                "arguments": "{}",
                            },
                        },
                    ]
                },
            },
        }
    return {"status": "in_progress", "required_action": None}


def create_run(
    thread_id: str,
    idempotency_key: str | None = None,
    assistant_id: str | None = None,
    instructions: str | None = None,
) -> dict | None:
    with _lock:
        if thread_id not in threads:
            return None
        if idempotency_key and idempotency_key in idem_keys:
            existing_id = idem_keys[idempotency_key]
            existing = runs.get(existing_id)
            # Solo reutiliza si pertenece al mismo thread; si no, crea uno nuevo.
            if existing is not None and existing.get("thread_id") == thread_id:
                return existing
        run_id = _new_id("run")
        run: dict = {
            "id": run_id,
            "thread_id": thread_id,
            "status": "queued",
            "assistant_id": assistant_id,
            "instructions": instructions,
            "idempotency_key": idempotency_key,
            "created_at": _now(),
            "required_action": None,
        }
        runs[run_id] = run
        if idempotency_key:
            idem_keys[idempotency_key] = run_id

    # Transición fuera del lock para no bloquear lecturas.
    simulated = _simulate_status(thread_id)
    with _lock:
        run["status"] = "in_progress"
        if simulated["status"] == "requires_action":
            run["status"] = "requires_action"
            run["required_action"] = simulated["required_action"]
        return dict(run)


def get_run(run_id: str) -> dict | None:
    with _lock:
        run = runs.get(run_id)
        return dict(run) if run is not None else None


# ---- F3: tool outputs, steps, inbox (SPEC 006, no toca F1/F2) ----

tool_outputs: dict[str, dict[str, dict]] = {}
run_steps: dict[str, list[dict]] = {}


def get_run_in_thread(thread_id: str, run_id: str) -> dict | None:
    with _lock:
        run = runs.get(run_id)
        if run is None or run.get("thread_id") != thread_id:
            return None
        return dict(run)


def _pending_call_ids(run: dict) -> list[str]:
    try:
        calls = run.get("required_action", {}).get("submit_tool_outputs", {}).get(
            "tool_calls", []
        )
        return [c.get("id") for c in calls if isinstance(c, dict) and c.get("id")]
    except AttributeError:
        return []


def save_tool_output(thread_id: str, run_id: str, tool_call_id: str, output: str) -> dict | None:
    """Guarda un output (idempotente por tool_call_id) y registra el step.

    Retorna el step creado/existente, o None si thread/run no coinciden.
    """
    with _lock:
        run = runs.get(run_id)
        if run is None or run.get("thread_id") != thread_id:
            return None
        bucket = tool_outputs.setdefault(run_id, {})
        if tool_call_id in bucket:
            # Idempotente: devuelve el step ya registrado si existe.
            for st in run_steps.get(run_id, []):
                if st.get("tool_call_id") == tool_call_id:
                    return dict(st)
            return {"id": tool_call_id, "tool_call_id": tool_call_id, "output": bucket[tool_call_id]["output"]}
        bucket[tool_call_id] = {
            "tool_call_id": tool_call_id,
            "output": output,
            "created_at": _now(),
        }
        step = {
            "id": _new_id("step"),
            "run_id": run_id,
            "thread_id": thread_id,
            "type": "tool_output",
            "tool_call_id": tool_call_id,
            "output": output,
            "created_at": _now(),
        }
        run_steps.setdefault(run_id, []).append(step)
        return dict(step)


def list_steps(thread_id: str, run_id: str) -> list[dict] | None:
    with _lock:
        run = runs.get(run_id)
        if run is None or run.get("thread_id") != thread_id:
            return None
        return [dict(s) for s in run_steps.get(run_id, [])]


def mark_run_status(run_id: str, status: str, required_action: dict | None = None) -> dict | None:
    with _lock:
        run = runs.get(run_id)
        if run is None:
            return None
        run["status"] = status
        if required_action is not None:
            run["required_action"] = required_action
        elif status == "completed":
            run["required_action"] = None
        return dict(run)


def maybe_complete_run(run_id: str) -> dict | None:
    """Si ya no hay tool_calls pendientes, pasa a completed; si no, in_progress."""
    with _lock:
        run = runs.get(run_id)
        if run is None:
            return None
        pending = _pending_call_ids(run)
        done = set(tool_outputs.get(run_id, {}).keys())
        if pending and all(p in done for p in pending):
            run["status"] = "completed"
            run["required_action"] = None
        elif run.get("status") not in ("completed", "failed"):
            # Transición intermedia requerida por SPEC: in_progress antes de completed.
            if run.get("status") == "requires_action":
                run["status"] = "in_progress"
        return dict(run)


def list_runs(status: str | None = None) -> list[dict]:
    with _lock:
        out = [dict(r) for r in runs.values()]
    if status:
        out = [r for r in out if r.get("status") == status]
    return out
