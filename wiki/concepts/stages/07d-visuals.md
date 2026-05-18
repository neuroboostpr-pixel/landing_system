---
type: stage
name: 07d-visuals
sources: ["template/07d_VISUALS/README.md"]
updated: 2026-05-15
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation", "landing-visuals", "block-composer", "landing-compose"]
tags: ["icons", "infographics", "codex", "image-gen", "visual", "ai-generation"]
---

# 07d VISUALS — AI-генерация иконок и инфографики

## Что делает
Генерирует PNG-иконки и инфографику для лендинга через codex (gpt-image-2), вставляет их в `composed.html` вместо текстовых плейсхолдеров. Брендинг берётся автоматически из `tokens.json` и `market-profile.md` проекта.

## Когда вызывать / в каком этапе
Этап 07d — после того как утверждён этап 05 (design-system) и сформирован `07b_COMPOSED/composed.html` (этап 07b/07c). Запускается командой `/landing-visuals`. Повторный запуск использует кэш и не тратит API-токены на уже сгенерированные слоты.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — скомпонованный лендинг с плейсхолдерами `[SLOT: ...]` типа `data-slot-type="icon"` и `data-slot-type="infographic"`
- `tokens.json` — цвета и стиль проекта
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ниша для подбора визуального стиля

**Выход:**
- `icons/<slot-name>.png` — сгенерированные иконки
- `infographics/<slot-name>.png` — сгенерированная инфографика
- `_slots.yaml` — реестр найденных слотов (авто)
- `prompts.yaml` — аудит: промпт → PNG (attribution)
- `STATE.yaml` — статус каждого слота
- `.cache/<hash>.png` — локальный кэш по `hash(hint + style + brand_color + niche)`
- `.logs/` — лог запросов codex
- Обновлённый `composed.html` — плейсхолдеры заменены на `<img>`

**Кэш:** повторный вызов без `--force` пропускает уже сгенерированные слоты. Опции: `--force`, `--type icons|infographics`, `--slot <name>`.

**Ограничение:** PNG в `icons/` и `infographics/` не редактировать вручную — `--force` перезапишет. Папку `.cache/` не коммитить в git.

## Связанные концепты
- [[visual-curator]] — агент-оркестратор этапа 07d: сканирует слоты, диспатчит генераторы, управляет STATE.yaml
- [[visual-generation]] — скилл AI-генерации: промпт-пикер, хэш-кэш, вызов codex image_gen
- [[landing-visuals]] — slash-команда запуска этапа 07d
- [[block-composer]] — создаёт `composed.html` на этапе 07b (входной артефакт для 07d)
- [[landing-compose]] — команда этапа 07b, предшествующая 07d
- [[icon-generator]] — субагент генерации одной иконки
- [[infographic-builder]] — субагент генерации одной инфографики

## Источник
- `template/07d_VISUALS/README.md`