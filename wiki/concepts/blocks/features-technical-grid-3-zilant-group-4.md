---
type: block
name: features-technical-grid-3-zilant-group-4
sources: ["block-library/features/features-technical-grid-3-zilant-group-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "grid-3", "technical", "b2b-saas", "services", "tech", "education", "ru-market"]
---

# Воздушный блок с контрастным заголовком и тремя карточками (Zilant Group)

## Что делает

Отображает секцию «Преимущества» или «Возможности» в виде трёх белых карточек на воздушном фоне с крупным контрастным заголовком и декоративной бумажной графикой. Подходит для технических и сервисных лендингов.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)**, когда `ux-composer` подбирает блок для секции features. Также задействуется на этапе **07b (Block Compose)** при финальной сборке `composed.html` через `block-composer`. Блок выбирается из библиотеки автоматически по категории `features` и паттерну `grid-3` — либо вручную маркетологом через `wireframe.html`.

Анимации нет (`has_animation: false`), поэтому блок подходит для проектов без GSAP-сцен.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — контрастный заголовок секции
- Токены дизайна из `tokens.json` (цвета, шрифты) — инжектируются автоматически при compose

**Выход:**
- HTML-фрагмент блока с тремя белыми карточками и декоративной графикой, готовый к встраиванию в `composed.html`
- Контент подставляется из `prototype.yaml` при прогоне `block-composer`

**Источник:** импортирован с `https://zilant.group/` методом `codex-block-generation` (2026-05-16).

## Связанные концепты

- [[ux-composer]] — выбирает этот блок при построении wireframe.html на этапе 07a
- [[block-composer]] — инжектирует токены и тексты прототипа на этапе 07b
- [[wireframe-rendering]] — скилл рендеринга, в рамках которого блок получает 2–3 кандидата для выбора
- [[block-composition]] — скилл финальной сборки composed.html с токенами и заменой плейсхолдеров
- [[block-library-management]] — управление жизненным циклом блока в библиотеке

## Источник

- `block-library/features/features-technical-grid-3-zilant-group-4/meta.yaml`