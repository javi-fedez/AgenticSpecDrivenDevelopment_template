# AgenticSpecDrivenDevelopment_template — Agentic Spec-Driven Development

Plantilla de repositorio para trabajar con agentes de IA bajo **ASDD**: los agentes escriben el
spec, planifican, ejecutan en paralelo con subagentes, verifican y levantan acta de cada tarea;
el responsable humano aprueba en los puntos clave.

```
SPEC aprobado → PLAN aprobado → EXECUTE por oleadas → ACTA por tarea → VERIFY end-to-end
```

## Qué incluye

| Pieza | Para qué |
|-------|----------|
| `AGENTS.md` | La metodología completa. Fuente única para todos los agentes. |
| `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, `.windsurf/rules/` | Punteros a `AGENTS.md` para cada asistente. |
| `.claude/settings.json` + `.claude/hooks/` | Guard que bloquea escribir código sin plan aprobado o fuera de lo declarado, y log automático de acciones. |
| `.github/workflows/asdd-check.yml` | CI que valida cada PR: plan completado, actas por tarea, archivos declarados o bypass con motivo. |
| `.github/pull_request_template.md` | PR con referencia al plan y sección de motivo de bypass. |
| `asdd_docs/` | Specs, planes, actas de ejecución, plantillas y referencias. |
| `scripts/asdd-init.sh` | Crea el label `asdd-bypass` y comprueba dependencias. |

## Empezar un proyecto nuevo

1. **Use this template → Create a new repository** (o `gh repo create <nombre> --template javi-fedez/AgenticSpecDrivenDevelopment_template --private --clone`).
2. En el repo nuevo: `./scripts/asdd-init.sh` (requiere `gh auth login`).
3. Settings → Branches → protege `main`: *Require a pull request* + *Require status checks* →
   `Agentic Spec-Driven Development`.
4. Pide a tu agente lo que quieras construir. Empezará por el SPEC.

Requisitos locales: `python3` (hooks) y `gh` (detección del bypass).

## Flujo en una imagen

```
asdd_docs/specs/2026-10-01-alta-clientes.md        ← agente redacta, humano aprueba
asdd_docs/plans/2026-10-01-alta-clientes.md        ← agente planifica en oleadas, humano da el go
asdd_docs/executions/2026-10-01-alta-clientes/
    T01.md  T02.md  T03.md  T_FINAL.md  RESUMEN.md ← un acta por tarea con la salida real
.asdd/logs/2026-10-01.jsonl                        ← traza automática (no se versiona)
```

## Documentación

- Metodología: [`AGENTS.md`](AGENTS.md)
- Cómo se hace cumplir y limitaciones: [`asdd_docs/references/hooks-y-ci.md`](asdd_docs/references/hooks-y-ci.md)
- Bypass (única vía de excepción): [`asdd_docs/references/bypass.md`](asdd_docs/references/bypass.md)
- Debugging: [`asdd_docs/references/debugging.md`](asdd_docs/references/debugging.md)
- Patrones por tipo de proyecto: [`asdd_docs/references/tipos-proyecto.md`](asdd_docs/references/tipos-proyecto.md)
