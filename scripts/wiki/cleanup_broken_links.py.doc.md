---
type: script
name: cleanup_broken_links
language: python
sources: ["scripts/wiki/cleanup_broken_links.py"]
updated: 2026-05-18
---

# cleanup_broken_links.py

Удаляет [[wikilinks]] на несуществующие концепты.

[[gate-check]] → gate-check (текст остаётся, ссылка снимается)
[[landing-orchestrator]] → [[landing-orchestrator]] (живая ссылка остаётся)

Запуск:
  python3 -m scripts.wiki.cleanup_broken_links --wiki wiki [--dry-run]

## Источник

- `scripts/wiki/cleanup_broken_links.py`
