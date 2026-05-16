---
type: block
name: ru-pricing-03-3tier-saas
sources: ["block-library/pricing/ru-pricing-03-3tier-saas/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses:
  - block-composer
  - ux-composer
  - block-composition
  - design-tokens-generation
tags:
  - pricing
  - saas
  - b2c
  - services
  - ru-market
  - 3-tier
  - opendesign
---

# Три тарифа SaaS — рекомендованный тир, чеклист (ru-pricing-03-3tier-saas)

## Что делает

Отображает три ценовых тарифа в одну строку с выделением среднего (рекомендованного) варианта — рамкой и бейджем. Под каждым тарифом — список функций с галочками и кнопка-CTA. Цены указываются в рублях. На мобильном — карточки складываются вертикально.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** — когда `block-composer` или `ux-composer` собирают `composed.html` из выбранных блоков. Подходит для посадочных страниц сервисов и B2C-продуктов, где нужно показать несколько тарифных планов и направить пользователя к среднему («Бизнес») варианту. Рекомендован для ниш: подписочные сервисы, онлайн-инструменты, агентские пакеты услуг.

## Что на вход / на выход

**На вход** (слоты, заполняются через `prototype.yaml` или вручную в `composed.html`):
- `headline` — заголовок секции (до 60 символов, обязательно)
- `subhead` — подзаголовок (до 160 символов, необязательно)
- Для каждого из трёх тарифов: название (`tier-N-name`), описание (`tier-N-desc`), цена (`tier-N-price`), до 3–4 функций (`tier-N-f1..f4`), кнопка (`tier-N-cta`)
- Тариф-3 может содержать «Индивидуально» вместо конкретной цены — это лучше конвертирует

**На выход**:
- HTML-блок в `composed.html` с тремя карточками, средняя — с `border-highlight` и badge «Рекомендуем» (или аналог)
- Адаптивная вёрстка: desktop — 3 колонки, mobile — вертикальный стек

## Технические характеристики

| Параметр | Значение |
|---|---|
| Категория | `pricing` |
| Стиль | white-surface, clean |
| Рекомендованные стили | Minimalism & Swiss Style, Corporate Clean, Flat Design 2.0 |
| Источник | OpenDesign / nexu-io/open-design (Apache-2.0) |
| Рынок | RU (цены в ₽) |

**Conversion note:** выделение среднего тарифа (border + badge) статистически увеличивает его выбор — всегда заполнять `tier-2` самым маржинальным предложением.

## Связанные концепты

- [[block-composer]] — рендерит блок в `composed.html` на этапе 07b
- [[ux-composer]] — выбирает блок из библиотеки при сборке wireframe на этапе 07a
- [[block-composition]] — скилл, управляющий подстановкой tokens и текстов в блоки
- [[design-tokens-generation]] — поставляет цвета и шрифты, которые инжектируются в стиль блока
- [[block-library-management]] — скилл учёта и версионирования блоков библиотеки

## Источник

- `block-library/pricing/ru-pricing-03-3tier-saas/meta.yaml`
- Атрибуция: `github.com/nexu-io/open-design: design-templates/saas-landing (Apache-2.0)`