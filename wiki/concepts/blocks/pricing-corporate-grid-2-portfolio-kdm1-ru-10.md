---
type: block
name: pricing-corporate-grid-2-portfolio-kdm1-ru-10
sources: ["block-library/pricing/pricing-corporate-grid-2-portfolio-kdm1-ru-10/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses:
  - block-composer
  - ux-composer
tags:
  - pricing
  - corporate
  - grid-2
  - ru-market
  - education
  - services
  - b2b-saas
---

# Pricing Corporate Grid-2 — Короткая секция стоимости с двумя карточками

## Что делает

Отображает секцию «Тарифы» / «Стоимость» в виде двух контрастных карточек выбора рядом и нижней бонусной полосы. Корпоративный стиль, без анимации, адаптирован под российский рынок.

## Когда вызывать / в каком этапе

Используется на **этапе 07b (Block Compose)**. Агент [[block-composer]] подставляет блок в `composed.html`, когда прототип содержит секцию сравнения тарифов или выбора пакета. Подходит для ниш: онлайн-образование, b2b-услуги, SaaS-сервисы.

Агент [[ux-composer]] может выбрать этот блок на этапе 07a при построении wireframe, если в `prototype.yaml` обнаружен раздел pricing с двумя опциями.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок секции, например «Выберите тариф»
- Токены дизайна из `tokens.json` (цвета, шрифты) — инжектируются [[block-composer]] автоматически
- Тексты карточек и бонусной полосы — берутся из `prototype.yaml` / `final-copy.md`

**Выход:**
- HTML-фрагмент, встроенный в `07b_COMPOSED/composed.html`
- Два контрастных блока-карточки (светлый / тёмный или акцент / нейтральный)
- Нижняя полоса бонуса (sticky-offer или highlight-bar)

## Связанные концепты

- [[block-composer]] — вставляет блок в composed.html и подставляет design-tokens
- [[ux-composer]] — выбирает блок при генерации wireframe из prototype.yaml
- [[block-composition]] — скилл, управляющий логикой сборки блоков
- [[block-library-management]] — скилл регистрации и обновления блоков в библиотеке
- [[07b-composed]] — этап, на котором блок становится частью финальной сборки

## Источник

- `block-library/pricing/pricing-corporate-grid-2-portfolio-kdm1-ru-10/meta.yaml`
- Импортирован из: `https://portfolio.kdm1.ru/...` методом `codex-block-generation` (2026-05-16)