# SPEC 003 - Function Calling Tools (Jira / GCal / CRM)

## Overview
Definir 3 schemas JSON optimizados para Groq tool calling OpenAI-compatible.

## Problem
Parámetros vagos provocan tool-choice erróneo y alucinación de fechas/emails.

## Goals
Rúbrica Criterio 3 (4pts): altamente relevantes, estructura clara, descripciones precisas.

## Requirements
### Functional
1. `crear_ticket_en_jira {proyecto, titulo<=120c, descripcion>=20c, prioridad enum, etiquetas[], email_reporter format:email}`
2. `agendar_reunion_en_google_calendar {titulo, fecha_inicio format:date-time ISO8601, duracion_minutos enum[30,45,60,90], asistentes[] format:email, zona_horaria, descripcion}`
3. `actualizar_contacto_en_crm {empresa, nombre_contacto, email, etapa enum[nuevo,contactado,propuesta,negociacion], notas}`
- Cada función: `name + description (cuándo SÍ/NO llamar) + parameters {type, description operativa con ejemplo+formato, enum/format/pattern} + required + additionalProperties:false`.
### Non-Functional
- Compatible Groq: `tool_choice:auto`, `parallel_tool_calls:true`, no confiar en `strict:true` (validar en backend con pydantic).
- Descripciones <150 palabras c/u.

## Acceptance Criteria
- [ ] 3 JSON válidos pegables en informe y en `tools[]` Groq.
- [ ] Todos los params tienen type+description+validador.
- [ ] Fechas exigen ISO8601, emails exigen formato.
- [ ] Test mental: correo Ana Torres dispara los 3 sin ambigüedad de elección.

## Out of Scope
Ejecución real (SPEC-006).

## Dependencies
Depende 002.
