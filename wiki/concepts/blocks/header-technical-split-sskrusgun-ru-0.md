---
type: block
name: header-technical-split-sskrusgun-ru-0
sources: ["block-library/header/header-technical-split-sskrusgun-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["header", "technical", "split", "ru-market", "navigation", "cta"]
---

# Header Technical Split — компактная навигационная шапка

## Что делает

Отображает верхнюю панель сайта с логотипом слева, горизонтальной навигацией по центру, иконками (например, корзина, поиск) и яркой кнопкой призыва к действию справа. Визуальный стиль — технический, лаконичный, без анимации.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** — `ux-composer` подбирает блок из библиотеки при формировании wireframe.html. Подходит для проектов в нишах **услуги**, **образование** и **e-commerce**, ориентированных на российский рынок. Выбирается, когда прототип предполагает компактный хедер с навигацией и одной акцентной кнопкой.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — текст логотипа или названия бренда в шапке.
- Токены дизайна из `tokens.json` (цвет кнопки, шрифт навигации) — инжектируются на этапе 07b.

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (07a) и затем в `composed.html` (07b).
- На этапе 07b `block-composer` заменяет placeholder-тексты на реальные данные из `prototype.yaml`.

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при рендере wireframe.html
- [[block-library-management]] — навык, управляющий каталогом блоков, в котором хранится данный блок
- [[wireframe-rendering]] — скилл, использующий блок для сборки интерактивного wireframe на этапе 07a
- [[block-composition]] — скилл этапа 07b: инжектирует tokens и тексты в скомпонованный блок
- [[block-composer]] — агент, запускающий block-composition и формирующий composed.html

## Источник

- `block-library/header/header-technical-split-sskrusgun-ru-0/meta.yaml`