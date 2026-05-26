---
type: stage
name: 07d-visuals
sources: ["template/07d_VISUALS/README.md"]
updated: 2026-05-26
triggers: []
stage: "07d"
uses: ["landing-visuals", "07b-composed"]
tags: ["visuals", "icons", "infographics", "ai-generation", "codex"]
---

# 07d_VISUALS — AI-генерация иконок и инфографики

## Что делает

Этап автоматически генерирует иконки и инфографику для лендинга с помощью AI (codex / gpt-image-2). Готовые PNG создаются под брендинг проекта и вставляются вместо визуальных заглушек в макет.

## Когда вызывать / в каком этапе

Запускается командой `/landing-visuals` после того, как утверждён этап 05 (design-system) и готов `07b_COMPOSED/composed.html`. Вызывается вручную — не через `landing-orchestrator`. Этап расположен параллельно с этапом 07c (photos).

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — макет с placeholder-слотами `[SLOT: feature-1-icon]` и атрибутами `data-slot-type="icon"` / `data-slot-type="infographic"`
- `tokens.json` — цвета и стиль бренда
- `market-profile.md` — ниша проекта

**Выход:**
- `icons/<slot-name>.png` — сгенерированные иконки
- `infographics/<slot-name>.png` — сгенерированная инфографика
- `_slots.yaml` — список найденных слотов (авто)
- `prompts.yaml` — соответствие промпт → PNG (для аудита)
- `STATE.yaml` — статусы обработки слотов
- `.cache/<hash>.png` — локальный кэш генераций
- `.logs/` — логи запросов к codex
- Обновлённый `composed.html` — placeholders заменены на `<img>`

**Кэш:** повторный запуск не вызывает codex API для уже сгенерированных слотов. Для принудительной перегенерации — флаг `--force`.

**Опциональные флаги:**
- `--type icons` / `--type infographics` — частичный прогон
- `--slot <name>` — один конкретный слот
- `--force` — игнорировать кэш

**Важно:** не редактировать PNG вручную — `--force` перезапишет. Не коммитить `.cache/` в git.

## Связанные концепты

- [[landing-visuals]] — команда, которая запускает этот этап
- [[07b-composed]] — источник слотов; composed.html обновляется после генерации

## Источник

- `template/07d_VISUALS/README.md`