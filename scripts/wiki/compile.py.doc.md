---
type: script
name: compile
language: python
sources: ["scripts/wiki/compile.py"]
updated: 2026-05-18
---

# compile.py

Wiki compiler CLI.

Три режима компиляции:
  --source-mode=system          компилит landing-system в landing-system/wiki/
  --source-mode=project-graph   компилит артефакты проекта в <project>/wiki/
                                требует --project=<slug>
  --source-mode=conversations   компилит daily logs сессий (coleam00 default)
                                требует --project=<slug>

В PR-F.1 — только скелет. Логика добавляется в PR-F.2 (system),
PR-F.3 (project-graph), PR-F.4 (conversations).

## Источник

- `scripts/wiki/compile.py`
