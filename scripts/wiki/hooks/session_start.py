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


def _read_model_from_settings() -> str:
    """Читает модель из ~/.claude/settings.json — fallback когда CLAUDE_CODE_MODEL не задан."""
    try:
        settings_path = Path.home() / ".claude" / "settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        return data.get("model", "")
    except Exception:
        return ""


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
    """Preflight + 50-token hint + stats строка.

    Только если CWD находится внутри LANDING_SYSTEM.
    """
    import os
    try:
        cwd.resolve().relative_to(LANDING_SYSTEM)
    except ValueError:
        return ""

    index_yaml = LANDING_SYSTEM / "wiki" / "index.yaml"
    if not index_yaml.exists():
        return ""

    # Preflight checks
    if not os.environ.get("WIKI_PREFLIGHT_SKIP"):
        try:
            sys.path.insert(0, str(LANDING_SYSTEM))
            from scripts.wiki.preflight import run_preflight
            failures = [r for r in run_preflight() if not r.ok]
            if failures:
                lines = ["⚠️  Wiki preflight failed:"]
                for f in failures:
                    lines.append(f"  - {f.message}")
                    lines.append(f"    Fix: {f.fix_hint}")
                lines.append("Set WIKI_PREFLIGHT_SKIP=1 to bypass and continue without logging.")
                return "<wiki_runtime>\n" + "\n".join(lines) + "\n</wiki_runtime>"
        except Exception:
            pass  # если preflight сам упал — не блокируем

    try:
        import yaml
        data = yaml.safe_load(index_yaml.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    total = (data.get("counts") or {}).get("total", "?")

    # Stats строка
    stats_line = "Wiki routing (7d): no data yet"
    try:
        from scripts.wiki import routing_log, stats as wiki_stats
        events = routing_log.read_events(since_days=7)
        if events:
            s = wiki_stats.compute_stats(events)
            stats_line = wiki_stats.one_line_summary(s)
    except Exception:
        pass

    return (
        "<wiki_runtime>\n"
        f"Landing-system wiki: {total} concepts indexed at wiki/index.yaml.\n"
        "Query: python -m scripts.wiki.query --stage=N --type=T --tag=X --slug=Y\n"
        "Read card: cat wiki/concepts/<dir>/<slug>.md\n"
        f"{stats_line}\n"
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
            import os
            from scripts.lib.paths import project_dir
            from scripts.wiki import routing_log

            session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
            model = os.environ.get("CLAUDE_CODE_MODEL", "") or _read_model_from_settings()

            project = project_dir(slug)
            proj_index_path = project / "wiki" / "index.md"
            proj_index = _read_or_empty(proj_index_path)
            if proj_index:
                chunks.append(
                    f"<project_wiki_index project=\"{slug}\">\n{proj_index}\n</project_wiki_index>"
                )
                try:
                    routing_log.log_context_inject(
                        session_id=session_id,
                        source_category="session_start",
                        source_label="project_wiki",
                        est_tokens=int(len(proj_index) / 3.5),
                        can_be_wiki=False,
                        path=str(proj_index_path),
                        model=model,
                    )
                except Exception:
                    pass

            memory_path = project / "memory"
            memory_recent = _latest_daily(memory_path)
            if memory_recent:
                chunks.append(
                    f"<project_recent_memory project=\"{slug}\">\n{memory_recent}\n</project_recent_memory>"
                )
                try:
                    latest_file = sorted((memory_path / "daily").glob("*.md"))[-1]
                    routing_log.log_context_inject(
                        session_id=session_id,
                        source_category="session_start",
                        source_label="project_memory",
                        est_tokens=int(len(memory_recent) / 3.5),
                        can_be_wiki=False,
                        path=str(latest_file),
                        model=model,
                    )
                except Exception:
                    pass
        except ImportError:
            pass

    if chunks:
        print("\n\n".join(chunks))

    return 0


if __name__ == "__main__":
    sys.exit(main())
