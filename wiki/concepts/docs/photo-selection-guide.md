---
type: rule
name: photo-selection-guide
sources: ["docs/photo-selection-guide.md"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["photo-matcher", "photo-curator", "photo-classifier", "photo-preview-board", "wp-builder"]
tags: ["photos", "photo-pipeline", "identity-safe", "pr-b", "slots", "matching"]
---

# Photo Selection Guide — Руководство по выбору фотографий

## Что делает
Формальный стандарт для подбора фото в слоты лендинга. Определяет, какой тип фотографии подходит для каждого блока: hero, model card, features, trust, CTA. Устраняет «рандом» при matching — агент и человек следуют одним правилам.

## Когда вызывать / в каком этапе
Применяется на этапе **07c** (photo-pipeline, PR-B): при классификации клиентских фото, при матчинге фото к слотам, при генерации fallback через codex. Также используется на этапах 07d/07e (composed final) и 08 (wp-builder) при подстановке `<picture>` элементов.

## Что на вход / на выход

**На вход:**
- Клиентские фотографии из `07c_PHOTOS/inbox/`
- Inspiration-фото (внешние референсы)
- Список слотов из `composed.html` и wireframe-блоков

**На выход:**
- Классификация каждого фото по типу (`exterior_studio`, `interior_dashboard`, `top_down_lifestyle` и др. — всего 14 типов)
- Правила matching: какой тип фото разрешён / запрещён для каждого типа блока
- Порядок слайдов в model card (exterior → lifestyle → dashboard → detail → top-down)
- Fallback-приоритет: client photo → inspiration (с `needs_replacement: true`) → AI codex → SVG placeholder
- Чек-лист из 7 пунктов перед финальной подстановкой фото в слот

## Ключевые правила
- **Hero-слот** — только полная машина (`exterior_studio` или `exterior_lifestyle`). Top-down и close-up запрещены.
- **Top-down фото** — это lifestyle (что влезает в машину), не главное фото модели. Идут последним слайдом или в отдельный showcase-блок.
- **Identity-safe**: реальные лица без разрешения — под запретом. AI-генерация лиц для testimonials требует `ai_approved_by_user: true` в photo-mapping.yaml.
- **Mobile/desktop**: hero нуждается в двух вариантах кропа через `<picture>` с media queries.
- Все источники фото помечаются в `photo-mapping.yaml`: `client` / `inspiration` / `ai`.

## Связанные концепты
- [[photo-matcher]] — использует этот guide как source of truth при скоринге фото → слот
- [[photo-curator]] — orchestrator PR-B, читает guide при классификации inbox-фото
- [[photo-classifier]] — теггирует фото по типам из таблицы guide
- [[photo-preview-board]] — визуализирует результат matching для approve пользователем
- [[wp-builder]] — генерирует `<picture>` с mobile/desktop вариантами на этапе 08
- [[visual-generation]] — codex image_gen для fallback-генерации недостающих типов

## Источник
- `docs/photo-selection-guide.md`