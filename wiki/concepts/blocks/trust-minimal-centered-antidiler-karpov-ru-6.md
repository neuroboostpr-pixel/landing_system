---
type: block
name: trust-minimal-centered-antidiler-karpov-ru-6
sources: ["block-library/trust/trust-minimal-centered-antidiler-karpov-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["trust", "partners", "minimal", "dark-bg", "premium-auto", "b2b-saas", "services", "ru-market"]
---

# Trust: Короткая секция партнёров на тёмном фоне (antidiler-karpov-ru-6)

## Что делает

Короткая секция «Партнёры» или «Нам доверяют» — тёмный фон, крупный заголовок по центру и большая пустая зона под логотипы партнёров. Минималистичный стиль без анимации, ставка на весомость и «воздух».

## Когда вызывать / в каком этапе

Используется на **этапе 07a** (UX Wireframe) агентом [[ux-composer]] при выборе блока типа `trust` из библиотеки. Подходит когда нужно показать партнёров или клиентов в сдержанной премиальной манере: без каруселей, без мелких деталей.

Хорошо вписывается в ниши:
- **premium-auto** — демонстрация автодилеров / брендов
- **services** — B2C-услуги с известными клиентами
- **b2b-saas** — партнёрская экосистема

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции, например «Нам доверяют» или «Наши партнёры»
- Логотипы партнёров — визуальные placeholder-слоты под PNG/SVG (не описаны в slots, подразумеваются свободной зоной)

**Выход:**
- HTML-блок готов к вставке в `wireframe.html` (этап 07a) и далее в `composed.html` (этап 07b) агентом [[block-composer]]

**Особенности:**
- `has_animation: false` — блок статичный, без JS/GSAP
- `ru_market: true` — адаптирован под отечественные рынки
- Импортирован с antidiler-karpov.ru методом codex-block-generation

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composition]] — инжектирует дизайн-токены и тексты в блок на этапе 07b
- [[wireframe-rendering]] — рендерит блок в интерактивный wireframe.html
- [[block-library-management]] — управляет каталогом, хранит meta.yaml этого блока
- [[block-composer]] — агент, собирающий composed.html из одобренных блоков

## Источник

- `block-library/trust/trust-minimal-centered-antidiler-karpov-ru-6/meta.yaml`