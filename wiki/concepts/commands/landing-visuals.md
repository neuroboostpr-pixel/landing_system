---
type: command
name: landing-visuals
sources: ["commands/landing-visuals.md"]
updated: 2026-05-20
triggers:
  - "сгенерируй иконки для лендинга"
  - "добавь инфографику в composed.html"
  - "запусти генерацию визуалов"
  - "заполни слоты иконок"
stage: "07d"
uses:
  - visual-curator
  - icon-generator
  - infographic-builder
  - landing-compose
  - landing-go
tags: [icons, infographics, codex, image-gen, stage-07d]
---

# /landing-visuals — Генерация иконок и инфографики (этап 07d)

## Что делает

Команда автоматически создаёт PNG-иконки и инфографику для всех пустых визуальных слотов в `composed.html`. Картинки генерируются через codex image_gen в стиле бренда проекта (цвета из `tokens.json`, ниша из `market-profile.md`). После завершения все плейсхолдеры `[SLOT: ...]` в `composed.html` заменяются на реальные теги `<img>`.

## Когда вызывать / в каком этапе

**Этап 07d.** Вызывается вручную или автоматически через `/landing-go`.

Перед запуском обязательно должны быть выполнены:
1. Этап 05 (`DESIGN.md`) утверждён (`status == approved`) — без `tokens.json` codex не попадёт в стиль бренда.
2. Файл `07b_COMPOSED/composed.html` существует — его создаёт `/landing-compose` (PR-A).

Поддерживает флаги: `--type icons|infographics` (частичный прогон), `--force` (игнорировать кэш), `--slot <name>` (один слот), `--project <slug>` (другой проект).

## Что на вход / на выход

**На вход:**
- `07b_COMPOSED/composed.html` — с плейсхолдерами `data-slot type="icon"` и `type="infographic"`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета бренда
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ниша (для стиля промптов)

**На выход (папка `07d_VISUALS/`):**
- `_slots.yaml` — найденные слоты
- `icons/<slot-name>.png` — сгенерированные иконки
- `infographics/<slot-name>.png` — сгенерированная инфографика
- `.cache/<hash>.png` — кэш по hash(hint+style+brand_color+niche)
- `prompts.yaml` — лог промптов с attribution
- `STATE.yaml` — статусы генерации

**Побочный эффект:** `07b_COMPOSED/composed.html` перерендерится — плейсхолдеры заменятся на `<img class="lp-icon">` / `<img class="lp-infographic">`.

## Связанные концепты

- [[visual-curator]] — агент-оркестратор этапа 07d: сканирует слоты, управляет кэшем, диспатчит генераторы
- [[icon-generator]] — генерирует один PNG иконки через codex image_gen
- [[infographic-builder]] — генерирует одну инфографику через codex image_gen
- [[landing-compose]] — предшествующий этап 07b, создаёт `composed.html` с плейсхолдерами
- [[landing-go]] — главная команда оркестратора, вызывает landing-visuals автоматически

## Источник

- `commands/landing-visuals.md`