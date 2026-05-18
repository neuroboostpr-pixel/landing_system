---
type: block
name: trust-corporate-grid-2-portfolio-kdm1-ru-7
sources: ["block-library/trust/trust-corporate-grid-2-portfolio-kdm1-ru-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["trust", "corporate", "grid-2", "ecommerce", "b2b-saas", "services", "ru-market", "icons", "logos"]
---

# Блок доверия: наличие и доставка с иконками и логотипами партнёров

## Что делает
Отображает информацию о наличии товара и условиях доставки в виде двухколоночной сетки серых карточек с иконками. В нижней части — логотипы партнёров, усиливающие доверие. Подходит для корпоративного стиля без анимации.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при сборке прототипа: `ux-composer` выбирает этот блок из библиотеки, когда прототип содержит секцию доверия с акцентом на логистику, партнёрство или наличие товара. Далее на этапе **07b (Compose)** блок наполняется реальными текстами через `block-composer`.

Подходящие ниши: **ecommerce**, **services**, **b2b-saas**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции
- Иконки для карточек (слоты под визуальные элементы, тип — icon)
- Логотипы партнёров (изображения)

**Выход:**
- HTML-блок в стиле `corporate`, паттерн `grid-2`
- Серые карточки с иконками и подписями
- Строка логотипов партнёров внизу
- Без анимации (`has_animation: false`)

**Импорт:** блок сгенерирован через `codex-block-generation` на основе PDF-портфолио kdm1.ru (16 мая 2026).

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — наполняет блок токенами и текстами прототипа на этапе 07b
- [[wireframe-rendering]] — рендерит блок в `wireframe.html` с вариантами выбора
- [[block-composition]] — скилл, управляющий подстановкой design-токенов в блок
- [[block-library-management]] — скилл учёта и обновления библиотеки блоков
- [[visual-curator]] — заполняет icon/logo слоты блока на этапе 07d

## Источник
- `block-library/trust/trust-corporate-grid-2-portfolio-kdm1-ru-7/meta.yaml`