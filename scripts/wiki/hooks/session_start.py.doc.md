---
type: script
name: session_start
language: python
sources: ["scripts/wiki/hooks/session_start.py"]
updated: 2026-05-18
---

# session_start.py

SessionStart hook: печатает wiki/index + memory index в stdout.

Claude Code инжектит вывод как system context.

Логика:
1. cwd = текущая папка сессии (передаётся через stdin JSON).
2. Если cwd внутри landing-system/ → читать landing-system/wiki/index.md.
3. Если cwd похож на ~/Lendings/<slug>/ → читать <slug>/wiki/index.md + последний daily log.
4. Если оба пути актуальны (например работаем в landing-system над проектом)
   → инжектить ОБА индекса.

Скрипт быстрый (<1 сек), без сетевых вызовов.

## Источник

- `scripts/wiki/hooks/session_start.py`
