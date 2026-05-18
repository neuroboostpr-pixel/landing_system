---
type: script
name: pre_compact
language: python
sources: ["scripts/wiki/hooks/pre_compact.py"]
updated: 2026-05-18
---

# pre_compact.py

PreCompact hook: страховка перед авто-сжатием контекста.

Логика та же что у session_end — спавним flush detached.
Это сохраняет уроки из текущей сессии ДО того как Claude её сожмёт.

## Источник

- `scripts/wiki/hooks/pre_compact.py`
