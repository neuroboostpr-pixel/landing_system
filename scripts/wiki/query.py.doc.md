---
type: script
name: query
language: python
sources: ["scripts/wiki/query.py"]
updated: 2026-05-18
---

# query.py

Pure-Python filter over wiki/index.yaml.

CLI:
    python -m scripts.wiki.query --stage=08 --type=agent
    python -m scripts.wiki.query --tag=wordpress
    python -m scripts.wiki.query --slug=block-composer
    python -m scripts.wiki.query --trigger=landing-build
    python -m scripts.wiki.query --grep=gutenberg
    python -m scripts.wiki.query --slug=X --format=cards

Formats: compact (default), cards, slugs, json.
No SDK calls. <100ms for any query.

## Источник

- `scripts/wiki/query.py`
