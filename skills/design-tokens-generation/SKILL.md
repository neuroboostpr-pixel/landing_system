---
name: design-tokens-generation
description: Generates DESIGN.md and tokens.json from brand-kit.md. Used by design-system-generator agent at stage 05.
allowed-tools: Bash, Read, Write
---

# design-tokens-generation

Reads `04_БРЕНД/brand-kit.md` YAML frontmatter and builds a complete design token set.

## Scripts

- `scripts/build-tokens.py <project-dir>` — writes `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` + `tokens.json`
- `scripts/render-preview.py <project-dir>` — writes `05_ДИЗАЙН-СИСТЕМА/design-preview.html`
