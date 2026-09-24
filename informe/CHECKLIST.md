# CHECKLIST F4 — Rúbrica 5 criterios x 4 pts (SPEC 008)

> Total: 20 pts. Cada criterio vale 4 pts. Se evidencia dónde está cada exigencia en el informe `TA_U2_GRUPO_X.md`.

| # | Criterio (4 pts) | Exigencia | Evidencia en informe | Estado |
|---|---|---|---|---|
| S1 | Arquitectura (4 pts) | Tabla comparativa Chat Completions vs Assistants API + veredicto con modelo Production `openai/gpt-oss-120b` | Sec. 1.1 tabla 8 filas (estado, orquestación, tools, file_search, costo, control, latencia, portabilidad Groq) + Sec. 1.1 veredicto final (Assistants API diseño lógico, Groq gpt-oss-120b runtime portable) + Sec. 1.3 tabla de adaptación Groq + Sec. 1.4 diagrama. Fuente: `docs/seccion-01-arquitectura.md` | OK |
| S2 | System Prompt (4 pts) | Texto plano íntegro con 6 bloques + R3 confirmación + 3 ejemplos de ambigüedad | Sec. 2 bloque ```text con `prompts/system.txt` íntegro: 1 ROL, 2 OBJETIVOS a-d, 3 REGLAS R1-R5 (R3 = "¿Confirmas para proceder? Nunca simular envío"), 4 PROTOCOLO AMBIGÜEDAD con Ej1/Ej2/Ej3, 5 FORMATO SALIDA (JSON + resumen 120 palabras), 6 TONO. Fuente: `prompts/system.txt` | OK |
| S3 | Function Calling (4 pts) | 3 JSON válidos y pegables en `tools[]` | Sec. 3.1 `crear_ticket_en_jira`, 3.2 `agendar_reunion_en_google_calendar`, 3.3 `actualizar_contacto_en_crm` — JSON íntegros verificados con `json.load` (3/3 válidos). Fuente: `tools/*.json`, `tool_choice: auto` | OK |
| S4 | Flujo Run Ana Torres (4 pts) | 8 pasos + 2 `requires_action` con tool_calls paralelas + respuesta final interna | Sec. 4 Pasos 1-8: P1 ingesta→thread, P2 Run (instructions+tools), P3 requires_action #1 (extract_entities + parse_adjunto), P4 submit→in_progress, P5 requires_action #2 (check_disponibilidad + crear_ticket_jira), P6 submit (slots Mar 29 10:00 / Mié 30 15:00 + UTPC-142), P7 completed con borrador + "¿Confirmas para proceder?", P8 cierre UI (timeline + JSON + Aprobar/Editar/Descartar). Fuente: `docs/seccion-04-flujo-run.md` | OK |
| S5 | Riesgos y Ética (4 pts) | R1/R2 + matriz + idempotencia/HITL/sanitización | Sec. 5: R1 alucinación (fecha inventada, Jira duplicado UTPC-142) + R2 PII/prompt-injection en adjunto; cada uno con mitigación diseño + proceso; matriz 2 filas (impacto/probabilidad/mitigaciones); idempotencia `hash(correo+tool+args)`, HITL "¿Confirmas para proceder?", sanitización DLP/enmascarado (`\d{8}`, emails) + jerarquía system>tool>user/adjunto + audit log. Fuente: `docs/seccion-05-riesgos.md` | OK |

## Verificación de artefactos (cierre SPEC 008 — 24/09/2026)

| Artefacto | Ruta | Resultado 24/09/2026 |
|---|---|---|
| PDF final Sección | `informe/TA_U2_SECCION_44888.pdf` | Existe, 13 páginas, <15 MB, abre con pypdf. Carátula SECCIÓN 44888 + 4 capturas incrustadas + repo clicable. OK |
| PDF réplica Grupo X | `informe/TA_U2_GRUPO_X.pdf` | Existe, 13 páginas, <15 MB, abre con pypdf. Réplica del anterior. OK |
| Capturas demo (4/4) | `informe/capturas/01-inbox-chat.png`, `02-thread-requires_action.png`, `03-approvals.png`, `04-board.png` | 4/4 existen e incrustadas en ambos PDF (max ancho 450px) con pie A1-A4. OK |
| Link repo (privado) | https://github.com/devmirai/TA2-UTP-Assistant-44888 | En carátula de ambos .md + anexos + PDF carátula y anexo final como link clicable. OK |
| Runtime Production | Groq `openai/gpt-oss-120b` (principal) + fallback `qwen` | En carátula de ambos .md y PDF. OK |
| Backend | `backend/app/main.py` + routers/schemas/services | Código existe. `GET /health` NO alcanzable (servidor apagado al chequear) — levantar con uvicorn antes de las capturas |
| Frontend build | `frontend/dist/index.html` + `assets/` | Existe build Vite. Servir con `vite preview` o despliegue antes de las capturas |

## Pendientes del grupo (cierre SPEC 008 — todo OK)

- [x] Integrantes: Matias Alejandro Mendez Cabrejos, Jhan Alexis Julca Huaman → carátula + nombre PDF.
- [x] Docente: Carlos Alberto Castillo Catturini → carátula.
- [x] Curso/sección y fecha de entrega: TIC Sección 44888, 24/09/2026 → carátula.
- [x] Título `# TA U2 SECCIÓN 44888` + PDFs `TA_U2_SECCION_44888.pdf` y réplica `TA_U2_GRUPO_X.pdf` regenerados (F3).
- [x] 4 capturas demo: 01-inbox-chat, 02-thread-requires_action, 03-approvals, 04-board → anexos del informe + PDF (F3). OK.
- [x] Link del repositorio https://github.com/devmirai/TA2-UTP-Assistant-44888 (privado) → carátula + anexos + PDF clicable. OK.
- [PENDIENTE] Levantar backend (`GET /health` OK) y frontend build servido antes de tomar nuevas capturas (las 4 actuales ya están cerradas).
