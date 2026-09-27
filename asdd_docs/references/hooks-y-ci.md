# Cómo se hace cumplir ASDD

ASDD tiene tres capas. Las instrucciones son una petición; el hook y la CI son el control real.

## Capa 1 — Instrucciones (todos los agentes)

`AGENTS.md` es la única fuente de verdad. El resto de archivos solo remiten a él:

| Asistente | Archivo que lee |
|-----------|-----------------|
| Codex, Copilot coding agent, Cursor y otros compatibles con AGENTS.md | `AGENTS.md` |
| Claude Code | `CLAUDE.md` (importa `@AGENTS.md`) |
| GitHub Copilot (chat en IDE) | `.github/copilot-instructions.md` |
| Cursor | `.cursor/rules/asdd.mdc` (`alwaysApply: true`) |
| Gemini CLI | `GEMINI.md` |
| Windsurf | `.windsurf/rules/asdd.md` (`trigger: always_on`) |

Las herramientas cambian a menudo qué archivos leen: comprueba en cada asistente que uses que
efectivamente carga las instrucciones (pregúntale "¿qué metodología sigue este repo?").
**Nunca añadas reglas en los punteros**: se desincronizan.

## Capa 2 — Guard local (Claude Code)

`.claude/settings.json` registra dos hooks:

- **`PreToolUse` → `.claude/hooks/asdd_guard.py`** en `Edit|Write|MultiEdit|NotebookEdit`.
  Permite siempre escribir en `asdd_docs/`. Fuera de ahí, solo si:
  1. hay un plan con `**Estado:** EN EJECUCIÓN` y `**Aprobado:** [x]`,
  2. su SPEC referenciado tiene `**Aprobado:** [x]`,
  3. y el archivo está declarado en ese plan (tabla o líneas `Archivos:`, admite globs y carpetas);
  o bien la rama tiene un PR abierto con `asdd-bypass`. Si no, sale con código 2: la edición se
  bloquea y el agente recibe el motivo. Aplica también a los subagentes.
- **`PostToolUse` → `.claude/hooks/asdd_log.py`**: añade cada acción a
  `.asdd/logs/YYYY-MM-DD.jsonl` (fuera de git).

Requisitos: `python3`; `gh` autenticado para detectar el bypass.

## Capa 3 — CI (cualquier agente)

`.github/workflows/asdd-check.yml` ejecuta `.github/scripts/asdd_check.py` en cada PR
(al abrir, editar la descripción, hacer push y poner/quitar labels):

- **Con `asdd-bypass`**: exige `## Motivo del bypass` con contenido. Nada más.
- **Sin label**: si el PR toca algo fuera de `asdd_docs/`, su descripción debe referenciar
  planes que estén `COMPLETADO` y aprobados, con SPEC aprobado, todas las tareas en `[x]`, un acta
  `TXX.md` por tarea más `RESUMEN.md`, y **todos** los archivos modificados declarados.
- PRs que solo tocan `asdd_docs/` (specs y planes para revisión) pasan siempre.

Para que la CI sea obligatoria: Settings → Branches → regla para `main` → *Require a pull request*
y *Require status checks to pass* → `Agentic Spec-Driven Development`.

## Limitaciones conocidas (asumidas)

- **Autoaprobación**: un agente podría marcar él mismo `**Aprobado:** [x]` o poner el label.
  Lo prohíbe `AGENTS.md`, pero no se bloquea por código. Cierre futuro posible: `CODEOWNERS`
  sobre `asdd_docs/specs/` y `asdd_docs/plans/` + revisión obligatoria.
- **Escrituras por shell**: el guard vigila las herramientas de edición, no comandos como
  `echo > archivo` o `sed -i`. La CI lo detecta al comprobar los archivos declarados.
- **Otros asistentes** no tienen el guard local: dependen de la Capa 1 y la CI los frena al hacer PR.
