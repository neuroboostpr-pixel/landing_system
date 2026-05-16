---
type: block
name: cta-corporate-grid-3-medregistrant-ru-5
sources: ["block-library/cta/cta-corporate-grid-3-medregistrant-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "corporate", "grid-3", "ru-market", "services", "medical", "b2b-saas", "tech"]
---

# CTA — Голубая сетка с тремя карточками преимуществ

## Что делает

Блок «продающей зоны» в корпоративном стиле: на голубом фоне располагаются три карточки с преимуществами компании и центральный призыв к действию. Подходит для финального убеждения посетителя перед конверсионной формой.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** при выборе блока CTA из библиотеки через [[ux-composer]]. Включается в итоговый `wireframe.html` и затем переносится в `composed.html` на этапе **07b** через [[block-composer]].

Подходит для ниш: услуги, медицина, B2B SaaS, tech. Ориентирован на российский рынок (`ru_market: true`). Анимации отсутствуют (`has_animation: false`) — подходит для строгих корпоративных заказчиков.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок блока CTA.
- Дополнительный контент карточек и текст кнопок передаётся через `prototype.yaml` при подстановке токенов.

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (кандидат) и `composed.html` (финал).
- Стилизация применяется через `tokens.json` (цвета, типографика) на этапе compose.

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки по нише и layout-паттерну при построении wireframe
- [[block-composer]] — инжектирует токены и текст прототипа в блок при compose
- [[wireframe-rendering]] — скилл рендера `wireframe.html`, куда включается этот блок
- [[block-composition]] — скилл финальной сборки `composed.html`
- [[block-library-management]] — управление каталогом, куда входит данный блок

## Источник

- `block-library/cta/cta-corporate-grid-3-medregistrant-ru-5/meta.yaml`
- Импортирован с [medregistrant.ru](https://medregistrant.ru/) · 2026-05-16 · метод: `codex-block-generation`