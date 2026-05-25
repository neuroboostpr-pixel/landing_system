---
type: skill
name: visual-generation
sources: ["skills/visual-generation/SKILL.md"]
updated: 2026-05-25
triggers: ["/landing-visuals"]
stage: "07d"
uses: ["landing-visuals", "landing-compose", "landing-design", "landing-orchestrator"]
tags: ["visuals", "icons", "infographics", "codex", "image-gen", "pr-c"]
---

# Visual Generation — Генерация иконок и инфографики (этап 07d)

## Что делает
Автоматически генерирует иконки и инфографику для лендинга через codex image_gen, подбирая стиль под бренд-токены и нишу. Подставляет готовые PNG прямо в `composed.html` вместо placeholders.

## Когда вызывать / в каком этапе
Запускается командой `/landing-visuals` на этапе **07d** (PR-C). Обязательные условия: утверждённый этап **05** (design-system) и существующий файл `07b_COMPOSED/composed.html`. Вызывается вручную, не через оркестратор (интеграция — задача PR-D).

Опциональные флаги:
- `--type icons` или `--type infographics` — частичный прогон
- `--force` / `FORCE=1` — игнорировать кэш
- `--slot <name>` — один конкретный слот

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — с placeholders вида `[SLOT: feature-1-icon]`
- `tokens.json` — цвета и стиль бренда
- `market-profile.md` — ниша проекта

**Выход:**
- `07d_VISUALS/_slots.yaml` — список обнаруженных слотов (icon/infographic)
- `07d_VISUALS/.cache/<hash>.png` — кэш сгенерированных PNG по hash(hint + style + brand_color + niche)
- `07d_VISUALS/STATE.yaml` — прогресс прогона (scan / generate / inject)
- `07b_COMPOSED/composed.html` — обновлённый: `[SLOT: ...]` заменены на `<img class="lp-icon">`

**Три шага конвейера:**
1. **scan** — `scripts/slot-scanner.py` парсит `composed.html`, выдаёт `_slots.yaml`
2. **generate** — `scripts/codex-generate-icon.sh` / `-infographic.sh` с кэш-lookup перед вызовом codex
3. **inject** — `inject-content.py` подставляет PNG в composed.html

**Prompt-picker waterfall:**
- Иконки: keyword-матч по `icons.csv` → generic template
- Инфографика: tag/category-матч по OpenDesign 90 JSON → generic template

## Связанные концепты
- [[landing-visuals]] — slash-команда, которая вызывает этот скилл
- [[landing-compose]] — этап 07b, создаёт `composed.html` с placeholders, который этот скилл заполняет
- [[landing-design]] — этап 05, design-system должен быть approved перед запуском
- [[landing-orchestrator]] — оркестратор, который в будущем (PR-D) будет диспатчить этот скилл автоматически

## Источник
- `skills/visual-generation/SKILL.md`