---
type: script
name: wizard-check-materials
language: python
sources: ["scripts/wizard-check-materials.py"]
updated: 2026-05-18
---

# wizard-check-materials.py

Verify materials in a project folder per wizard step.

Output: JSON to stdout with {step, status, found, missing, summary}.
Exit code: 0 if pass or warn, 1 if fail.

Steps:
- prototype: REQUIRED. 07_ПРОТОТИП/source/prototype.{pdf,md,html}
- photos: optional. Count files in 07c_PHOTOS/inbox/**/*.{jpg,jpeg,png,heic}
- logos: optional. 04_БРЕНД/logos/logo.* or any image in logos/
- references: optional. 03_РЕФЕРЕНСЫ/index.yaml non-empty OR screenshots/ non-empty

## Источник

- `scripts/wizard-check-materials.py`
