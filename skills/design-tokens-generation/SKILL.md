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

## Palette library export (post-approve hook)

When stage `05_design_system` is approved (gate-check passes), run:

```bash
python scripts/export-palettes-to-library.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml"
```

This adds new palette ids to the global library. Existing ids are preserved
(skipped with a notice — see `scripts/export-palettes-to-library.py`).

Invariant: do NOT call this script before approval. Black-box behaviour is
"approved palettes are reusable across projects." Drafts must not pollute
the library.
