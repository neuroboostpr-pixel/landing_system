---
name: wp-gutenberg-block-builder
description: Generate Lazy-Blocks-based Gutenberg blocks + theme scaffold + page content for a landing project (stage 08).
---

# wp-gutenberg-block-builder

Generates stage-08 WordPress artifacts using **Lazy Blocks (free)** — blocks live
under the `lazyblock/` namespace and are registered at runtime via
`lazyblocks()->add_block()`. This is **NOT** ACF Pro Blocks (`acf/` namespace) —
we migrated off that in 2026-05-13 to stay on free plugins.

## Prerequisites

Before running any generator the project must have:

1. Stage 05 complete — `05_ДИЗАЙН-СИСТЕМА/tokens.json` exists.
2. Stage 06 complete — `06_СТЕК/design-stack.yaml` exists.
3. Stage 07 complete — `07_КОНТЕНТ/final-copy.md` reviewed.
4. `08_КОД/block-spec.yaml` filled in (см. шаблон `template/08_КОД/block-spec.example.yaml`).
   Generators 2–5 read this file; without it they fail fast with a clear message.

## Pipeline (5 generators, dependency order)

Run them all via the orchestrator:

```bash
python scripts/generate-wp-blocks.py --project <project-dir>
```

Or invoke individually:

| # | Script | Purpose |
|---|--------|---------|
| 1 | `generate-theme.py <project>` | wp-theme scaffold: `style.css`, `functions.php`, `blocks/` dir, base `assets/css/main.css`. |
| 2 | `generate-lzb-templates.py --project <path>` | One `wp-theme/blocks/lazyblock-<slug>/block.php` per block. **Never overwrites** existing — safe for manager hand-edits. |
| 3 | `generate-lzb-registration.py --project <path>` | `lzb/init` `add_block()` block injected into `functions.php` between `AUTO-GENERATED` markers. |
| 4 | `generate-css-patches.py --project <path>` | `display: contents` rules in `assets/css/main.css` (AUTO-GENERATED block) for InnerBlocks wrappers in section+card blocks. |
| 5 | `generate-page-content.py --project <path>` | `08_КОД/page-content.html` with Gutenberg block markup + image placeholders for deploy substitution. |

Step 1 takes the project path as a positional argument; steps 2–5 use `--project`.

## Outputs

- `08_КОД/wp-theme/style.css`
- `08_КОД/wp-theme/functions.php` — contains AUTO-GENERATED `lzb/init` section
- `08_КОД/wp-theme/assets/css/main.css` — contains AUTO-GENERATED inner-blocks CSS patches
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — one per block
- `08_КОД/page-content.html` — Gutenberg markup seed for the front page

## What this skill does NOT produce

- **No `acf-fields.json`** — ACF Blocks are deprecated here. ACF Free is still installed
  for potential page-level meta but plays no role in block rendering.
- **No `block.json` files** — Lazy Blocks reads block config from the
  `lazyblocks()->add_block()` PHP call, not from JSON.
- **No `front-page.php`** — the front page is a regular Gutenberg page set via
  `page_on_front`. Deploy seeds it from `page-content.html`.
- **No `template-parts/` directory** — block PHP lives under `blocks/lazyblock-<slug>/block.php`.

## Honest scope

- **Flat repeaters only.** Lazy Blocks Free does not support nested repeaters.
  For "list of cards with sub-items" use the **section+card** pattern
  (parent block with InnerBlocks of a child card block).
- **Toggle defaults must be YAML boolean** (`true` / `false`), not the strings
  `"true"`/`"false"`. The generator rejects strings.
- **Image control defaults** are placeholders like
  `__IMAGE_ATTACHMENT_ID__<file>__`; deploy substitutes them with real Media
  Library attachment IDs after `wp media import`.
- **Existing `block.php` is not overwritten** on regeneration — managers can
  safely edit a block template by hand and re-run the orchestrator.
- Does NOT register form integrations, analytics, or SEO — those are separate
  generators invoked later in `/landing-build`.
