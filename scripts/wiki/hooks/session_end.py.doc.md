---
type: script
name: session_end
language: python
sources: ["scripts/wiki/hooks/session_end.py"]
updated: 2026-05-18
---

# session_end.py

SessionEnd hook: спавнит detached flush.py в фоне.

Не блокирует завершение сессии. flush сам разберётся с транскриптом.

## Источник

- `scripts/wiki/hooks/session_end.py`
