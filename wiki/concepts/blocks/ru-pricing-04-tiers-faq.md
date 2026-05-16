---
type: block
name: ru-pricing-04-tiers-faq
sources: ["block-library/pricing/ru-pricing-04-tiers-faq/meta.yaml"]
updated: 2026-05-13
triggers: []
stage: "07a"
uses:
  - block-composer
  - block-composition
  - ux-composer
tags:
  - pricing
  - faq
  - ru_market
  - b2c
  - services
  - tiers
---

# Тарифы + FAQ о стоимости — комбинированный блок

## Что делает

Отображает три тарифных карточки с выделенным рекомендованным вариантом (featured-бейдж) и сразу под ними — три вопроса-ответа об оплате. Всё на одной странице без аккордеона, чтобы клиент видел ответы немедленно и принимал решение прямо в секции цен.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** при подборе блоков из библиотеки через агента [[ux-composer]] или скилл [[wireframe-rendering]]. Подходит для лендингов услуг (b2c) с тремя уровнями тарификации, когда нужно снять возражения по оплате без перехода на отдельную страницу. Рекомендован для ниш, где у аудитории типичные страхи вокруг стоимости (предоплата, возврат, рассрочка).

## Что на вход / на выход

**На вход (слоты — 21 штука):**
- `headline` (обяз., до 60 симв.) — заголовок секции тарифов
- `subhead` (до 160 симв.) — подзаголовок
- `tier-1-name / tier-1-price / tier-1-desc / tier-1-cta` — карточка тарифа 1
- `tier-2-name / tier-2-price / tier-2-desc / tier-2-cta` — карточка тарифа 2 (featured, с border-highlight)
- `tier-3-name / tier-3-price / tier-3-desc / tier-3-cta` — карточка тарифа 3
- `faq-headline` (до 60 симв.) — заголовок FAQ-секции
- `faq-1-q / faq-1-a`, `faq-2-q / faq-2-a`, `faq-3-q / faq-3-a` — три вопроса-ответа (ответы до 300 симв.)

**На выход:**
- Готовый HTML-блок, встраиваемый в `wireframe.html` и `composed.html`
- Адаптивная верстка: на мобильном карточки и FAQ складываются в вертикальный стек

**Рекомендованные стили:** Minimalism & Swiss Style, Corporate Clean. Синий акцент из дизайн-токенов проекта.

## Особенности конверсии

FAQ без collapse (все ответы раскрыты сразу) работает лучше на лендингах, чем accordion — пользователь видит возражения закрытыми без клика. Рекомендуется вписывать типичные барьеры: предоплата, способы оплаты, возврат средств.

## Связанные концепты

- [[ux-composer]] — агент выбирает этот блок при wireframe-сборке
- [[block-composer]] — вставляет блок в composed.html с design-tokens и прототипными текстами
- [[block-composition]] — скилл, управляющий сборкой composed.html
- [[wireframe-rendering]] — скилл, рендерящий wireframe.html с блоком

## Источник

- `block-library/pricing/ru-pricing-04-tiers-faq/meta.yaml`
- Адаптирован из `github.com/nexu-io/open-design: design-templates/pricing-page` (Apache-2.0)