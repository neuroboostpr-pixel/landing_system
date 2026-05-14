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

## NOT used

- Daemon (Node + Express + SQLite) — we don't run a server
- Next.js SPA
- BYOK proxy
