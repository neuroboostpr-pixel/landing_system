---
type: command
name: landing-visuals
sources: ["commands/landing-visuals.md"]
updated: 2026-05-26
triggers:
  - "сгенерировать иконки для лендинга"
  - "создать инфографику для лендинга"
  - "запустить генерацию визуалов"
  - "нужны иконки и инфографика для composed.html"
stage: "07d"
uses:
  - visual-curator
  - icon-generator
  - infographic-builder
  - landing-compose
  - landing-design
  - landing-go
tags:
  - visuals
  - icons
  - infographics
  - codex
  - stage-07d
  - pr-c
---

# /landing-visuals — Генерация иконок и инфографики (Stage 07d)

## Что делает

Автоматически создаёт иконки и инфографику для всех визуальных слотов в `composed.html` с помощью AI-генерации через codex. Генерируемые изображения подбираются под стиль бренда проекта — цвета и нишу — и вставляются прямо в страницу.

## Когда вызывать / в каком этапе

Этап **07d** — после того как утверждены дизайн-система (этап 05) и собран `composed.html` (этап 07b). Запускается вручную командой `/landing-visuals` или автоматически через `/landing-go`. Без approved этапа 05 и готового `composed.html` команда не запустится.

**Гейты перед запуском:**
- `.landing-state.yaml:stages.05_design.status == approved`
- `07b_COMPOSED/composed.html` существует в папке проекта

**Флаги:**
- `--type icons` / `--type infographics` — частичный прогон только одного типа
- `--force` — принудительная перегенерация, игнорируя кэш
- `--slot <name>` — обработка одного конкретного слота

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — с placeholder-слотами `[SLOT: ...]` и `[INFOGRAPHIC: ...]`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета и стиль бренда
- `01_БРИФ/market-profile.md` — ниша проекта (влияет на стиль генерации)

**Выход** (в папке `07d_VISUALS/`):
- `_slots.yaml` — список найденных слотов
- `icons/<slot-name>.png` — сгенерированные иконки
- `infographics/<slot-name>.png` — инфографика
- `.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche)
- `prompts.yaml` — лог промптов для атрибуции
- `STATE.yaml` — статус каждого слота

**Итог:** `07b_COMPOSED/composed.html` перерендерится — все placeholder-слоты заменяются на `<img class="lp-icon">` / `<img class="lp-infographic">`.

## Связанные концепты

- [[visual-curator]] — агент-оркестратор: сканирует слоты, диспатчит генераторы, обновляет composed.html
- [[icon-generator]] — субагент для генерации иконок через codex image_gen
- [[infographic-builder]] — субагент для генерации инфографики
- [[landing-compose]] — предшествующий этап 07b, создаёт composed.html с placeholder-слотами
- [[landing-design]] — предшествующий этап 05, создаёт tokens.json с цветами бренда
- [[landing-go]] — главная команда-оркестратор, включает 07d в общий pipeline

## Источник

- `commands/landing-visuals.md`