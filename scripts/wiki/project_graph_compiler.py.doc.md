---
type: script
name: project_graph_compiler
language: python
sources: ["scripts/wiki/project_graph_compiler.py"]
updated: 2026-05-18
---

# project_graph_compiler.py

Компилит артефакты проекта-лендинга в <project>/wiki/.

Все артефакты, включая index.md, генерятся БЕЗ SDK (парсинг yaml/json/html →
markdown). SDK раньше звался для index.md, но выдавал мусор и путал имя
проекта — заменён на детерминированный stub.

## Источник

- `scripts/wiki/project_graph_compiler.py`
