# Research Task: ACF Block Frontend Rendering — NOT YET FIXED

**Date:** 2026-05-12
**Status:** Open research — blocks register but don't render on frontend
**Priority:** Blocks "manager edits via Gutenberg" goal on existing landings

## Problem

After stage-08 fix is implemented and applied to neuroupgrade-v2:
- ACF 6.8.0 plugin active ✓
- 15 ACF field-groups synced via `wp acf json sync` ✓
- 15 blocks registered in `WP_Block_Type_Registry` (visible via `wp eval`) ✓
- BUT every registered block has `render_callback: NO` ✗
- Result: `do_blocks($content)` on a post with `<!-- wp:acf/lp-blok-1-hero -->` markup returns empty string

## What was tried (live on neuroupgrade-v2, all reverted)

1. **Registration via `register_block_type($path_to_block_json)`** (WP standard) — blocks register, but no render_callback attached. ACF doesn't auto-detect them.

2. **Registration via `acf_register_block_type([...])` on `acf/init`** — same result. Blocks register, but render_callback still NO. Either ACF re-registers them without the callback, or our timing is off.

3. **Block template path variations:**
   - `renderTemplate: "template-parts/block-<slug>.php"` (relative to theme)
   - Copied PHP to `gutenberg-blocks/<slug>/template-parts/block-<slug>.php` (relative to block.json)
   - Neither variant attached a render_callback.

## Hypotheses to investigate

1. **`block.json` `acf` field syntax outdated.** ACF 6.x may have moved to `acfBlockVersion` or different key. Check ACF 6.8 changelog.

2. **`acf_register_block_type()` vs `register_block_type()` collision.** When both fire, the WP one may win and strip the ACF callback. Test: use only one path, never both.

3. **`render_template` requires an absolute path on ACF 6.x.** Old API used relative. Try `__DIR__ . '/template-parts/block-<slug>.php'` from theme functions.php.

4. **ACF doesn't register block render unless `block.json` is inside the ACF blocks dir.** Some plugins enforce a specific dir layout. Check ACF settings.

5. **Block name namespace.** `acf/` prefix may be reserved/restricted in modern ACF — try a different namespace (`lp/`).

## Research steps before next attempt

1. Read [ACF Blocks docs (current version)](https://www.advancedcustomfields.com/resources/blocks/) — verify the registration API for 6.x.
2. Read [`block.json` ACF extension docs](https://www.advancedcustomfields.com/resources/registering-a-block-with-block-json/).
3. Find a public WordPress theme using ACF Blocks via `block.json` (search GitHub for `acf/lp-` or `"renderTemplate"`).
4. Locally reproduce: minimal WP install + ACF + ONE block with `block.json` + verify render_callback gets attached.
5. **Only after local works, port to neuroupgrade-v2.**

## What to keep / what to throw away

**Keep** (works correctly):
- `scripts/lib/content_parser.py` — parser is correct.
- `scripts/generate-acf.py` — ACF JSON output is correct (proven by `wp acf json sync` accepting all 15 groups).
- `scripts/generate-block-json.py` — block.json files are valid (registry sees them).
- All bats tests — pipeline works.

**Throw away or rewrite:**
- `scripts/generate-block-registration.py` — current output (`register_block_type($path)` via init hook) does NOT attach render_callback. Needs research to determine correct registration API for ACF 6.x.

**Decision needed:**
- Option A: stick with `block.json` registration; figure out why ACF doesn't pick up render. Modern path.
- Option B: drop `block.json` entirely, register only through `acf_register_block_type()` in functions.php. Older API but proven to work.

## Current state of neuroupgrade-v2 on prod

- Site renders correctly (HTTP 200, 115KB) via `front-page.php` (PHP-template flow, NOT Gutenberg).
- WordPress DB freshly initialized (admin user `esper21`, pwd in deploy script context).
- ACF active, 15 field-groups synced.
- 15 blocks registered but without render_callback.
- `inc/lp-preview-panel-axes.php` registered, preview-panel and parallax work.
- Backups of pre-experiment theme deleted (was on prod, fresh install).

Manager-editable Gutenberg flow: **NOT YET WORKING**. Manager can see blocks in inserter, but adding them to a page produces no frontend render.
