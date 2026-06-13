---
type: script
name: stages 2
language: python
sources: ["scripts/stages 2.py"]
updated: 2026-05-18
---

# stages 2.py

Единый источник списка этапов (E1). Читает config/stages.yaml.

Usage:
    python3 scripts/stages.py --order    # id по одному в строке
    python3 scripts/stages.py --labels   # id<TAB>label по одному в строке

Как библиотека:
    from scripts.stages import stage_ids, load_stages

## Источник

- `scripts/stages 2.py`
