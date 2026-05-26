---
slug: stage-01a
type: stage
name: "01a. Анализ ниши"
stage: "01a"
tags: [niche, research, analysis, zero-touch]
triggers: [landing-niche]
inputs:
  - 00_БРИФ/brief.md
  - 01_КОНТЕКСТ/context.md
outputs:
  - 01a_АНАЛИЗ_НИШИ/niche-analysis.md
  - 01a_АНАЛИЗ_НИШИ/competitors.yaml
  - 01a_АНАЛИЗ_НИШИ/market-profile.md
  - 01a_АНАЛИЗ_НИШИ/positioning.md
  - 01a_АНАЛИЗ_НИШИ/landing-structure.md
  - 01a_АНАЛИЗ_НИШИ/visual-requirements.md
gates: []
pre_reqs: []
related:
  - niche-analyst
  - landing-niche
  - references-curator
  - moodboard-composer
  - brand-architect
  - content-writer
  - wp-builder
  - seo-optimizer
  - client-assets-collector
sources: ["template/01a_АНАЛИЗ_НИШИ/README.md"]
updated: 2026-05-26
confidence: {gates: low, pre_reqs: low}
---

# 01a. Анализ ниши

## Что делает

Этап автоматического исследования продукта и рынка. Агент `niche-analyst` по брифу определяет тип бренда, режим позиционирования (rational / emotional_aspiration / trust_authority или гибрид), формирует базу конкурентов, рыночный профиль и контракт структуры лендинга. Работает в zero-touch режиме: при нехватке данных помечает поля `[ДОПУЩЕНИЕ]` вместо того чтобы задавать вопросы пользователю.

## Когда вызывается

Запускается командой `/landing-niche` после того, как заполнен `00_БРИФ/brief.md`. Контекст из `01_КОНТЕКСТ/context.md` используется если присутствует, но не обязателен. Этап выполняется один раз до старта визуальных и контентных этапов.

## Вход → выход

**Вход:** `00_БРИФ/brief.md` (обязательно), `01_КОНТЕКСТ/context.md` (опционально).

**Выход:** 6 артефактов — нарративный отчёт `niche-analysis.md`, машиночитаемая база конкурентов `competitors.yaml` (15–25 игроков, 7 ролей), рыночный профиль `market-profile.md` (8 секций включая accessibility tier и emotional load), `positioning.md` (один из 3 шаблонов, поле `**Mode:**` обязательно), карта блоков лендинга `landing-structure.md` (контракт для wp-builder) и визуальные требования `visual-requirements.md` (hero focal point, стиль фото, red flags).

## Чем закрывается этап (gates)

- Все 6 артефактов созданы и не пустые
- В `positioning.md` присутствует строка `**Mode:** <режим>`
- `competitors.yaml` содержит не менее 15 записей в допустимых ролях

## Failure modes

- Бриф слишком скудный — агент заполняет почти всё через `[ДОПУЩЕНИЕ]`, позиционирование выходит неточным.
- Несуществующая ниша или экзотический продукт — `competitors.yaml` содержит менее 15 игроков или заполняется нерелевантными аналогами.
- `positioning.md` создан без обязательного заголовка `**Mode:**` — ломает парсинг в `brand-architect` и `wp-builder`.
- Старые проекты с `Mode: legacy_v1` проходят валидацию, но не получают новые template-секции — нужна ручная миграция через `scripts/migrate-niche-to-v2.sh`.
- `visual-requirements.md` генерируется без `config/niche-visual-rules.yaml` — правила берутся только из competitors, качество ниже.

## Related

- [[niche-analyst]] — агент, который исполняет 12-шаговый алгоритм этапа
- [[landing-niche]] — команда-триггер этапа
- [[references-curator]] — потребляет `competitors.yaml` и `visual-requirements.md` на этапе 03
- [[moodboard-composer]] — использует `niche-analysis.md` и `visual-requirements.md`
- [[brand-architect]] — читает `positioning.md`, `market-profile.md`, `landing-structure.md`
- [[content-writer]] — опирается на `positioning.md`, `landing-structure.md`, `market-profile.md`, `competitors.yaml`
- [[wp-builder]] — использует `landing-structure.md` как контракт template-parts
- [[seo-optimizer]] — потребляет `competitors.yaml` на этапе 12
- [[client-assets-collector]] — читает `visual-requirements.md` для сбора материалов клиента