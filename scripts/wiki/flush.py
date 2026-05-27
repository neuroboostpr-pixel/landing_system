# scripts/wiki/flush.py
"""Извлекает уроки из транскрипта Claude Code сессии через SDK.

Запускается detached из SessionEnd / PreCompact хуков.

Использование:
  python3 flush.py --transcript <path> --cwd <cwd> [--mode session-end|pre-compact]

Логика:
1. Читает transcript JSONL.
2. Определяет target memory/ по cwd (landing-system vs ~/Lendings/<slug>).
3. Зовёт SDK с промптом flush.md → markdown с уроками.
4. Аппендит в memory/daily/YYYY-MM-DD.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from scripts.wiki import sdk_client

PROMPTS_DIR = Path(__file__).parent / "prompts"
LANDING_SYSTEM = Path(__file__).resolve().parents[1]


def read_transcript(path: Path) -> list[dict]:
    """JSONL → list[dict]. Игнорирует битые строки."""
    msgs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msgs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return msgs


def format_transcript(msgs: list[dict]) -> str:
    """Plain text для SDK: 'role: content' с переносами."""
    lines = []
    for m in msgs:
        role = m.get("role", "?")
        content = m.get("content", "")
        if isinstance(content, list):
            # Claude Code Format: list of blocks
            content = " ".join(
                b.get("text", "") for b in content if isinstance(b, dict)
            )
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def _detect_memory_dir(cwd: Path) -> Path:
    """По cwd определяет куда писать memory/."""
    from scripts.lib.paths import LANDINGS_ROOT
    try:
        rel = cwd.resolve().relative_to(LANDINGS_ROOT)
        slug = rel.parts[0]
        return LANDINGS_ROOT / slug / "memory"
    except (ValueError, IndexError):
        pass
    # Fallback — landing-system/memory/
    return LANDING_SYSTEM / "memory"


def flush_transcript(transcript_path: Path, memory_dir: Path = None, cwd: Path = None) -> None:
    """Извлекает уроки и аппендит в daily log."""
    if memory_dir is None:
        memory_dir = _detect_memory_dir(cwd or Path.cwd())

    msgs = read_transcript(transcript_path)
    if not msgs:
        return

    text = format_transcript(msgs)
    # Ограничим вход (последние ~30 сообщений)
    if len(msgs) > 30:
        text = format_transcript(msgs[-30:])

    prompt = (PROMPTS_DIR / "flush.md").read_text(encoding="utf-8")
    try:
        lessons = sdk_client.generate(system=prompt, user=text)
    except sdk_client.SDKError:
        return  # silent — мы в фоне, не пугаем юзера

    if lessons.strip() in ("_(пусто)_", "_пусто_", ""):
        return

    daily = memory_dir / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    today_file = daily / f"{date.today().isoformat()}.md"

    header = f"\n## flush @ {date.today().isoformat()}\n\n"
    with today_file.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(lessons)
        f.write("\n")

    # Анализ routing: детектим direct reads (bypass wiki)
    try:
        from pathlib import Path as _Path
        from scripts.wiki import transcript_parser, routing_log
        tool_calls = transcript_parser.extract_tool_calls(transcript_path)
        session_id = transcript_parser.get_session_id(transcript_path)

        queried_slugs: set[str] = set()
        queried_stages: set[str] = set()
        for tc in tool_calls:
            if transcript_parser.is_wiki_query(tc):
                queried_slugs.update(transcript_parser.extract_query_slugs(tc))
                stage = transcript_parser.extract_query_stage(tc)
                if stage:
                    queried_stages.add(stage)

        for tc in tool_calls:
            if transcript_parser.is_source_read(tc):
                path = tc.input_params.get("file_path", "")
                slug = _Path(path).stem
                had_prior = slug in queried_slugs or bool(queried_stages)
                est = routing_log.estimate_tokens_file(_Path(path))
                routing_log.log_direct_read(session_id, path, est, had_prior)
    except Exception:
        pass  # silent — мы в фоне


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--cwd", default="")
    parser.add_argument("--mode", default="session-end")
    args = parser.parse_args()

    transcript = Path(args.transcript)
    if not transcript.exists():
        return 1
    cwd = Path(args.cwd) if args.cwd else Path.cwd()

    flush_transcript(transcript_path=transcript, cwd=cwd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
