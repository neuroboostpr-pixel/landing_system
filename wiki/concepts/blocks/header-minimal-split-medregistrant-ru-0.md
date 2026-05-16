---
type: block
name: header-minimal-split-medregistrant-ru-0
sources: ["block-library/header/header-minimal-split-medregistrant-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["header", "minimal", "split", "ru-market", "services", "medical", "education"]
---

# Header Minimal Split — Узкая навигация с акцентом справа

## Что делает

Отрисовывает узкую верхнюю навигационную полосу: логотип слева, пункты меню по центру, контактный призыв (телефон или кнопка) справа. Подходит для сайтов, где нужен лаконичный хедер без лишних элементов.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** и **07b (Block Compose)**. Агент [[ux-composer]] выбирает этот блок из библиотеки, когда прототип содержит раздел «шапка» с минималистичным стилем. Подходит для ниш: услуги, медицина, образование. Ориентирован на русскоязычный рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (обязательный, тип `text`) — текстовое содержимое заголовка/логотипа из `prototype.yaml`
- Дизайн-токены из `tokens.json` (цвета, шрифты) — инжектируются на этапе 07b

**Выход:**
- HTML-фрагмент хедера, встраиваемый в `wireframe.html` (07a) и `composed.html` (07b)
- Нет анимаций (`has_animation: false`), статичная вёрстка
- Нет обязательных слотов для фото или иконок — только текст

## Детали блока

| Параметр | Значение |
|---|---|
| Категория | `header` |
| Настроение стиля | `minimal` |
| Паттерн раскладки | `split` (логотип слева / контакт справа) |
| Анимация | нет |
| Рынок | Россия / ru |
| Источник импорта | medregistrant.ru (codex-block-generation, 2026-05-16) |

## Связанные концепты

- [[ux-composer]] — агент, выбирающий блоки из библиотеки для wireframe
- [[wireframe-rendering]] — скилл, рендерящий итоговый wireframe.html с этим блоком
- [[block-composition]] — скилл этапа 07b, инжектирует токены и тексты в блок
- [[block-library-management]] — скилл, управляющий регистрацией и обновлением блоков в библиотеке

## Источник

- `block-library/header/header-minimal-split-medregistrant-ru-0/meta.yaml`