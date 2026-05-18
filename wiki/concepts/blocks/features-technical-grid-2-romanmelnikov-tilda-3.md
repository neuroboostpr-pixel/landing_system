---
type: block
name: features-technical-grid-2-romanmelnikov-tilda-3
sources: ["block-library/features/features-technical-grid-2-romanmelnikov-tilda-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-library-management"]
tags: ["features", "technical", "grid-2", "ru-market", "b2b-saas", "services", "education"]
---

# Контрастный проблемный блок с двумя колонками аргументов

## Что делает
Секция «Features» в техническом стиле: крупный заголовок-проблема или ключевой тезис на весь экран, под ним — два симметричных столбца с аргументами или преимуществами. Контрастное оформление сразу привлекает взгляд и удерживает читателя.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Block Compose)** — агент [[block-composer]] вставляет блок в `composed.html`, когда прототип содержит секцию с преимуществами или аргументами в двухколоночной сетке. Подходит для ниш: профессиональные услуги (`services`), B2B SaaS (`b2b-saas`) и образование (`education`). Ориентирован на российский рынок (`ru_market: true`). Анимации нет — блок статичный, загружается мгновенно.

## Что на вход / на выход

**Вход:**
- Слот `heading` (текст, обязательный) — главный заголовок блока; подтягивается из `prototype.yaml` при compose.
- Дизайн-токены из `tokens.json` (цвета, шрифты) — инжектируются [[block-composer]] автоматически.

**Выход:**
- HTML-фрагмент блока, готовый к вставке в `07b_COMPOSED/composed.html`.
- Две колонки аргументов — контент-плейсхолдеры; финальный текст поставляет [[content-writer]].

## Связанные концепты
- [[block-composer]] — рендерит composed.html и вставляет этот блок на этапе 07b
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe (07a)
- [[block-library-management]] — скилл управления библиотекой, отвечает за импорт и регистрацию блока
- [[content-writer]] — заполняет текстовые слоты блока финальным копирайтом на этапе 07
- [[design-tokens-generation]] — поставляет токены, которые block-composer инжектирует в стили блока

## Источник
- `block-library/features/features-technical-grid-2-romanmelnikov-tilda-3/meta.yaml`