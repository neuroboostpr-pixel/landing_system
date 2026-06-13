---
type: script
name: extract-content-from-prototype
language: python
sources: ["scripts/extract-content-from-prototype.py"]
updated: 2026-05-18
---

# extract-content-from-prototype.py

Extract real content from prototype.yaml and generate content.md + extraction-log.md.

This fixes BUG-001: Content extraction from prototype should produce real texts, not generic templates.

Usage:
  python3 extract-content-from-prototype.py <prototype.yaml> [--output <content.md>] [--log-output <extraction-log.md>] [--debug]

## Источник

- `scripts/extract-content-from-prototype.py`
