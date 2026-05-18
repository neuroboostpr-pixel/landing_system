---
type: script
name: conversations_compiler
language: python
sources: ["scripts/wiki/conversations_compiler.py"]
updated: 2026-05-18
---

# conversations_compiler.py

Компилит daily/ → memory/compiled/concepts/.

Зовётся хуком SessionEnd или вручную:
  python -m scripts.wiki.compile --source-mode=conversations --project=<slug>

## Источник

- `scripts/wiki/conversations_compiler.py`
