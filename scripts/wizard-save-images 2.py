"""Извлекает все base64 изображения из JSONL транскрипта текущей сессии.

Использование:
    python scripts/wizard-save-images.py --dst <папка> [--session <session_id>] [--prefix ref]

Находит последний JSONL текущей сессии в ~/.claude/projects/<project>/,
извлекает все image-блоки из user-сообщений, сохраняет как ref-01.jpg, ref-02.jpg, ...

Возвращает JSON-список сохранённых файлов в stdout.
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import sys
from pathlib import Path


CLAUDE_PROJECTS = Path.home() / ".claude" / "projects" / "d--AI-TEAMS-landing-system"


def find_session_jsonl(session_id: str | None) -> Path | None:
    if session_id:
        candidate = CLAUDE_PROJECTS / f"{session_id}.jsonl"
        return candidate if candidate.exists() else None
    files = [Path(f) for f in glob.glob(str(CLAUDE_PROJECTS / "*.jsonl"))]
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def extract_images(jsonl_path: Path, dst: Path, prefix: str) -> list[str]:
    dst.mkdir(parents=True, exist_ok=True)
    saved = []
    idx = 0
    with open(jsonl_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = obj.get("message", {})
            if msg.get("role") != "user":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "image":
                    continue
                src = block.get("source", {})
                if src.get("type") != "base64":
                    continue
                data = src.get("data", "")
                media_type = src.get("media_type", "image/jpeg")
                ext = "jpg" if "jpeg" in media_type else "png"
                fname = f"{prefix}-{idx + 1:02d}.{ext}"
                fpath = dst / fname
                with open(fpath, "wb") as out:
                    out.write(base64.b64decode(data))
                saved.append(fname)
                idx += 1
    return saved


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Save chat images to disk")
    p.add_argument("--dst", required=True, help="Destination folder")
    p.add_argument("--session", default=None, help="Session ID (default: latest)")
    p.add_argument("--prefix", default="ref", help="File prefix (default: ref)")
    args = p.parse_args(argv[1:])

    jsonl = find_session_jsonl(args.session)
    if not jsonl:
        print(json.dumps({"error": "session jsonl not found"}))
        return 1

    saved = extract_images(jsonl, Path(args.dst), args.prefix)
    print(json.dumps({"saved": saved, "count": len(saved), "source": str(jsonl)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
