---
description: Generate or regenerate the design system for a landing project (stage 05). Run within a landing project folder after brand-kit is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-design

Run within a landing project after `brand-architect` has produced `04_БРЕНД/brand-kit.md`.

## What I do

1. Invoke `design-system-generator` agent.
2. Run `skills/design-tokens-generation/scripts/build-tokens.py` → `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` + `tokens.json`.
3. Run `skills/design-tokens-generation/scripts/render-preview.py` → `05_ДИЗАЙН-СИСТЕМА/design-preview.html`.
4. If `--cinematic` flag present: also invoke `scene-director` agent → `scenes.md`.
5. **HARD GATE**: show preview path, wait for user approval before proceeding to stage 06.

## Usage

Run: `/landing-design`

Requires `04_БРЕНД/brand-kit.md` produced by `brand-architect` (run after `/landing-brand` is approved).

## Options

- `--cinematic` — also generate `scenes.md` via `scene-director` agent

## Output

- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — token source of truth with YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — machine-readable tokens
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — live components preview
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — cinematic scene grammar (if --cinematic)
