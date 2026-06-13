---
type: script
name: stats 2
language: python
sources: ["scripts/wiki/stats 2.py"]
updated: 2026-05-18
---

# stats 2.py

Агрегация wiki routing событий и генерация отчёта.

CLI:
    python -m scripts.wiki.stats                       # summary в терминал
    python -m scripts.wiki.stats --report              # пишет wiki/routing-report.md
    python -m scripts.wiki.stats --days=30             # за месяц
    python -m scripts.wiki.stats --exact-tokens        # точный подсчёт через Anthropic API (требует ANTHROPIC_API_KEY)

## Источник

- `scripts/wiki/stats 2.py`
