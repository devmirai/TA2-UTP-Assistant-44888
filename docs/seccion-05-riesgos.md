# 5. Riesgos y Ética - UTP Assistant

## R1 Alucinación operativa (fecha inventada, Jira duplicado UTPC-142)

**Riesgo:** El asistente confirma una reunión "lunes 10am" sin verificar disponibilidad real en el calendario, o duplica un ticket Jira (ej. UTPC-142) al reintentar un Run fallido. En contexto de consultora esto genera doble reserva con cliente y contaminación del backlog.

**Mitigación diseño:**
- Tools como única fuente de verdad: ninguna fecha o ticket existe hasta que la tool lo devuelve.
- Validación schema/pydantic + regex de fecha antes de ejecutar cualquier acción.
- Modo dry-run por defecto para previsualizar sin efectos laterales.

**Mitigación proceso:**
- HITL obligatorio con pregunta explícita "¿Confirmas para proceder?" antes de crear eventos o tickets.
- Idempotencia con `idempotency_key=hash(correo+tool+args)` para evitar duplicados en reintentos.

## R2 Filtración PII / prompt injection en adjunto (DNI, cuentas, instrucción oculta ignora reglas)

**Riesgo:** Un adjunto contiene datos sensibles (DNI, cuentas) o una instrucción oculta ("ignora reglas") que el modelo podría tratar como orden, provocando filtración de PII o bypass de políticas.

**Mitigación diseño:**
- Sanitización DLP/enmascarar (`\d{8}`, emails) antes del Thread con presidio/regex.
- Scope tools sin envío externo.
- Jerarquía system>tool>user/adjunto (adjunto es dato).

**Mitigación proceso:**
- Audit log + banner "Contiene PII - no incluir en Jira público" + revisión humana.

## Matriz de riesgos

| Riesgo | Impacto | Probabilidad | Mitigación diseño | Mitigación proceso |
| --- | --- | --- | --- | --- |
| R1 Alucinación operativa (fecha inventada, Jira duplicado) | Alto: doble reserva con cliente y backlog contaminado | Media: reintentos y fechas ambiguas son frecuentes | Tools como única fuente de verdad, validación schema/pydantic y dry-run por defecto | HITL con confirmación explícita e idempotency_key en reintentos |
| R2 Filtración PII / prompt injection en adjunto | Alto: exposición de DNI/cuentas y bypass de políticas | Media: adjuntos externos no controlados | Sanitización DLP/enmascarado previo, scope sin envío externo, jerarquía system>tool>user | Audit log, banner de PII y revisión humana antes de publicar |
