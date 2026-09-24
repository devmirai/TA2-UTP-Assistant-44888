# SPEC 005 - Riesgos, Ética y Mitigación

## Overview
Identificar 2 riesgos relevantes con mitigación diseño/proceso creativa.

## Problem
Mitigaciones genéricas ("tener cuidado") pierden puntos.

## Goals
Rúbrica Criterio 5 (4pts): riesgos técnicos+éticos + estrategias creativas + documento profesional.

## Requirements
### Functional
- R1 Alucinación operativa (fecha inventada, Jira duplicado): mitigación tools única fuente verdad + idempotency_key=hash(correo+tool+args) + HITL obligatorio + validación regex/schema + dry-run.
- R2 Filtración PII / prompt injection en adjunto: mitigación DLP/enmascarar antes del Thread + scope tools sin envío + jerarquía system>tool>user/adjunto + audit log + banner "Contiene PII".
- Matriz tabla: riesgo | impacto | probabilidad | mitigación diseño | mitigación proceso.

## Acceptance Criteria
- [ ] 2 riesgos específicos al caso consultora, no genéricos.
- [ ] Cada uno tiene mitigación diseño + proceso accionable.
- [ ] Menciona idempotencia, HITL y sanitización explícitamente.

## Out of Scope
Implementación código.

## Dependencies
Depende 004.
