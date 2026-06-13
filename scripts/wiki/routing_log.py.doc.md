---
type: script
name: routing_log
language: python
sources: ["scripts/wiki/routing_log.py"]
updated: 2026-05-18
---

# routing_log.py

Запись и чтение logs/wiki-usage.jsonl.

Единственная точка логирования wiki routing событий.
LOG_PATH можно переопределить через monkeypatch в тестах.

## Источник

- `scripts/wiki/routing_log.py`
