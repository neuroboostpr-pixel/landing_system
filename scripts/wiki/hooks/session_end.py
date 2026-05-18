#!/usr/bin/env python3
"""SessionEnd hook: спавнит detached flush.py в фоне.

Не блокирует завершение сессии. flush сам разберётся с транскриптом.
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

    # Detach: спавним процесс, не ждём завершения
    subprocess.Popen(
        ["python3", str(FLUSH), "--transcript", transcript, "--cwd", cwd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
