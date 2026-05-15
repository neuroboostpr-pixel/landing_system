---
type: command
name: landing-photos
sources: ["commands/landing-photos.md"]
updated: 2026-05-15
triggers:
  - "обработать фотографии клиента"
  - "добавить фото на лендинг"
  - "запустить photo pipeline"
  - "расставить фотки по слотам"
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - block-composer
tags:
  - photos
  - stage-07c
  - pr-b
---

# /landing-photos — Конвейер клиентских фотографий

## Что делает

Запускает полный pipeline обработки фотографий клиента: принимает «сырые» снимки, классифицирует их через AI, подбирает лучшие кандидаты для каждого слота лендинга, показывает пользователю галерею для финального выбора и встраивает утверждённые фото в `composed.html`.

## Когда вызывать / в каком этапе

**Stage 07c** — после утверждения дизайн-системы (этап 05) и после того, как выбраны варианты блоков в wireframe (этап 07a). Вызывается вручную, не через `landing-orchestrator`. Обязательные гейты:

1. `.landing-state.yaml:stages.05_design.status == approved`
2. `07a_WIREFRAME/selections.yaml` существует с выбранными вариантами блоков

**Флаги:**
- `--project <slug>` — указать конкретную папку проекта
- `--force-stage <intake|classify|match|preview>` — повторить конкретный шаг
- `--all-ai` — пропустить клиентские фото, генерировать все слоты через codex (с подтверждением пользователя)
- `--interactive` — диалоговый режим: агент по очереди спрашивает что положить в каждый слот

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (7 подпапок по типу)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — для промптов codex
- `07a_WIREFRAME/selections.yaml` — список photo-слотов финального лендинга

**Выход (в `07c_PHOTOS/`):**
- `catalog.yaml` — каталог фото с AI-тегами
- `selections.draft.yaml` — черновая расстановка от AI
- `selections.yaml` — финальная расстановка (утверждается пользователем)
- `processed/` — финальные JPEG/AVIF для сайта
- `photo-board.html` — drag-drop UI для выбора фото по слотам
- `photo-preview.html` — превью «фото в местах»
- `STATE.yaml` — статусы шагов pipeline
- Обновлённый `07b_COMPOSED/composed.html` — placeholders `[photo slot: ...]` заменяются на реальные `<img>` или `<picture>`

**Identity-safe:** клиентские лица никогда не перерисовываются AI. Для testimonial/team-слотов AI-генерация требует явного `ai_approved_by_user`.

## Связанные концепты

- [[photo-curator]] — главный агент-оркестратор этапа 07c
- [[photo-classifier]] — тегирует отдельные фото через codex CLI
- [[photo-matcher]] — ранжирует топ-3 кандидата на каждый слот
- [[photo-preview-board]] — кадрирует фото и генерирует generative fallback
- [[07c-photos]] — папка-этап, рабочее место всего pipeline
- [[block-composer]] — собирает composed.html, куда в итоге встраиваются фото
- [[07a-wireframe]] — предоставляет список слотов для matching

## Источник

- `commands/landing-photos.md`