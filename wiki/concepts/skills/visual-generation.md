---
type: skill
name: visual-generation
sources: ["skills/visual-generation/SKILL.md"]
updated: 2026-05-15
triggers: ["/landing-visuals", "сгенерируй иконки", "создай инфографику", "запусти визуалы"]
stage: "07d"
uses: ["visual-curator", "block-composition", "design-tokens-generation", "landing-visuals"]
tags: ["visuals", "icons", "infographics", "codex", "image-gen", "stage-07d", "pr-c"]
---

# Visual Generation — конвейер генерации иконок и инфографики

## Что делает

Автоматически генерирует иконки и инфографику через codex image_gen и подставляет их в `composed.html` вместо текстовых плейсхолдеров. Брендинг берётся из `tokens.json`, тематика — из профиля ниши.

## Когда вызывать / в каком этапе

**Этап 07d (PR-C).** Вызывается командой `/landing-visuals` после того, как:
- этап 05 (design-system) утверждён,
- файл `07b_COMPOSED/composed.html` существует (результат PR-A).

Поддерживает флаги: `--type icons`, `--type infographics`, `--force` (обход кэша), `--slot <name>` (один слот).

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — плейсхолдеры вида `[SLOT: feature-1-icon]`
- `tokens.json` — цвета и стиль бренда
- `market-profile.md` — ниша проекта
- `07d_VISUALS/_slots.yaml` — список слотов (генерируется автоматически на шаге scan)

**Выход:**
- `07d_VISUALS/.cache/<hash>.png` — сгенерированные PNG (кэшированные по hash)
- `07d_VISUALS/STATE.yaml` — состояние прогона (scan / generate / inject)
- `07b_COMPOSED/composed.html` — обновлённый файл с реальными `<img class="lp-icon">` вместо плейсхолдеров

## Детали работы

Конвейер состоит из трёх шагов:

1. **scan** — `scripts/slot-scanner.py` парсит `composed.html` и выдаёт список icon/infographic слотов в `_slots.yaml`.
2. **generate** — для каждого слота запускается `scripts/codex-generate-icon.sh` или `-infographic.sh`. Перед вызовом codex проверяется кэш по hash(hint + style + brand_color + niche). Prompt-picker waterfall: иконки → icons.csv keyword match → generic template; инфографика → OpenDesign 90 JSON tag match → generic template.
3. **inject** — `inject-content.py` подставляет PNG в `composed.html`.

Перезапуск продолжает с прерванного — `STATE.yaml` фиксирует прогресс. Identity-safe правила **не применяются** — в иконках и чартах нет людей.

## Связанные концепты

- [[visual-curator]] — агент-оркестратор этого конвейера, управляет STATE.yaml и диспатчит генераторы
- [[block-composition]] — этап 07b, создаёт `composed.html` с плейсхолдерами, которые заполняет этот скилл
- [[design-tokens-generation]] — поставляет `tokens.json` с цветами бренда для промптов генерации
- [[landing-visuals]] — команда-точка входа (`/landing-visuals`)
- [[icon-generator]] — субагент для генерации одной иконки
- [[infographic-builder]] — субагент для генерации одной инфографики

## Источник

- `skills/visual-generation/SKILL.md`