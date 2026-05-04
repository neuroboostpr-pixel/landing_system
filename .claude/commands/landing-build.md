---
description: Generate or regenerate the WordPress theme, Gutenberg blocks, ACF fields, integrations, analytics, and SEO config for a landing project (stage 08). Run within a landing project folder after /landing-content is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-build

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 08_build --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 08_build --project <project> --approve`

Run within a landing project after `content-writer` has produced `07_КОНТЕНТ/final-copy.md`.

## What I do

### Step 1 — Theme Scaffold (deterministic)
Run `generate-theme.py` to create `08_КОД/wp-theme/` structure with CSS variables, functions.php, template-parts stubs.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-theme.py .
```

### Step 2 — ACF Fields (deterministic)
Run `generate-acf.py` to create `08_КОД/acf-fields.json` from final-copy.md sections.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-acf.py .
```

### Step 3 — Gutenberg Blocks (AI agent)
Invoke `wp-builder` agent → fills template-parts PHP code, writes main.css + main.js, creates generateblocks-templates.json.

### Step 4 — Forms & Integrations (AI agent)
Invoke `integrations-engineer` agent → adds Fluent Forms webhook (Telegram/CRM) to functions.php.

### Step 5 — Analytics (AI agent)
Invoke `analytics-engineer` agent → adds Yandex Metrika code to functions.php, creates 11_АНАЛИТИКА/ files.

### Step 6 — SEO (AI agent)
Invoke `seo-optimizer` agent → adds meta tags + Schema.org to functions.php, creates 12_SEO/ files.

### Step 7 — Bundle Assets
Run `bundle-assets.py` to note fonts, download icons, copy processed photos.

```bash
python3 <landing-system>/skills/wp-theme-assembler/scripts/bundle-assets.py .
```

### Step 8 — Build Preview
Run `render-build-preview.py` to create static `08_КОД/build-preview.html`.

```bash
python3 <landing-system>/skills/wp-theme-assembler/scripts/render-build-preview.py .
```

### Step 10 — Popup System
Run `generate-popup.py` to add built-in popup (JS + CSS + PHP overlay).

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-popup.py .
```

### Step 11 — JS Library Initialization
Run `generate-js-init.py` to create main.js, sliders.js, animations.js, counters.js.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-js-init.py .
```

### Step 12 — Analytics (Yandex Metrika + GTM)
Run `generate-analytics.py` to inject YM counter and GTM container from brief.md.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-analytics.py .
```

### Step 13 — CRM Integrations
Run `generate-integrations.py` to inject Fluent Forms webhook (AmoCRM / Bitrix24 / Telegram).

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-integrations.py .
```

### Step 9 — HARD GATE
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

## Output

- `08_КОД/wp-theme/` — complete WP theme (PHP + CSS + JS + assets)
- `08_КОД/acf-fields.json` — ACF field configuration
- `08_КОД/gutenberg-blocks/` — custom Gutenberg blocks
- `08_КОД/generateblocks-templates.json` — GenerateBlocks template export
- `08_КОД/wp-theme/assets/js/popup.js` — popup system
- `08_КОД/wp-theme/assets/js/main.js`, `sliders.js`, `animations.js`, `counters.js` — JS init
- `08_КОД/integrations/` — CRM setup instructions
- `08_КОД/build-preview.html` — static preview for approval
- `11_АНАЛИТИКА/metrika-config.md`, `goals-and-events.json`, `utm-templates.md`
- `12_SEO/meta-tags.yaml`, `structured-data.json`, `robots.txt`, `keywords.md`
