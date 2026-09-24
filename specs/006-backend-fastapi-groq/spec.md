# SPEC 006 - Backend FastAPI + Groq Run Loop + SSE

## Overview
Backend contrato único que emula Assistants con Groq y expone SSE para front.

## Problem
Groq no tiene threads/runs; hay que emular sin exponer API key.

## Goals
Demo funcional local `localhost:8000` + `/docs` probables.

## Requirements
### Functional
- Endpoints: `POST /api/v1/threads, POST /threads/{id}/messages, POST /threads/{id}/runs (Idempotency-Key), POST /threads/{id}/runs/{run_id}/submit_tool_outputs, GET /runs/{run_id}/steps, GET /inbox, GET /threads/{id}/runs/{run_id}/stream (SSE), POST /files`.
- Runner: `groq.Groq()` model `openai/gpt-oss-120b` (principal Production, fallback `qwen/qwen3.8-27b`), `tools=TOOLS`, `tool_choice:auto`, loop max 5 iters, `queued->in_progress->requires_action->completed/failed`.
- Validación pydantic v2 + mocks `jira/gcal/crm` en `services/mocks/`.
- Files: `python-multipart`, whitelist pdf/docx/txt/md, extraer con pypdf/docx, inyectar excerpt 4000c como system.
### Non-Functional
- CORS solo `localhost:5173`, `.env GROQ_API_KEY`, SQLite/SQLModel para MVP, `sse-starlette`.

## Acceptance Criteria
- [ ] `uvicorn app.main:app --reload --port 8000` levanta y `/docs` responde.
- [ ] Crear run con correo Ana dispara 2 tool_calls y queda en requires_action visible en SSE.
- [ ] Reintento misma Idempotency-Key no duplica run.
- [ ] Ningún secreto en logs/front.

## Out of Scope
Front (SPEC-007).

## Dependencies
Depende 003. Desbloquea 007,008.
Deps pip: fastapi, uvicorn[standard], groq, pydantic, pydantic-settings, sse-starlette, python-multipart, sqlmodel, aiosqlite, httpx, pypdf, python-docx.
