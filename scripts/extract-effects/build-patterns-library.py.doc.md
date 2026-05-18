---
type: script
name: build-patterns-library
language: python
sources: ["scripts/extract-effects/build-patterns-library.py"]
updated: 2026-05-18
---

# build-patterns-library.py

Из extracted patterns создаёт reusable HTML+CSS снипеты в _patterns/.

Каждый снипет — папка с index.html (демо) + styles.css (стили) + meta.yaml.

Usage:
    build-patterns-library.py <findings.json>
    cat findings.json | build-patterns-library.py

Env:
    PATTERNS_DIR_OVERRIDE — путь до _patterns/, иначе block-library/_patterns

## Источник

- `scripts/extract-effects/build-patterns-library.py`
