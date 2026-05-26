#!/usr/bin/env python3
"""SessionStart hook: печатает компактный wiki hint (~50 tokens).

Old behavior (deprecated): инжектил полный wiki/index.md (~3K tokens) на каждой
сессии. New behavior: печатает только пойнтер на wiki/index.yaml + команду
запроса. Orchestrator решает САМ, когда подгружать карточки.

Сохраняет проектный wiki (~/Lendings/<slug>/wiki/index.md) и recent memory —
они контекстные и компактные.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LANDING_SYSTEM = Path(__file__).resolve().parents[3]


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


def _system_wiki_hint(cwd: Path) -> str:
    """50-token hint про существование системной wiki + команду запроса.

    Только если CWD находится внутри LANDING_SYSTEM.
    """
    try:
        cwd.resolve().relative_to(LANDING_SYSTEM)
    except ValueError:
        return ""

    index_yaml = LANDING_SYSTEM / "wiki" / "index.yaml"
    if not index_yaml.exists():
        return ""
    try:
        import yaml
        data = yaml.safe_load(index_yaml.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    total = (data.get("counts") or {}).get("total", "?")
    return (
        "<wiki_runtime>\n"
        f"Landing-system wiki: {total} concepts indexed at wiki/index.yaml.\n"
        "Query: python -m scripts.wiki.query --stage=N --type=T --tag=X --slug=Y\n"
        "Read card: cat wiki/concepts/<dir>/<slug>.md\n"
        "</wiki_runtime>"
    )


def _detect_project_slug(cwd: Path) -> str | None:
    try:
        from scripts.lib.paths import LANDINGS_ROOT
        rel = cwd.resolve().relative_to(LANDINGS_ROOT)
        parts = rel.parts
        return parts[0] if parts else None
    except (ValueError, ImportError):
        return None


def _latest_daily(memory_dir: Path) -> str:
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

    # System wiki hint (~50 tokens, only when inside landing-system)
    hint = _system_wiki_hint(cwd)
    if hint:
        chunks.append(hint)

    # Project wiki — full inject (small per-project file, kept as-is)
    slug = _detect_project_slug(cwd)
    if slug:
        try:
            from scripts.lib.paths import project_dir
            project = project_dir(slug)
            proj_index = _read_or_empty(project / "wiki" / "index.md")
            if proj_index:
                chunks.append(
                    f"<project_wiki_index project=\"{slug}\">\n{proj_index}\n</project_wiki_index>"
                )
            memory_recent = _latest_daily(project / "memory")
            if memory_recent:
                chunks.append(
                    f"<project_recent_memory project=\"{slug}\">\n{memory_recent}\n</project_recent_memory>"
                )
        except ImportError:
            pass

    if chunks:
        print("\n\n".join(chunks))

    return 0


if __name__ == "__main__":
    sys.exit(main())
