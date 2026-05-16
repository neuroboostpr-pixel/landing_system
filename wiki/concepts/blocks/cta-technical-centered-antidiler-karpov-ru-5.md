---
type: block
name: cta-technical-centered-antidiler-karpov-ru-5
sources: ["block-library/cta/cta-technical-centered-antidiler-karpov-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags:
  - cta
  - technical
  - centered
  - premium-auto
  - services
  - ecommerce
  - ru-market
  - form
---

# CTA: Подбор запчастей — технический центрированный блок

## Что делает

Блок призыва к действию в техническом стиле: крупный заголовок по центру + горизонтальная форма подбора в одну строку + акцентная оранжевая кнопка. Подходит для автосервисов, интернет-магазинов запчастей и технических сервисов на российском рынке.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — `ux-composer` подбирает блок из библиотеки по нише и layout-паттерну. На этапе **07b (Compose)** — `block-composer` инжектирует design-tokens и реальные тексты из `prototype.yaml`. Хорошо встаёт в секцию CTA в середине или в конце лендинга для ниш `premium-auto`, `services`, `ecommerce`.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — сильный заголовок, формулирующий оффер подбора
- Design-tokens из `tokens.json` (цвет акцента, типографика)
- Контент из `prototype.yaml` (текст кнопки, placeholder формы)

**Выход:**
- HTML-секция CTA с центрированным layout, инлайн-формой и оранжевой кнопкой
- Встраивается в `wireframe.html` (07a) и в `composed.html` (07b)

**Особенности:**
- `has_animation: false` — нет GSAP/CSS-анимаций, блок статичный
- `ru_market: true` — оптимизирован под российскую аудиторию
- `layout_pattern: centered` — всё выровнено по центру
- Импортирован с [antidiler-karpov.ru](https://antidiler-karpov.ru/) методом codex-block-generation

## Связанные концепты

- [[ux-composer]] — подбирает этот блок из библиотеки при сборке wireframe.html
- [[block-composer]] — инжектирует tokens и тексты на этапе 07b
- [[wireframe-rendering]] — скилл, в рамках которого блок рендерится с вариантами
- [[block-composition]] — скилл 07b, финальная сборка composed.html
- [[block-library-management]] — управление библиотекой, откуда взят блок

## Источник

- `block-library/cta/cta-technical-centered-antidiler-karpov-ru-5/meta.yaml`