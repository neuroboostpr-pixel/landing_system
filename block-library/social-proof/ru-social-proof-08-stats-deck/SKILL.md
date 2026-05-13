---
name: ru-social-proof-08-stats-deck
description: Четыре метрики с акцентными символами в сетке с чередующимися фонами. Адаптирован из stats-slide open-design-landing-deck (Apache-2.0).
---

# ru-social-proof-08-stats-deck

## Когда применять

Блок для демонстрации ключевых **цифровых результатов** компании. Хорошо работает между features и pricing. Чередующиеся фоны создают визуальный ритм без явных бордеров.

## Slots

- `kicker`, `headline` — заголовочная часть.
- `stat-{1,2,3,4}-value` (text, ≤12 char) — цифра с символом (например "120+", "93%").
- `stat-{1,2,3,4}-label` (text, ≤60 char) — описание метрики.
- `stat-{1,2,3,4}-desc` (text, ≤60 char) — уточнение (необязательное).

## Mobile considerations

Сетка 2×2 вместо 4×1. Ширина 375px.
