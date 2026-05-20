---
type: command
name: landing-visuals
sources: ["commands/landing-visuals.md"]
updated: 2026-05-20
triggers:
  - "сгенерируй иконки для лендинга"
  - "нарисуй инфографику"
  - "заполни визуальные слоты"
  - "запусти генерацию иконок"
  - "visual-curator запусти"
stage: "07d"
uses:
  - visual-curator
  - icon-generator
  - infographic-builder
  - landing-compose
  - landing-go
tags: [visuals, icons, infographics, codex, stage-07d, pr-c]
---

# /landing-visuals — Генерация иконок и инфографики (Этап 07d)

## Что делает

Автоматически создаёт иконки и инфографику для всех визуальных слотов в `composed.html` — через codex image_gen с учётом бренд-токенов и ниши проекта. Все placeholders `[SLOT: ...]` заменяются реальными PNG-файлами прямо в `composed.html`.

## Когда вызывать / в каком этапе

Этап **07d** (PR-C). Запускать после того, как:
1. Дизайн-система утверждена (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`, статус `approved` в `.landing-state.yaml`) — без `tokens.json` стиль генерации не задан.
2. Файл `07b_COMPOSED/composed.html` существует — его создаёт `/landing-compose`.

Рекомендуется вызывать через `/landing-go` (оркестратор сам выберет момент). Ручной запуск: `/landing-visuals [--type icons|infographics] [--force] [--slot <name>]`.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — собранная страница со слотами `data-slot type="icon"` и `type="infographic"`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета и стиль бренда
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ниша (влияет на стиль промптов)

**Выход** (в папке `07d_VISUALS/`):
- `_slots.yaml` — список найденных слотов
- `icons/<slot-name>.png` — сгенерированные иконки
- `infographics/<slot-name>.png` — инфографика
- `.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche)
- `prompts.yaml` — лог промптов с attribution
- `STATE.yaml` — статусы выполнения

**Результат:** `07b_COMPOSED/composed.html` перерендерится — placeholders заменятся на `<img class="lp-icon">` и `<img class="lp-infographic">`.

## Связанные концепты

- [[visual-curator]] — агент-оркестратор этапа: сканирует слоты, управляет кэшем, диспатчит генераторы
- [[icon-generator]] — генерирует одну иконку PNG через codex image_gen
- [[infographic-builder]] — генерирует одну инфографику PNG через codex image_gen
- [[landing-compose]] — предшествующий этап 07b, создаёт composed.html с placeholder-слотами
- [[landing-go]] — главная точка входа, автоматически вызывает landing-visuals в нужный момент

## Источник

- `commands/landing-visuals.md`