---
type: script
name: content_parser
language: python
sources: ["scripts/lib/content_parser.py"]
updated: 2026-05-18
---

# content_parser.py

Parse 07_КОНТЕНТ/final-copy.md into a list of blocks.

Single source of truth for stage-08 generators. Each H2 (`## `) heading
becomes one Block. Field types are inferred by ordered regex heuristics
(see Field type detection table in spec).

## Источник

- `scripts/lib/content_parser.py`
