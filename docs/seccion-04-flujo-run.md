# 4. Flujo Run - Caso Ana Torres (TechCorp)

> Correo original (caso base): remitente Ana Torres (ana@techcorp.com), empresa TechCorp, tema módulo pagos, compromiso reunión próxima semana, con adjunto de requisitos. Caso: aceptación de propuesta + pedido de reunión técnica + adjunto para revisar.

## Paso 1 — Ingesta -> Thread

- Se ingesta el correo + adjunto y se crea `thread_id: thr_xxx` (ej. `thr_techcorp_pagos_001`).
- Se guarda el historial en `session_state` / DB (`messages[]` con correo + metadatos: empresa TechCorp, contacto Ana Torres, adjunto=true).
- Estado del Run: `queued` (correo encolado, aún sin instrucciones ni tools asociadas).

## Paso 2 — Crear Run (instructions + tools)

- Se crea el Run sobre `thr_xxx` con `instructions` = contenido de `prompts/system.txt` (rol gestor PM UTPConsult, reglas R1-R5, protocolo ambigüedad, formato dual JSON + resumen).
- Se adjuntan `tools` = los 3 de `tools/`: `crear_ticket_en_jira`, `agendar_reunion_en_google_calendar`, `actualizar_contacto_en_crm`.
- Estado del Run: `in_progress` (modelo razonando con instrucciones y tools disponibles, previo a `requires_action`).

<!-- F2 Done: Paso 3 y Paso 4 -->
## Paso 3 — Requires_action #1 (estado requires_action: 2 tool_calls paralelas)

- Estado del Run: `requires_action` (el modelo pausa y pide ejecutar tools).
- `required_action.submit_tool_outputs.tool_calls[]` trae 2 llamadas en paralelo:
  1. `extract_entities(text=correo)` con input = cuerpo del correo de Ana Torres (ana@techcorp.com, TechCorp, módulo pagos, reunión próxima semana).
  2. `parse_adjunto(file_id=req_inicial.pdf)` con input = adjunto de requisitos.
- Se ejecutan ambas en paralelo y se recolectan sus outputs para el Paso 4.

## Paso 4 — Submit_tool_outputs (outputs ejemplo y transición a in_progress)

- Se llama `submit_tool_outputs` con los outputs combinados, ejemplo:
  ```json
  {
    "empresa": "TechCorp",
    "contacto": "Ana Torres ana@techcorp.com",
    "tema": "módulo pagos",
    "compromiso": "reunión próxima semana",
    "adjunto": true,
    "requisitos": ["pasarela", "conciliación", "PCI"]
  }
  ```
- Transición de estado: `requires_action` -> `in_progress` (el modelo retoma el razonamiento con las entidades + requisitos ya resueltos, previo al requires_action #2 de F3).

## Paso 5 — Requires_action #2 (estado requires_action: 2 tool_calls paralelas)

- Estado del Run: `requires_action` (el modelo pausa y pide ejecutar tools).
- `required_action.submit_tool_outputs.tool_calls[]` trae 2 llamadas en paralelo:
  1. `check_disponibilidad(range=2026-09-28/2026-10-02, duracion=60min)` para buscar huecos de reunión de 60 min en ese rango.
  2. `crear_ticket_en_jira(proyecto=UTPC, titulo="[TechCorp] Revisar requisitos módulo pagos", prioridad=Medium, email=ana@techcorp.com)` para registrar la revisión del adjunto.
- Se ejecutan ambas en paralelo y se recolectan sus outputs para el Paso 6.

## Paso 6 — Submit_tool_outputs (outputs ejemplo y transición a in_progress)

- Se llama `submit_tool_outputs` con los outputs combinados, ejemplo:
  ```json
  {
    "slots": ["Mar 29 10:00", "Mié 30 15:00 Lima"],
    "jira": { "key": "UTPC-142" }
  }
  ```
- Los slots vienen del output real del tool `check_disponibilidad`, no inventados por el modelo.
- Transición de estado: `requires_action` -> `in_progress` (el modelo retoma el razonamiento con slots + ticket ya resueltos, previo al Paso 7 de F4).

## Paso 7 — Respuesta final (estado completed, PARA EQUIPO INTERNO)

- Transición de estado: `in_progress` -> `completed` (el modelo cierra el razonamiento y entrega la respuesta final, sin más tool_calls).
- La respuesta final es PARA EL EQUIPO INTERNO, no se envía al cliente (Ana Torres). Es un borrador listo para revisión interna.
- Contenido obligatorio de la respuesta final:
  1. Slots reales del tool `check_disponibilidad`: Mar 29 10:00 y Mié 30 15:00 Lima (sin fechas inventadas: solo estos 2 slots).
  2. Ticket Jira UTPC-142 con los 3 requisitos del adjunto: pasarela, conciliación, PCI.
  3. Borrador de respuesta al cliente listo (propone los 2 slots y confirma revisión de requisitos).
  4. Pregunta de confirmación interna: "¿Confirmas para proceder?" (el equipo debe aprobar antes de agendar o responder).
- Ejemplo de respuesta final (interna):
  > Borrador listo para Ana Torres (TechCorp): confirmamos revisión de requisitos (pasarela, conciliación, PCI, ticket UTPC-142) y proponemos Mar 29 10:00 o Mié 30 15:00 Lima. ¿Confirmas para proceder?

## Paso 8 — Cierre UI (timeline + JSON + botones)

- Timeline ThoughtChain/Bubble: se renderiza la secuencia completa del Run (ingesta -> requires_action #1 -> submit #1 -> requires_action #2 -> submit #2 -> completed) como burbujas de pensamiento encadenadas, cada paso con su estado visible.
- JSON tools: se muestra el JSON de cada tool_call y su output (extract_entities, parse_adjunto, check_disponibilidad, crear_ticket_en_jira) para auditoría, sin ocultar los slots ni el key UTPC-142.
- Botones de acción interna: `Aprobar` (agenda el slot elegido y envía el borrador), `Editar` (modifica el borrador antes de enviar), `Descartar` (cierra el Run sin actuar). Ningún botón se activa sin confirmación del equipo.
