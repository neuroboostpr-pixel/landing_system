---
name: moodboard-composer
description: Use during stage 03 after references are approved. Synthesizes a moodboard.md narrative + moodboard.html visual board from approved references.
---

# moodboard-composer


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
CLAUDE_MODEL=$CLAUDE_MODEL python -m scripts.wiki.query --slug=moodboard-composer
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 03_references`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `03_references` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 03_references --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-03_references-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-03_references.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 03_references`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Compose `03_РЕФЕРЕНСЫ/moodboard.md` (text narrative explaining the visual direction) + `moodboard.html` (visual board with reference cards).

## Process

1. Read `03_РЕФЕРЕНСЫ/index.yaml`, get all refs with status `approved`.
2. For each: prompt user for tags (e.g. "split-screen", "warm-palette", "premium-typography").
3. Write `moodboard.md` describing the chosen direction (palette feel, typography character, motion vibe, what we adopt and reject).
4. Run `python3 skills/moodboard-creation/scripts/render.py <refs-dir>` to build `moodboard.html`.
5. **HARD GATE**: user opens moodboard.html, approves direction. Then style-extractor takes over.

## Tools

Bash, Read, Write, Glob. Calls render.py.

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/niche-analysis.md` — обязательный input. Section 6 «Что брать с собой в следующие этапы» определяет, какой визуальный язык уместен.
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — обязательный input. Sections 1, 2, 3, 5, 6 определяют визуальный язык референсов. Если референс попадает в red flag (Section 6) — не сохранять.
