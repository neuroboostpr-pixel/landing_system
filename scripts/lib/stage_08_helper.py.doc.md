---
type: script
name: stage_08_helper
language: python
sources: ["scripts/lib/stage_08_helper.py"]
updated: 2026-05-18
---

# stage_08_helper.py

Stage-08 structural check for the Lazy Blocks pipeline.

Called from gate-check.sh as type=script. Validates that the project has the
required Lazy Blocks artifacts (no longer ACF Blocks JSON / template-parts /
gutenberg-blocks/<slug>/block.json — those belong to the deprecated pipeline).

Required artifacts (hard fail if missing/invalid):
  - 08_КОД/block-spec.yaml exists and validates via block_spec.load + validate
  - 08_КОД/wp-theme/functions.php contains both `lzb/init` and
    `lazyblocks()->add_block(`
  - 08_КОД/wp-theme/blocks/ exists and contains AT LEAST one
    lazyblock-*/block.php
  - 08_КОД/page-content.html exists

Soft (warn-only):
  - if block-spec.yaml has any section-card blocks, the AUTO-GENERATED
    lzb-inner-blocks marker should be present in assets/css/main.css.

Exit 0 = pass. Exit 1 = hard fail.

Usage: python stage_08_helper.py <project-root>

## Источник

- `scripts/lib/stage_08_helper.py`
