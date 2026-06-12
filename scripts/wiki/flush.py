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


def _extract_script_label(command: str) -> str:
    """Извлекает имя скрипта из команды bash (напр. 'landing-rename.sh')."""
    import re
    m = re.search(r'([\w\-]+\.sh)', command)
    if m:
        return m.group(1)
    return command[:40].strip()


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

    # Анализ routing: детектим direct reads (bypass wiki) — независимо от SDK
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
                routing_log.log_direct_read(
                    session_id, path, est, had_prior,
                    model=tc.model, thinking_tokens=tc.thinking_tokens,
                    speed=tc.speed, entrypoint=tc.entrypoint,
                    is_sidechain=tc.is_sidechain,
                )

        # Block A: framework_load — Skill и Command tool invocations
        SKILL_TOOL_NAMES = {"Skill", "skill", "mcp__claude_ai__skill"}
        COMMAND_TOOL_NAMES = {"mcp__claude_ai__slash_command"}
        for tc in tool_calls:
            if tc.tool_name in SKILL_TOOL_NAMES:
                skill_name = tc.input_params.get("skill", "")
                if not skill_name:
                    continue
                skill_file = _Path(LANDING_SYSTEM) / "skills" / skill_name / "SKILL.md"
                if skill_file.exists():
                    routing_log.log_context_inject(
                        session_id, "framework_load", f"skill:{skill_name}",
                        est_tokens=routing_log.estimate_tokens_file(skill_file),
                        can_be_wiki=False,
                        path=str(skill_file),
                        model=tc.model,
                    )
            elif tc.tool_name in COMMAND_TOOL_NAMES:
                cmd_name = tc.input_params.get("command", "").lstrip("/")
                if not cmd_name:
                    continue
                cmd_file = _Path(LANDING_SYSTEM) / ".claude" / "commands" / f"{cmd_name}.md"
                if cmd_file.exists():
                    routing_log.log_context_inject(
                        session_id, "framework_load", f"command:{cmd_name}",
                        est_tokens=routing_log.estimate_tokens_file(cmd_file),
                        can_be_wiki=False,
                        path=str(cmd_file),
                        model=tc.model,
                    )

        # Block B: bash_stdout — stdout из Bash tool calls с большим выводом
        TOKEN_THRESHOLD = 100
        for tc in tool_calls:
            if tc.tool_name != "Bash":
                continue
            output = tc.output or ""
            est = int(len(output) / 3.5)
            if est <= TOKEN_THRESHOLD:
                continue
            cmd = tc.input_params.get("command", "")
            label = _extract_script_label(cmd)
            routing_log.log_context_inject(
                session_id, "bash_stdout", label,
                est_tokens=est,
                can_be_wiki=False,
                model=tc.model,
            )
    except Exception:
        pass  # silent — мы в фоне

    prompt = (PROMPTS_DIR / "flush.md").read_text(encoding="utf-8")
    try:
        lessons = sdk_client.generate(system=prompt, user=text)
    except sdk_client.SDKError:
        return  # silent — мы в фоне, не пугаем юзера

    if lessons.strip() in ("_(пусто)_", "_пусто_", ""):
        _refresh_routing_report()
        return

    daily = memory_dir / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    today_file = daily / f"{date.today().isoformat()}.md"

    header = f"\n## flush @ {date.today().isoformat()}\n\n"
    with today_file.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(lessons)
        f.write("\n")

    _refresh_routing_report()


def _refresh_routing_report() -> None:
    """Пересобирает wiki/routing-report.md из текущего лога. Silent."""
    try:
        from scripts.wiki import routing_log, stats as wiki_stats
        events = routing_log.read_events(since_days=7)
        result = wiki_stats.compute_stats(events)
        md = wiki_stats.generate_report(result, since_days=7)
        report_path = LANDING_SYSTEM / "wiki" / "routing-report.md"
        report_path.write_text(md, encoding="utf-8")
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
