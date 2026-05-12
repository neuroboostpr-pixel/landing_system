---
name: wp-gutenberg-block-builder
description: Generate ACF Block Gutenberg blocks + ACF fields + theme template parts from 07_КОНТЕНТ/final-copy.md. Used by wp-builder agent during stage 08.
---

# wp-gutenberg-block-builder

Generates the four stage-08 WP artifacts from a single source of truth (`07_КОНТЕНТ/final-copy.md`):

1. `08_КОД/acf-fields.json` — ACF field groups, one per H2 block.
2. `08_КОД/gutenberg-blocks/<slug>/block.json` — block descriptor per block.
3. `08_КОД/wp-theme/functions.php` — `register_block_type()` for each block, inside `AUTO-GENERATED` markers.
4. `08_КОД/wp-theme/template-parts/block-<slug>.php` — scaffolded render template (only for missing files).

Use the orchestrator:

```bash
python scripts/generate-wp-blocks.py --project <project-dir>
```

It calls the four generators in order:
- `scripts/generate-acf.py`
- `scripts/generate-block-json.py`
- `scripts/generate-block-registration.py`
- `scripts/generate-theme.py --blocks-only`

All four are driven by `scripts/lib/content_parser.py` — a single source of truth that parses H2 headings into `Block` objects. Field types are inferred by ordered regex heuristics; see spec `docs/superpowers/specs/2026-05-12-stage-08-acf-gutenberg-design.md` for details.

## Honest scope

- Generates ACF Block-style Gutenberg blocks (`apiVersion: 3`, `acf/` namespace).
- Does NOT generate Native Gutenberg blocks (no React, no `edit.js`, no build step).
- Does NOT register form integrations (Fluent Forms, CRM webhooks) — that's `generate-integrations.py`.
- Does NOT generate analytics — `generate-analytics.py`.

## Stage-08 hard-gate

After generation, `bash scripts/gate-check.sh --stage 08_build --project <path>` enforces:

1. wp-theme/ exists.
2. `register_block_type` present in functions.php.
3. `acf-fields.json` exists, is valid JSON.
4. One ACF group per H2 block.
5. Each ACF group has ≥1 field.
6. Each block has `template-parts/block-<slug>.php`.
7. Each block has `gutenberg-blocks/<slug>/block.json`.
8. Warnings: block.json has title/description/category/icon; manual_field_review_needed empty.

Projects pre-dating this hardening can be marked `legacy: true` (auto via `scripts/mark-legacy-projects.sh`) to bypass the gate. Migrate them with `scripts/backport-acf-to-legacy.sh <project>`.
