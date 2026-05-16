---
type: block
name: process-technical-cards-medregistrant-ru-3
sources: ["block-library/process/process-technical-cards-medregistrant-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "cards", "tabs", "technical", "ru-market", "medical", "education", "services"]
---

# Процесс: технические карточки с вкладками (medregistrant-ru-3)

## Что делает

Светлый блок с вопросительным заголовком, вкладками для переключения разделов и карточками, расположенными вокруг размытого декоративного объекта. Стиль — строгий, технический, без анимации. Подходит для объяснения процессов, услуг или этапов работы.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** при выборе блока категории `process` для проектов медицинской, образовательной или сервисной тематики. Агент [[ux-composer]] выбирает этот блок из библиотеки, если прототип содержит раздел «как это работает» / «этапы» в техническом стиле. На этапе **07b (Block Compose)** агент [[block-composer]] подставляет реальные тексты и токены дизайна.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — вопросительный заголовок блока
- Токены дизайна из `tokens.json` (цвета, шрифты)
- Контент вкладок и карточек из `prototype.yaml`

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Карточки с описанием шагов/услуг, разбитые по вкладкам

## Ключевые характеристики

| Параметр | Значение |
|---|---|
| Категория | process |
| Паттерн | cards |
| Настроение | technical |
| Анимация | нет |
| Рынок | RU |
| Ниши | услуги, медицина, образование |
| Источник | medregistrant.ru |

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html
- [[block-composer]] — подставляет токены и тексты прототипа при compose
- [[wireframe-rendering]] — скилл, управляющий рендером 07a
- [[block-composition]] — скилл, управляющий рендером 07b
- [[block-library-management]] — скилл, отвечающий за каталог и импорт блоков

## Источник

- `block-library/process/process-technical-cards-medregistrant-ru-3/meta.yaml`