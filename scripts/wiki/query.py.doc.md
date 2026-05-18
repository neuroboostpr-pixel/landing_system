---
type: script
name: query
language: python
sources: ["scripts/wiki/query.py"]
updated: 2026-05-18
---

# query.py

Запросы к wiki из CLI.

Использование:
  python -m scripts.wiki.query "что делает landing-orchestrator"
  python -m scripts.wiki.query "..." --project=dubai-avto-liza
  python -m scripts.wiki.query "..." --file-back  # сохраняет ответ в memory/qa/

## Источник

- `scripts/wiki/query.py`
