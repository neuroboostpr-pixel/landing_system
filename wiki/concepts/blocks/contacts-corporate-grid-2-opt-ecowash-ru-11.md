---
type: block
name: contacts-corporate-grid-2-opt-ecowash-ru-11
sources: ["block-library/contacts/contacts-corporate-grid-2-opt-ecowash-ru-11/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["contacts", "corporate", "grid-2", "ru-market", "services", "ecommerce"]
---

# Контактная секция на ярком фоне с двумя карточками адресов

## Что делает
Отображает контактный раздел лендинга на ярком фоне: две крупные карточки с адресами и декоративные визуальные объекты. Подходит для компаний с несколькими офисами или точками выдачи.

## Когда вызывать / в каком этапе
Используется на этапе **07b (compose)** и **08 (build)** при сборке секции контактов. Выбирается в wireframe-шаге как вариант блока категории `contacts` для ниш `services` или `ecommerce` с корпоративным стилем оформления.

## Что на вход / на выход
**Вход:**
- `heading` (text, обязательный) — заголовок контактной секции.

**Выход:**
- HTML-блок контактной секции с двумя карточками адресов на ярком фоне, готовый к встраиванию в `composed.html`.

## Характеристики блока

| Параметр | Значение |
|---|---|
| Категория | contacts |
| Раскладка | grid-2 (две колонки) |
| Стиль | corporate |
| Анимация | нет |
| Рынок | RU |
| Ниши | services, ecommerce |
| Источник импорта | opt.ecowash.ru (2026-05-16, codex-block-generation) |

## Связанные концепты
- [[landing-wireframe]] — на этапе 07a пользователь выбирает этот блок как один из вариантов секции контактов
- [[landing-compose]] — на этапе 07b блок встраивается в `composed.html` с подстановкой токенов и текстов
- [[landing-build]] — на этапе 08 блок компилируется в WordPress Lazy Blocks PHP-шаблон

## Источник
- `block-library/contacts/contacts-corporate-grid-2-opt-ecowash-ru-11/meta.yaml`