"""SPEC 008 F2 — Demo Streamlit UTP Assistant (Ana Torres).

Solo F2: chat + upload contra backend FastAPI http://localhost:8000/api/v1.
No toca F1. No implementa F3/F4.

Endpoints backend (SPEC 006):
- GET  /api/v1/health
- POST /api/v1/threads (+ POST /threads/{id}/messages, POST /threads/{id}/runs)
- POST /api/v1/files (upload pdf/docx/txt/md, max 10MB)
- GET  /api/v1/runs/{run_id}

Compat: si el backend expone POST /api/v1/chat (alias legado
"health/chat/upload" del enunciado), se intenta primero y si da 404
se usa el flujo threads/runs. Si el backend cae, fallback mock local
de Ana Torres (sin red).
"""

from __future__ import annotations

import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1").rstrip("/")
TIMEOUT = float(os.getenv("BACKEND_TIMEOUT", "8"))

ALLOWED_TYPES = ["pdf", "docx", "txt", "md"]


# ---------------------------------------------------------------- fallback mock

def mock_ana_torres_reply(text: str) -> str:
    low = (text or "").lower()
    if "reuni" in low:
        return (
            "Soy Ana Torres (modo local, sin backend). "
            "Detecté que quieres agendar una reunión: simularía "
            "`agendar_reunion_en_google_calendar` y "
            "`actualizar_contacto_en_crm`, y luego te confirmaría fecha y contacto. "
            "Levanta el backend (`uvicorn app.main:app`) para el flujo real F2."
        )
    if "hola" in low or "quién eres" in low or "quien eres" in low:
        return (
            "Hola, soy Ana Torres, asistente UTP (modo local, sin backend). "
            "Puedo ayudarte con reuniones, contactos y consultas académicas. "
            "Levanta el backend para el flujo completo."
        )
    return (
        "Soy Ana Torres (modo local, sin backend). Recibí tu mensaje y lo procesé "
        "en modo demostración. Levanta el backend en http://localhost:8000 "
        "para usar threads/runs y subida de archivos real."
    )


# ---------------------------------------------------------------- backend helpers

def api_health() -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if r.ok:
            return r.json()
        return None
    except requests.RequestException:
        return None


def api_ensure_thread(thread_id: str | None) -> str | None:
    if thread_id:
        return thread_id
    try:
        r = requests.post(f"{BASE_URL}/threads", json={"metadata": {}}, timeout=TIMEOUT)
        if r.ok:
            return r.json().get("id")
        return None
    except requests.RequestException:
        return None


def api_chat_legacy(message: str, thread_id: str | None) -> dict | None:
    """Intenta POST /chat si el backend lo expone. None si 404/no existe."""
    try:
        r = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "thread_id": thread_id},
            timeout=TIMEOUT,
        )
        if r.status_code == 404:
            return None
        if r.ok:
            return r.json()
        return {"_error": f"chat:{r.status_code}"}
    except requests.RequestException:
        return {"_down": True}


def api_send_message(thread_id: str, content: str) -> dict | None:
    try:
        r = requests.post(
            f"{BASE_URL}/threads/{thread_id}/messages",
            json={"role": "user", "content": content},
            timeout=TIMEOUT,
        )
        if r.ok:
            return r.json()
        return None
    except requests.RequestException:
        return None


def api_create_run(thread_id: str) -> dict | None:
    try:
        r = requests.post(
            f"{BASE_URL}/threads/{thread_id}/runs",
            json={},
            headers={"Idempotency-Key": f"st-{uuid.uuid4().hex[:12]}"},
            timeout=TIMEOUT,
        )
        if r.ok:
            return r.json()
        return None
    except requests.RequestException:
        return None


def api_get_run(run_id: str) -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}/runs/{run_id}", timeout=TIMEOUT)
        if r.ok:
            return r.json()
        return None
    except requests.RequestException:
        return None


def run_to_reply(run: dict | None, user_text: str) -> str:
    if not run:
        return mock_ana_torres_reply(user_text)
    status = run.get("status")
    if status == "requires_action":
        try:
            calls = run["required_action"]["submit_tool_outputs"]["tool_calls"]
            names = [c["function"]["name"] for c in calls]
        except (KeyError, TypeError):
            names = []
        detalle = ", ".join(f"`{n}`" for n in names) if names else "herramientas"
        return (
            f"Soy Ana Torres. Para tu solicitud activé {detalle}. "
            "En el flujo F2 el run quedó en `requires_action` "
            f"(run `{run.get('id')}`). Te confirmaré en cuanto se ejecuten."
        )
    return (
        f"Soy Ana Torres. Procesé tu mensaje en el thread `{run.get('thread_id')}` "
        f"(run `{run.get('id')}`, estado `{status}`). ¿En qué más te ayudo?"
    )


