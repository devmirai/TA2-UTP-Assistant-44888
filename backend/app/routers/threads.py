"""Router threads F2: POST /threads, POST /threads/{id}/messages."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.store import add_message, create_thread, get_thread
from app.schemas.run import MessageCreate, ThreadCreate

router = APIRouter(prefix="/threads", tags=["threads"])


@router.post("")
def post_thread(body: ThreadCreate | None = None) -> dict:
    metadata = (body.metadata if body else {}) or {}
    return create_thread(metadata=metadata)


@router.post("/{thread_id}/messages")
def post_message(thread_id: str, body: MessageCreate) -> dict:
    if get_thread(thread_id) is None:
        raise HTTPException(status_code=404, detail="thread_not_found")
    msg = add_message(thread_id, role=body.role, content=body.content)
    if msg is None:
        raise HTTPException(status_code=404, detail="thread_not_found")
    return msg
