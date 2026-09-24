"""Router runs F2: POST /threads/{id}/runs (Idempotency-Key), GET /runs/{id}."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from app.core.store import create_run, get_run, get_thread
from app.schemas.run import RunCreate

router = APIRouter(tags=["runs"])


@router.post("/threads/{thread_id}/runs")
def post_run(
    thread_id: str,
    body: RunCreate | None = None,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    if get_thread(thread_id) is None:
        raise HTTPException(status_code=404, detail="thread_not_found")
    run = create_run(
        thread_id,
        idempotency_key=idempotency_key,
        assistant_id=body.assistant_id if body else None,
        instructions=body.instructions if body else None,
    )
    if run is None:
        raise HTTPException(status_code=404, detail="thread_not_found")
    return run


@router.get("/runs/{run_id}")
def read_run(run_id: str) -> dict:
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    return run
