#!/usr/bin/env python3
"""SessionStart hook: печатает wiki/index + memory index в stdout.

Claude Code инжектит вывод как system context.

Логика:
1. cwd = текущая папка сессии (передаётся через stdin JSON).
2. Если cwd внутри landing-system/ → читать landing-system/wiki/index.md.
3. Если cwd похож на ~/Lendings/<slug>/ → читать <slug>/wiki/index.md + последний daily log.
4. Если оба пути актуальны (например работаем в landing-system над проектом)
   → инжектить ОБА индекса.

Скрипт быстрый (<1 сек), без сетевых вызовов.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


LANDING_SYSTEM = Path(__file__).resolve().parents[2]


def _read_or_empty(p: Path, max_chars: int = 8000) -> str:
    if not p.exists():
        return ""
    try:
        text = p.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[...обрезано]"
        return text
    except OSError:
        return ""


def _detect_project_slug(cwd: Path) -> str | None:
    """Если cwd внутри ~/Lendings/<slug>/ — вернуть slug."""
    lendings = Path.home() / "Lendings"
    try:
        rel = cwd.resolve().relative_to(lendings)
    except ValueError:
        return None
    parts = rel.parts
    return parts[0] if parts else None


def _latest_daily(memory_dir: Path) -> str:
    """Читает последний файл из memory/daily/."""
    daily = memory_dir / "daily"
    if not daily.exists():
        return ""
    files = sorted(daily.glob("*.md"))
    if not files:
        return ""
    return _read_or_empty(files[-1], max_chars=4000)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    cwd_str = payload.get("cwd") or str(Path.cwd())
    cwd = Path(cwd_str)

    chunks: list[str] = []

    # Системный wiki — если работаем в landing-system или его дочерней папке
    try:
        cwd.resolve().relative_to(LANDING_SYSTEM)
        sys_index = LANDING_SYSTEM / "wiki" / "index.md"
        text = _read_or_empty(sys_index)
        if text:
            chunks.append(f"<system_wiki_index>\n{text}\n</system_wiki_index>")
    except ValueError:
        pass

    # Проектный wiki — если работаем в ~/Lendings/<slug>/
    slug = _detect_project_slug(cwd)
    if slug:
        project = Path.home() / "Lendings" / slug
        proj_index = _read_or_empty(project / "wiki" / "index.md")
        if proj_index:
            chunks.append(f"<project_wiki_index project=\"{slug}\">\n{proj_index}\n</project_wiki_index>")
        memory_recent = _latest_daily(project / "memory")
        if memory_recent:
            chunks.append(f"<project_recent_memory project=\"{slug}\">\n{memory_recent}\n</project_recent_memory>")

    if chunks:
        print("\n\n".join(chunks))

    return 0


if __name__ == "__main__":
    sys.exit(main())
