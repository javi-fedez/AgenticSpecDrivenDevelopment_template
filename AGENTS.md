# AGENTS.md — Agentic Spec-Driven Development (ASDD)

_Versión del framework: ver `VERSION` (actual: 1.0.0-beta) · cambios en `CHANGELOG.md`_

> **Fuente única de verdad** para cualquier agente de IA que trabaje en este repositorio
> (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Windsurf u otros).
> Los archivos `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/` y
> `.windsurf/rules/` solo remiten aquí. **No añadas reglas en ellos.**

ASDD es un método en el que **los agentes hacen todo el ciclo** —escriben el spec, planifican,
ejecutan en paralelo con subagentes y verifican cada tarea con evidencia— y el **humano responsable**
aporta los puntos de aprobación. El spec manda; el agente lo escribe; el humano lo aprueba.

---

## Regla de oro

```
SPEC aprobado → PLAN aprobado → EXECUTE por oleadas → VERIFICACIÓN por tarea → T_FINAL end-to-end
```

- Sin SPEC aprobado: **para y haz el SPEC**.
- Sin PLAN aprobado y en estado `EN EJECUCIÓN`: **para y haz el PLAN**.
- Sin verificación con evidencia: **la tarea no está hecha**.
- No hay excepciones. Ni para "cambios pequeños". Ni para "solo una línea".

Todo vive en `asdd_docs/`:

```
asdd_docs/
├── specs/        YYYY-MM-DD-<feature>.md            ← Fase 1
├── plans/        YYYY-MM-DD-<feature>.md            ← Fase 2
├── verifications/ YYYY-MM-DD-<feature>/             ← Fase 3
│                 ├── T01.md … T_FINAL.md            (un .md por tarea: justificación + evidencias)
│                 └── RESUMEN.md                     (lo escribe el orquestador)
├── templates/    spec.md, plan.md, verification.md, resumen.md
└── references/   bypass.md, hooks-y-ci.md, debugging.md, tipos-proyecto.md
```

**Un SPEC = un PLAN, con el mismo nombre de archivo.** Ese `<feature>` es también el nombre de la
carpeta de verificaciones. Si algo necesita dos planes, son dos SPECs. La CI lo comprueba.

---

## FASE 1 — SPEC

1. **Explora el contexto** antes de preguntar: este archivo, código existente, esquema de
   Supabase, workflows de n8n, specs y planes anteriores.
2. **Pregunta de una en una.** Prefiere opción múltiple. Aplica YAGNI: saca todo lo que no sea
   imprescindible para esta versión.
3. **Propón 2-3 enfoques** con sus trade-offs antes de decidir.
4. **Escribe el SPEC** con `asdd_docs/templates/spec.md` en `asdd_docs/specs/YYYY-MM-DD-<feature>.md`.
5. **Preséntalo por secciones** y valida cada una.
6. **Autorrevisión antes de presentarlo:**
   - ¿Todos los criterios de aceptación son verificables sin ambigüedad?
   - ¿Se ha aplicado YAGNI?
   - ¿Los recursos afectados están completos (tablas, workflows, archivos)?
   - ¿Hay contradicciones internas?
   - ¿El alcance es realista?
7. **Espera aprobación explícita** ("ok", "adelante", "aprobado"). Solo el humano marca
   `**Aprobado:** [x]` y `**Estado:** APROBADO`. **Tú no lo marcas.**

---

## FASE 2 — PLAN

1. **Mapea archivos y recursos**: cada uno con una responsabilidad única, con **ruta exacta**
   (nunca "el archivo de config", sino `src/config/supabase.ts`).
2. **Declara todo lo que se va a tocar** en la tabla *Archivos / recursos afectados* y en la
   línea `Archivos:` de cada tarea, siempre entre backticks. **Lo que no esté declarado no se
   podrá editar**: el guard lo bloquea y la CI lo rechaza.
3. **Tareas atómicas** (2-5 min), cada una con `Tipo verificación`, `Archivos`, `Depende de`,
   `Qué hace` y `Verificar` (comando exacto + resultado esperado).
   **Tipo de verificación** (elige el más fuerte posible):
   - `auto` → el comando es reproducible fuera de tu máquina (scripts, tests, builds, `curl` a
     staging). La CI lo **vuelve a ejecutar** en cada PR. Sin secretos en el comando: usa
     variables de entorno.
   - `local` → necesita credenciales o sistemas internos. Se ejecuta en local con
     `asdd-verify.sh` y queda la evidencia registrada.
   - `manual` → no automatizable (revisión visual, escuchar una llamada…). La confirma el
     responsable humano.
   **`T_FINAL` debe ser `auto` siempre que sea posible.**
