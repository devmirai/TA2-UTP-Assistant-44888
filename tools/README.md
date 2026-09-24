# Tools — SPEC 003 (F4)

Schemas Groq function-calling OpenAI-compatible. 3 JSON válidos en esta carpeta, pegables en `tools[]`.

## 1. Lista de tools

| # | Tool | Ruta | Cuándo se dispara (correo Ana Torres / TechCorp / módulo pagos / reunión próxima semana + adjunto) |
|---|------|------|------------------------------------------------------------------------------------------------------|
| 1 | `crear_ticket_en_jira` | `tools/crear_ticket_en_jira.json` | SÍ cuando el correo acepta la propuesta o pide revisar requisitos del módulo de pagos y hay acción concreta que registrar. NO si solo pregunta sin acción o faltan datos para el ticket. |
| 2 | `agendar_reunion_en_google_calendar` | `tools/agendar_reunion_en_google_calendar.json` | SÍ cuando acepta la propuesta o pide coordinar la reunión técnica de la próxima semana y hay fecha + asistentes + contexto. NO si no confirma interés o faltan asistentes/fecha. |
| 3 | `actualizar_contacto_en_crm` | `tools/actualizar_contacto_en_crm.json` | SÍ solo cuando el correo confirma un dato nuevo (email, etapa, notas) y están completos empresa + nombre_contacto + email + etapa. NO si solo pide info general o hay que inventar valores. |

Caso Ana Torres dispara los 3 en paralelo sin ambigüedad: el adjunto + aceptación de propuesta da materia para ticket (requisitos), la reunión pedida da materia para GCal, y los datos confirmados (TechCorp / Ana Torres / ana@techcorp.com / propuesta) dan materia para CRM.

## 2. Notas Groq

- `tool_choice: "auto"` — deja que el modelo elija 0..N tools según descripciones SÍ/NO.
- `parallel_tool_calls: true` — el caso Ana Torres requiere las 3 en el mismo turno.
- No confiar en `strict: true` — Groq OpenAI-compatible puede ignorarlo; validar siempre en backend con **pydantic**.
- Fechas exigen **ISO8601** (`format: date-time`, ej `2026-09-30T15:00:00Z`, patrón `YYYY-MM-DDTHH:mm:ssZ`).
- Emails exigen formato (`format: email` en `email`, `email_reporter`, `asistentes[]`).
- Todos los params llevan `type` + `description` operativa (ejemplo + formato) + validador (`enum`/`format`); cada schema cierra con `required` + `additionalProperties: false`.
- Descripciones < 150 palabras c/u.

## 3. Test mental — correo Ana Torres

| Intención detectada | Tool | Args ejemplo |
|---------------------|------|--------------|
| Registrar revisión de requisitos del módulo pagos (adjunto) | `crear_ticket_en_jira` | `{"proyecto": "UTPC", "titulo": "[TechCorp] Revisar requisitos módulo pagos", "descripcion": "TechCorp, contacto Ana Torres (ana@techcorp.com), revisar requisitos del módulo de pagos del adjunto", "prioridad": "High", "etiquetas": ["techcorp", "pagos"], "email_reporter": "ana@techcorp.com"}` |
| Coordinar reunión técnica próxima semana | `agendar_reunion_en_google_calendar` | `{"titulo": "[TechCorp] Reunión técnica módulo pagos", "fecha_inicio": "2026-09-30T15:00:00Z", "duracion_minutos": 60, "asistentes": ["ana@techcorp.com"], "zona_horaria": "America/Lima", "descripcion": "Revisión técnica módulo de pagos TechCorp con Ana Torres"}` |
| Confirmar dato comercial (empresa/contacto/etapa) | `actualizar_contacto_en_crm` | `{"empresa": "TechCorp", "nombre_contacto": "Ana Torres", "email": "ana@techcorp.com", "etapa": "propuesta", "notas": "Aceptó propuesta módulo pagos, agendar reunión técnica"}` |

Resultado esperado: 3 llamadas en paralelo, sin elección ambigua ni valores inventados.
