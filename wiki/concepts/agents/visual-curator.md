---
type: agent
name: visual-curator
sources: ["agents/visual-curator.md"]
updated: 2026-05-15
triggers: ["/landing-visuals", "сгенерировать иконки", "создать инфографику", "заполнить визуальные слоты"]
stage: "07d"
uses: ["icon-generator", "infographic-builder", "block-composition", "landing-visuals"]
tags: ["visual", "icons", "infographics", "codex", "stage-07d", "pr-c"]
---

# Visual Curator — оркестратор визуальной генерации (этап 07d)

## Что делает

Сканирует `composed.html` на наличие слотов для иконок и инфографики, запускает AI-генерацию через codex, кэширует результаты и вставляет готовые PNG обратно в сборку. После работы агента все плейсхолдеры вида `[SLOT: feature-1-icon]` заменяются реальными изображениями.

## Когда вызывать / в каком этапе

Этап **07d**, запускается командой `/landing-visuals` после того, как выполнены:
- Этап 05 (дизайн-система) утверждён — `stages.05_design.status == approved`
- Файл `07b_COMPOSED/composed.html` существует (этап PR-A выполнен)

Если одно из условий не выполнено, агент завершает работу с русским сообщением об ошибке и не идёт дальше.

Поддерживаются флаги:
- `--type icons` / `--type infographics` — частичный прогон
- `--force` — игнорировать кэш
- `--slot <name>` — обработать один конкретный слот

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — сборка с плейсхолдерами иконок и инфографики
- `tokens.json` — цвета бренда (используются при генерации)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ниша проекта (контекст для промптов)
- `.cache/` — кэш по hash(hint + style + brand_color + niche)

**Выход:**
- `07d_VISUALS/icons/*.png` — сгенерированные иконки
- `07d_VISUALS/infographics/*.png` — сгенерированная инфографика
- `07d_VISUALS/_slots.yaml` — список обнаруженных слотов
- `07d_VISUALS/STATE.yaml` — статус каждой стадии (scan / generate / inject)
- Обновлённый `07b_COMPOSED/composed.html` с вставленными `<img class="lp-icon">`

## Связанные концепты

- [[icon-generator]] — субагент для генерации одной иконки PNG через codex image_gen
- [[infographic-builder]] — субагент для генерации одной инфографики PNG через codex image_gen
- [[block-composition]] — скилл, чей `compose-blocks.py` выполняет финальную инъекцию PNG в composed.html
- [[landing-visuals]] — slash-команда, триггерящая этот агент
- [[ux-composer]] — создаёт wireframe с исходными слотами (этап 07a)
- [[block-composer]] — создаёт composed.html с плейсхолдерами (этап 07b)

## Источник

- `agents/visual-curator.md`