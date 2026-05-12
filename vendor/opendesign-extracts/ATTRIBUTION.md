# OpenDesign Extracts — Attribution

**Source:** https://github.com/nexu-io/open-design
**License:** Apache-2.0 (see `LICENSE`)
**Extraction date:** 2026-05-12
**Pinned commit:** TBD-COMMIT-HASH ← обновить после первой реальной выгрузки файлов

## What we use

| Letter | What | Files in this repo | Used by |
|---|---|---|---|
| A | Skill-block format (SKILL.md + assets + meta.yaml) | `skill-block-template/` | `block-library/*` |
| B | 93 prompt-templates for gpt-image-2 | `prompt-templates/` (populate in PR-C) | PR-C icon/infographic generators |
| C | 72 reference DESIGN.md files | `design-systems-refs/` (populate later) | Design-system-generator references |
| D | Pre-flight injection pattern | applied in `ux-composer` mission | ux-composer logic |
| G | 9-section DESIGN.md structure | applied in `design-tokens-generation` skill | DESIGN.md template |
| H | `saas-landing` skill seed | adapted in `block-library/hero/ru-hero-02-b2c-expert` | seed blocks |
| I | Device frames | `device-frames/` (populate later) | wireframe.html mobile preview |
| J | TodoWrite plan streaming pattern | applied in landing-orchestrator (PR-D) | Orchestrator UX |
| K | Sandboxed iframe preview | applied in `wireframe-rendering` skill | wireframe.html iframe |

## NOT used

- Daemon (Node + Express + SQLite) — we don't run a server
- Next.js SPA
- BYOK proxy
