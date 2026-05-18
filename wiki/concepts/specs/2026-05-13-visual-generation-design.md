---
type: stage
name: stage-07d-visuals
sources: ["docs/superpowers/specs/2026-05-13-visual-generation-design.md"]
updated: 2026-05-18
triggers: []
stage: "07d"
uses:
  - visual-curator
  - icon-generator
  - infographic-builder
  - visual-generation
  - landing-visuals
  - block-composer
  - design-tokens-generation
  - niche-analysis
tags: [pr-c, icons, infographics, codex, image-gen, composed-html]
---

# PR-C — Генерация иконок и инфографики (Stage 07d)

## Что делает

Автоматически генерирует PNG-иконки и инфографику через codex `image_gen` и подставляет их в `composed.html` вместо placeholder-заглушек вида `[SLOT: feature-1-icon]`. Цвета и стиль визуалов берутся из `tokens.json` — иконки точно попадают в дизайн-систему проекта.

## Когда вызывать / в каком этапе

Этап **07d** — после того как утверждена дизайн-система (`05_design.approved == true`) и существует `07b_COMPOSED/composed.html` (PR-A). Запускается вручную командой `/landing-visuals`. PR-B (фотографии) **не требуется** — PR-C независим.

Опциональные флаги:
- `--type icons` / `--type infographics` — прогон только одного типа
- `--force` — игнорировать кэш, перегенерить всё
- `--slot <name>` — только один конкретный слот

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — HTML с разметкой `data-slot type="icon"` и `data-slot type="infographic"`
- `05_ДИЗАЙН/tokens.json` — цвета (`colors.accent`, `design.icon_style`, `design.visual_style`)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ниша для параметризации промптов

**Выход:**
- `07d_VISUALS/icons/<slot-name>.png` — прозрачные PNG-иконки
- `07d_VISUALS/infographics/<slot-name>.png` — PNG-инфографика
- `07d_VISUALS/_slots.yaml` — список найденных слотов
- `07d_VISUALS/STATE.yaml` — статус генерации (scan / generate / inject)
- `07d_VISUALS/.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche)
- `07b_COMPOSED/composed.html` — перерендеренный с `<img src="...">` вместо заглушек

## Связанные концепты

- [[visual-curator]] — агент-оркестратор: сканирует слоты, диспатчит sub-агентов, управляет STATE.yaml и inject
- [[icon-generator]] — суб-агент: генерирует один PNG-иконку через codex image_gen
- [[infographic-builder]] — суб-агент: генерирует один PNG-инфографику через codex image_gen
- [[visual-generation]] — skill: содержит шаблоны промптов, prompt-picker, кэш-скрипты, slot-scanner
- [[landing-visuals]] — slash-команда, точка входа пользователя
- [[block-composer]] — создаёт composed.html (PR-A), чей артефакт PR-C расширяет
- [[design-tokens-generation]] — поставляет tokens.json с цветами для промптов
- [[niche-analysis]] — поставляет market-profile.md с нишей для параметризации

## Источник

- `docs/superpowers/specs/2026-05-13-visual-generation-design.md`