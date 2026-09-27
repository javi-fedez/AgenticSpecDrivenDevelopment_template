#!/usr/bin/env python3
"""ASDD guard — hook PreToolUse de Claude Code.

1) Protege las evidencias: el agente no puede crear, editar ni reescribir bloques
   ASDD-EVIDENCE (solo los escribe scripts/asdd-verify.sh).
2) Bloquea cualquier escritura fuera de asdd_docs/ salvo que:
  a) exista un PLAN en estado EN EJECUCIÓN, aprobado, cuyo SPEC también esté
     aprobado, y el archivo esté declarado en ese plan; o
  b) la rama actual tenga un PR abierto con el label `asdd-bypass`.

Salida 0 = permitir. Salida 2 = bloquear (stderr se devuelve al agente).
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

BYPASS_LABEL = "asdd-bypass"
DOCS_DIR = "asdd_docs"
CACHE_TTL_SECONDS = 300

APPROVED_RE = re.compile(r"\*\*Aprobado:\*\*\s*\[[xX]\]")
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([A-ZÁÉÍÓÚ ]+)")
SPEC_REF_RE = re.compile(r"(asdd_docs/specs/[\w./-]+\.md)")
BACKTICK_RE = re.compile(r"`([^`]+)`")
EVIDENCE_MARK = "ASDD-EVIDENCE"


def project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def plan_state(text: str) -> str:
    m = STATE_RE.search(text)
    return m.group(1).strip() if m else ""


def declared_paths(plan_text: str) -> set[str]:
    """Rutas declaradas en líneas 'Archivos:' y en filas de tabla."""
    paths: set[str] = set()
    for line in plan_text.splitlines():
        stripped = line.strip()
        if re.match(r"^[-*]?\s*Archivos?\s*:", stripped):
            paths.update(p.strip() for p in BACKTICK_RE.findall(stripped))
        elif stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells:
                paths.update(p.strip() for p in BACKTICK_RE.findall(cells[0]))
    return {p for p in paths if p}


def path_matches(rel: str, pattern: str) -> bool:
    pattern = pattern.lstrip("./")
    if pattern.endswith("/"):
        return rel.startswith(pattern)
    return rel == pattern or fnmatch.fnmatch(rel, pattern)


def active_plans(root: Path) -> list[tuple[Path, str]]:
    plans = []
    for plan in sorted((root / DOCS_DIR / "plans").glob("*.md")):
        text = plan.read_text(encoding="utf-8")
        if "EN EJECUCI" not in plan_state(text) or not APPROVED_RE.search(text):
            continue
        spec_ref = SPEC_REF_RE.search(text)
        if not spec_ref:
            continue
        spec = root / spec_ref.group(1)
        if spec.exists() and APPROVED_RE.search(spec.read_text(encoding="utf-8")):
            plans.append((plan, text))
    return plans


def has_bypass_label(root: Path) -> bool:
    cache = root / ".asdd" / "bypass-cache.json"
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return False
    if not branch or branch in ("main", "master", "HEAD"):
        return False
    try:
        data = json.loads(cache.read_text())
        if data.get("branch") == branch and time.time() - data.get("ts", 0) < CACHE_TTL_SECONDS:
            return bool(data.get("bypass"))
    except (OSError, ValueError):
        pass
    bypass = False
    try:
        out = subprocess.run(
            ["gh", "pr", "view", branch, "--json", "labels,state"],
            cwd=root, capture_output=True, text=True, timeout=15,
        )
        if out.returncode == 0:
            info = json.loads(out.stdout)
            names = {lbl.get("name") for lbl in info.get("labels", [])}
            bypass = info.get("state") == "OPEN" and BYPASS_LABEL in names
    except (OSError, subprocess.SubprocessError, ValueError):
        bypass = False
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"branch": branch, "ts": time.time(), "bypass": bypass}))
    except OSError:
        pass
    return bypass


def block(msg: str) -> None:
    print(f"[ASDD] BLOQUEADO: {msg}", file=sys.stderr)
    sys.exit(2)


def guard_evidence(path: Path, tool_input: dict) -> None:
    """Las evidencias solo las escribe asdd-verify.sh, nunca el agente."""
    edits = tool_input.get("edits") or [tool_input]
    for edit in edits:
        for key in ("old_string", "new_string", "content"):
            if EVIDENCE_MARK in str(edit.get(key) or ""):
                block(
                    "no puedes escribir ni editar bloques de evidencia a mano. Ejecuta la "
                    "verificación con ./scripts/asdd-verify.sh <feature> <TXX> -- <comando>."
                )
    if "content" in tool_input and path.exists() and EVIDENCE_MARK in path.read_text(encoding="utf-8"):
        block(
            f"'{path.name}' ya contiene evidencias: no se puede reescribir entero. "
            "Usa ediciones parciales (Edit) sobre tus secciones."
        )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        sys.exit(0)

    root = project_dir()
    try:
        rel = Path(target).resolve().relative_to(root).as_posix()
    except ValueError:
        sys.exit(0)  # fuera del proyecto: no es asunto de ASDD

    if rel.startswith(f"{DOCS_DIR}/verifications/"):
        guard_evidence(root / rel, tool_input)

    if rel.startswith(f"{DOCS_DIR}/"):
        sys.exit(0)  # Fases SPEC y PLAN y verificaciones: siempre permitido

    if has_bypass_label(root):
        sys.exit(0)

    plans = active_plans(root)
    if not plans:
        block(
            f"no hay ningún PLAN en estado 'EN EJECUCIÓN' y aprobado (con su SPEC aprobado) "
            f"que cubra '{rel}'. Vuelve a la Fase 1 (SPEC) o Fase 2 (PLAN) según AGENTS.md. "
            f"Nunca pongas tú el label '{BYPASS_LABEL}'."
        )
    for plan, text in plans:
        if any(path_matches(rel, p) for p in declared_paths(text)):
            sys.exit(0)
    names = ", ".join(p.name for p, _ in plans)
    block(
        f"'{rel}' no está declarado en el plan activo ({names}). Es scope creep: PARA, "
        f"anúncialo y pide que se actualice el PLAN antes de tocarlo."
    )


if __name__ == "__main__":
    main()