4. **Agrupa en oleadas:**
   - **Oleada paralela**: tareas sin dependencias entre sí y **sin archivos ni recursos
     compartidos**.
   - **Oleada secuencial**: todo lo que comparta recursos o dependa de otra tarea.
   - **Siempre secuencial**: migraciones de Supabase, cambios en un mismo workflow de n8n,
     cualquier cosa que toque una misma tabla, API externa con estado o archivo de configuración
     compartido. Ante la duda, secuencial.
5. **Cierra siempre con `T_FINAL`**: verificación end-to-end contra todos los criterios de
   aceptación del SPEC.
6. Si el SPEC cubre subsistemas independientes, **propón planes separados** que funcionen solos.
7. Usa `asdd_docs/templates/plan.md` → `asdd_docs/plans/YYYY-MM-DD-<feature>.md` (mismo nombre
   que el SPEC), con la referencia al SPEC en la cabecera.
8. **Espera el "go" explícito.** El humano marca `**Aprobado:** [x]`. Al empezar a ejecutar,
   cambia el estado a `**Estado:** EN EJECUCIÓN` (eso sí lo haces tú, y solo con el plan aprobado).

Nada de "para futuras versiones" en el plan: eso va al SPEC, en *Fuera de alcance*.

---

## FASE 3 — EXECUTE (por oleadas)

### Roles

| Rol | Qué hace |
|-----|----------|
| **Orquestador** | Agente principal. Lee el plan, lanza las oleadas, lanza subagentes, integra resultados, marca `[x]`, escribe `RESUMEN.md`. No implementa tareas de una oleada paralela. |
| **Implementador** | Subagente con contexto limpio. Recibe **una** tarea (texto de la tarea + SPEC + archivos declarados). Implementa solo eso, la verifica con `asdd-verify.sh` y escribe su justificación. |
| **Revisor** | Subagente distinto del implementador. Comprueba 1) que se hizo exactamente lo pedido y cumple el SPEC, 2) calidad, 3) que la evidencia demuestra lo que dice la justificación. Completa *Revisión*. Si pide cambios, vuelve al implementador. |

### Ciclo por oleada

1. El orquestador anuncia: `Oleada N (paralela|secuencial): T01, T02…`.
2. **Oleada paralela**: lanza un implementador por tarea a la vez. **Oleada secuencial**: uno
   detrás de otro.
3. Cada implementador:
   1. Implementa exactamente su tarea. Nada más.
   2. **Verifica siempre a través de la herramienta**, nunca a mano:
      ```bash
      ./scripts/asdd-verify.sh <feature> TXX -- <comando de la tarea>
      ```
      Ejecuta el comando y añade a `asdd_docs/verifications/<feature>/TXX.md` un bloque de
      evidencia (fecha, commit, comando, código de salida, salida real y hash de integridad).
      Si falla, también queda registrado: corrige y vuelve a ejecutarlo. La CI valida el último.
      Para tuberías: `-- bash -c "comando | otro"`.
   3. Completa en ese mismo `.md` (plantilla `asdd_docs/templates/verification.md`) las secciones
      *Qué se hizo*, *Archivos tocados* y *Por qué cumple*.
   4. **Nunca escribas ni edites los bloques de evidencia**: el guard lo bloquea y la CI detecta
      cualquier manipulación por el hash.
   5. Si el tipo es `manual`, describe en *Verificación manual* qué debe comprobar el responsable
      y **para**: la casilla la marca él.
4. Un revisor revisa cada tarea, contrasta justificación y evidencia, y pone
   `Veredicto: APROBADA` o pide cambios.
5. Tras una oleada paralela, el orquestador hace una **revisión de integración** de todos los
   cambios juntos (conflictos, acoplamientos no previstos).
6. El orquestador marca en el plan `[x]` **solo** las tareas con evidencia OK (o confirmación
   manual), justificación completa y revisión APROBADA.
7. Reporta al humano el resultado de la oleada y pregunta si continúa.

Al terminar `T_FINAL`, el orquestador escribe `RESUMEN.md` con `asdd_docs/templates/resumen.md`
y cambia el plan a `**Estado:** COMPLETADO`. **Done solo si todos los criterios de aceptación pasan.**

### Degradación a modo secuencial

Si tu herramienta **no puede lanzar subagentes**, ejecuta el mismo plan tú solo, oleada a
oleada y tarea a tarea, en orden. Todo lo demás es igual: `asdd-verify.sh` por tarea,
justificación y revisión, que harás en un paso separado releyendo la tarea y el SPEC antes de
marcar `[x]`. Indica `Ejecutada por: agente único` en el `.md` y `Modo: secuencial` en el resumen.

### Verificación: concreta, ejecutable y con evidencia

