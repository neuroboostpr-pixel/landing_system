---
type: block
name: features-corporate-grid-3-opt-ecowash-ru-8
sources: ["block-library/features/features-corporate-grid-3-opt-ecowash-ru-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["features", "corporate", "grid-3", "ru-market", "b2b", "ecommerce", "services"]
---

# Блок преимуществ: шесть пронумерованных карточек + CTA-полоса

## Что делает

Отображает шесть пронумерованных карточек с преимуществами в три колонки и завершает блок горизонтальной полосой с призывом к действию. Корпоративный стиль, без анимации — подходит для строгих b2b-сайтов и интернет-магазинов.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при подборе блоков для секции «Преимущества» / «Почему мы». Агент [[ux-composer]] выбирает этот блок из библиотеки, когда прототип требует компактного перечисления 5–6 фич с нумерацией и завершающим CTA. Блок не активируется автоматически — [[ux-composer]] выбирает его по соответствию `layout_pattern: grid-3` и `style_mood: corporate`.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок блока преимуществ.
- Контент шести карточек (тексты передаются из `prototype.yaml` на этапе [[block-composition]]).

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (этап 07a) и `composed.html` (этап 07b).
- Нижняя CTA-полоса с кнопкой — текст кнопки берётся из прототипа.

## Связанные концепты

- [[ux-composer]] — выбирает блок при рендеринге wireframe.html на основе meta.yaml
- [[block-composition]] — инжектирует design-tokens и тексты из prototype.yaml в слоты блока
- [[block-library-management]] — управляет библиотекой, индексирует этот блок
- [[wireframe-rendering]] — рендерит интерактивный вариант блока (desktop + mobile) в 07a

## Источник

- `block-library/features/features-corporate-grid-3-opt-ecowash-ru-8/meta.yaml`
- Импортирован с: `https://opt.ecowash.ru/` — 2026-05-16, метод: codex-block-generation