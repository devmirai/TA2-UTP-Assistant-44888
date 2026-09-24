# SPEC 008 - Informe PDF + Evidencias Demo

## Overview
Cerrar entregable `TA_U2_GRUPO_#GRUPO.pdf` con carátula + 5 secciones + capturas.

## Problem
Sin capturas el informe es solo teoría; sin PDF no hay nota.

## Goals
Entregable que cumple nombre, formato y rúbrica 20/20.

## Requirements
### Functional
- Estructura: carátula (grupo, integrantes, curso) + 1 arquitectura + 2 system prompt texto plano + 3 tools JSON + 4 flujo Ana + 5 riesgos + anexos capturas.
- Fallback rápido: `app.py` Streamlit (`st.chat_message + st.chat_input + st.session_state + st.file_uploader`) apuntando al mismo FastAPI para sacar 4 capturas en 2h si SPEC-007 se atrasa.
- Generación PDF: `reportlab` o `weasyprint` o Markdown->PDF, nombre exacto.
### Non-Functional
Redacción profesional, sin plagio.

## Acceptance Criteria
- [ ] PDF abre, <15MB, nombre exacto, carátula completa.
- [ ] Contiene tabla comparativa, prompt plano, 3 JSON, flujo 8 pasos, matriz riesgos.
- [ ] >=4 capturas (chat, upload, requires_action, approvals) + link repo.
- [ ] Checklist rúbrica 5x4pts OK.

## Out of Scope
Nada, es cierre.

## Dependencies
Depende 001-005 + evidencias 006/007.
