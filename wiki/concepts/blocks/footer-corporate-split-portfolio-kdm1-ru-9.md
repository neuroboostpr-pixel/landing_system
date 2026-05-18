---
type: block
name: footer-corporate-split-portfolio-kdm1-ru-9
sources: ["block-library/footer/footer-corporate-split-portfolio-kdm1-ru-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses:
  - ux-composer
  - block-composer
  - block-library-management
  - wireframe-rendering
  - block-composition
tags:
  - footer
  - corporate
  - split
  - dark
  - ru-market
  - ecommerce
  - services
  - b2b-saas
---

# Тёмный подвал с навигацией, иконками соцсетей и контактами (kdm1-ru-9)

## Что делает

Готовый блок «подвал» для лендинга: тёмный фон, двухколоночный split-layout, навигационные ссылки, иконки социальных сетей и контактные строки. Подходит для деловых и корпоративных сайтов, не содержит анимаций.

## Когда вызывать / в каком этапе

Используется на этапах **07a (Wireframe)** и **07b (Compose)**.

- `ux-composer` выбирает блок как вариант footer-секции при построении `wireframe.html`.
- `block-composer` вставляет блок в `composed.html`, подставляя дизайн-токены и текст из `prototype.yaml`.
- Подходит для ниш: **ecommerce**, **services**, **b2b-saas**.
- Ориентирован на **российский рынок** (`ru_market: true`).

## Что на вход / на выход

**Вход:**

| Слот | Тип | Обязательность |
|------|-----|---------------|
| `heading` | text | обязательный |

Дополнительно блок ожидает дизайн-токены (цвета, шрифты) из `tokens.json` и контентные строки из `prototype.yaml` (навигация, ссылки соцсетей, контакты).

**Выход:**

HTML-фрагмент footer-секции, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b). Без анимации (`has_animation: false`) — не требует дополнительных JS-зависимостей.

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html на этапе 07a
- [[block-composer]] — подставляет токены и текст, вставляет блок в composed.html на этапе 07b
- [[wireframe-rendering]] — скилл рендеринга, в рамках которого блок попадает в интерактивный wireframe
- [[block-composition]] — скилл сборки, использует блок при финальном compose
- [[block-library-management]] — управляет реестром блоков, включая этот

## Источник

- `block-library/footer/footer-corporate-split-portfolio-kdm1-ru-9/meta.yaml`