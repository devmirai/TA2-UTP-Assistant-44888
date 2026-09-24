# SPEC 004 - Flujo Run + Caso Ana Torres TechCorp

## Overview
Describir ciclo de vida del Run paso a paso aplicado al correo ejemplo (reunión próxima semana módulo pagos + adjunto requisitos).

## Problem
Rúbrica exige mostrar `requires_action` e integración de resultados, no solo lista genérica.

## Goals
Rúbrica Criterio 4 (4pts): estructurado, lógico, incluye requires_action.

## Requirements
### Functional
Secuencia 8 pasos:
1. Ingesta -> thread_id.
2. Crear Run (instructions + tools).
3. requires_action #1: extract_entities + parse_adjunto.
4. submit_tool_outputs.
5. requires_action #2: check_disponibilidad + crear_ticket UTPC-142.
6. submit_tool_outputs.
7. completed -> respuesta interna (slots reales, Jira creado, borrador, pide confirmar).
8. Cierre UI (timeline + JSON + botones).
- Detallar qué se extrae: {empresa:TechCorp, contacto:Ana Torres, tema:módulo pagos, compromiso:reunión, adjunto:true} y args concretos de cada tool.

## Acceptance Criteria
- [ ] Los 8 pasos nombran estado del Run y transición.
- [ ] Muestra 2 rondas requires_action con inputs/outputs ejemplo.
- [ ] Respuesta final es para equipo interno, no correo al cliente, y pide confirmación humana.
- [ ] Sin fechas inventadas: slots vienen de tool.

## Out of Scope
Riesgos (SPEC-005).

## Dependencies
Depende 002,003.
