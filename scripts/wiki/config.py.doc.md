---
type: script
name: config
language: python
sources: ["scripts/wiki/config.py"]
updated: 2026-05-18
---

# config.py

Конфигурация wiki-компайлера.

Определяет источники для трёх режимов компиляции:
- system: компилит landing-system/{agents,skills,commands,template,docs/standards}
- project-graph: компилит артефакты конкретного лендинга (~/Lendings/<slug>/)
- conversations: компилит daily logs сессий в knowledge базу (coleam00 default)

## Источник

- `scripts/wiki/config.py`
