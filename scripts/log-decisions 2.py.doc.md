---
type: script
name: log-decisions 2
language: python
sources: ["scripts/log-decisions 2.py"]
updated: 2026-05-18
---

# log-decisions 2.py

Append stage decisions to <project>/decisions.log.md.

CLI:
  python scripts/log-decisions.py --project <path> --stage 04_brand
  python scripts/log-decisions.py --project <path> --stage 04_brand \
    --decisions-file <project>/.stage-decisions/04_brand.md

## Источник

- `scripts/log-decisions 2.py`
