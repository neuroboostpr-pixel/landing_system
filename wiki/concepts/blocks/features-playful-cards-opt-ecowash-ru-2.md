---
type: block
name: features-playful-cards-opt-ecowash-ru-2
sources: ["block-library/features/features-playful-cards-opt-ecowash-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "cards", "playful", "ru-market", "ecommerce", "services", "education"]
---

# Горизонтальная подборка карточек аудиторий (Playful Cards)

## Что делает

Отображает горизонтальную подборку карточек для разных целевых аудиторий — округлые белые плитки с маленькими иллюстрациями. Подходит для блока «Для кого это» или «Наши клиенты». Стиль игривый, дружелюбный, без анимации.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** и **07b (Block Compose)**. Агент [[ux-composer]] выбирает блок из библиотеки при построении wireframe, если прототип содержит раздел с аудиториями или карточками преимуществ в игривом стиле. [[block-composer]] инжектирует токены и заменяет плейсхолдеры на финальный текст.

Подходящие ниши: **ecommerce**, **services**, **education**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `heading` — обязательный текстовый слот (заголовок секции, например «Кому подойдёт»)
- `tokens.json` — цвета и шрифты из дизайн-системы (инжектируются на этапе 07b)
- Контент аудиторий из `prototype.yaml`

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (07a) или `composed.html` (07b)
- Карточки с иллюстрациями остаются как визуальные плейсхолдеры до прохождения этапов PR-B / PR-C

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe, не изобретает новых блоков
- [[block-composer]] — рендерит `composed.html`, подставляет токены и текст прототипа
- [[wireframe-rendering]] — скилл, управляющий генерацией wireframe.html из block-library
- [[block-composition]] — скилл этапа 07b, отвечает за финальную сборку
- [[block-library-management]] — скилл ведения и импорта блоков в библиотеку

## Источник

- `block-library/features/features-playful-cards-opt-ecowash-ru-2/meta.yaml`
- Импортирован с [opt.ecowash.ru](https://opt.ecowash.ru/) методом `codex-block-generation` 2026-05-16