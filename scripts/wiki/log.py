"""CLI для записи launch-событий в logs/wiki-usage.jsonl.

Использование:
    python -m scripts.wiki.log --type stage_start --stage 04_brand --project <slug>
    python -m scripts.wiki.log --type agent_call --agent <slug> --stage 04
    python -m scripts.wiki.log --type skill_call --skill <slug> --stage 04

--session-id необязателен: берётся из $CLAUDE_SESSION_ID, иначе "unknown".
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from scripts.wiki import routing_log


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Log wiki launch event")
    p.add_argument("--type", required=True,
                   choices=["stage_start", "agent_call", "skill_call"])
    p.add_argument("--stage", default="")
    p.add_argument("--project", default="")
    p.add_argument("--agent", default="")
    p.add_argument("--skill", default="")
    p.add_argument("--session-id", default="")
    args = p.parse_args(argv[1:])

    session_id = args.session_id or os.environ.get("CLAUDE_SESSION_ID", "unknown")

    # Support WIKI_LOG_PATH env override (used in tests)
    wiki_log_path = os.environ.get("WIKI_LOG_PATH")
    if wiki_log_path:
        routing_log.LOG_PATH = Path(wiki_log_path)

    try:
        if args.type == "stage_start":
            routing_log.log_stage_start(session_id, args.stage, args.project)
        elif args.type == "agent_call":
            routing_log.log_agent_call(session_id, args.agent, args.stage)
        elif args.type == "skill_call":
            routing_log.log_skill_call(session_id, args.skill, args.stage)
    except Exception as e:
        print(f"[wiki log] failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
