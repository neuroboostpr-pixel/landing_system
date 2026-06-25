---
description: Stage 07b — assemble composed.html with design-tokens injected and prototype content substituted. Visual placeholders remain.
---

# /landing-compose

Запускает этап **07b_COMPOSED**.

## Что делает

1. Проверяет наличие активного прототипа (`07_ПРОТОТИП/prototype-*.yaml` с `meta.active: true`) и `05_ДИЗАЙН-СИСТЕМА/tokens.json`.
2. **Если есть `07b_COMPOSED/build-spec.md` (ТЗ) — он ГЛАВНЫЙ источник правды для генерации**
   (поблочные требования, роли, адаптация, контроль). Агент обязан читать ТЗ и следовать ему.
3. Передаёт работу агенту `block-composer`.
4. Сообщает путь к артефакту.

## Источники правды (в порядке приоритета)

1. **ТЗ** `07b_COMPOSED/build-spec.md` — если существует, ведёт генерацию: что в каждом блоке,
   какие роли, адаптация ролей→прототип, контроль. ИСТОЧНИКИ внутри ТЗ ведут к остальным файлам.
2. **Дизайн-система (муды)** `05_ДИЗАЙН-СИСТЕМА/moods/{mood}/` — `objects.yaml` (роли+вид+состояния,
   формат `_OBJECT-SPEC-FORMAT.md` с 21-уровневым чек-листом), `compositions/hero.yaml`
   (раскладка+расположение текстов), `palette/typography/motion.css`. **Каждый мод — свой набор.**
3. **Структура/тексты** АКТИВНЫЙ прототип `07_ПРОТОТИП/prototype-*.yaml` (`active: true` — см. `prototypes-index.md`). Дословно.
4. **Токены** `05_ДИЗАЙН-СИСТЕМА/tokens.json` (выведены из референса).

> Если ТЗ нет — агент работает по reference-driven-rules напрямую (prototype+tokens+референс).
> Если ТЗ есть — он ОБЯЗАТЕЛЕН (генерация без сверки с ТЗ = дефект, «ТЗ протекает мимо флоу»).

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
