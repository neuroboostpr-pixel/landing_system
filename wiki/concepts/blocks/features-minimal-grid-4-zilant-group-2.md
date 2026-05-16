---
type: block
name: features-minimal-grid-4-zilant-group-2
sources: ["block-library/features/features-minimal-grid-4-zilant-group-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "minimal", "grid-4", "ru-market", "no-animation", "services", "b2b-saas", "tech"]
---

# Узкая строка преимуществ — Minimal Grid 4 (Zilant Group)

## Что делает

Тонкая горизонтальная полоса с четырьмя иконками и текстом, которая визуально разделяет первый экран (hero) и следующий раздел лендинга. Работает как «мост» между hero и основным контентом — кратко показывает ключевые преимущества без перегрузки.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** при выборе блока категории `features`. Подходит, когда нужно ненавязчиво обозначить 4 преимущества сразу после hero-блока, не создавая отдельного полноразмерного раздела. Особенно уместен для ниш: услуги, B2B SaaS, tech-продукты. Анимации нет — рекомендуется для проектов с приоритетом скорости загрузки.

Агент [[ux-composer]] выбирает этот блок из библиотеки через скилл [[wireframe-rendering]]. На этапе **07b** скилл [[block-composition]] подставляет дизайн-токены и тексты из прототипа.

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип: `text`, обязательный) — заголовок или краткие подписи к 4 иконкам.
- Иконки-слоты генерируются автоматически агентом [[icon-generator]] на этапе 07d.

**Выход:**
- HTML-фрагмент блока с 4-колоночной сеткой (layout: `grid-4`), стиль `minimal`.
- Интегрируется в `wireframe.html` (07a) и `composed.html` (07b).

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[wireframe-rendering]] — скилл рендеринга интерактивного wireframe.html
- [[block-composition]] — скилл, подставляющий токены и тексты в composed.html
- [[icon-generator]] — генерирует иконки для слотов этого блока на этапе 07d
- [[block-library-management]] — управляет пополнением и обновлением библиотеки блоков
- [[visual-curator]] — оркестрирует генерацию визуальных слотов (07d)

## Источник

- `block-library/features/features-minimal-grid-4-zilant-group-2/meta.yaml`
- Импортирован с https://zilant.group/ методом `codex-block-generation` (2026-05-16)