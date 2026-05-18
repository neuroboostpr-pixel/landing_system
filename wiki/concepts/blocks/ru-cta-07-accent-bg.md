---
type: block
name: ru-cta-07-accent-bg
sources: ["block-library/cta/ru-cta-07-accent-bg/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composition", "block-library-management", "ux-composer"]
tags: ["cta", "b2c", "services", "ru-market", "accent-bg", "минимализм", "opendesign"]
---

# CTA на акцентном фоне — контраст, минимум элементов

## Что делает

Полноширинный блок призыва к действию с ярким акцентным фоном (терракотовый), белым текстом и белой кнопкой. Максимально простой, контрастный, без лишних деталей — работает как финальный толчок к конверсии перед футером.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** — агент [[block-composer]] выбирает этот блок из библиотеки по результатам wireframe-голосования (`selections.yaml`). Подходит для сайтов в нишах **услуги** и **b2c**. Рекомендован для визуальных стилей: Minimalism & Swiss Style, Bold & Expressive, Flat Design 2.0.

Хорошо встаёт в конец лендинга: после блоков с преимуществами, кейсами или тарифами — прямо перед footer.

## Что на вход / на выход

**Слоты (входные данные из `prototype.yaml`):**

| Слот | Тип | Макс. символов | Обязательный |
|---|---|---|---|
| `headline` | text | 70 | да |
| `subhead` | text | 180 | нет |
| `primary-cta` | cta | — | да (дефолт: «Начать сейчас») |
| `footnote` | text | 100 | нет |

**Выход:** готовый HTML-фрагмент с акцентным фоном, встроенный в `07b_COMPOSED/composed.html`. Footnote снимает возражения (пример: «без обязательств», «бесплатно первые N дней»).

**Ограничения:** WhatsApp и Telegram-кнопки в этом блоке НЕ используются.

## Источник блока

Адаптирован из OpenDesign (шаблон `saas-landing`).  
Лицензия: Apache-2.0 — `github.com/nexu-io/open-design`.

## Связанные концепты

- [[block-composer]] — агент, который вставляет блок в composed.html с токенами и текстами
- [[block-composition]] — скилл, управляющий логикой сборки блоков
- [[block-library-management]] — скилл ведения и обновления библиотеки блоков
- [[ux-composer]] — агент wireframe, который предлагает этот блок как вариант в 07a

## Источник

- `block-library/cta/ru-cta-07-accent-bg/meta.yaml`