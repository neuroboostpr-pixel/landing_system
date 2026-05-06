# 01a. Анализ ниши

Этап автоматического исследования: что за продукт, какой тип бренда, кто конкуренты, на что давим.

## Артефакты

- `niche-analysis.md` — нарративный отчёт (400–800 слов): тип бренда, описание ниши, рекомендация «на что давим», список допущений.
- `competitors.yaml` — машиночитаемая база 15–25 игроков в 7 ролях: direct, local_dealer, manufacturer, analog, category_leader, local_competitor, indirect.
- `positioning.md` — единый источник истины для следующих этапов: core promise, tone of voice, 1–2 угла отстройки, чего избегать.

## Кто пишет

Агент `niche-analyst`. Запускается командой `/landing-niche`.

## Что читает

- `00_БРИФ/brief.md` (обязательно)
- `01_КОНТЕКСТ/context.md` (если есть)

## Что читает после

- `references-curator` (этап 03) — `competitors.yaml`
- `moodboard-composer` (этап 03) — `niche-analysis.md`
- `brand-architect` (этап 04) — `positioning.md`
- `content-writer` (этап 07) — `positioning.md` + `competitors.yaml`
- `seo-optimizer` (этап 12) — `competitors.yaml`

## Принцип

Zero-touch: пользователь не отвечает на вопросы агента. При нехватке данных агент помечает поля `[ДОПУЩЕНИЕ]`.

## Язык

Все значения полей и тексты на русском. Имена ключей YAML/Markdown на английском. Имена брендов и URL без транслита.
