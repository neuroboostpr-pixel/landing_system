---
type: block
name: process-corporate-stacked-portfolio-kdm1-ru-13
sources: ["block-library/process/process-corporate-stacked-portfolio-kdm1-ru-13/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "corporate", "stacked", "ru-market", "services", "education", "b2b-saas", "no-animation"]
---

# Секция процесса с карточкой эксперта, описанием и иллюстрациями команды

## Что делает

Блок для раздела «Как мы работаем» или «О процессе»: показывает карточку эксперта рядом с текстовым описанием этапов и иллюстрациями команды. Выглядит строго и профессионально — подходит для корпоративных и B2B-сайтов на русском рынке.

## Когда вызывать / в каком этапе

Используется на этапах **07a (UX Wireframe)** и **07b (Block Compose)**. `ux-composer` выбирает блок из библиотеки, когда прототип содержит секцию процесса с элементами доверия (эксперт/команда). `block-composer` подставляет реальный текст и токены дизайна.

Подходит для ниш: **услуги**, **образование**, **B2B-SaaS**.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции процесса
- Токены дизайна из `tokens.json` (цвета, шрифты)
- Текстовые слоты из `prototype.yaml`

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Плейсхолдеры для иллюстраций команды (заполняются на этапе 07c/07d)

**Параметры блока:**
- `style_mood: corporate` — строгая корпоративная эстетика
- `layout_pattern: stacked` — вертикальная стопка секций
- `has_animation: false` — без JS-анимаций, статичный рендер
- `ru_market: true` — тексты и типографика адаптированы для русского рынка

## Связанные концепты

- [[ux-composer]] — выбирает этот блок при сборке wireframe.html на этапе 07a
- [[block-composer]] — рендерит итоговый composed.html с подставленными токенами
- [[wireframe-rendering]] — скилл, управляющий отрисовкой блоков в wireframe
- [[block-composition]] — скилл финальной сборки с design-tokens
- [[block-library-management]] — общий реестр, в котором зарегистрирован блок

## Источник

- `block-library/process/process-corporate-stacked-portfolio-kdm1-ru-13/meta.yaml`
- Импортирован: 2026-05-16, метод: `codex-block-generation`, оригинал: [portfolio.kdm1.ru](https://portfolio.kdm1.ru/upload/iblock/b31/i0qylig13hzo7ow4qcpia0qhtn3i87pk/Onlai_n_shkola-Dmitriya-Vykhodtseva.pdf)