---
type: script
name: test-pipeline
language: bash
sources: ["scripts/test-pipeline.sh"]
updated: 2026-05-18
---

# test-pipeline.sh

test-pipeline.sh — Complete PR-A test for ANY project in one command.

Creates a new project, drops a prototype, runs the full pipeline:
prototype.md/pdf  →  prototype.yaml  →  wireframe.html  →  composed.html

Usage:
bash scripts/test-pipeline.sh <slug> <path-to-prototype>

Examples:
bash scripts/test-pipeline.sh coffee-shop ~/Downloads/my-prototype.pdf
bash scripts/test-pipeline.sh saas-product ./samples/example-prototype.md
bash scripts/test-pipeline.sh leysan-dubai ~/Downloads/Книга.pdf

Optional env vars:
TOKENS_FILE   — path to existing tokens.json. Default: built-in stub
NICHE         — services|b2c|local. Default: derived from prototype or asks
SKIP_OPEN     — set to 1 to skip opening files at the end

## Источник

- `scripts/test-pipeline.sh`
