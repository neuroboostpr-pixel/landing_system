---
description: Stage 07b — assemble composed.html with design-tokens injected and prototype content substituted. Visual placeholders remain.
---

# /landing-compose

Запускает этап **07b_COMPOSED**.

## Что делает

1. Проверяет наличие `07_ПРОТОТИП/prototype.yaml` и `05_ДИЗАЙН-СИСТЕМА/tokens.json`.
2. Передаёт работу агенту `block-composer`.
3. Сообщает путь к артефакту.

## Артефакты

- `07b_COMPOSED/composed.html`
- `07b_COMPOSED/composed-mobile.html`
- `07b_COMPOSED/block-injection-log.md`

## Условия запуска

- tokens.json в `05_ДИЗАЙН-СИСТЕМА/` существует

## Запуск

Автоматически через `/landing-go` (рекомендуется) или вручную этой командой.
Финальный визуальный контент (фото/иконки/инфографика) добавляют этапы 07c/07d (`/landing-photos`, `/landing-visuals`).

## Стандарты этапа

- [`docs/standards/reference-driven-rules.md`](../docs/standards/reference-driven-rules.md) —
  правило трёх источников, поблочная сверка, composed.html = единственная правда о виде.
- Агент РИСУЕТ макет (коллаж, глубина), а не склеивает готовые блоки.
- **ПАНЕЛЬ МУДОВ — ОБЯЗАТЕЛЬНА в composed.html** (premium-07b-checklist §12.5):
  переключатель дизайн-систем (референсы проекта из `references-index.md` + 6
  системных `_styles/`), чтобы видеть лендинг в разных палитрах ДО публикации.
  Единый источник мудов с WP-плагином `lp-preview-panel` (превью и прод не расходятся).
  Флаг on/off (`data-preview`): едет на тестовый сайт включённой, перед продом — выкл.
  Работает только при 100% токенизации. См. reference-driven-flow-spec §2.5.
