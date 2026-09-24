"""SSE F4 (SPEC 006).

GET /threads/{tid}/runs/{rid}/stream con sse-starlette EventSourceResponse.
Emite run.queued / run.in_progress / run.requires_action|completed (+ message.delta),
polling al store cada 1s, cierra en completed/failed o timeout.
Sin log de secretos.
"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.core import store

router = APIRouter(tags=["stream"])

POLL_INTERVAL = 1.0
MAX_POLLS = 30


def _payload(run: dict) -> str:
    return json.dumps(
        {
            "id": run.get("id"),
            "thread_id": run.get("thread_id"),
            "status": run.get("status"),
            "required_action": run.get("required_action"),
        },
        ensure_ascii=False,
    )


def _delta_payload(run: dict) -> str:
    status = run.get("status", "")
    calls: list = []
    try:
        calls = (
            (run.get("required_action") or {})
            .get("submit_tool_outputs", {})
            .get("tool_calls", [])
        )
    except AttributeError:
        calls = []
    names = [
        ((c.get("function") or {}).get("name", ""))
        for c in calls
        if isinstance(c, dict)
    ]
    text = f"run {run.get('id')} status={status}"
    if names:
        text += " tools=" + ",".join(n for n in names if n)
    return json.dumps(
        {"id": run.get("id"), "object": "message.delta", "delta": text},
        ensure_ascii=False,
    )


async def _gen(thread_id: str, run_id: str) -> AsyncGenerator[dict, None]:
    run = store.get_run_in_thread(thread_id, run_id) or {}
    rid = run.get("id", run_id)

    # Secuencia inicial sintética + estado real del store.
    yield {"event": "run.queued", "data": json.dumps({"id": rid, "status": "queued"})}
    await asyncio.sleep(0.1)
    yield {"event": "run.in_progress", "data": json.dumps({"id": rid, "status": "in_progress"})}

    current = store.get_run_in_thread(thread_id, run_id) or run
    status = current.get("status", "in_progress")
    if status not in ("queued", "in_progress"):
        yield {"event": f"run.{status}", "data": _payload(current)}
    else:
        # Refleja el estado real aunque sea in_progress.
        yield {"event": "run.in_progress", "data": _payload(current)}
    yield {"event": "message.delta", "data": _delta_payload(current)}

    last = status
    if last in ("completed", "failed"):
        return

    for _ in range(MAX_POLLS):
        await asyncio.sleep(POLL_INTERVAL)
        cur = store.get_run_in_thread(thread_id, run_id)
        if cur is None:
            break
        st = cur.get("status", "")
        if st != last:
            last = st
            yield {"event": f"run.{st}", "data": _payload(cur)}
            yield {"event": "message.delta", "data": _delta_payload(cur)}
            if st in ("completed", "failed"):
                break


@router.get("/threads/{thread_id}/runs/{run_id}/stream")
async def stream_run(thread_id: str, run_id: str) -> EventSourceResponse:
    run = store.get_run_in_thread(thread_id, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    return EventSourceResponse(_gen(thread_id, run_id))
