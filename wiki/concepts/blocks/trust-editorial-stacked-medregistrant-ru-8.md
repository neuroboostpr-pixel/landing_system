---
type: block
name: trust-editorial-stacked-medregistrant-ru-8
sources: ["block-library/trust/trust-editorial-stacked-medregistrant-ru-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["trust", "editorial", "stacked", "ru-market", "medical", "education", "services", "цитата"]
---

# Trust Editorial Stacked — Минималистичный блок с крупной цитатой

## Что делает

Отображает крупную цитату или ключевое утверждение на всю ширину блока, а реквизиты доверия (имя, должность, логотип) располагает компактно сбоку или снизу. Создаёт редакционный, журнальный стиль — строго, без лишних деталей.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при выборе блоков секции доверия (trust). Подходит для лендингов в нишах **медицина**, **образование**, **услуги** — там, где важно передать авторитет через слова эксперта или клиента. Особенно уместен на российском рынке (флаг `ru_market: true`). Блок статичный — анимации нет.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — крупная цитата или заголовок-утверждение
- Опционально: реквизиты доверия (имя, должность, организация) — зависит от шаблона блока

**Выход:**
- HTML-секция в `wireframe.html` (этап 07a) или в `composed.html` (этап 07b) с редакционной вёрсткой: цитата крупным кеглем + реквизиты малым шрифтом сбоку

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при сборке wireframe.html
- [[block-composer]] — инжектирует design-tokens и подставляет тексты прототипа в слот `heading`
- [[wireframe-rendering]] — скилл, в рамках которого блок рендерится с CSS-вариантами
- [[block-composition]] — скилл этапа 07b, собирает composed.html с реальным контентом
- [[block-library-management]] — управляет каталогом, в котором хранится данный блок

## Источник

- `block-library/trust/trust-editorial-stacked-medregistrant-ru-8/meta.yaml`