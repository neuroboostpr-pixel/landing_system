---
name: ru-hero-05-centered-bold
description: Центрированный hero с гигантской типографикой (64px desktop, 36px mobile), декоративными горизонтальными линиями и единственной CTA. Apple/Stripe-стиль.
---

# ru-hero-05-centered-bold

## Когда применять

Hero-блок для **premium / luxury / premium-service** брендов, где визуальная идентичность строится на типографике, а не фото. Подходит для: дизайн-студий, архитекторов, консалтинга, премиум-продуктов, b2c-сервисов с сильным позиционированием.

Отличие от `ru-hero-01-services-calc` и `ru-hero-04-split-form` — здесь нет ни фото, ни формы. Только слово.

## Slots

- `tagline` (text, ≤30 char) — метка над заголовком, uppercase (напр. «С 2010 ГОДА» или «ДИЗАЙН-СТУДИЯ»). Опциональный.
- `headline` (text, ≤80 char) — основной заголовок, 64px desktop. Обязательный.
- `subhead` (text, ≤160 char) — уточняющий подзаголовок. Опциональный.
- `primary-cta` (cta, default "Начать сотрудничество") — единственная CTA. Обязательный.

## Conversion notes

- Единственная CTA = ноль конкуренции за внимание. Фокус максимальный.
- Генерозный padding (spacing-lg × 3 top/bottom) создаёт «воздух» премиум-стиля.
- Декоративные тонкие линии — CSS `height: 1px`, не изображения — масштабируются без потерь.
- Tagline в uppercase с letter-spacing создаёт доверие через авторитет (годы, статус).

## Mobile considerations

`template-mobile.html`: headline 36px, padding уменьшен до spacing-lg × 2, CTA полноширинная. Декоративные линии сохраняются — 48px вместо 80px.

