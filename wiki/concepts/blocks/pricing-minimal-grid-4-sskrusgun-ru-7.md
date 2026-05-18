---
type: block
name: pricing-minimal-grid-4-sskrusgun-ru-7
sources: ["block-library/pricing/pricing-minimal-grid-4-sskrusgun-ru-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses:
  - ux-composer
  - block-composer
  - block-library-management
tags: ["pricing", "minimal", "grid-4", "ru-market", "services", "education", "b2b-saas"]
---

# Табличная сетка тарифов — minimal grid-4

## Что делает
Отображает прайсинг в виде компактной таблично-сеточной раскладки из четырёх колонок с минималистичным оформлением: тонкие линии-разделители, красные акцентные ссылки. Подходит для сравнительного отображения тарифных планов и дополнительных опций.

## Когда вызывать / в каком этапе
Используется на этапе **07a (wireframe)** — `ux-composer` выбирает блок из библиотеки при наличии в прототипе секции цен/тарифов. Затем на этапе **07b (compose)** — `block-composer` инжектирует дизайн-токены и подставляет тексты из prototype.yaml. Подходит для ниш: услуги, образование, B2B-SaaS.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции с ценами
- Дизайн-токены из `tokens.json` (цвета, шрифты)
- Тексты тарифов из `prototype.yaml`

**Выход:**
- HTML-фрагмент блока, готовый к встройке в `wireframe.html` или `composed.html`
- Четырёхколоночная сетка тарифов с заголовком и дополнительными строками опций
- Статичный блок (анимация отсутствует — `has_animation: false`)

## Особенности блока
- **Стиль:** minimal — без лишних декораций, акцент на читаемость цифр
- **Раскладка:** grid-4 — четыре равные колонки, удобно для сравнения 4 тарифов
- **Акцент:** красные ссылки внутри таблицы (для CTA или пояснений к опциям)
- **Рынок:** оптимизирован под российский рынок (`ru_market: true`)
- **Источник:** импортирован с sskrusgun.ru методом codex-block-generation

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при рендере wireframe.html из prototype.yaml
- [[block-composer]] — встраивает блок в composed.html с токенами и контентом
- [[block-library-management]] — управляет библиотекой, в которой хранится этот блок
- [[design-tokens-generation]] — поставляет токены (цвета, шрифты), используемые блоком
- [[block-composition]] — скилл этапа 07b, в рамках которого блок рендерится финально

## Источник
- `block-library/pricing/pricing-minimal-grid-4-sskrusgun-ru-7/meta.yaml`