---
type: script
name: session_start
language: python
sources: ["scripts/wiki/hooks/session_start.py"]
updated: 2026-05-18
---

# session_start.py

SessionStart hook: печатает компактный wiki hint (~50 tokens).

Old behavior (deprecated): инжектил полный wiki/index.md (~3K tokens) на каждой
сессии. New behavior: печатает только пойнтер на wiki/index.yaml + команду
запроса. Orchestrator решает САМ, когда подгружать карточки.

Сохраняет проектный wiki (~/Lendings/<slug>/wiki/index.md) и recent memory —
они контекстные и компактные.

## Источник

- `scripts/wiki/hooks/session_start.py`
