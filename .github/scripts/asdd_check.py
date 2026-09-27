#!/usr/bin/env python3
"""ASDD check — validación de PRs en CI (vale para cualquier agente).

Con label `asdd-bypass`: exige '## Motivo del bypass' con contenido. Nada más.

Sin label, si el PR toca algo fuera de asdd_docs/, su descripción debe referenciar planes que:
  * estén COMPLETADO y aprobados, con su SPEC aprobado y con el MISMO nombre que el plan;
  * tengan todas las tareas en [x] y todos los archivos modificados declarados;
  * tengan en asdd_docs/verifications/<plan>/ un .md por tarea más RESUMEN.md, donde cada .md:
      - explica "Qué se hizo" y "Por qué cumple" (no vacíos) y tiene "Veredicto: APROBADA";
      - según el tipo de verificación declarado en el plan:
          local  → última evidencia de asdd-verify íntegra, con exit 0 y commit de la rama;
          auto   → lo mismo y, además, la CI vuelve a ejecutar el comando y debe salir 0;
          manual → "**Verificado por el responsable:** [x]".

Variables de entorno: PR_BODY, PR_LABELS (JSON), BASE_SHA, HEAD_SHA.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

BYPASS_LABEL = "asdd-bypass"
DOCS_DIR = "asdd_docs"
AUTO_TIMEOUT = 900

APPROVED_RE = re.compile(r"\*\*Aprobado:\*\*\s*\[[xX]\]")
STATE_RE = re.compile(r"\*\*Estado:\*\*\s*([A-ZÁÉÍÓÚ ]+)")
SPEC_REF_RE = re.compile(r"(asdd_docs/specs/[\w./-]+\.md)")
PLAN_REF_RE = re.compile(r"(asdd_docs/plans/[\w./-]+\.md)")
TASK_HEAD_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*\*\*(T\d+|T_FINAL)\b")
TYPE_RE = re.compile(r"Tipo verificaci[oó]n\s*:\s*`?(auto|local|manual)`?", re.I)
BACKTICK_RE = re.compile(r"`([^`]+)`")
BYPASS_SECTION_RE = re.compile(r"^##\s*Motivo del bypass\s*$(.*?)(?=^##\s|\Z)", re.M | re.S | re.I)
EVIDENCE_RE = re.compile(r"<!-- ASDD-EVIDENCE:BEGIN -->(.*?)<!-- ASDD-EVIDENCE:END -->", re.S)
EVIDENCE_DATA_RE = re.compile(r"<!-- ASDD-EVIDENCE:DATA (\{.*?\}) -->")
EVIDENCE_OUT_RE = re.compile(r"~~~~text\n(.*?)\n~~~~", re.S)
MANUAL_OK_RE = re.compile(r"\*\*Verificado por el responsable:\*\*\s*\[[xX]\]")
VERDICT_OK_RE = re.compile(r"Veredicto:\s*\**APROBADA", re.I)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def section(text: str, title: str) -> str:
    m = re.search(rf"^##\s*{re.escape(title)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    if not m:
        return ""
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S)
    body = "\n".join(l for l in body.splitlines() if not re.fullmatch(r"\s*[-*]?\s*\[[^\]]*\]\s*", l))
    return body.strip()


def declared_paths(plan_text: str) -> set[str]:
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


def parse_tasks(plan_text: str) -> list[dict]:
    tasks: list[dict] = []
    current: dict | None = None
    for line in plan_text.splitlines():
        head = TASK_HEAD_RE.match(line)
        if head:
            current = {"id": head.group(2), "done": head.group(1) != " ", "type": "local"}
            tasks.append(current)
            continue
        if line.lstrip().startswith("#"):
            current = None
        elif current:
            m = TYPE_RE.search(line)
            if m:
                current["type"] = m.group(1).lower()
    return tasks


def last_evidence(text: str) -> tuple[dict | None, str]:
    blocks = EVIDENCE_RE.findall(text)
    if not blocks:
        return None, "no tiene evidencia de asdd-verify"
    block = blocks[-1]
    data_m, out_m = EVIDENCE_DATA_RE.search(block), EVIDENCE_OUT_RE.search(block)
    if not data_m or not out_m:
        return None, "la última evidencia está mal formada (¿editada a mano?)"
    try:
        data = json.loads(data_m.group(1))
    except ValueError:
        return None, "la última evidencia tiene datos ilegibles (¿editada a mano?)"
    if hashlib.sha256(out_m.group(1).encode("utf-8")).hexdigest() != data.get("out_sha256"):
        return None, "la salida de la última evidencia no coincide con su hash (editada a mano)"
    return data, ""


def check_evidence(label: str, data: dict, head: str) -> list[str]:
    errors = []
    if data.get("exit") != 0:
        errors.append(f"{label}: la última verificación terminó con exit {data.get('exit')}.")
    sha = data.get("sha", "")
    if sha == "sin-commit" or git("merge-base", "--is-ancestor", sha, head).returncode != 0:
        errors.append(f"{label}: la evidencia se generó sobre un commit ({sha[:12]}) que no pertenece a esta rama.")
    return errors


def rerun(label: str, cmd: str) -> list[str]:
    print(f"\n▶ Reejecutando {label}: {cmd}")
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=AUTO_TIMEOUT)
    except FileNotFoundError:
        return [f"{label}: la CI no encuentra el comando '{cmd}'. Añade su instalación al workflow."]
    except subprocess.TimeoutExpired:
        return [f"{label}: timeout en la CI tras {AUTO_TIMEOUT}s."]
    print((proc.stdout + proc.stderr)[-4000:])
    if proc.returncode != 0:
        return [f"{label}: reejecutada en la CI terminó con exit {proc.returncode} (en local dio 0)."]
    print(f"✔ {label}: OK en la CI")
    return []


def check_plan(plan_path: str, head: str) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    plan = Path(plan_path)
    if not plan.exists():
        return [f"El plan referenciado no existe: {plan_path}"], set()
    text = plan.read_text(encoding="utf-8")
    state_m = STATE_RE.search(text)
    state = state_m.group(1).strip() if state_m else ""
    if state != "COMPLETADO":
        errors.append(f"{plan_path}: estado '{state or '?'}', debe ser COMPLETADO.")
    if not APPROVED_RE.search(text):
        errors.append(f"{plan_path}: no está aprobado (**Aprobado:** [x]).")

    spec_m = SPEC_REF_RE.search(text)
    if not spec_m:
        errors.append(f"{plan_path}: no referencia ningún SPEC.")
    else:
        spec = Path(spec_m.group(1))
        if spec.stem != plan.stem:
            errors.append(f"{plan_path}: el SPEC ({spec.name}) debe tener el mismo nombre que el plan.")
        if not spec.exists():
            errors.append(f"{plan_path}: el SPEC {spec} no existe.")
        elif not APPROVED_RE.search(spec.read_text(encoding="utf-8")):
            errors.append(f"{spec}: el SPEC no está aprobado.")

    tasks = parse_tasks(text)
    if not tasks:
        errors.append(f"{plan_path}: no se encontraron tareas (formato '- [ ] **T01 — ...**').")
    vdir = Path(DOCS_DIR) / "verifications" / plan.stem
    for task in tasks:
        label = f"{vdir}/{task['id']}.md"
        if not task["done"]:
            errors.append(f"{plan_path}: la tarea {task['id']} no está marcada como hecha.")
        vfile = vdir / f"{task['id']}.md"
        if not vfile.exists():
            errors.append(f"Falta {label}")
            continue
        vtext = vfile.read_text(encoding="utf-8")
        if len(section(vtext, "Qué se hizo")) < 15:
            errors.append(f"{label}: la sección 'Qué se hizo' está vacía.")
        if len(section(vtext, "Por qué cumple")) < 15:
            errors.append(f"{label}: la sección 'Por qué cumple' está vacía.")
        if not VERDICT_OK_RE.search(vtext):
            errors.append(f"{label}: la revisión no tiene 'Veredicto: APROBADA'.")
        if task["type"] == "manual":
            if not MANUAL_OK_RE.search(vtext):
                errors.append(f"{label}: verificación manual sin '**Verificado por el responsable:** [x]'.")
            continue
        data, problem = last_evidence(vtext)
        if not data:
            errors.append(f"{label}: {problem}.")
            continue
        ev_errors = check_evidence(label, data, head)
        errors.extend(ev_errors)
        if task["type"] == "auto" and not ev_errors:
            if data.get("cmd_masked"):
                errors.append(f"{label}: el comando contiene secretos enmascarados; la CI no puede "
                              "reejecutarlo. Usa variables de entorno y secrets de GitHub.")
            else:
                errors.extend(rerun(label, data["cmd"]))
    if not (vdir / "RESUMEN.md").exists():
        errors.append(f"Falta {vdir}/RESUMEN.md")
    return errors, declared_paths(text)


def fail(errors: list[str]) -> None:
    print("\n❌ ASDD check falló:\n")
    for err in errors:
        print(f"  - {err}")
    print("\nConsulta AGENTS.md y asdd_docs/references/.")
    sys.exit(1)


def main() -> None:
    body = os.environ.get("PR_BODY") or ""
    labels = set(json.loads(os.environ.get("PR_LABELS") or "[]"))
    base, head = os.environ["BASE_SHA"], os.environ["HEAD_SHA"]

    if BYPASS_LABEL in labels:
        m = BYPASS_SECTION_RE.search(body)
        content = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip() if m else ""
        if len(content) < 10:
            fail([f"El PR tiene el label '{BYPASS_LABEL}' pero '## Motivo del bypass' falta o está vacía."])
        print(f"⚠️  PR con '{BYPASS_LABEL}' y motivo documentado. Check ASDD omitido.")
        return

    diff = git("diff", "--name-only", "--diff-filter=ACMRD", f"{base}...{head}")
    changed = [l.strip() for l in diff.stdout.splitlines() if l.strip()]
    code_files = [f for f in changed if not f.startswith(f"{DOCS_DIR}/")]
    if not code_files:
        print("✅ Solo cambios en asdd_docs/ (specs, planes o verificaciones). OK.")
        return

    plan_refs = sorted(set(PLAN_REF_RE.findall(body)))
    if not plan_refs:
        fail(["El PR modifica código pero su descripción no referencia ningún plan (asdd_docs/plans/…md)."])

    errors: list[str] = []
    declared: set[str] = set()
    for ref in plan_refs:
        plan_errors, paths = check_plan(ref, head)
        errors.extend(plan_errors)
        declared |= paths
    for f in code_files:
        if not any(path_matches(f, p) for p in declared):
            errors.append(f"'{f}' se modificó pero no está declarado en ningún plan referenciado.")
    if errors:
        fail(errors)
    print(f"\n✅ ASDD OK: {len(code_files)} archivo(s) cubiertos por {', '.join(plan_refs)}.")


if __name__ == "__main__":
    main()
