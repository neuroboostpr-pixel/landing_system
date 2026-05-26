---
type: command
name: landing-visuals
sources: ["commands/landing-visuals.md"]
updated: 2026-05-26
triggers:
  - "сгенерируй иконки для лендинга"
  - "создай инфографику"
  - "нужны визуалы для composed.html"
  - "запусти генерацию иконок"
  - "stage 07d"
stage: "07d"
uses:
  - visual-curator
  - landing-compose
  - landing-design
  - landing-go
tags:
  - visuals
  - icons
  - infographics
  - codex
  - pr-c
---

# landing-visuals — генерация иконок и инфографики

## Что делает

Автоматически создаёт иконки и инфографику для всех визуальных слотов в `composed.html` — средствами AI-генерации через codex image_gen. Стиль подбирается под бренд проекта: цвета из `tokens.json`, ниша из `market-profile.md`.

## Когда вызывать / в каком этапе

Этап **07d** (PR-C). Вызывается после того, как:
1. Утверждена дизайн-система (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`, статус `approved`).
2. Существует `07b_COMPOSED/composed.html` (этап PR-A выполнен через `/landing-compose`).

Запускается автоматически через `/landing-go` (рекомендуется) или вручную командой `/landing-visuals`.

**Флаги для частичного запуска:**
- `--type icons` / `--type infographics` — только один тип визуалов.
- `--slot <name>` — один конкретный слот.
- `--force` — игнорировать кэш и перегенерить всё.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — файл с плейсхолдерами `[SLOT: ...]` и `[INFOGRAPHIC: ...]`.
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета и стили бренда.
- `.landing-state.yaml` — статус этапов и параметры проекта.

**Выход (в папке `07d_VISUALS/`):**
- `_slots.yaml` — список найденных слотов.
- `icons/<slot-name>.png` — сгенерированные иконки.
- `infographics/<slot-name>.png` — сгенерированная инфографика.
- `.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche).
- `prompts.yaml` — лог промптов с attribution.
- `STATE.yaml` — статусы этапов.

**Результат:** `07b_COMPOSED/composed.html` перерендерится — плейсхолдеры заменятся на реальные теги `<img class="lp-icon">` / `<img class="lp-infographic">`.

## Связанные концепты

- [[visual-curator]] — агент, которого диспатчит команда; управляет генерацией и кэшированием
- [[landing-compose]] — создаёт `composed.html` (обязательный предшественник)
- [[landing-design]] — создаёт `tokens.json` с цветами бренда (обязательный предшественник)
- [[landing-go]] — рекомендуемая точка входа; запускает 07d автоматически в нужный момент

## Источник

- `commands/landing-visuals.md`