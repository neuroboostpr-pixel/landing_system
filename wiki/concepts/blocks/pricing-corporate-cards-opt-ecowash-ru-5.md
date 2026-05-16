---
type: block
name: pricing-corporate-cards-opt-ecowash-ru-5
sources: ["block-library/pricing/pricing-corporate-cards-opt-ecowash-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags:
  - pricing
  - corporate
  - cards
  - b2b
  - ecommerce
  - services
  - ru-market
  - no-animation
---

# Pricing Corporate Cards — горизонтальный ряд карточек предложений

## Что делает

Отображает секцию коммерческих предложений в виде горизонтального ряда карточек. Каждая карточка содержит параметры тарифа/пакета и кнопку действия. Стиль — корпоративный (строгий, деловой), без анимации. Подходит для российского рынка.

## Когда вызывать / в каком этапе

Используется на этапах **07a (Wireframe)** и **07b (Compose)**:

- `ux-composer` выбирает этот блок из библиотеки, когда прототип содержит секцию «тарифы», «пакеты» или «коммерческие предложения» для B2B- или e-commerce-проекта.
- `block-composer` рендерит блок в `composed.html`, подставляя дизайн-токены и тексты из прототипа.

Подходит для ниш: **ecommerce**, **b2b-saas**, **услуги**.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции (например, «Наши тарифы», «Пакеты услуг»).
- Дизайн-токены из `tokens.json` (цвета, шрифты, отступы) — подставляются при compose.
- Тексты карточек из `prototype.yaml`.

**Выход:**
- HTML-фрагмент с горизонтальным рядом корпоративных карточек, встроенный в `composed.html` или `wireframe.html`.
- Слоты для параметров и кнопок заполнены либо placeholder-текстом (wireframe), либо реальным контентом из прототипа (compose).

## Связанные концепты

- [[ux-composer]] — агент, выбирающий блок из библиотеки при построении wireframe; не изобретает новых блоков — только выбирает существующие.
- [[block-composer]] — агент этапа 07b, инжектирует токены и тексты в выбранный блок.
- [[wireframe-rendering]] — скилл рендера `wireframe.html`; использует этот блок как один из кандидатов для секции pricing.
- [[block-composition]] — скилл этапа 07b; отвечает за финальную сборку `composed.html` из выбранных блоков.
- [[block-library-management]] — скилл управления библиотекой; описывает правила импорта и регистрации новых блоков.

## Источник

- `block-library/pricing/pricing-corporate-cards-opt-ecowash-ru-5/meta.yaml`
- Импортирован с: https://opt.ecowash.ru/ (2026-05-16, метод: codex-block-generation)