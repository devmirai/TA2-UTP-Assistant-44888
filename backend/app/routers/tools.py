"""Router tools F3 (SPEC 006).

- POST /threads/{tid}/runs/{rid}/submit_tool_outputs: valida con pydantic,
  ejecuta mocks según tool name, guarda outputs/steps, transiciona
  requires_action -> in_progress -> completed cuando no hay pendientes.
- GET /threads/{tid}/runs/{rid}/steps
- GET /inbox?status=requires_action
Sin log de secretos.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from app.core import store
from app.schemas.tools import CrmArgs, GcalArgs, JiraArgs, SubmitToolOutputsRequest
from app.services.mocks import crm as crm_mock
from app.services.mocks import gcal as gcal_mock
from app.services.mocks import jira as jira_mock

router = APIRouter(tags=["tools"])

JIRA_DEFAULTS = {
    "proyecto": "UTPC",
    "titulo": "[TechCorp] Revisar requisitos módulo pagos",
    "descripcion": (
        "TechCorp, contacto Ana Torres (ana@techcorp.com), "
        "revisar requisitos del módulo de pagos del adjunto"
    ),
    "prioridad": "High",
    "email_reporter": "ana@techcorp.com",
    "etiquetas": ["techcorp", "pagos"],
}

GCAL_DEFAULTS = {
    "titulo": "[TechCorp] Reunión técnica módulo pagos",
    "fecha_inicio": "2026-09-30T15:00:00Z",
    "duracion_minutos": 60,
    "asistentes": ["ana@techcorp.com"],
    "zona_horaria": "America/Lima",
    "descripcion": "Revisión técnica módulo de pagos TechCorp con Ana Torres",
}

CRM_DEFAULTS = {
    "empresa": "TechCorp",
    "nombre_contacto": "Ana Torres",
    "email": "ana@techcorp.com",
    "etapa": "propuesta",
    "notas": "Aceptó propuesta módulo pagos, agendar reunión técnica",
}

_TOOL_BY_NAME = {
    "crear_ticket_en_jira": "crear_ticket_en_jira",
    "agendar_reunion_en_google_calendar": "agendar_reunion_en_google_calendar",
    "actualizar_contacto_en_crm": "actualizar_contacto_en_crm",
}


def _call_map(run: dict) -> dict[str, dict]:
    try:
        calls = run.get("required_action", {}).get("submit_tool_outputs", {}).get(
            "tool_calls", []
        )
    except AttributeError:
        return {}
    out: dict[str, dict] = {}
    for c in calls:
        if isinstance(c, dict) and c.get("id"):
            fn = (c.get("function") or {}) if isinstance(c.get("function"), dict) else {}
            out[c["id"]] = {
                "name": fn.get("name", ""),
                "arguments": fn.get("arguments", "{}"),
            }
    return out


def _parse_stored_args(raw: object) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _validation_detail(exc: ValidationError) -> list[dict]:
    # Sanea ctx (puede traer ValueError no serializable) para evitar 500.
    return exc.errors(include_url=False, include_context=False)


def _execute_mock(name: str, args: dict, tool_call_id: str) -> dict:
    if name == "crear_ticket_en_jira":
        merged = {**JIRA_DEFAULTS, **args}
        try:
            valid = JiraArgs(**merged)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=_validation_detail(exc))
        return jira_mock.crear_issue(
            proyecto=valid.proyecto,
            titulo=valid.titulo,
            descripcion=valid.descripcion,
            prioridad=valid.prioridad,
            email=valid.email_reporter,
            email_reporter=valid.email_reporter,
            etiquetas=valid.etiquetas,
            tool_call_id=tool_call_id,
        )
    if name == "agendar_reunion_en_google_calendar":
        merged = {**GCAL_DEFAULTS, **args}
        try:
            valid = GcalArgs(**merged)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=_validation_detail(exc))
        return gcal_mock.crear_evento(
            titulo=valid.titulo,
            fecha_inicio=valid.fecha_inicio.isoformat().replace("+00:00", "Z"),
            duracion_minutos=valid.duracion_minutos,
            asistentes=valid.asistentes,
            zona_horaria=valid.zona_horaria,
            descripcion=valid.descripcion,
            tool_call_id=tool_call_id,
        )
    if name == "actualizar_contacto_en_crm":
        merged = {**CRM_DEFAULTS, **args}
        # Alias nombre -> nombre_contacto.
        if "nombre" in merged and "nombre_contacto" not in merged:
            merged["nombre_contacto"] = merged.pop("nombre")
        try:
            valid = CrmArgs(**merged)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=_validation_detail(exc))
        return crm_mock.actualizar(
            empresa=valid.empresa,
            nombre_contacto=valid.nombre_contacto,
            email=valid.email,
            etapa=valid.etapa,
            notas=valid.notas,
            tool_call_id=tool_call_id,
        )
    raise HTTPException(status_code=400, detail=f"tool_no_soportado:{name}")


@router.post("/threads/{thread_id}/runs/{run_id}/submit_tool_outputs")
def submit_tool_outputs(thread_id: str, run_id: str, body: SubmitToolOutputsRequest) -> dict:
    run = store.get_run_in_thread(thread_id, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    if run.get("status") == "completed":
        # Reintento idempotente: si todos los ids ya están guardados, éxito.
        already = set((store.tool_outputs.get(run_id) or {}).keys())
        wanted = {item.tool_call_id for item in body.tool_outputs}
        if wanted and wanted <= already:
            steps = store.list_steps(thread_id, run_id) or []
            mine = [s for s in steps if s.get("tool_call_id") in wanted]
            return {"run": run, "tool_outputs": mine}
        raise HTTPException(status_code=400, detail="run_no_requiere_tool_outputs")
    if run.get("status") not in ("requires_action", "in_progress"):
        raise HTTPException(status_code=400, detail="run_no_requiere_tool_outputs")

    cmap = _call_map(run)
    saved: list[dict] = []
    for item in body.tool_outputs:
        call_id = item.tool_call_id
        if call_id in cmap:
            tool_name = cmap[call_id]["name"]
            stored_args = _parse_stored_args(cmap[call_id]["arguments"])
        else:
            # Fuera de required_action: inferir por argumentos enviados.
            stored_args = {}
            tool_name = ""
            if item.arguments:
                stored_args = dict(item.arguments)
        provided = (item.output or "").strip()
        if provided:
            output_str = item.output or ""
        else:
            if not tool_name:
                raise HTTPException(status_code=400, detail=f"tool_call_desconocido:{call_id}")
            if tool_name not in _TOOL_BY_NAME:
                raise HTTPException(status_code=400, detail=f"tool_no_soportado:{tool_name}")
            merged_args = {**stored_args, **(item.arguments or {})}
            result = _execute_mock(tool_name, merged_args, call_id)
            output_str = json.dumps(result, ensure_ascii=False)
        step = store.save_tool_output(thread_id, run_id, call_id, output_str)
        if step is not None:
            saved.append(step)

    # Transición: a in_progress durante el procesamiento...
    current = store.get_run_in_thread(thread_id, run_id) or {}
    if current.get("status") == "requires_action":
        store.mark_run_status(run_id, "in_progress", required_action=current.get("required_action"))
    # ...y a completed si ya no hay pendientes.
    final_run = store.maybe_complete_run(run_id) or {}
    return {"run": final_run, "tool_outputs": saved}


@router.get("/threads/{thread_id}/runs/{run_id}/steps")
def read_steps(thread_id: str, run_id: str) -> dict:
    steps = store.list_steps(thread_id, run_id)
    if steps is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    return {"data": steps}


@router.get("/inbox")
def read_inbox(status: str | None = Query(default=None)) -> dict:
    return {"data": store.list_runs(status=status)}
