#!/usr/bin/env python3
"""ASDD log — hook PostToolUse de Claude Code.

Traza automática de cada acción del agente (entrada y extracto de la respuesta) en .asdd/logs/YYYY-MM-DD.jsonl.
No la escribe el agente y no se versiona (está en .gitignore).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_LEN = 500


def summarize(tool_input: dict) -> dict:
    keys = ("file_path", "notebook_path", "command", "pattern", "path", "url", "description")
    out = {}
    for key in keys:
        if key in tool_input:
            out[key] = str(tool_input[key])[:MAX_LEN]
    return out


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    now = datetime.now(timezone.utc)
    entry = {
        "ts": now.isoformat(timespec="seconds"),
        "session": payload.get("session_id"),
        "tool": payload.get("tool_name"),
        "input": summarize(payload.get("tool_input") or {}),
        "response": str(payload.get("tool_response") or "")[:MAX_LEN],
    }
    log_dir = root / ".asdd" / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / f"{now:%Y-%m-%d}.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


if __name__ == "__main__":
    main()
