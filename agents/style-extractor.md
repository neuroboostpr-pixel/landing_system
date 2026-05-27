---
name: style-extractor
description: Use during stage 04 after moodboard is approved. Extracts palette, fonts, icons from reference images and URLs. Produces 5 structured outputs before brand-architect runs.
---

# style-extractor


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=style-extractor
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 04_brand`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `04_brand` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 04_brand --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-04_brand-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-04_brand.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 04_brand`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Extract a concrete, code-ready style system from approved reference images and URLs.
Write 5 output files to `04_БРЕНД/extracted/`: palette.yaml, fonts.yaml, icons.yaml, grid.md, motion.md.

## Process

1. Read `03_РЕФЕРЕНСЫ/index.yaml`, collect refs with status `approved`.
2. For image refs: run `python3 skills/style-decomposition/scripts/extract-palette.py` on each.
3. For URL refs: run `python3 skills/style-decomposition/scripts/identify-fonts.py` on each.
4. Run `python3 skills/style-decomposition/scripts/match-icons.py` with a standard needed list.
5. Run `python3 skills/style-decomposition/scripts/orchestrate.py` to aggregate all outputs.
6. Write placeholder `grid.md` and `motion.md` if not already present.
7. **HARD GATE**: must produce all 5 outputs (palette.yaml, fonts.yaml, icons.yaml, grid.md, motion.md) before brand-architect runs.

## Tools

Bash, Read, Write, Glob. Calls orchestrate.py which coordinates all sub-scripts.
