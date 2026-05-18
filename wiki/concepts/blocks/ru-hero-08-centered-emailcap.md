---
type: block
name: ru-hero-08-centered-emailcap
sources: ["block-library/hero/ru-hero-08-centered-emailcap/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition", "ux-composer"]
tags: ["hero", "email", "b2c", "services", "ru-market", "opendesign", "ticker"]
---

# Центрированный герой — email-форма + бегущая строка

## Что делает
Блок-герой с центрированным заголовком и встроенной формой сбора email: терракотовый фон, бегущая строка внизу и декоративный цветной подвал. Создаёт ощущение ажиотажа и подходит для лид-магнитов и пресейлов.

## Когда вызывать / в каком этапе
Используется на этапе **07b (block-composition / composed.html)**. Агент [[block-composer]] выбирает этот блок из библиотеки при сборке `composed.html`, если в `prototype.yaml` определён hero-слот с inline email-формой. Подходит для B2C и сервисных продуктов на русскоязычном рынке.

Рекомендован при стилях: **Brutalist Design**, **Bold & Expressive**, **Flat Design 2.0**.

## Что на вход / на выход

**Слоты (заполняются из prototype.yaml / prototype.md):**

| Слот | Тип | Макс. символов | Обязателен |
|---|---|---|---|
| `kicker` | text | 50 | нет |
| `headline` | text | 60 | **да** |
| `subhead` | text | 160 | нет |
| `email-placeholder` | text | 30 | нет |
| `primary-cta` | cta | — | **да** (default: «Получить доступ») |
| `ticker-text` | text | 60 | нет |

**На выходе:** HTML-блок в `07b_COMPOSED/composed.html` с заполненными слотами и брендовыми токенами из `tokens.json`. На мобильных — форма переходит в вертикальный стек.

**Важное ограничение:** в `primary-cta` **не использовать** WhatsApp/Telegram — только email или нейтральная кнопка.

## Связанные концепты
- [[block-composer]] — агент, который вставляет блок в composed.html на этапе 07b
- [[block-composition]] — скилл, управляющий сборкой блоков с токенами и текстами
- [[ux-composer]] — агент этапа 07a, который выбирает этот блок при рендере wireframe.html
- [[block-library-management]] — скилл управления библиотекой, куда входит этот блок

## Источник
- `block-library/hero/ru-hero-08-centered-emailcap/meta.yaml`
- Адаптировано из `github.com/nexu-io/open-design: design-templates/waitlist-page` (Apache-2.0)