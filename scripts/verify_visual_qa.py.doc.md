---
type: script
name: verify_visual_qa
language: python
sources: ["scripts/verify_visual_qa.py"]
updated: 2026-05-18
---

# verify_visual_qa.py

Проверяет наличие visual-qa-report.md и отсутствие critical issues.

Exit 0 — отчёт есть и нет critical
Exit 1 — есть critical
Exit 2 — отчёт не создан (visual-qa никогда не запускался)

## Источник

- `scripts/verify_visual_qa.py`
