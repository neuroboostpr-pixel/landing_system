---
type: command
name: landing-visuals
sources: ["commands/landing-visuals.md"]
updated: 2026-05-15
triggers:
  - "сгенерировать иконки и инфографику"
  - "запустить генерацию визуалов"
  - "заполнить слоты иконок в лендинге"
  - "/landing-visuals"
stage: "07d"
uses:
  - visual-curator
  - icon-generator
  - infographic-builder
  - block-composition
  - design-tokens-generation
tags:
  - pr-c
  - visual-generation
  - codex
  - icons
  - infographics
---

# /landing-visuals — генерация иконок и инфографики

## Что делает

Автоматически генерирует PNG-иконки и инфографику для лендинга через codex image_gen, встраивает их в `composed.html` вместо текстовых плейсхолдеров. Стиль генерации согласован с брендом: цвета берутся из `tokens.json`, тематика — из профиля ниши.

## Когда вызывать / в каком этапе

**Stage 07d (PR-C).** Вызывается вручную после того, как:

1. Дизайн-система утверждена (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`, статус `approved` в `.landing-state.yaml`).
2. Файл `07b_COMPOSED/composed.html` существует (создаётся командой `/landing-compose`).

До PR-D команда **не встроена** в `landing-orchestrator` — запускается отдельно.

Поддерживает флаги:
- `--type icons` / `--type infographics` — частичный прогон;
- `--force` — сброс кэша;
- `--slot <name>` — один слот.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` с data-слотами `type="icon"` и `type="infographic"`.
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета бренда для промптов.
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — тематика ниши.
- Опционально: `07d_VISUALS/.cache/` — хэш-кэш предыдущих генераций.

**Выход (в `07d_VISUALS/`):**
- `_slots.yaml` — список найденных слотов.
- `icons/<slot>.png` — сгенерированные иконки.
- `infographics/<slot>.png` — сгенерированная инфографика.
- `.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche).
- `prompts.yaml` — лог промптов с attribution.
- `STATE.yaml` — статусы этапов.
- Обновлённый `07b_COMPOSED/composed.html` — плейсхолдеры `[SLOT: ...]` и `[INFOGRAPHIC: ...]` заменены на `<img class="lp-icon">` / `<img class="lp-infographic">`.

## Связанные концепты

- [[visual-curator]] — агент-оркестратор, сканирует слоты, управляет кэшем, диспатчит субагентов.
- [[icon-generator]] — генерирует один PNG-иконки через codex.
- [[infographic-builder]] — генерирует одну инфографику через codex.
- [[block-composition]] — re-render composed.html после замены плейсхолдеров.
- [[design-tokens-generation]] — поставляет `tokens.json` с цветами бренда.

## Источник

- `commands/landing-visuals.md`