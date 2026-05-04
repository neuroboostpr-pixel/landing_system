---
description: Adapt the landing prototype text to Gutenberg blocks (stage 07). Run within a landing project folder after stack is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-content

Run within a landing project after `06_СТЕК/design-stack.yaml` is approved.

## What I do

1. Invoke `content-writer` agent.
2. Read `07_КОНТЕНТ/prototype.md` and block structure from `DESIGN.md`.
3. Read real testimonials from `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/`.
4. Produce `07_КОНТЕНТ/final-copy.md` — text laid out per Gutenberg block.
5. Produce `07_КОНТЕНТ/seo-copy.md` — SEO titles, descriptions, h1 variants.
6. **HARD GATE**: show `final-copy.md`, wait for user approval before proceeding to stage 08.

## Usage

Run: `/landing-content`

Requires:
- `07_КОНТЕНТ/prototype.md` — source prototype text
- `06_СТЕК/design-stack.yaml` — block definitions (run after `/landing-stack`)

## Output

- `07_КОНТЕНТ/final-copy.md` — final copy per block
- `07_КОНТЕНТ/seo-copy.md` — SEO copy variants
