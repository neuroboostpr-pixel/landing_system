---
type: block
name: features-minimal-grid-2-sskrusgun-ru-4
sources: ["block-library/features/features-minimal-grid-2-sskrusgun-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a / 07b"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "minimal", "grid-2", "ru-market", "ecommerce", "services", "no-animation"]
---

# Features Minimal Grid-2 — Лаконичная витрина категорий

## Что делает

Отображает категории товаров или услуг в виде двухколоночной сетки с крупными изолированными изображениями на светлом фоне. Стиль — минималистичный, без анимаций, акцент на чистоте и простоте восприятия.

## Когда вызывать / в каком этапе

Используется на этапах **07a (Wireframe)** и **07b (Compose)**. Агент [[ux-composer]] выбирает этот блок из библиотеки при построении wireframe.html, если прототип содержит секцию с перечнем категорий или услуг. Агент [[block-composer]] подставляет реальные тексты и placeholders изображений при сборке composed.html.

Подходит для ниш: **ecommerce** (каталог категорий) и **services** (витрина направлений).

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок секции витрины.
- Изображения категорий (слоты типа `image`, описываемые в финальном шаблоне блока) — заполняются photo-pipeline (PR-B) или AI-генерацией (PR-C).

**Выход:**
- HTML-фрагмент секции features в стиле minimal grid-2, встраиваемый в wireframe.html / composed.html.
- Нет анимаций (`has_animation: false`) — блок рендерится статично.

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html на этапе 07a
- [[block-composer]] — использует блок при сборке composed.html на этапе 07b
- [[wireframe-rendering]] — скилл, отвечающий за отрисовку wireframe с вариантами блоков
- [[block-composition]] — скилл, инжектирующий design-tokens и прототипные тексты в блок
- [[block-library-management]] — скилл управления библиотекой, в которую входит этот блок
- [[photo-curator]] — заполняет image-слоты блока клиентскими фото (этап 07c)

## Источник

- `block-library/features/features-minimal-grid-2-sskrusgun-ru-4/meta.yaml`
- Импортирован с [sskrusgun.ru](https://sskrusgun.ru/) методом `codex-block-generation` 2026-05-16