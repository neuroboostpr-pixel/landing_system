---
type: block
name: hero-technical-split-portfolio-kdm1-ru-1
sources: ["block-library/hero/hero-technical-split-portfolio-kdm1-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "split", "technical", "ecommerce", "services", "tech", "ru-market"]
---

# Hero Technical Split — Заголовок слева, фото продукта справа

## Что делает
Первый экран лендинга в стиле «технический сплит»: крупный заголовок занимает левую половину, большое предметное фото продукта — правую. Подходит для брендов, которым важно сразу показать товар и чётко обозначить оффер без лишних украшений.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** — агент [[ux-composer]] выбирает блок из библиотеки при построении wireframe.html. На этапе **07b (Block Compose)** агент [[block-composer]] инжектирует в блок дизайн-токены и финальные тексты из prototype.yaml.

Подходит для проектов в нишах: **ecommerce**, **services**, **tech**. Ориентирован на российский рынок (`ru_market: true`). Анимация отсутствует (`has_animation: false`), что ускоряет рендер и упрощает QA.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — главный заголовок блока
- Дизайн-токены из `tokens.json` (цвета, шрифты)
- Фото продукта — визуальный placeholder, заполняется на этапе 07c ([[photo-curator]]) или 07d ([[visual-curator]])

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` или `composed.html`
- Слот `[SLOT: hero-product-photo]` остаётся placeholder-ом до прохождения PR-B/PR-C

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при сборке wireframe
- [[block-composer]] — инжектирует токены и тексты на этапе 07b
- [[wireframe-rendering]] — скилл, рендерящий wireframe.html из prototype.yaml + block-library
- [[block-composition]] — скилл этапа 07b, собирает composed.html
- [[photo-curator]] — заполняет фото-слот продукта на этапе 07c
- [[block-library-management]] — скилл управления библиотекой блоков, куда входит этот блок

## Источник
- `block-library/hero/hero-technical-split-portfolio-kdm1-ru-1/meta.yaml`