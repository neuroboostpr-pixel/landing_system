---
type: script
name: preflight
language: python
sources: ["scripts/wiki/preflight.py"]
updated: 2026-05-18
---

# preflight.py

Preflight checks для wiki routing системы.

Вызывается из session_start.py перед логированием.
При failures — блокирует запуск и предлагает fix_hint.
Переопределить через WIKI_PREFLIGHT_SKIP=1.

## Источник

- `scripts/wiki/preflight.py`
