---
type: block
name: gallery-editorial-grid-3-portfolio-kdm1-ru-6
sources: ["block-library/gallery/gallery-editorial-grid-3-portfolio-kdm1-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["gallery", "editorial", "grid-3", "ecommerce", "luxury", "services", "ru-market"]
---

# Gallery Editorial Grid-3 — Мозаика фотографий и текстовых карточек

## Что делает
Показывает продукт в деталях, цветах и реальных сценариях через мозаику из фотографий и текстовых карточек. Идеально подходит для лендингов, где важно передать атмосферу и визуальное богатство товара или услуги.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при выборе блока-галереи для разделов демонстрации продукта. Агент [[ux-composer]] выбирает этот блок из библиотеки при условии, что в прототипе обозначен раздел с сеткой фотографий (3 колонки) в editorial-стиле. Подходит для ниш: e-commerce, люкс, услуги. Рынок: Россия (`ru_market: true`).

## Что на вход / на выход

**На вход:**
- Обязательный слот `heading` (тип: text) — заголовок секции галереи
- Фотографии продукта/сервиса (заполняются на этапе 07c через [[photo-curator]])
- Токены дизайн-системы из `tokens.json` (цвета, типографика)

**На выход:**
- HTML-блок с трёхколоночной сеткой (`grid-3`) в editorial-настроении
- Статичный блок без анимации (`has_animation: false`)
- Placeholders для фото-слотов до этапа 07c

## Технические характеристики
- **Категория:** gallery
- **Layout:** grid-3 (три колонки)
- **Настроение:** editorial
- **Анимации:** нет
- **Источник:** импортирован из [portfolio.kdm1.ru](https://portfolio.kdm1.ru/upload/iblock/f94/slk0g7ub4mnpodwty9jl8iyrq4zk33uv/LCase.pdf) методом `codex-block-generation` (2026-05-16)

## Связанные концепты
- [[ux-composer]] — выбирает блок при рендере wireframe.html на этапе 07a
- [[block-library-management]] — управляет регистрацией и поиском блоков в библиотеке
- [[photo-curator]] — заполняет фото-слоты блока на этапе 07c
- [[wireframe-rendering]] — скилл, который рендерит этот блок в интерактивный wireframe
- [[block-composition]] — скилл этапа 07b, инжектит design-tokens и контент в финальный composed.html

## Источник
- `block-library/gallery/gallery-editorial-grid-3-portfolio-kdm1-ru-6/meta.yaml`