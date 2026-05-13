---
description: Generate or regenerate the WordPress theme, Lazy Blocks, integrations, analytics, and SEO config for a landing project (stage 08). Run within a landing project folder after /landing-content is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-build

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 08_build --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. **Verify `08_КОД/block-spec.yaml` exists** (filled in from `template/08_КОД/block-spec.example.yaml`).
   Without it, generators 2–5 of the stage-08 pipeline fail with a clear message and the build halts.
5. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 08_build --project <project> --approve`

Run within a landing project after `content-writer` has produced `07_КОНТЕНТ/final-copy.md`.

## What I do

### Step 1 — Lazy Blocks pipeline (deterministic)

Run the orchestrator. It chains the 5 stage-08 generators in dependency order:

1. `generate-theme.py` — wp-theme scaffold (`style.css`, `functions.php`, `blocks/`, `assets/css/main.css`).
2. `generate-lzb-templates.py` — `wp-theme/blocks/lazyblock-<slug>/block.php` per block (never overwrites).
3. `generate-lzb-registration.py` — `lzb/init` `add_block()` block in `functions.php`.
4. `generate-css-patches.py` — `display: contents` CSS patches for InnerBlocks wrappers.
5. `generate-page-content.py` — `08_КОД/page-content.html` (Gutenberg markup + image placeholders).

```bash
python3 <landing-system>/scripts/generate-wp-blocks.py --project .
```

Requires `08_КОД/block-spec.yaml` (see Pre-flight).

### Step 2 — Forms & Integrations (AI agent)
Invoke `integrations-engineer` agent → adds Fluent Forms webhook (Telegram/CRM) to functions.php.

### Step 3 — Analytics (AI agent)
Invoke `analytics-engineer` agent → adds Yandex Metrika code to functions.php, creates 11_АНАЛИТИКА/ files.

### Step 4 — SEO (AI agent)
Invoke `seo-optimizer` agent → adds meta tags + Schema.org to functions.php, creates 12_SEO/ files.

### Step 5 — Bundle Assets
Run `bundle-assets.py` to note fonts, download icons, copy processed photos.

```bash
python3 <landing-system>/skills/wp-theme-assembler/scripts/bundle-assets.py .
```

### Step 6 — Build Preview
Run `render-build-preview.py` to create static `08_КОД/build-preview.html`.

```bash
python3 <landing-system>/skills/wp-theme-assembler/scripts/render-build-preview.py .
```

### Step 7 — Popup System
Run `generate-popup.py` to add built-in popup (JS + CSS + PHP overlay).

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-popup.py .
```

### Step 8 — JS Library Initialization
Run `generate-js-init.py` to create main.js, sliders.js, animations.js, counters.js.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-js-init.py .
```

### Step 9 — Analytics (Yandex Metrika + GTM)
Run `generate-analytics.py` to inject YM counter and GTM container from brief.md.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-analytics.py .
```

### Step 10 — CRM Integrations
Run `generate-integrations.py` to inject Fluent Forms webhook (AmoCRM / Bitrix24 / Telegram).

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-integrations.py .
```

### Step 11 — HARD GATE
Show path to `08_КОД/build-preview.html`. Wait for user approval before proceeding to stage 09 (deploy).

## Usage

```
/landing-build
/landing-build --cinematic   # also wire GSAP/ScrollTrigger in wp-builder step
```

## Requirements

- `07_КОНТЕНТ/final-copy.md` — from `/landing-content`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — from `/landing-design`
- `06_СТЕК/design-stack.yaml` — from `/landing-stack`
- `08_КОД/block-spec.yaml` — filled in from `template/08_КОД/block-spec.example.yaml`

## Output

- `08_КОД/wp-theme/` — complete WP theme (PHP + CSS + JS + assets)
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — per-block PHP templates
- `08_КОД/wp-theme/functions.php` — with AUTO-GENERATED `lzb/init` registration
- `08_КОД/wp-theme/assets/css/main.css` — with AUTO-GENERATED inner-blocks patches
- `08_КОД/page-content.html` — Gutenberg block markup for front-page seed
- `08_КОД/wp-theme/assets/js/popup.js` — popup system
- `08_КОД/wp-theme/assets/js/main.js`, `sliders.js`, `animations.js`, `counters.js` — JS init
- `08_КОД/integrations/` — CRM setup instructions
- `08_КОД/build-preview.html` — static preview for approval
- `11_АНАЛИТИКА/metrika-config.md`, `goals-and-events.json`, `utm-templates.md`
- `12_SEO/meta-tags.yaml`, `structured-data.json`, `robots.txt`, `keywords.md`
