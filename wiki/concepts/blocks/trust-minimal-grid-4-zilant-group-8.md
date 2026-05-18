---
type: block
name: trust-minimal-grid-4-zilant-group-8
sources: ["block-library/trust/trust-minimal-grid-4-zilant-group-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-library-management"]
tags: ["trust", "minimal", "grid-4", "logos", "ru-market", "b2b", "services", "education"]
---

# Trust — Горизонтальная полоса логотипов (minimal, grid-4)

## Что делает
Отображает горизонтальную полосу небольших логотипов партнёров или клиентов на большом белом фоне — простой и чистый способ усилить доверие к услуге без перегруза.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** при сборке `composed.html`. Подходит для ниш **услуги**, **b2b-saas** и **образование**. Выбирается в wireframe-этапе (07a) как один из кандидатов блока `trust`; после подтверждения `selections.yaml` — вставляется в финальный `composed.html`.

Блок ориентирован на **российский рынок** (`ru_market: true`). Анимации нет (`has_animation: false`), стиль — минимализм (`style_mood: minimal`), раскладка — сетка из 4 колонок (`layout_pattern: grid-4`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок секции, например: «Нам доверяют» или «Работаем с брендами».
- Логотипы партнёров/клиентов (визуальные placeholders; реальные изображения подставляются на этапе PR-B/PR-C или вручную).

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html` с токенами дизайна из `tokens.json`.

## Связанные концепты
- [[block-composer]] — рендерит composed.html и встраивает блок с токенами
- [[ux-composer]] — выбирает этот блок как кандидат на wireframe-этапе 07a
- [[block-library-management]] — отвечает за регистрацию и индексацию блоков в библиотеке
- [[block-composition]] — скилл, описывающий логику сборки блоков в composed.html
- [[07b-composed]] — этап пайплайна, в рамках которого блок используется

## Источник
- `block-library/trust/trust-minimal-grid-4-zilant-group-8/meta.yaml`