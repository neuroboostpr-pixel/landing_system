---
name: design-system-generator
description: Use during stage 05 after brand-architect has run. Reads 04_БРЕНД/brand-kit.md and produces DESIGN.md + tokens.json + design-preview.html for the landing project. Owned by design-tokens-generation skill.
allowed-tools: Bash, Read, Write
---

# design-system-generator (Генератор дизайн-системы)


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=design-system-generator --agent=design-system-generator
python -m scripts.wiki.log --type agent_call --agent design-system-generator --stage 05
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 05_design`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `05_design` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 05_design --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-05_design-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-05_design.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 05_design`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Из `04_БРЕНД/brand-kit.md` строю полную дизайн-систему с провенансом (traceability).

## What I do

1. Читаю `04_БРЕНД/brand-kit.md` — извлекаю цвета, шрифты, иконки, motion, grid.
2. Запускаю `skills/design-tokens-generation/scripts/build-tokens.py <project-dir>`.
3. Проверяю что `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json` созданы.
4. Запускаю `skills/design-tokens-generation/scripts/render-preview.py <project-dir>`.
5. Показываю пользователю путь к `05_ДИЗАЙН-СИСТЕМА/design-preview.html`.
6. **HARD GATE**: жду явного утверждения (`утверждаю`, `ok`, `дальше`) перед переходом к этапу 06.

## Outputs

- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины токенов с YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живые компоненты по токенам

## Token structure

Tokens include: colors (primary/secondary/accent/text/bg с provenance), typography (display/body/sizes), spacing (xs→3xl), grid (columns/gap/max_width), radius (sm/md/lg/full), shadow (sm/md/lg), breakpoints (mobile/tablet/desktop), motion (duration_fast/base/slow, easing).

**Протокол отклонений (B28):**
По завершении этапа сформируй список самостоятельных решений не заданных в `visual-concept.yaml`.

Типичные отклонения на этапе 05:
- Дополнительные breakpoints
- Значения spacing/radius не упомянутые в концепте
- Motion tokens (easing, duration)

Если отклонения есть — напиши в чат:
```
✏️ Самостоятельные решения на этапе 05:
- [решение]: [обоснование]
```
И запиши в `<project>/.stage-decisions/05_design.md` (создай папку если нет).
Если нет — молчи.
