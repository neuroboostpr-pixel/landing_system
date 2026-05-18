---
type: block
name: pricing-luxury-split-romanmelnikov-tilda-8
sources: ["block-library/pricing/pricing-luxury-split-romanmelnikov-tilda-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["pricing", "luxury", "split", "typography", "ru-market"]
---

# Pricing Luxury Split — типографическая секция стоимости

## Что делает
Оформляет раздел цены как крупную типографическую секцию с минимальным текстом и портретным визуальным акцентом. Разделённая (split) компоновка: цена и короткий заголовок занимают большую часть экрана, без лишнего описательного текста.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — когда `block-composer` собирает `composed.html` из одобренных блоков wireframe. Подходит для проектов в нишах **услуги, luxury-бренды, образование**, ориентированных на российский рынок. Выбирается на этапе 07a (wireframe) как вариант блока секции «Цены».

## Что на вход / на выход

**Вход:**
- `prototype.yaml` с заполненным слотом `heading` (обязательный текстовый слот — название пакета, цена или CTA)
- `tokens.json` с дизайн-токенами проекта (цвета, шрифты)
- Опционально: портретное фото для визуального акцента (слот не задан явно, используется как фоновый/декоративный элемент)

**Выход:**
- HTML-блок, встроенный в `07b_COMPOSED/composed.html`
- Визуал занимает максимальную высоту секции, текст минимален
- Анимации отсутствуют (`has_animation: false`)

## Связанные концепты
- [[block-composer]] — агент, который вставляет блок в composed.html на этапе 07b
- [[ux-composer]] — агент, который предлагает блок как вариант в wireframe.html на этапе 07a
- [[block-composition]] — скилл, управляющий логикой сборки блоков с подстановкой токенов
- [[block-library-management]] — скилл, ведущий реестр всех блоков библиотеки
- [[07b-composed]] — этап, на котором блок активируется

## Источник
- `block-library/pricing/pricing-luxury-split-romanmelnikov-tilda-8/meta.yaml`