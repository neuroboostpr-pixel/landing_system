---
type: script
name: derive-landing-structure
language: python
sources: ["scripts/derive-landing-structure.py"]
updated: 2026-05-18
---

# derive-landing-structure.py

Derive 01a_АНАЛИЗ_НИШИ/landing-structure.md from 07_ПРОТОТИП/prototype.yaml.

Bridge for prototype-first flow (PR-D): wp-builder reads landing-structure.md to
know which template-parts/*.php to generate. In prototype-first flow we skip
01a niche analysis, so we synthesize this file from the prototype block list.

## Источник

- `scripts/derive-landing-structure.py`
