---
type: block
name: hero-cinematic-centered-portfolio-kdm1-ru-1
sources: ["block-library/hero/hero-cinematic-centered-portfolio-kdm1-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition", "wireframe-rendering"]
tags: ["hero", "cinematic", "centered", "ru-market", "services", "education", "b2b-saas", "tech"]
---

# Hero Cinematic Centered (KDM1-RU-1)

## Что делает

Блок первого экрана (hero) с крупным центральным заголовком, холодными персонажными иллюстрациями и кнопкой-призывом к действию (CTA). Создаёт кинематографичное, профессиональное первое впечатление без лишней анимации.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** при сборке `composed.html`. Агент [[ux-composer]] выбирает блок из библиотеки на этапе 07a (wireframe), если прототип предполагает герой-секцию с центральным лейаутом и кинематографичным настроением. Подходит для проектов в нишах:

- **Услуги** (services)
- **Образование** (education)
- **B2B SaaS**
- **Технологии** (tech)

Стилистика `cinematic` означает тёмную, строгую палитру с акцентными элементами — ориентирован на русскоязычный рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип: `text`) — главный заголовок блока
- Дизайн-токены из `tokens.json` (цвета, шрифты) — инжектирует [[block-composer]]
- Тексты из `prototype.yaml` — подставляются при сборке на этапе 07b

**Выход:**
- Готовый HTML-фрагмент блока, вставляемый в `07b_COMPOSED/composed.html`
- Слоты для иллюстраций остаются плейсхолдерами до этапа 07c (фото) и 07d (визуалы)

**Параметры блока:**
- `layout_pattern: centered` — все элементы выровнены по центру
- `has_animation: false` — нет JS-анимаций, только CSS
- `style_mood: cinematic` — тёмная, кинематографичная атмосфера

## Источник блока

Блок был импортирован из портфолио [portfolio.kdm1.ru](https://portfolio.kdm1.ru/upload/iblock/b31/i0qylig13hzo7ow4qcpia0qhtn3i87pk/Onlai_n_shkola-Dmitriya-Vykhodtseva.pdf) методом `codex-block-generation` (2026-05-16). Это означает, что структура и верстка были синтезированы codex на основе визуального референса из PDF-портфолио.

## Связанные концепты

- [[block-composer]] — агент, который инжектирует токены и тексты в этот блок при сборке 07b
- [[ux-composer]] — агент, выбирающий блок из библиотеки на wireframe-этапе 07a
- [[block-composition]] — скилл, описывающий механику сборки composed.html
- [[wireframe-rendering]] — скилл 07a, где блок впервые попадает в wireframe как кандидат
- [[block-library-management]] — скилл управления библиотекой блоков

## Источник

- `block-library/hero/hero-cinematic-centered-portfolio-kdm1-ru-1/meta.yaml`