# 01a. Анализ ниши

Этап автоматического исследования: что за продукт, какой тип бренда, какой режим позиционирования (rational / emotional_aspiration / trust_authority), кто конкуренты, какая структура лендинга нужна.

## Артефакты (6)

- `niche-analysis.md` — нарративный отчёт (400–800 слов): тип бренда, описание ниши, рекомендация «на что давим», список допущений.
- `competitors.yaml` — машиночитаемая база 15–25 игроков в 7 ролях: direct, local_dealer, manufacturer, analog, category_leader, local_competitor, indirect.
- `market-profile.md` — рыночный профиль (8 секций): accessibility tier по медианному доходу региона, consideration cycle, decision unit, regulated, emotional load, cultural context, predicted positioning mode, источники.
- `positioning.md` — позиционирование в одном из 3 шаблонов (rational / emotional_aspiration / trust_authority) или гибрид. Заголовок `**Mode:** <режим>` обязателен.
- `landing-structure.md` — карта блоков лендинга: какой Hero, какие секции, в каком порядке для конкретного типа бренда × режима. Контракт с wp-builder.
- `visual-requirements.md` — визуальные требования: hero focal point, photography style, product treatment, фоны, red flags. Источник правил: `config/niche-visual-rules.yaml` + derive из competitors.yaml + adaptation per Mode.

## Кто пишет

Агент `niche-analyst` (12-шаговый алгоритм). Запускается командой `/landing-niche`.

## Что читает

- `00_БРИФ/brief.md` (обязательно)
- `01_КОНТЕКСТ/context.md` (если есть)

## Что читает после

- `references-curator` (этап 03) — `competitors.yaml`, `visual-requirements.md`
- `moodboard-composer` (этап 03) — `niche-analysis.md`, `visual-requirements.md`
- `brand-architect` (этап 04) — `positioning.md`, `market-profile.md`, `landing-structure.md`
- `content-writer` (этап 07) — `positioning.md`, `landing-structure.md`, `market-profile.md`, `competitors.yaml`
- `wp-builder` (этап 08) — `landing-structure.md` (контракт template-parts), `positioning.md` (Mode-aware behavior), `market-profile.md` (accessibility_tier → price display), `visual-requirements.md` (sanity-checks)
- `seo-optimizer` (этап 12) — `competitors.yaml`
- `client-assets-collector` (этап 02) — `visual-requirements.md`

## Принцип

Zero-touch: пользователь не отвечает на вопросы агента. При нехватке данных агент помечает поля `[ДОПУЩЕНИЕ]`.

## Язык

Все значения полей и тексты на русском. Имена ключей YAML/Markdown на английском. Имена брендов и URL без транслита.

## Backward compat

Старые проекты с `Mode: legacy_v1` в positioning.md проходят валидацию без проверки template-секций. См. `scripts/migrate-niche-to-v2.sh` для миграции.
