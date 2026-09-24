# SPEC 001 - Arquitectura General (Assistants vs Chat + Adapter Groq)

## Overview
Definir núcleo del sistema UTP Assistant para consultora UTPConsult. Decisión teórica: Assistants API. Runtime real: Groq `openai/gpt-oss-120b` (principal Production, fallback `qwen/qwen3.8-27b`) OpenAI-compatible.

## Problem
Equipo gestión/ventas saturado por correos: extraer requisitos de hilos largos, crear tareas Jira/Asana, agendar seguimiento, actualizar CRM.

## Goals
- Justificar elección para rúbrica Criterio 1 (4pts): comparativa + ventajas Threads/Runs/tools.
- Mapear a Groq sin mentir: diseño lógico Assistants, implementación emulada.

## Requirements
### Functional
- Tabla comparativa Chat Completions vs Assistants (estado, hilos, Run, file_search, costo, control, latencia, portabilidad Groq).
- Diagrama: Gmail/GCal/Jira/CRM -> Backend FastAPI (ingesta+validación) -> Groq -> loop Run -> acciones + audit log.
- Definir: Thread = `session_state`/DB, Run = loop manual, `requires_action` = validación HITL.
### Non-Functional
- Trazabilidad, idempotencia, no exponer GROQ_API_KEY en front.

## Acceptance Criteria
- [ ] Tabla con 7 criterios y veredicto explícito Assistants.
- [ ] 4 ventajas clave ligadas al caso (hilos largos, multi-tool, adjunto, auditabilidad).
- [ ] Sección "Adaptación Groq" explica por qué Groq no tiene threads/runs y cómo se emula.
- [ ] Diagrama texto válido para pegar en PDF.

## Out of Scope
Código backend (SPEC-006), prompt (SPEC-002).

## Dependencies
Ninguna. Bloquea a 002,003.
