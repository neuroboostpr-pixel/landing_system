---
type: block
name: social-proof-minimal-centered-project21993216-tild-3
sources: ["block-library/social-proof/social-proof-minimal-centered-project21993216-tild-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["social-proof", "minimal", "centered", "carousel", "ru-market", "services", "ecommerce", "education"]
---

# Секция отзывов с каруселью (минимализм, по центру)

## Что делает
Отображает блок отзывов или логотипов клиентов с заголовком по центру и маленькими кнопками-стрелками карусели. Подходит для брендов, которым важна лаконичность и чистота оформления без лишних деталей.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — `block-composer` вставляет блок в `composed.html` после того, как выбран в `wireframe.html` на этапе 07a. Подходит для ниш: услуги, e-commerce, образование. Целевой рынок — РФ.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип: `text`) — заголовок секции отзывов (например, «Что говорят наши клиенты»)
- Контент карточек отзывов или логотипов клиентов (текстовые данные из `prototype.yaml`)
- Токены дизайна из `tokens.json` (цвета, типографика)

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html`
- Карусель управляется маленькими кнопками-стрелками; анимация отсутствует (`has_animation: false`)
- Макет центрированный (`layout_pattern: centered`), стиль минималистичный (`style_mood: minimal`)

## Связанные концепты
- [[block-composer]] — агент этапа 07b, который рендерит блок в `composed.html` с подстановкой токенов и текстов
- [[ux-composer]] — агент этапа 07a, который предлагает блок как кандидат в `wireframe.html`
- [[block-composition]] — скилл, описывающий правила сборки блоков с токенами и слотами
- [[block-library-management]] — скилл управления библиотекой; отвечает за импорт и регистрацию блоков

## Источник
- `block-library/social-proof/social-proof-minimal-centered-project21993216-tild-3/meta.yaml`