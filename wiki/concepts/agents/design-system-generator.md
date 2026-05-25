---
type: agent
name: design-system-generator
sources: ["agents/design-system-generator.md"]
updated: 2026-05-25
triggers: []
stage: "05"
uses: ["brand-architect", "design-tokens-generation", "landing-orchestrator"]
tags: ["design", "tokens", "stage-05", "dизайн-система"]
---

# design-system-generator (Генератор дизайн-системы)

## Что делает

Берёт готовый бренд-кит маркетолога и автоматически строит полную дизайн-систему: набор токенов (цвета, шрифты, отступы, сетка, анимации), единый документ-справочник `DESIGN.md` и живой HTML-превью со всеми компонентами.

## Когда вызывать / в каком этапе

Этап **05_design**. Запускается после того, как [[brand-architect]] завершил этап 04 и создал `04_БРЕНД/brand-kit.md`. Агент сам проверяет `.landing-state.yaml` — если `current_stage != 05_design`, он останавливается и сообщает об этом.

Перед любым действием агент обязан:
1. Прочитать `.landing-state.yaml` и показать Mermaid-карту пайплайна.
2. Выполнить `gate-check.sh --stage 05_design` (exit 0 обязателен).
3. Создать TodoWrite со всеми оставшимися этапами.

После генерации агент ждёт явного подтверждения пользователя (`утверждаю`, `ok`, `дальше`) — это **HARD GATE** перед переходом к этапу 06.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — бренд-кит с цветами, шрифтами, иконками, стилистикой
- `.landing-state.yaml` — состояние проекта (для gate-check)

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины: все токены с провенансом (traceability), YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены для инструментов (билдер темы, compose-агент)
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — интерактивный HTML с живыми компонентами по токенам

**Токены включают:** цвета (primary/secondary/accent/text/bg), типографику (display/body/sizes), отступы (xs–3xl), сетку (columns/gap/max_width), радиусы, тени, брейкпоинты, motion (duration_fast/base/slow, easing).

## Связанные концепты

- [[brand-architect]] — предшественник: генерирует `brand-kit.md`, который является входом для этого агента
- [[design-tokens-generation]] — скилл-владелец: предоставляет скрипты `build-tokens.py` и `render-preview.py`
- [[landing-orchestrator]] — вызывает агента в составе общего пайплайна через `/landing-go`

## Источник

- `agents/design-system-generator.md`