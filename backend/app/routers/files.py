"""Router files F4 (SPEC 006).

- POST /files: UploadFile, whitelist pdf/docx/txt/md, max 10MB,
  guarda backend/uploads/{file_id}_{name}, extrae texto (pypdf/docx/txt)
  primeras 4000c, retorna {file_id, filename, size, thread_id?, excerpt}.
- GET /files/{file_id}: meta en memoria.
Sin log de secretos.
"""

from __future__ import annotations

import io
import re
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/files", tags=["files"])

MAX_BYTES = 10 * 1024 * 1024
ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}
EXCERPT_LEN = 4000

# backend/app/routers/files.py -> parents[2] = backend/
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Meta en memoria: file_id -> dict
FILES: dict[str, dict] = {}


def _new_file_id() -> str:
    return f"file_{uuid.uuid4().hex[:12]}"


def _safe_name(name: str) -> str:
    base = Path(name or "upload.bin").name
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", base).strip("._") or "upload.bin"
    return safe[:100]


def _extract_text(ext: str, data: bytes) -> str:
    if ext == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            parts: list[str] = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    continue
            return "\n".join(parts)
        except Exception:
            return ""
    if ext == ".docx":
        try:
            from docx import Document

            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    # .txt / .md
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    thread_id: Optional[str] = Form(default=None),
) -> dict:
    original = file.filename or "upload.bin"
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"file_type_no_soportado:{ext or '?'}")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file_too_large")
    file_id = _new_file_id()
    safe = _safe_name(original)
    stored_name = f"{file_id}_{safe}"
    dest = UPLOAD_DIR / stored_name
    # Evita traversal: resuelve y confirma que queda dentro de UPLOAD_DIR.
    try:
        dest.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="filename_invalido")
    dest.write_bytes(data)
    text = _extract_text(ext, data)
    excerpt = (text or "")[:EXCERPT_LEN]
    meta = {
        "file_id": file_id,
        "filename": original,
        "stored_name": stored_name,
        "size": len(data),
        "content_type": file.content_type,
        "thread_id": thread_id,
        "excerpt": excerpt,
        "created_at": int(time.time()),
    }
    FILES[file_id] = meta
    return {
        "file_id": file_id,
        "filename": original,
        "size": len(data),
        "thread_id": thread_id,
        "excerpt": excerpt,
    }


@router.get("/{file_id}")
def read_file(file_id: str) -> dict:
    meta = FILES.get(file_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="file_not_found")
    return dict(meta)
