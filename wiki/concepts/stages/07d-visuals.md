---
type: stage
name: 07d-visuals
sources: ["template/07d_VISUALS/README.md"]
updated: 2026-05-25
triggers: []
stage: "07d"
uses: ["landing-visuals", "07b-composed"]
tags: ["visuals", "icons", "infographics", "codex", "ai-generation"]
---

# 07d VISUALS — AI-генерация иконок и инфографики

## Что делает

Автоматически генерирует иконки и инфографику для лендинга с помощью AI (codex / gpt-image-2) в стиле бренда — цвета, ниша, настроение берутся из токенов проекта. Готовые PNG встраиваются прямо в `composed.html`, заменяя визуальные плейсхолдеры.

## Когда вызывать / в каком этапе

Этап **07d**, запускается командой `/landing-visuals` после того, как утверждён этап 05 (design-system) и готов `07b_COMPOSED/composed.html`. Вызывается вручную — не через `landing-orchestrator`. Вход в этап: наличие слотов `data-slot-type="icon"` или `data-slot-type="infographic"` в `composed.html`.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — источник слотов для генерации
- `tokens.json` + `market-profile.md` — бренд-параметры (цвет, ниша, стиль)
- `skills/visual-generation/templates/` — шаблоны промптов

**Выход:**
- `07d_VISUALS/icons/<slot-name>.png` — сгенерированные иконки
- `07d_VISUALS/infographics/<slot-name>.png` — сгенерированная инфографика
- `07d_VISUALS/_slots.yaml` — список найденных слотов (авто)
- `07d_VISUALS/prompts.yaml` — лог: промпт → PNG (для аудита)
- `07d_VISUALS/.cache/<hash>.png` — кэш по `hash(hint + style + brand_color + niche)`
- `07d_VISUALS/STATE.yaml` — статусы этапа
- `07d_VISUALS/.logs/` — полные промпты и ответы codex
- Обновлённый `composed.html` — плейсхолдеры `[SLOT: ...]` заменены на `<img>`

## Ключевые правила

- **Кэш**: повторный запуск не тратит API — берёт из `.cache/` по хешу параметров. Для полного перегенерирования — флаг `--force`.
- **Частичный запуск**: `--type icons` / `--type infographics` / `--slot <name>` — пересобрать только нужное.
- **Не редактировать PNG вручную** — `--force` перезапишет. Нужно изменить промпт — правь шаблон в `skills/visual-generation/templates/`.
- **`.cache/` не коммитить** в git — это локальный кэш для экономии API.
- **Identity-safe не применяется**: иконки и чарты не содержат людей, дополнительного подтверждения не требуется.

## Связанные концепты

- [[landing-visuals]] — slash-команда, запускающая генерацию на этом этапе
- [[07b-composed]] — источник слотов; после генерации перерендеривается с реальными PNG

## Источник

- `template/07d_VISUALS/README.md`