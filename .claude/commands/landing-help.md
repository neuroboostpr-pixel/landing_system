---
description: Show all landing-system slash commands and their usage
allowed-tools: Read
---

# /landing-help

Print a summary of all available landing-system commands.

## Output

Print exactly:

```
Landing System — Commands

ENTRY POINTS:
  /landing-new <slug>              — new project from scratch
  /landing-from-context <slug>     — new project from parent agency folder
  /landing-clone <src> --as <new>  — A/B copy of existing landing (Phase 5)

PER-STAGE (Phase 2+):
  /landing-references              — stage 03
  /landing-moodboard               — stage 03
  /landing-brand                   — stage 04
  /landing-design                  — stage 05
  /landing-stack                   — stage 06
  /landing-content                 — stage 07
  /landing-build                   — stage 08

OPERATIONS (Phase 5):
  /landing-deploy                  — deploy to Бегет
  /landing-redeploy                — redeploy after edits
  /landing-rollback <version>      — rollback
  /landing-qa                      — run QA audit

SERVICE:
  /landing-status                  — current state
  /landing-help                    — this help
  /landing-update                  — update master system

Phase 1 of MVP is in progress. Most stage commands return "not yet implemented".
See docs/superpowers/plans/ for roadmap.
```

End of help.
