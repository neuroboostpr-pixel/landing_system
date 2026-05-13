# Third Party Notices

This product includes software developed by third parties.

## OpenDesign

- **Project:** https://github.com/nexu-io/open-design
- **License:** Apache License 2.0
- **License text:** [`vendor/opendesign-extracts/LICENSE`](vendor/opendesign-extracts/LICENSE)
- **What we use:** see [`vendor/opendesign-extracts/ATTRIBUTION.md`](vendor/opendesign-extracts/ATTRIBUTION.md)

## ui-ux-pro-max (user-local skill)

Pattern engine referenced for landing.csv / web-interface.csv / ux-guidelines.csv.
Source: user's local Claude skill at `~/.claude/skills/ui-ux-pro-max`.

## awesome-design-md (via OpenDesign)

The 72 reference DESIGN.md files in `vendor/opendesign-extracts/design-systems-refs/`
originate from https://github.com/VoltAgent/awesome-design-md.

## anthropic-skills:pdf

Used for PDF parsing in `prototype-import` skill. See `~/.claude/skills/anthropic-skills/pdf`.

## nexu-io/open-design — PR-B Photo Pipeline patterns (Apache-2.0)

Added 2026-05-13 as part of PR-B (Photo Pipeline). Patterns ported from
https://github.com/nexu-io/open-design (Apache-2.0):

1. **selections.yaml `strategy` enum** (`generate | placeholder | bring-your-own`) —
   from `design-templates/open-design-landing/schema.ts:413`.
2. **Slot description fields** (id, file, width, height, ratio, required) —
   adapted from `design-templates/open-design-landing/assets/image-manifest.json`.
3. **SVG-placeholder as PNG** technique — re-implemented in
   `skills/photo-curation/scripts/svg-placeholder.py`. Original:
   `design-templates/open-design-landing/scripts/placeholder.ts`.
4. **AI-imagery anti-patterns list** (no lens flare, glitch, AI faces in collage,
   watermarks, surreal artifacts) — incorporated into
   `skills/photo-curation/templates/generate-fallback.md`. Original:
   `design-systems/atelier-zero/DESIGN.md` §11 + anti-patterns section.
5. **Skip-if-exists + --force pattern** — applied to
   `skills/photo-curation/scripts/codex-generate-fallback.sh` and STATE.yaml stage
   tracking. Original: `design-templates/open-design-landing/scripts/imagegen.ts`.

License: Apache-2.0. Full text:
https://github.com/nexu-io/open-design/blob/main/LICENSE

## OpenDesign image-prompts — PR-C Visual Generation (CC-BY-4.0 main + per-prompt)

PR-C (2026-05-13) uses 90 image-prompt JSON templates from
`vendor/opendesign-extracts/prompt-templates/image/` (Apache-2.0 wrapper repo,
per-prompt licenses in `source.license` field — mostly CC-BY-4.0, some MIT).

When PR-C selects a prompt for infographic generation, the per-prompt
attribution is preserved in `07d_VISUALS/prompts.yaml` with fields:
- `id` — prompt ID
- `license` — per-prompt license (e.g. CC-BY-4.0)
- `author` — original creator
- `url` — original URL

Original repo: YouMind-OpenLab/awesome-gpt-image-2 (CC-BY-4.0 wrapper).

Use locations in this codebase:
- `skills/visual-generation/scripts/prompt-picker.py` — selects + adapts prompts
- `skills/visual-generation/templates/infographic-prompt.md` — fallback template inspired by open-design style