def api_upload(file, thread_id: str | None) -> dict:
    try:
        files = {"file": (file.name, file.getvalue(), file.type or "application/octet-stream")}
        data = {"thread_id": thread_id} if thread_id else {}
        r = requests.post(f"{BASE_URL}/files", files=files, data=data, timeout=TIMEOUT * 4)
        if r.ok:
            return {"ok": True, "data": r.json()}
        try:
            detail = r.json().get("detail", r.text)
        except ValueError:
            detail = r.text
        return {"ok": False, "error": f"{r.status_code}: {detail}"}
    except requests.RequestException as exc:
        return {"ok": False, "error": f"backend_no_disponible: {exc}"}


# ---------------------------------------------------------------- state

def init_state() -> None:
    st.session_state.setdefault("messages", [])  # [{role, content}]
    st.session_state.setdefault("thread_id", None)
    st.session_state.setdefault("run_id", None)
    st.session_state.setdefault("backend_ok", None)
    st.session_state.setdefault("uploaded", [])


# ---------------------------------------------------------------- UI

st.set_page_config(page_title="UTP Assistant — Ana Torres (F2)", page_icon="💬")
init_state()

st.title("UTP Assistant — Ana Torres")
st.caption("Demo F2 · Streamlit + FastAPI · con fallback local si el backend cae")

with st.sidebar:
    st.subheader("Backend")
    st.code(BASE_URL, language="text")
    if st.button("Probar conexión"):
        health = api_health()
        st.session_state["backend_ok"] = health is not None
        if health is not None:
            st.success(f"OK · model {health.get('model', '?')}")
        else:
            st.error("Backend no disponible · se usará mock local")
    if st.session_state["backend_ok"] is True:
        st.success("Backend: conectado")
    elif st.session_state["backend_ok"] is False:
        st.warning("Backend: no disponible (mock local)")
    else:
        st.info("Backend: sin probar")

    st.divider()
    st.subheader("Sesión")
    st.write(f"thread: `{st.session_state['thread_id'] or '—'}`")
    st.write(f"run: `{st.session_state['run_id'] or '—'}`")
    if st.button("Nuevo thread"):
        st.session_state["thread_id"] = None
        st.session_state["run_id"] = None
        st.session_state["messages"] = []
        st.session_state["uploaded"] = []
        st.rerun()

    st.divider()
    st.subheader("Adjuntar archivo")
    up = st.file_uploader(
        "pdf / docx / txt / md (máx 10 MB)",
        type=ALLOWED_TYPES,
        accept_multiple_files=False,
    )
    if up is not None and st.button(f"Subir {up.name}"):
        tid = api_ensure_thread(st.session_state["thread_id"])
        if tid is not None:
            st.session_state["thread_id"] = tid
        res = api_upload(up, st.session_state["thread_id"])
        if res["ok"]:
            st.session_state["uploaded"].append(res["data"])
            st.success(f"Subido: {res['data'].get('filename')} ({res['data'].get('size')} B)")
            excerpt = (res["data"].get("excerpt") or "")[:500]
            if excerpt:
                st.text_area("Extracto (primeros 500 c)", excerpt, height=120)
        else:
            st.error(f"No se pudo subir: {res['error']} (modo local: archivo no enviado)")

# Historial
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrada de chat
prompt = st.chat_input("Escríbele a Ana Torres…")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply: str
    backend_down = False

    # 1) Intento alias POST /chat (compat con enunciado health/chat/upload).
    legacy = api_chat_legacy(prompt, st.session_state["thread_id"])
    if legacy and "_down" not in legacy and "_error" not in legacy:
        reply = str(legacy.get("reply") or legacy.get("content") or mock_ana_torres_reply(prompt))
        if legacy.get("thread_id"):
            st.session_state["thread_id"] = legacy["thread_id"]
        if legacy.get("run_id"):
            st.session_state["run_id"] = legacy["run_id"]
    elif legacy and "_error" in legacy:
        reply = mock_ana_torres_reply(prompt)
    else:
        # 2) Flujo F2 real: threads -> messages -> runs -> get run.
        tid = api_ensure_thread(st.session_state["thread_id"])
        if tid is None:
            backend_down = True
            reply = mock_ana_torres_reply(prompt)
        else:
            st.session_state["thread_id"] = tid
            sent = api_send_message(tid, prompt)
            if sent is None:
                backend_down = True
                reply = mock_ana_torres_reply(prompt)
            else:
                run = api_create_run(tid)
                if run is None:
                    backend_down = True
                    reply = mock_ana_torres_reply(prompt)
                else:
                    st.session_state["run_id"] = run.get("id")
                    fresh = api_get_run(run["id"]) or run
                    reply = run_to_reply(fresh, prompt)

    if backend_down:
        st.session_state["backend_ok"] = False

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
        if backend_down:
            st.caption("⚠️ Respuesta generada en modo local (backend no disponible).")
