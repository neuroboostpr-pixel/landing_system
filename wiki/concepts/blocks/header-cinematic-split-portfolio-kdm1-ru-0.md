---
type: block
name: header-cinematic-split-portfolio-kdm1-ru-0
sources: ["block-library/header/header-cinematic-split-portfolio-kdm1-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["header", "cinematic", "split", "navigation", "ru-market", "services", "education", "b2b-saas"]
---

# Header Cinematic Split — Узкая навигация на светлом фоне

## Что делает

Блок-заголовок с узкой горизонтальной навигацией на светлом фоне: компактные ссылки выровнены по центру или левому краю, справа — контрастная кнопка призыва к действию. Визуальный стиль — кинематографичный (cinematic), макет разбит на две зоны (split).

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)**, когда [[ux-composer]] подбирает блок-заголовок из библиотеки под прототип. Подходит для проектов в нишах **услуги, образование, b2b-saas** с российским рынком (`ru_market: true`). Анимация не предусмотрена (`has_animation: false`), поэтому блок одинаково хорошо работает в статичных и облегчённых сборках.

На этапе **07b (Block Compose)** [[block-composer]] инжектирует в блок дизайн-токены из `tokens.json` и подставляет текст из `prototype.yaml` в слот `heading`.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — главный заголовок/название сайта или бренда, берётся из `prototype.yaml`.
- Дизайн-токены (`tokens.json`) — цвета, шрифты, отступы.

**Выход:**
- Готовый HTML-фрагмент навигации, встраиваемый в `wireframe.html` (этап 07a) и `composed.html` (этап 07b).

## Связанные концепты

- [[ux-composer]] — выбирает этот блок при сборке wireframe.html на основе `prototype.yaml` и библиотеки блоков
- [[block-composer]] — рендерит финальный composed.html: подставляет токены и тексты
- [[wireframe-rendering]] — скилл, управляющий генерацией интерактивного wireframe.html на этапе 07a
- [[block-composition]] — скилл этапа 07b, отвечает за инжекцию токенов в выбранные блоки
- [[block-library-management]] — скилл управления всей библиотекой блоков, в которой зарегистрирован этот блок

## Источник

- `block-library/header/header-cinematic-split-portfolio-kdm1-ru-0/meta.yaml`