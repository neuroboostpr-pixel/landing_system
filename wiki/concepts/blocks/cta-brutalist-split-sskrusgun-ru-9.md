---
type: block
name: cta-brutalist-split-sskrusgun-ru-9
sources: ["block-library/cta/cta-brutalist-split-sskrusgun-ru-9/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["cta", "brutalist", "split", "ru-market", "services", "education", "b2b-saas"]
---

# Яркий красный лид-магнит с фото людей и короткой формой

## Что делает
Блок призыва к действию в брутальном стиле: яркий красный фон, фотографии людей, короткая лид-форма и контрастная чёрная кнопка. Привлекает внимание и мотивирует оставить заявку.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** и **08 (Build)** при сборке лендинга. Подходит для блоков CTA в нишах услуг, образования и B2B-SaaS, когда нужен агрессивный визуальный акцент без анимации.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок лид-магнита.

**Выход:**
- Готовый HTML/PHP-блок Lazy Blocks с красным фоном, разделённой компоновкой (split-layout), фотографией людей слева/справа и короткой формой с чёрной кнопкой.

**Параметры блока:**
- `style_mood`: brutalist — жёсткий контрастный дизайн.
- `layout_pattern`: split — двухколоночная структура (текст + форма).
- `has_animation`: false — без анимаций.
- `ru_market`: true — адаптирован под российский рынок.

## Детали импорта
Блок сгенерирован через codex-block-generation по образцу сайта [sskrusgun.ru](https://sskrusgun.ru/) и импортирован 2026-05-16.

## Связанные концепты
- [[landing-compose]] — этап, на котором блок вставляется в composed.html
- [[landing-wireframe]] — wireframe-этап, где выбирается вариант CTA-блока из библиотеки
- [[landing-build]] — финальная сборка WordPress-темы с подключением Lazy Blocks блоков

## Источник
- `block-library/cta/cta-brutalist-split-sskrusgun-ru-9/meta.yaml`