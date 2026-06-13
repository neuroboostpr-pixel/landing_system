---
type: script
name: log-decisions
language: python
sources: ["scripts/log-decisions.py"]
updated: 2026-05-18
---

# log-decisions.py

Append stage decisions to <project>/decisions.log.md.

CLI:
  python scripts/log-decisions.py --project <path> --stage 04_brand
  python scripts/log-decisions.py --project <path> --stage 04_brand \
    --decisions-file <project>/.stage-decisions/04_brand.md

## Источник

- `scripts/log-decisions.py`
