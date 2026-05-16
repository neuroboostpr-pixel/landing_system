---
type: block
name: contacts-corporate-split-medregistrant-ru-9
sources: ["block-library/contacts/contacts-corporate-split-medregistrant-ru-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["contacts", "corporate", "split", "ru-market", "medical", "b2b-saas", "services", "no-animation"]
---

# Контактная секция на голубом фоне (split-макет)

## Что делает
Отображает контактный раздел лендинга в двухколоночном (split) макете на голубом фоне: слева — логотип, телефон и иконки связи, справа — форма заявки. Подходит для корпоративного и медицинского сегмента на российском рынке.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при выборе блока для секции контактов. `ux-composer` подбирает блок из библиотеки, когда прототип содержит контактную секцию корпоративного стиля с формой. Подходит, если ниша — услуги, медицина или B2B-SaaS, и нужен строгий деловой вид без анимаций.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции (например, «Свяжитесь с нами»)
- Логотип клиента (из `04_БРЕНД/logos/`)
- Контактные данные: телефон, иконки мессенджеров/соцсетей

**Выход:**
- HTML-блок контактной секции, встроенный в `wireframe.html` (этап 07a) и `composed.html` (этап 07b)
- При финальной сборке — подключённая форма через Fluent Forms (этап 08)

## Связанные концепты
- [[ux-composer]] — подбирает этот блок из библиотеки при рендере wireframe
- [[block-composer]] — подставляет токены и тексты при compose (этап 07b)
- [[block-library-management]] — скилл, отвечающий за каталог блоков и их метаданные
- [[wireframe-rendering]] — скилл рендера wireframe.html, куда встраивается блок
- [[integrations-engineer]] — подключает форму заявки (Fluent Forms + Telegram webhook) на этапе 08

## Источник
- `block-library/contacts/contacts-corporate-split-medregistrant-ru-9/meta.yaml`