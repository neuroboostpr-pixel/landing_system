---
description: Collect and curate visual references for a landing project (stage 03). Run within a landing project folder after stage 01 is complete.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-references

## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage 03_references --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage 03_references --project <project> --approve`

Run within a landing project at any time after stage 01.

## What I do

1. Invoke `references-curator` agent to collect and tag visual references.
2. Maintain `03_РЕФЕРЕНСЫ/index.yaml` with status (`candidate` / `approved` / `rejected`) for each reference.
3. After user selects approved references, render `03_РЕФЕРЕНСЫ/moodboard.html` via `moodboard-composer`.
4. **HARD GATE**: present `moodboard.html` path, wait for explicit approval before continuing to stage 04.

## Usage

Run: `/landing-references`

Then follow the agent prompts to add reference URLs or files.

## Output

- `03_РЕФЕРЕНСЫ/index.yaml` — reference registry
- `03_РЕФЕРЕНСЫ/moodboard.html` — visual moodboard preview

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

