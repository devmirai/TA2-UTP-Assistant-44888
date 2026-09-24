# 1. Arquitectura General del Asistente - UTP Assistant (UTPConsult)

> Contexto del caso: UTPConsult es una consultora de software B2B saturada por correos. El asistente debe extraer requisitos desde emails, crear tickets en Jira, agendar reuniones en Google Calendar (GCal) y actualizar el CRM. El diseño lógico de esta sección usa Assistants API; el runtime real implementado es Groq `openai/gpt-oss-120b` (principal Production, fallback `qwen/qwen3.8-27b`) vía Chat Completions (ver Secciones 5-6 para el mapeo de portabilidad).

## 1.1 Tabla comparativa Chat Completions vs Assistants API

| Criterio | Chat Completions | Assistants API |
|---|---|---|
| Gestión de estado / hilos | Stateless: el cliente debe reenviar todo el historial en cada llamada; sin hilos nativos | Stateful: Threads persistentes en OpenAI; el historial lo gestiona la plataforma |
| Orquestación de Runs | Manual: el desarrollador implementa el bucle tool-call → ejecución → reenvío | Automática: objeto Run con estados (`queued`, `requires_action`, `completed`); polling o streaming de eventos |
| Herramientas (function calling) | `tools` + `tool_choice` por llamada; el cliente ejecuta la función y devuelve `tool` messages | Tools definidas en el Assistant (`functions`, `code_interpreter`, `file_search`); el Run pausa en `requires_action` hasta resolverlas |
| file_search / RAG | No nativo: hay que montar vector store propio (embeddings + retrieval manual) | Nativo: `file_search` con vector stores gestionados, chunking y re-ranking incluidos |
| Costo | Pago por tokens enviados (incluye reenvío de historial) + infraestructura propia mínima | Pago por tokens + sobrecosto por almacenamiento de Threads/vector stores y pasos de Run |
| Control / debug | Total: prompts, historial, reintentos y truncado bajo control del código; fácil de trazar | Opaco: estados internos del Run, menos visibilidad; depuración vía dashboard y `run steps` |
| Latencia | Menor y predecible: una llamada request/response directa | Mayor y variable: polling de Runs, colas y múltiples pasos internos |
| Portabilidad a Groq | Alta: Groq expone API compatible OpenAI Chat Completions; `llama-3.3-70b-versatile` funciona directo | Nula: Threads/Runs/file_search son propietarios de OpenAI; en Groq hay que reimplementar el bucle manualmente |

Veredicto: se elige Assistants API como diseño lógico por sus hilos persistentes, orquestación de Runs y `file_search` nativo, que modelan mejor el flujo correos → requisitos → Jira/GCal/CRM; Chat Completions (Groq `openai/gpt-oss-120b` principal Production, fallback `qwen/qwen3.8-27b`) se usa como runtime real portable replicando ese mismo bucle de forma manual.

## 1.2 Justificación: 4 ventajas clave para UTPConsult

1. **Hilos largos (Threads) para contexto conversacional persistente.** Los casos de UTPConsult se extienden durante semanas en hilos de correo con TechCorp, donde cada mensaje añade restricciones al adjunto de requisitos inicial. Un Thread conserva todo el historial sin reenviarlo en cada llamada, evitando truncados y reduciendo el costo de tokens frente al modelo stateless.
2. **Orquestación multi-tool (Run + `requires_action`) en un solo caso.** Resolver un caso típico exige encadenar `crear_ticket_jira`, `agendar_gcal` y `actualizar_crm` con dependencias entre sí (el ticket precede a la reunión de Ana Torres). El objeto Run pausa en `requires_action`, ejecuta cada herramienta y reanuda el razonamiento hasta `completed`, sin que el backend reimplemente el bucle manualmente.
3. **File Search nativo para el adjunto del módulo pagos.** El documento de requisitos iniciales del módulo pagos (alcance, historias de usuario, restricciones) se ingiere una vez en un vector store con chunking y re-ranking gestionados. El asistente cita fragmentos exactos del adjunto en cada extracción, eliminando la infraestructura RAG propia que exigiría Chat Completions.
4. **Auditabilidad y gobernanza (Run steps + instrucciones versionables).** Cada Run registra sus `run steps` (llamada al modelo, invocación de herramienta, recuperación de archivos), lo que permite trazar qué correo originó cada ticket de Jira ante una auditoría del cliente. Las instrucciones del Assistant se versionan de forma centralizada, garantizando respuestas consistentes aunque cambie el analista asignado al caso.

## 1.3 Adaptación a restricción Groq (runtime real)

Groq solo expone el endpoint `/v1/chat/completions` con function calling (`tools`), sin Threads, Runs ni `file_search` nativos. El diseño lógico de las secciones 1.1-1.2 se mantiene como referencia, pero el runtime real replica ese comportamiento de forma manual: el backend conserva el historial, implementa el bucle de herramientas y sustituye la recuperación nativa por un pipeline propio.

| Concepto Assistants API | Implementación equivalente en Groq |
|---|---|
| Thread (historial persistente) | `st.session_state` en frontend más persistencia en base de datos (`messages[]`); cada llamada reenvía el historial completo al endpoint Chat Completions |
| Run (orquestación automática) | Bucle manual `while tool_calls`: llamada al modelo → ejecución de la función → reenvío del resultado como mensaje `tool` hasta respuesta final |
| `requires_action` (pausa antes de actuar) | Punto de validación HITL: el bucle se detiene antes de side-effects (Jira/GCal/CRM) y exige confirmación del usuario en la interfaz |

El runtime usa el modelo `openai/gpt-oss-120b` (principal Production, fallback `qwen/qwen3.8-27b`) con `tool_choice: auto`, validación de argumentos con esquemas Pydantic en el backend y `GROQ_API_KEY` exclusivamente server-side, sin exponerla al frontend.

<!-- F3 -->

## 1.4 Diagrama y principios operativos

```
[Gmail API] -> [Backend FastAPI ingesta+validación] -> [Groq openai/gpt-oss-120b (fallback qwen/qwen3.8-27b)] -> [Loop Run manual] -> [Jira/GCal/CRM mocks] -> [audit log] -> [Streamlit/React]
```

- **Trazabilidad.** Cada iteración del bucle manual registra sus run steps (llamada al modelo, invocación de herramienta, resultado devuelto), lo que permite reconstruir qué correo originó cada ticket, evento o actualización de CRM ante una auditoría.
- **Idempotencia.** Cada ejecución de herramienta se identifica con `Idempotency-Key=hash(correo+tool+args)`; ante reintentos o correos duplicados el backend detecta la clave existente y evita crear tickets Jira repetidos.
- **Seguridad.** `GROQ_API_KEY` reside exclusivamente en el backend (variables de entorno server-side) y nunca se expone al frontend; Streamlit/React solo reciben respuestas finales y estados del run.
