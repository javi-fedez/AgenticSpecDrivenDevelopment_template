# AgenticSpecDrivenDevelopment_template — Agentic Spec-Driven Development

**Versión:** `1.0.0-beta` · [Changelog](CHANGELOG.md)

Plantilla de repositorio para trabajar con agentes de IA bajo **ASDD**: los agentes escriben el
spec, planifican, ejecutan en paralelo con subagentes, verifican cada tarea con evidencia
capturada por una herramienta;
el responsable humano aprueba en los puntos clave.

```
SPEC aprobado → PLAN aprobado → EXECUTE por oleadas → VERIFICACIÓN por tarea → T_FINAL end-to-end
```

## Qué incluye

| Pieza | Para qué |
|-------|----------|
| `AGENTS.md` | La metodología completa. Fuente única para todos los agentes. |
| `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, `.windsurf/rules/` | Punteros a `AGENTS.md` para cada asistente. |
| `.claude/settings.json` + `.claude/hooks/` | Guard que bloquea escribir código sin plan aprobado o fuera de lo declarado, y log automático de acciones. |
| `.github/workflows/asdd-check.yml` | CI que valida cada PR: plan completado, verificaciones con evidencia íntegra, reejecución de las tareas `auto`, archivos declarados o bypass con motivo. |
| `.github/pull_request_template.md` | PR con referencia al plan y sección de motivo de bypass. |
| `asdd_docs/` | Specs, planes, verificaciones, plantillas y referencias. |
| `scripts/asdd-verify.sh` | Ejecuta la verificación de una tarea y registra la evidencia (salida, exit, commit, hash). |
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
asdd_docs/verifications/2026-10-01-alta-clientes/
    T01.md  T02.md  T03.md  T_FINAL.md  RESUMEN.md ← por tarea: justificación del agente
                                                     + evidencia generada por asdd-verify.sh
.asdd/logs/2026-10-01.jsonl                        ← traza automática (no se versiona)
```

## ¿Cómo sé que las verificaciones se han hecho?

Cada `.md` de `verifications/` separa lo que **dice el agente** de lo que **registró la máquina**:

| Tipo | Prueba | Quién la genera |
|------|--------|-----------------|
| `auto` | La CI vuelve a ejecutar el comando en cada PR | GitHub Actions |
| `local` | Bloque de evidencia con salida, exit, commit y hash de integridad | `asdd-verify.sh` |
| `manual` | Casilla *Verificado por el responsable* | Tú |

El guard impide al agente escribir evidencias a mano y la CI detecta cualquier manipulación
por el hash. Además, `.asdd/logs/` registra en local cada comando realmente ejecutado.

## Versionado

ASDD sigue [SemVer](https://semver.org/lang/es/): `MAYOR.MENOR.PARCHE[-pre]`.

| Cambio | Sube | Ejemplo |
|--------|------|---------|
| Rompe proyectos existentes (estructura de `asdd_docs/`, formato de plan o verificación, reglas de la CI) | MAYOR | `2.0.0` |
| Añade capacidades compatibles (nuevo tipo de verificación, nueva plantilla, soporte de otro asistente) | MENOR | `1.1.0` |
| Corrige errores o documentación sin cambiar el comportamiento | PARCHE | `1.0.1` |
| Versión de prueba antes de estabilizar | sufijo | `1.0.0-beta` |

- La versión vigente está en [`VERSION`](VERSION) y cada cambio se documenta en
  [`CHANGELOG.md`](CHANGELOG.md).
- Cada versión publicada se etiqueta en git (`v1.0.0-beta`).
- **Los proyectos creados desde la plantilla heredan el archivo `VERSION`**: así sabes con qué
  versión de ASDD nació cada proyecto. Para actualizar uno, revisa el changelog entre su versión
  y la actual y copia los archivos afectados (`AGENTS.md`, `.claude/`, `.github/`, `scripts/`,
  `asdd_docs/templates/`, `asdd_docs/references/`). Nunca sobrescribas sus `specs/`, `plans/` ni
  `verifications/`.
- Los cambios en el propio framework se hacen siguiendo ASDD en este repositorio.

## Documentación

- Metodología: [`AGENTS.md`](AGENTS.md)
- Cómo se hace cumplir y limitaciones: [`asdd_docs/references/hooks-y-ci.md`](asdd_docs/references/hooks-y-ci.md)
- Bypass (única vía de excepción): [`asdd_docs/references/bypass.md`](asdd_docs/references/bypass.md)
- Debugging: [`asdd_docs/references/debugging.md`](asdd_docs/references/debugging.md)
- Patrones por tipo de proyecto: [`asdd_docs/references/tipos-proyecto.md`](asdd_docs/references/tipos-proyecto.md)
