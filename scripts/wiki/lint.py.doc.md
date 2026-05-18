---
type: script
name: lint
language: python
sources: ["scripts/wiki/lint.py"]
updated: 2026-05-18
---

# lint.py

Линтер wiki — 7 проверок здоровья.

Структурные проверки (бесплатно):
1. Битые wikilinks
2. Сирые страницы
3. Некомпилированные daily logs
4. Устаревшие концепты
5. Пропущенные обратные ссылки
6. Пустые концепты

LLM-проверка (платно, по флагу --llm-check):
7. Противоречия между концептами

## Источник

- `scripts/wiki/lint.py`
