---
type: block
name: trust-editorial-grid-2-zilant-group-7
sources: ["block-library/trust/trust-editorial-grid-2-zilant-group-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["trust", "editorial", "grid-2", "ru-market", "animation", "b2b", "services", "education", "medical"]
---

# Trust Editorial Grid 2 — Zilant Group 7

## Что делает
Отображает секцию кейса в редакционном стиле: большой заголовок, две документальные карточки с подробностями и бирюзовые блоки-выводы. Создаёт ощущение серьёзного, доказательного контента — «вот что мы сделали и вот результат».

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** — агент [[ux-composer]] выбирает блок из библиотеки при построении wireframe.html. На этапе **07b (Compose)** агент [[block-composer]] подставляет реальный текст из prototype.yaml и токены дизайна. Подходит для страниц с доказательной базой: кейсы, портфолио, результаты проектов.

Наиболее уместен для ниш: **services, b2b-saas, education, medical** — там, где важно показать компетентность через документальный визуальный стиль.

## Что на вход / на выход

**Вход:**
- Слот `heading` (обязательный, тип `text`) — заголовок секции кейса
- Токены дизайна из `tokens.json` (цвета, типографика)
- Контент из `prototype.yaml` (тексты для карточек и выводов)

**Выход:**
- HTML-блок с сеткой `grid-2`: два документальных карточки + бирюзовые блоки выводов
- Встроенная анимация (`has_animation: true`)
- Адаптирован под российский рынок (`ru_market: true`)

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при построении wireframe на этапе 07a
- [[block-composer]] — на этапе 07b наполняет блок реальными текстами и токенами
- [[wireframe-rendering]] — скилл, в рамках которого блок попадает в wireframe.html
- [[block-composition]] — скилл, отвечающий за финальную сборку composed.html
- [[block-library-management]] — управляет каталогом блоков, включая этот

## Источник
- `block-library/trust/trust-editorial-grid-2-zilant-group-7/meta.yaml`