| Tipo de tarea | Válida | Inválida |
|---------------|--------|----------|
| Script Python | `python script.py` devuelve X | "Parece correcto" |
| Endpoint API | `curl` devuelve 200 + body esperado | "El código tiene buena pinta" |
| Migración Supabase | `SELECT` devuelve lo esperado | "La migración se aplicó" |
| Workflow n8n | Ejecución de prueba con nodo en success | "El workflow está configurado" |
| Función JS/TS | Test o `console.log` con input/output | "La lógica es correcta" |

### Nunca

- Implementar más de lo que dice la tarea.
- Avanzar sin verificar la tarea actual.
- Marcar `[x]` sin evidencia de `asdd-verify.sh` (o confirmación manual), o declarar "listo" sin verificar.
- Escribir o editar bloques `ASDD-EVIDENCE`, o pegar salidas "a mano" como si fueran evidencia.
- Poner secretos en comandos de verificación: usa variables de entorno.
- Tocar archivos no declarados en el plan (el guard lo bloqueará igualmente).
- Marcar tú `**Aprobado:** [x]` en un SPEC o un PLAN.
- **Poner, pedir a otra herramienta que ponga o sugerir que se ponga el label `asdd-bypass`.**
  Si crees que no hay alternativa, **para y díselo al humano**.

### Si algo falla

1. **Para.** No parchees tocando otros archivos.
2. **Diagnostica** la causa raíz (ver `asdd_docs/references/debugging.md`).
3. **Documenta** el fallo: la evidencia fallida ya queda registrada por `asdd-verify.sh`; añade
   la causa en el `.md` de la tarea.
4. **Reporta** al humano: qué falló, por qué y opciones.
5. Si el plan estaba mal diseñado, **propón el cambio de plan** y espera aprobación.

---

## Señales de peligro → PARA y consulta

| Señal | Qué hacer |
|-------|-----------|
| "Voy a modificar también X porque lo necesito para Y" | Para, anúncialo, pide actualizar el plan |
| Una tarea tarda mucho más de 5 minutos | Para: el plan necesita revisión |
| El archivo a modificar no existe | Para: verifica el plan |
| Hay que tocar algo no declarado | Para: posible scope creep |
| El criterio de verificación no es claro | Para: aclara antes de ejecutar |
| Falla algo que "debería funcionar" | Para: diagnostica, no parchees |
| Dos tareas paralelas acaban necesitando el mismo archivo | Para la oleada: pásalas a secuencial |
| El guard te bloquea | No busques rodeos (p. ej. escribir por shell): para y reporta |

---

## Bypass

El **único** mecanismo para saltarse ASDD es el label `asdd-bypass` en un PR, que pone
**exclusivamente el humano responsable** cuando no hay alternativa. Exige una sección
`## Motivo del bypass` en la descripción del PR. Procedimiento completo:
`asdd_docs/references/bypass.md`. Como agente, tu único papel es **parar y avisar**.

---

## Git y PRs

- Nunca trabajes directamente en `main`. Una rama por plan: `asdd/<feature>`.
- Un commit por tarea: `T03(<feature>): <qué hace>` (imperativo, ≤72 caracteres).
- El PR referencia el plan en su descripción (plantilla en `.github/pull_request_template.md`).
  La CI valida plan COMPLETADO, tareas `[x]`, verificaciones con evidencia íntegra, reejecuta las
  `auto` y comprueba que todos los archivos modificados estaban declarados.

## Trazabilidad

| Qué | Dónde | Quién lo escribe | ¿En git? |
|-----|-------|------------------|----------|
| Qué se construye | `asdd_docs/specs/` | Agente, aprueba el humano | Sí |
| Cómo y en qué orden | `asdd_docs/plans/` | Agente, aprueba el humano | Sí |
| Qué se hizo y por qué cumple | `asdd_docs/verifications/` (secciones del `.md`) | Agentes | Sí |
| Prueba de que funciona | `asdd_docs/verifications/` (bloques de evidencia) | `asdd-verify.sh` (nunca el agente) | Sí |
| Prueba independiente | Reejecución de tareas `auto` | CI de GitHub | Log de Actions |
| Qué cambió en el código | Commits `TXX(<feature>)` | Agentes | Sí |
| Traza bruta de cada acción | `.asdd/logs/*.jsonl` | Hook automático (Claude Code) | No |

## Cheatsheet

```
"construye / implementa / crea / monta X"
        ↓
¿SPEC aprobado?  NO → Fase 1
        ↓ sí
¿PLAN aprobado?  NO → Fase 2
        ↓ sí → Estado: EN EJECUCIÓN
Oleada 1 → implementadores → asdd-verify.sh → revisores → [x]
Oleada 2 → …
T_FINAL → todos los CA ✓ → RESUMEN.md → Estado: COMPLETADO → PR
```
