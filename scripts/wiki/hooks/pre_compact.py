#!/usr/bin/env python3
"""PreCompact hook: страховка перед авто-сжатием контекста.

Логика та же что у session_end — спавним flush detached.
Это сохраняет уроки из текущей сессии ДО того как Claude её сожмёт.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
FLUSH = HERE.parent / "flush.py"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    transcript = payload.get("transcript_path", "")
    cwd = payload.get("cwd", str(Path.cwd()))

    if not transcript or not Path(transcript).exists():
        return 0

    subprocess.Popen(
        ["python3", str(FLUSH), "--transcript", transcript, "--cwd", cwd, "--mode", "pre-compact"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
