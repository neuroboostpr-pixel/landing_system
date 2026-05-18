---
type: block
name: header-corporate-split-portfolio-kdm1-ru-0
sources: ["block-library/header/header-corporate-split-portfolio-kdm1-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags: [header, corporate, split, ru-market, services, ecommerce, tech, no-animation]
---

# Компактная верхняя навигация на синем фоне (header-corporate-split)

## Что делает
Рендерит компактную шапку сайта: логотип слева, пункты навигационного меню по центру, контактная информация справа — всё на насыщенном синем фоне. Подходит для корпоративного стиля без лишних эффектов.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при подборе блока-шапки. `ux-composer` выбирает его из библиотеки по совпадению категории `header`, настроению `corporate` и паттерну `split`. Финально вставляется в `composed.html` на этапе **07b** агентом `block-composer`.

Подходящие ниши: **услуги**, **e-commerce**, **tech**. Блок ориентирован на российский рынок (`ru_market: true`), анимация отсутствует (`has_animation: false`).

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — текст заголовка / названия компании или раздела.
- Токены дизайна из `tokens.json` (цвет фона, шрифт, отступы) — инжектируются автоматически на этапе 07b.

**Выход:**
- HTML-фрагмент шапки, встроенный в `wireframe.html` (07a) и затем в `composed.html` (07b).
- В wireframe показывается как один из кандидатов-вариантов для выбора пользователем.

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки по категории и стилю при формировании wireframe
- [[block-composer]] — инжектирует токены и тексты прототипа в блок на этапе 07b
- [[wireframe-rendering]] — скилл, управляющий рендером кандидатов блоков в wireframe.html
- [[block-composition]] — скилл финальной сборки composed.html с подстановкой контента
- [[block-library-management]] — скилл управления каталогом блоков, куда входит данный блок

## Источник
- `block-library/header/header-corporate-split-portfolio-kdm1-ru-0/meta.yaml`