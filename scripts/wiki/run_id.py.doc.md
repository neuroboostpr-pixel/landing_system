---
type: script
name: run_id
language: python
sources: ["scripts/wiki/run_id.py"]
updated: 2026-05-18
---

# run_id.py

Управление run_id для wiki routing корреляции.

run_id — идентификатор одного рабочего запуска (один /landing-go или ручной старт).
Хранится в .wiki-run-id в корне репо. Новый запуск = reset().

## Источник

- `scripts/wiki/run_id.py`
