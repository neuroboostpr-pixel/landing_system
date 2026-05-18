---
type: block
name: header-cinematic-split-antidiler-karpov-ru-0
sources: ["block-library/header/header-cinematic-split-antidiler-karpov-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - wireframe-rendering
  - block-composition
  - ux-composer
tags:
  - header
  - cinematic
  - split
  - premium-auto
  - luxury
  - services
  - ru-market
---

# Header: Cinematic Split (antidiler-karpov)

## Что делает

Узкая тёмная панель навигации в верхней части страницы: логотип слева, меню по центру, контактные данные и иконки мессенджеров справа. Импортирован с сайта antidiler-karpov.ru и адаптирован для повторного использования в проектах схожей ниши.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при компоновке блоков хедера. Агент [[ux-composer]] выбирает этот блок из библиотеки, если проект относится к нишам `premium-auto`, `services` или `luxury`, и требует кинематографичного (`cinematic`) визуального настроения с разделённым (`split`) лейаутом. Финально рендерится на этапе **07b (Compose)** через [[block-composer]].

Подходит для русскоязычного рынка (`ru_market: true`). Анимации отсутствуют (`has_animation: false`), поэтому не требует сцен из [[scene-director]].

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип `text`, обязательный) — текстовое содержимое для заголовка/названия в навигации.
- Данные из `tokens.json` (цвета, шрифты) — инжектируются на этапе compose.

**Выход:**
- HTML-фрагмент блока хедера, встроенный в `wireframe.html` (07a) и `composed.html` (07b).

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — рендерит блок в composed.html с токенами и контентом
- [[wireframe-rendering]] — скилл, управляющий генерацией wireframe.html
- [[block-composition]] — скилл, управляющий генерацией composed.html
- [[block-library-management]] — скилл, отвечающий за ведение библиотеки блоков

## Источник

- `block-library/header/header-cinematic-split-antidiler-karpov-ru-0/meta.yaml`