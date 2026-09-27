# Changelog — Agentic Spec-Driven Development (ASDD)

Todas las versiones del framework se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado
[SemVer](https://semver.org/lang/es/).

## [1.0.0-beta] — 2026-09-27

Primera versión pública del framework, evolución de la skill interna `sdd-lite`.

### Metodología
- Nombre y enfoque: **Agentic Spec-Driven Development (ASDD)**. Los agentes escriben el spec,
  planifican, ejecutan y verifican; el responsable humano aprueba.
- Tres fases: SPEC → PLAN → EXECUTE, con la regla "un SPEC = un PLAN, mismo nombre".
- Ejecución por **oleadas** (paralelas o secuenciales) con roles de orquestador, implementador
  y revisor mediante subagentes, y **degradación a modo secuencial** en asistentes sin subagentes.
- Supabase, n8n y recursos compartidos: siempre en oleada secuencial.

### Verificación
- `asdd_docs/verifications/<feature>/`: un `.md` por tarea (justificación del agente + evidencias)
  y `RESUMEN.md`.
- `scripts/asdd-verify.sh`: ejecuta la verificación y registra la evidencia (fecha, commit,
  comando, código de salida, salida enmascarada y hash de integridad).
- Tipos de verificación por tarea: `auto` (la CI la reejecuta), `local` (evidencia registrada)
  y `manual` (confirma el responsable).

### Cumplimiento
- `AGENTS.md` como fuente única, con punteros para Claude Code, Copilot, Cursor, Gemini CLI y Windsurf.
- Hooks de Claude Code: guard (plan aprobado, archivos declarados, evidencias protegidas) y log
  automático en `.asdd/logs/` (no versionado).
- CI `asdd-check`: plan completado, verificaciones íntegras, reejecución de tareas `auto` y
  archivos declarados.
- Bypass único mediante el label `asdd-bypass`, con `## Motivo del bypass` obligatorio.

### Limitaciones conocidas
- Un agente podría autoaprobar specs y planes o poner el label (prohibido en `AGENTS.md`, no
  bloqueado por código).
- El guard local solo existe en Claude Code; el resto de asistentes dependen de las instrucciones
  y de la CI.
