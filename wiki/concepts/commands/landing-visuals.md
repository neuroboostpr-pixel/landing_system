---
type: command
name: landing-visuals
sources: ["commands/landing-visuals.md"]
updated: 2026-05-25
triggers:
  - "сгенерировать иконки для лендинга"
  - "создать инфографику"
  - "запустить генерацию визуалов"
  - "заполнить слоты иконок в composed.html"
uses:
  - visual-curator
  - landing-compose
  - landing-go
tags: ["stage-07d", "PR-C", "visuals", "icons", "infographics", "codex"]
stage: "07d"
---

# /landing-visuals — Генерация иконок и инфографики

## Что делает

Автоматически создаёт иконки и инфографику для лендинга с помощью AI (codex image_gen) и встраивает их в готовую страницу `composed.html`. После запуска все визуальные заглушки заменяются на реальные изображения, оформленные в стиле бренда.

## Когда вызывать / в каком этапе

Этап **07d** (PR-C). Команда вызывается после того, как:

1. Этап **05 (дизайн-система)** утверждён — статус `approved` в `.landing-state.yaml`. Без `tokens.json` codex не знает цвета и стиль бренда.
2. Файл **`07b_COMPOSED/composed.html`** существует — то есть команда `/landing-compose` уже выполнена.

Запускается вручную через `/landing-visuals` или автоматически через `/landing-go` (рекомендуется).

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — страница со слотами `data-slot type="icon"` и `type="infographic"`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета и стиль бренда
- `market-profile.md` — ниша проекта (влияет на стиль генерации)

**Выход (в `07d_VISUALS/`):**
- `_slots.yaml` — список найденных слотов
- `icons/<slot-name>.png` — сгенерированные иконки
- `infographics/<slot-name>.png` — сгенерированная инфографика
- `.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche)
- `prompts.yaml` — лог промптов с атрибуцией
- `STATE.yaml` — статусы этапов

**Итог:** `07b_COMPOSED/composed.html` перерендерится — заглушки `[SLOT: ...]` и `[INFOGRAPHIC: ...]` заменяются на теги `<img class="lp-icon">` / `<img class="lp-infographic">`.

**Флаги:**
- `--type icons` / `--type infographics` — частичный прогон
- `--force` — игнорировать кэш, перегенерить всё
- `--slot <name>` — один конкретный слот

## Связанные концепты

- [[visual-curator]] — агент, который сканирует слоты, управляет кэшем и диспатчит icon-generator / infographic-builder
- [[landing-compose]] — предшествующий этап (07b), создаёт composed.html со слотами
- [[landing-go]] — главная точка входа, запускает 07d автоматически в нужный момент
- [[landing-design]] — этап 05, без него гейт не пройден

## Источник

- `commands/landing-visuals.md`