# CHECKLIST F4 — Rúbrica 5 criterios x 4 pts (SPEC 008)

> Total: 20 pts. Cada criterio vale 4 pts. Se evidencia dónde está cada exigencia en el informe `TA_U2_GRUPO_X.md`.

| # | Criterio (4 pts) | Exigencia | Evidencia en informe | Estado |
|---|---|---|---|---|
| S1 | Arquitectura (4 pts) | Tabla comparativa Chat Completions vs Assistants API + veredicto con modelo Production `openai/gpt-oss-120b` | Sec. 1.1 tabla 8 filas (estado, orquestación, tools, file_search, costo, control, latencia, portabilidad Groq) + Sec. 1.1 veredicto final (Assistants API diseño lógico, Groq gpt-oss-120b runtime portable) + Sec. 1.3 tabla de adaptación Groq + Sec. 1.4 diagrama. Fuente: `docs/seccion-01-arquitectura.md` | OK |
| S2 | System Prompt (4 pts) | Texto plano íntegro con 6 bloques + R3 confirmación + 3 ejemplos de ambigüedad | Sec. 2 bloque ```text con `prompts/system.txt` íntegro: 1 ROL, 2 OBJETIVOS a-d, 3 REGLAS R1-R5 (R3 = "¿Confirmas para proceder? Nunca simular envío"), 4 PROTOCOLO AMBIGÜEDAD con Ej1/Ej2/Ej3, 5 FORMATO SALIDA (JSON + resumen 120 palabras), 6 TONO. Fuente: `prompts/system.txt` | OK |
| S3 | Function Calling (4 pts) | 3 JSON válidos y pegables en `tools[]` | Sec. 3.1 `crear_ticket_en_jira`, 3.2 `agendar_reunion_en_google_calendar`, 3.3 `actualizar_contacto_en_crm` — JSON íntegros verificados con `json.load` (3/3 válidos). Fuente: `tools/*.json`, `tool_choice: auto` | OK |
| S4 | Flujo Run Ana Torres (4 pts) | 8 pasos + 2 `requires_action` con tool_calls paralelas + respuesta final interna | Sec. 4 Pasos 1-8: P1 ingesta→thread, P2 Run (instructions+tools), P3 requires_action #1 (extract_entities + parse_adjunto), P4 submit→in_progress, P5 requires_action #2 (check_disponibilidad + crear_ticket_jira), P6 submit (slots Mar 29 10:00 / Mié 30 15:00 + UTPC-142), P7 completed con borrador + "¿Confirmas para proceder?", P8 cierre UI (timeline + JSON + Aprobar/Editar/Descartar). Fuente: `docs/seccion-04-flujo-run.md` | OK |
| S5 | Riesgos y Ética (4 pts) | R1/R2 + matriz + idempotencia/HITL/sanitización | Sec. 5: R1 alucinación (fecha inventada, Jira duplicado UTPC-142) + R2 PII/prompt-injection en adjunto; cada uno con mitigación diseño + proceso; matriz 2 filas (impacto/probabilidad/mitigaciones); idempotencia `hash(correo+tool+args)`, HITL "¿Confirmas para proceder?", sanitización DLP/enmascarado (`\d{8}`, emails) + jerarquía system>tool>user/adjunto + audit log. Fuente: `docs/seccion-05-riesgos.md` | OK |

## Verificación de artefactos (solo chequeo, no regenerados)

| Artefacto | Ruta | Resultado 24/09/2026 |
|---|---|---|
| PDF final | `informe/TA_U2_GRUPO_X.pdf` | Existe, 27238 bytes. Abrir y confirmar <15 MB y nombre exacto antes de entrega (renombrar X→#GRUPO real en F3) |
| Backend | `backend/app/main.py` + routers/schemas/services | Código existe. `GET /health` NO alcanzable (servidor apagado al chequear) — levantar con uvicorn antes de las capturas |
| Frontend build | `frontend/dist/index.html` + `assets/` | Existe build Vite. Servir con `vite preview` o despliegue antes de las capturas |

## Pendientes del grupo (bloquean nota si no se completan)

- [PENDIENTE] Integrantes: nombres y códigos → carátula + nombre PDF.
- [PENDIENTE] Docente: nombre del docente → carátula.
- [PENDIENTE] Curso/sección y fecha de entrega → carátula.
- [PENDIENTE] Renombrar `X` → número real: `TA_U2_GRUPO_X.md` y `TA_U2_GRUPO_X.pdf` → `TA_U2_GRUPO_#GRUPO.*`.
- [PENDIENTE] 4 capturas demo (SPEC 008, SPEC 007 fallback Streamlit si aplica): 1 chat, 1 upload, 1 requires_action, 1 approvals → anexos del informe + regenerar PDF (F3).
- [PENDIENTE] Link del repositorio → carátula + anexos.
- [PENDIENTE] Levantar backend (`GET /health` OK) y frontend build servido antes de tomar las capturas.
