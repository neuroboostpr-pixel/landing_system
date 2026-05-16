---
type: block
name: gallery-minimal-stacked-portfolio-kdm1-ru-2
sources: ["block-library/gallery/gallery-minimal-stacked-portfolio-kdm1-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["gallery", "minimal", "stacked", "ecommerce", "education", "services", "ru-market", "animation"]
---

# Крупный медиа-блок с товарным фото (gallery-minimal-stacked-portfolio-kdm1-ru-2)

## Что делает

Отображает товарное или продуктовое фото во всю ширину контейнера с круглой кнопкой воспроизведения поверх изображения. Минималистичный стек-макет — медиа занимает всё полотно, текст укладывается снизу или поверх. Подходит для демонстрации продукта или кейса с видеопревью.

## Когда вызывать / в каком этапе

Блок используется на этапе **07a (UX Wireframe)** и **07b (Block Compose)**:
- `ux-composer` выбирает блок из библиотеки при формировании `wireframe.html`, если прототип содержит галерею или медиа-секцию в нишах e-commerce, образования или услуг.
- `block-composer` инжектирует токены и подставляет тексты прототипа при рендере `composed.html`.

Блок ориентирован на **российский рынок** (`ru_market: true`) и содержит CSS-анимацию (`has_animation: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок блока, подтягивается из `prototype.yaml`.
- Медиа-плейсхолдер для товарного фото (photo-slot, заполняется на этапе 07c через `photo-curator`).
- Дизайн-токены из `tokens.json` (цвета, шрифты, радиусы).

**Выход:**
- HTML-фрагмент блока в составе `wireframe.html` (этап 07a) или `composed.html` (этап 07b).
- Круглая кнопка воспроизведения рендерится как SVG/CSS-элемент поверх медиа.

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при сборке wireframe, не изобретает новые блоки.
- [[block-composer]] — инжектирует токены и тексты прототипа в итоговый composed.html.
- [[wireframe-rendering]] — скилл, управляющий рендером интерактивного wireframe.html.
- [[block-composition]] — скилл этапа 07b, управляющий сборкой composed.html.
- [[photo-curator]] — заполняет медиа-слот реальным фото клиента на этапе 07c.
- [[block-library-management]] — скилл управления библиотекой блоков, в которой хранится этот блок.

## Источник

- `block-library/gallery/gallery-minimal-stacked-portfolio-kdm1-ru-2/meta.yaml`
- Импортирован: 2026-05-16 из `portfolio.kdm1.ru` методом `codex-block-generation`.