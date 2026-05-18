---
type: script
name: flush
language: python
sources: ["scripts/wiki/flush.py"]
updated: 2026-05-18
---

# flush.py

Извлекает уроки из транскрипта Claude Code сессии через SDK.

Запускается detached из SessionEnd / PreCompact хуков.

Использование:
  python3 flush.py --transcript <path> --cwd <cwd> [--mode session-end|pre-compact]

Логика:
1. Читает transcript JSONL.
2. Определяет target memory/ по cwd (landing-system vs ~/Lendings/<slug>).
3. Зовёт SDK с промптом flush.md → markdown с уроками.
4. Аппендит в memory/daily/YYYY-MM-DD.md.

## Источник

- `scripts/wiki/flush.py`
