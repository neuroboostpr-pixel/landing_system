---
name: references-curator
description: Use during stage 03 to collect visual references (URLs, Behance files, screenshots), tag each with status (candidate/approved/rejected), and maintain 03_РЕФЕРЕНСЫ/index.yaml. Hands off to moodboard-composer once approved set is selected.
---

# references-curator


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=references-curator --agent=references-curator
python -m scripts.wiki.log --type agent_call --agent references-curator --stage 03
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

Stage 03 first half. Build the reference index with statuses.

## Process

## Референс = скриншот от клиента (A3, обязательное правило)

Источник того, как сайт должен выглядеть, — **скриншот и/или текстовое
описание ОТ КЛИЕНТА**. Ссылка на живой сайт — только подсказка, никогда
единственный источник (спека reference-driven flow §2.3):

1. На этапе сбора у клиента **запрашиваются скриншоты** (вход первого класса,
   наравне с прототипом).
2. Ссылка недоступна (бот-защита/403/гео/авторизация) → агент **обязан
   запросить у клиента скриншот**. Молча пропустить референс или выдумать
   стиль — дефект. Реальный провал: Mercedes за CloudFront → 403, текстовый
   пересказ наврал про «белый/без засечек», по скриншоту — чёрный фон, serif,
   синие кнопки-пилюли.
3. **Палитра и шрифты снимаются с пикселей скриншота** (extract-palette →
   refs-palette.html), не с текстового пересказа и не «на глаз».
4. Если клиент дал референс на конкретный блок с пометкой «бери раскладку» —
   зафиксируй в index.yaml поле `take: design|layout|both`
   (см. docs/standards/reference-driven-rules.md §3).

1. Ask user for references: URLs to sites, Behance / Dribbble files, drag-drop screenshots into `03_РЕФЕРЕНСЫ/refs/`.
2. For each URL, capture screenshot if possible (Phase 5 will add headless browser support; Phase 2 stores URL only).
3. For each reference, prompt user for status: candidate / approved / rejected.
4. Maintain `03_РЕФЕРЕНСЫ/index.yaml` via `python3 skills/references-collection/scripts/index.py add|update|list`.
5. **HARD GATE**: minimum 3 references with status `approved` before moodboard-composer takes over.

## Tools

Bash, Read, Write, Glob. Calls index.py.

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — обязательный input. Поле `visual_notes` каждого конкурента читать перед поиском референсов: не клонировать визуал лидеров категории, искать gaps.
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — Section 6 (red flags) обязательна к проверке. При оценке любого референса (от пользователя или moodboard-composer) сравнивать с red flags. Референсы, попадающие в запреты, отвергать со ссылкой на конкретный пункт visual-requirements.md.
