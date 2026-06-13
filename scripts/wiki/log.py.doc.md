---
type: script
name: log
language: python
sources: ["scripts/wiki/log.py"]
updated: 2026-05-18
---

# log.py

CLI для записи launch-событий в logs/wiki-usage.jsonl.

Использование:
    python -m scripts.wiki.log --type stage_start --stage 04_brand --project <slug>
    python -m scripts.wiki.log --type agent_call --agent <slug> --stage 04
    python -m scripts.wiki.log --type skill_call --skill <slug> --stage 04

--session-id необязателен: берётся из $CLAUDE_SESSION_ID, иначе .wiki-run-id, иначе "unknown".

## Источник

- `scripts/wiki/log.py`
