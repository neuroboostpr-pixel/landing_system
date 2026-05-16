---
type: block
name: trust-editorial-grid-3-portfolio-kdm1-ru-4
sources: ["block-library/trust/trust-editorial-grid-3-portfolio-kdm1-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses:
  - block-composer
  - block-composition
  - ux-composer
tags:
  - trust
  - editorial
  - grid-3
  - ru-market
  - services
  - education
  - b2b-saas
  - premium-auto
---

# Trust Editorial Grid-3 — Секция принципов с диагональной подложкой

## Что делает

Отображает секцию принципов или ценностей компании в трёхколоночной сетке на диагональной светлой подложке. Каждая колонка сочетает крупный заголовок с предметной иллюстрацией — создаёт доверие через визуальную редакционную подачу.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** при сборке `composed.html`. `ux-composer` выбирает блок из библиотеки, если в прототипе есть секция принципов, ценностей или «почему мы». `block-composer` инжектирует токены дизайна и подставляет тексты из `prototype.yaml`.

Подходит для ниш: **услуги, образование, B2B-SaaS, премиум-авто**.

## Что на вход / на выход

**Вход:**
- Слот `heading` (обязательный, тип `text`) — заголовок секции принципов
- Токены дизайна из `tokens.json` (цвета, типографика)
- Тексты принципов/ценностей из `prototype.yaml`

**Выход:**
- HTML-блок, встроенный в `07b_COMPOSED/composed.html`
- Предметные иллюстрации остаются как labeled placeholders до прохождения этапа 07d (PR-C)

## Особенности

- **Стиль:** editorial — диагональная светлая подложка, крупные заголовки
- **Сетка:** grid-3 (три колонки)
- **Анимации:** отсутствуют (`has_animation: false`)
- **Рынок:** адаптирован под русскоязычный рынок (`ru_market: true`)
- **Источник:** импортирован из портфолио kdm1.ru через codex-block-generation 2026-05-16

## Связанные концепты

- [[block-composer]] — инжектирует токены и тексты в блок на этапе 07b
- [[block-composition]] — скилл, управляющий сборкой composed.html из блоков библиотеки
- [[ux-composer]] — выбирает данный блок из библиотеки при построении wireframe (07a)
- [[visual-curator]] — заменяет placeholders иллюстраций на реальные PNG на этапе 07d
- [[07b-composed]] — этап pipeline, в котором блок используется

## Источник

- `block-library/trust/trust-editorial-grid-3-portfolio-kdm1-ru-4/meta.yaml`