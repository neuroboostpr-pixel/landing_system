# OpenDesign Extracts — Attribution

**Source:** https://github.com/nexu-io/open-design
**License:** Apache-2.0 (see `LICENSE`)
**Extraction date:** 2026-05-13
**Pinned commit:** ef699df4cdaca8ddd5a39935145837332835ce42

## What we use

| Letter | What | Files in this repo | Used by |
|---|---|---|---|
| A | Skill-block format (SKILL.md + assets + meta.yaml) | `skill-block-template/` | `block-library/*` |
| B | 102 prompt-templates for gpt-image-2 | `prompt-templates/image/` (45 files) + `prompt-templates/video/` (57 files) | PR-C icon/infographic generators |
| C | 149 reference DESIGN.md files | `design-systems-refs/` | Design-system-generator references |
| D | Pre-flight injection pattern | applied in `ux-composer` mission | ux-composer logic |
| G | 9-section DESIGN.md structure | applied in `design-tokens-generation` skill | DESIGN.md template |
| H | `ui-ux-pro-max` skill seed (no saas-landing in repo — closest equivalent used) | `saas-landing-ref/` | seed blocks, pattern guidance |
| I | Device frames (5 HTML frames) | `device-frames/` | wireframe.html mobile preview |
| J | TodoWrite plan streaming pattern | applied in landing-orchestrator (PR-D) | Orchestrator UX |
| K | Sandboxed iframe preview | applied in `wireframe-rendering` skill | wireframe.html iframe |

## File counts

| Category | Files | Notes |
|---|---|---|
| `prompt-templates/image/` | 45 | JSON prompt files for gpt-image-2 (image generation) |
| `prompt-templates/video/` | 57 | JSON prompt files for video generation |
| `design-systems-refs/` | 149 | DESIGN.md files for each design system (one per system) |
| `device-frames/` | 5 HTML + 1 README | iPhone 15 Pro, Pixel, MacBook, iPad Pro, Chrome browser |
| `saas-landing-ref/` | 2 | ui-ux-pro-max SKILL.md + SOURCE-NOTE.md (no saas-landing in upstream) |

**Total files extracted:** 258

**Note on saas-landing:** The spec referenced `skills/saas-landing/` but this directory does not exist in the OpenDesign repository. We substituted `skills/ui-ux-pro-max/` SKILL.md as the closest SaaS landing reference. The actual pattern data is installed at `~/.claude/skills/ui-ux-pro-max/data/`.

## Design templates (6 HTML landings) — added PR-A.X 2026-05-14

**Pinned commit:** 75498838a911d5d7ab4299ac817774ab5e560824
**Source:** design-templates/*/example.html
**Use:** reference for layout patterns, scroll-reveal, CSS effects
**Files:** web-prototype-taste-soft, open-design-landing, saas-landing, pricing-page, waitlist-page, web-prototype-taste-editorial

| File | Lines | Notable patterns |
|---|---|---|
| `web-prototype-taste-soft.html` | 543 | ambient mesh, floating pill nav, double-bezel hero card |
| `open-design-landing.html` | 2646 | hero scroll-reveal, marquee, bento grid hairline |
| `saas-landing.html` | 154 | minimal SaaS: features + pricing tiers |
| `pricing-page.html` | 128 | toggle annual/monthly, comparison table |
| `waitlist-page.html` | 401 | email capture, social proof, countdown |
| `web-prototype-taste-editorial.html` | 393 | editorial typography, paper texture, dot grid |

## Craft knowledge (12 markdown rule-files) — added PR-A.X 2026-05-14

**Source:** craft/*.md
**Use:** anti-slop rules, animation discipline, typography hierarchy
**Files:** README.md, anti-ai-slop.md, animation-discipline.md, typography.md, typography-hierarchy.md, typography-hierarchy-editorial.md, color.md, accessibility-baseline.md, form-validation.md, laws-of-ux.md, rtl-and-bidi.md, state-coverage.md

| File | Key rules |
|---|---|
| `anti-ai-slop.md` | 7 cardinal sins: no indigo, no hero gradient, no emoji icons, no fake metrics |
| `animation-discipline.md` | 150ms default, cubic-bezier(0.2,0,0,1), prefers-reduced-motion mandatory |
| `typography-hierarchy.md` | Display/heading/body/label scale rules |
| `typography-hierarchy-editorial.md` | Magazine-style hierarchy for editorial projects |
| `accessibility-baseline.md` | WCAG 2.2 AA floor, focus-visible rules |
| `color.md` | Contrast ratios, semantic color tokens |

## NOT used

- Daemon (Node + Express + SQLite) — we don't run a server
- Next.js SPA
- BYOK proxy
