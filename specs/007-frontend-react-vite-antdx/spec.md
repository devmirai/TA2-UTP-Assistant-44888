# SPEC 007 - Frontend React+Vite + Ant Design X

## Overview
Web demo producto consultora: bandeja, detalle Thread/Run, aprobaciones HITL, board.

## Problem
Streamlit no da timeline agente ni UX multi-página fluida.

## Goals
Demo viva `localhost:5173` que visualiza SPEC-004.

## Requirements
### Functional
- Rutas: `/inbox, /thread/:id, /approvals, /board`.
- Componentes: `Conversations` (bandeja), `Bubble.List+Sender+Attachments` (detalle), `ThoughtChain` (timeline Run con footer Aprobar/Rechazar), `Prompts` (atajos), `Table/Card/Modal` antd (Jira/CRM).
- Store `zustand`, `axios -> VITE_API_URL=http://localhost:8000`, `react-router-dom`.
- Funciona con `mocks/*.json` si back cae.
### Non-Functional
- Fijar `antd@^6 + @ant-design/x@^2`, react>=18, imports puntuales, sin `dangerouslyApiKey`.

## Acceptance Criteria
- [ ] `npm run dev` muestra inbox mock navegable.
- [ ] ThreadDetail renderiza 2 rondas requires_action como ThoughtChain colapsable.
- [ ] Botón Aprobar llama `POST /submit_tool_outputs` y avanza a completed.
- [ ] Sin CORS en local, sin key expuesta.

## Out of Scope
Deploy prod.

## Dependencies
Depende 006 (pero arranca con mocks).
Deps npm: antd, @ant-design/x, @ant-design/x-sdk, @ant-design/icons, react-router-dom, axios, zustand, dayjs.
