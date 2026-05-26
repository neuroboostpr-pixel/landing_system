---
slug: design-system-generator
type: agent
name: "Генератор дизайн-системы"
stage: "05"
tags: [design, tokens, css, brand, preview]
triggers: [landing-design]
inputs: [04_БРЕНД/brand-kit.md]
outputs: [05_ДИЗАЙН-СИСТЕМА/DESIGN.md, 05_ДИЗАЙН-СИСТЕМА/tokens.json, 05_ДИЗАЙН-СИСТЕМА/design-preview.html]
gates: [design_approved]
pre_reqs: [brand-architect]
related: [design-tokens-generation, brand-architect, landing-orchestrator]
sources: ["agents/design-system-generator.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Генератор дизайн-системы

## Что делает

Принимает утверждённый `brand-kit.md` со этапа 04 и строит полную дизайн-систему проекта с провенансом токенов. Запускает скрипт `build-tokens.py`, извлекающий цвета, шрифты, отступы, grid, радиусы, тени, брейкпоинты и motion из бренд-кита. Затем генерирует живой HTML-превью через `render-preview.py`, чтобы пользователь мог визуально проверить систему до старта кодинга. Этап не закрывается без явного человеческого утверждения.

## Когда вызывается

Запускается командой `/landing-design` после того, как `brand-architect` завершил этап 04 и `brand-kit.md` утверждён. Оркестратор передаёт управление агенту, когда `.landing-state.yaml` показывает `current_stage == 05_design`. Gate-check должен вернуть exit 0 — иначе агент останавливается до решения проблем предшественника.

## Вход → выход

**Вход:** `04_БРЕНД/brand-kit.md` с описанием цветов, типографики, иконок, motion и сетки. Обязателен флаг `approved` у этапа 04 в `.landing-state.yaml`.

**Выход:** `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` (единый источник истины токенов с YAML frontmatter), `tokens.json` (машиночитаемые токены для сборки темы), `design-preview.html` (живые компоненты для визуальной проверки).

## Чем закрывается этап (gates)

- `design_approved` — пользователь явно написал «утверждаю», «ok» или «дальше» после просмотра `design-preview.html`. Без этого переход к этапу 06 заблокирован.

## Failure modes

- `build-tokens.py` падает, если `brand-kit.md` не содержит обязательных секций (цвета, шрифты) — проверить полноту бренд-кита у `brand-architect`.
- Stage gate enforcement (`enforce_stage_gate.py`) блокирует Write/Edit, если этап 04 не закрыт — не обходить, закрывать предшественника.
- `render-preview.py` генерирует пустой превью при отсутствии `tokens.json` — убедиться что `build-tokens.py` завершился успешно до вызова рендера.
- Агент ошибочно продолжает к этапу 06 без ожидания явного approve — HARD GATE обязателен, нельзя трактовать молчание как согласие.
- Токены записаны без провенанса (поле `source` пустое) — нарушает traceability, `build-tokens.py` должен копировать ссылки из brand-kit секций.

## Related

- [[brand-architect]] — предшественник: создаёт `brand-kit.md`, без него нет входных данных
- [[design-tokens-generation]] — skill, которому принадлежит агент; содержит `build-tokens.py` и `render-preview.py`
- [[landing-orchestrator]] — вызывает агента в рамках общего pipeline после approve этапа 04