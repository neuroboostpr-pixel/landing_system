---
type: block
name: features-technical-centered-medregistrant-ru-4
sources: ["block-library/features/features-technical-centered-medregistrant-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "technical", "centered", "medical", "services", "tech", "ru-market"]
---

# Features: Анатомическая схема услуги (технический стиль, центрированный)

## Что делает

Блок «преимущества / особенности услуги» в техническом стиле: визуальная схема с пунктами, расположенными по кругу вокруг центрального элемента, на фоне приглушённой графики. Подходит для медицины, B2B-сервисов и IT — там, где важно передать системность и профессионализм.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — `ux-composer` выбирает блок из библиотеки при построении wireframe.html. На этапе **07b (Compose)** — `block-composer` инжектирует дизайн-токены и подставляет текст из prototype.yaml.

Подходит для лендингов ниш: **медицина**, **услуги**, **технологии/IT**. Ориентирован на русскоязычный рынок (`ru_market: true`). Анимация отсутствует — уместен там, где нужна строгость без эффектов.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок блока с названием или концепцией услуги.
- Дизайн-токены из `tokens.json` (цвета, шрифты) — инжектируются автоматически на этапе compose.
- Контент из `prototype.yaml` — пункты по кругу и фоновая графика берутся из слотов прототипа.

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b).
- Слоты типа `text` заполнены реальными текстами; визуальные плейсхолдеры (фоновая графика) остаются для PR-C (visual-curator).

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe
- [[block-composer]] — рендерит composed.html с инжекцией токенов и текста
- [[wireframe-rendering]] — скилл, запускающий ux-composer на этапе 07a
- [[block-composition]] — скилл, запускающий block-composer на этапе 07b
- [[block-library-management]] — управление библиотекой, в которой живёт этот блок
- [[visual-curator]] — заполняет фоновую графику (приглушённый паттерн) на этапе 07d

## Источник

- `block-library/features/features-technical-centered-medregistrant-ru-4/meta.yaml`