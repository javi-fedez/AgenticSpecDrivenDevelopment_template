#!/usr/bin/env python3
"""ASDD verify — ejecuta la verificación de una tarea y registra la evidencia.

Uso:
    ./scripts/asdd-verify.sh <feature> <TXX> -- <comando> [args...]

Ejemplo:
    ./scripts/asdd-verify.sh 2026-10-01-alta-clientes T02 -- python3 src/alta.py --dry-run
    ./scripts/asdd-verify.sh 2026-10-01-alta-clientes T03 -- bash -c "curl -s https://x | jq .status"

Ejecuta el comando (sin shell; para tuberías usa `bash -c "..."`) y AÑADE al final de
asdd_docs/verifications/<feature>/<TXX>.md un bloque de evidencia con fecha, commit, comando,
código de salida y salida real, más un hash de integridad. Ese bloque lo escribe esta
herramienta, nunca el agente. Devuelve el mismo código de salida que el comando.
"""
from __future__ import annotations

import hashlib
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DOCS = Path("asdd_docs")
MAX_CHARS = 20_000
TIMEOUT = 900
SECRET_PATTERNS = [
    (re.compile(r"(sk|pk|rk)[-_](live|test|proj|ant)?[-_]?[A-Za-z0-9_\-]{16,}"), "***SECRET***"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "***GITHUB_TOKEN***"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "***JWT***"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{16,}"), r"\1***TOKEN***"),
    (re.compile(r"(?i)((?:api[_-]?key|token|secret|password)[\"']?\s*[:=]\s*[\"']?)[^\s\"',]{6,}"), r"\1***"),
]


def mask(text: str) -> str:
    for pattern, repl in SECRET_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def ensure_file(path: Path, task: str, feature: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    template = DOCS / "templates" / "verification.md"
    text = template.read_text(encoding="utf-8") if template.exists() else f"# {task}\n"
    text = text.replace("TXX", task).replace("YYYY-MM-DD-<feature>", feature)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    argv = sys.argv[1:]
    if "--" not in argv or argv.index("--") != 2 or len(argv) < 4:
        print(__doc__, file=sys.stderr)
        return 64
    feature, task, cmd = argv[0], argv[1], argv[3:]
    if not re.fullmatch(r"T\d+|T_FINAL", task):
        print(f"Tarea no válida: {task} (usa T01, T02… o T_FINAL)", file=sys.stderr)
        return 64
    if not (DOCS / "plans" / f"{feature}.md").exists():
        print(f"No existe el plan asdd_docs/plans/{feature}.md", file=sys.stderr)
        return 64

    started = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        exit_code, raw = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError:
        exit_code, raw = 127, f"Comando no encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        exit_code, raw = 124, f"Timeout tras {TIMEOUT}s"
    duration = (datetime.now(timezone.utc) - started).total_seconds()

    out = mask(raw).rstrip("\n")
    if len(out) > MAX_CHARS:
        out = out[:MAX_CHARS] + f"\n[… salida truncada a {MAX_CHARS} caracteres]"
    out = out.replace("~~~~", "~ ~ ~ ~")
    raw_cmd = shlex.join(cmd)
    cmd_str = mask(raw_cmd)
    sha = git("rev-parse", "HEAD") or "sin-commit"
    status = git("status", "--porcelain")
    dirty = bool(status)
    # ¿Hay cambios sin commitear FUERA de asdd_docs/? (clave para validar líneas base)
    dirty_code = any(
        line and not line[3:].strip('"').startswith("asdd_docs/") for line in status.splitlines()
    )

    data = {
        "task": task,
        "ts": started.isoformat(timespec="seconds"),
        "duration_s": round(duration, 1),
        "sha": sha,
        "dirty": dirty,
        "dirty_code": dirty_code,
        "cmd": cmd_str,
        "cmd_masked": cmd_str != raw_cmd,
        "exit": exit_code,
        "out_sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(),
    }
    estado = "✅ OK" if exit_code == 0 else "❌ FALLO"
    block = (
        "\n<!-- ASDD-EVIDENCE:BEGIN -->\n"
        f"### Evidencia capturada — {estado}\n"
        "_Generada por `scripts/asdd-verify.sh`. No editar: la CI comprueba su integridad._\n\n"
        f"- Fecha (UTC): {data['ts']} · duración {data['duration_s']} s\n"
        f"- Commit: `{sha[:12]}`{' (con cambios sin commitear)' if dirty else ''}\n"
        f"- Comando: `{cmd_str}`\n"
        f"- Código de salida: **{exit_code}**\n\n"
        f"~~~~text\n{out}\n~~~~\n"
        f"<!-- ASDD-EVIDENCE:DATA {json.dumps(data, ensure_ascii=False)} -->\n"
        "<!-- ASDD-EVIDENCE:END -->\n"
    )
    path = DOCS / "verifications" / feature / f"{task}.md"
    ensure_file(path, task, feature)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(block)

    if data["cmd_masked"]:
        print("[ASDD] ⚠ El comando contenía secretos y se han enmascarado. Usa variables de entorno: "
              "la CI no puede reejecutar un comando enmascarado (tareas 'auto').", file=sys.stderr)
    print(out)
    print(f"\n[ASDD] {estado} · exit {exit_code} · evidencia añadida a {path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
