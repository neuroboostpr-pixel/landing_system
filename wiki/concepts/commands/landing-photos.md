---
type: command
name: landing-photos
sources: ["commands/landing-photos.md"]
updated: 2026-05-26
triggers:
  - "обработать фотографии клиента"
  - "запустить photo pipeline"
  - "расставить фото по слотам лендинга"
  - "сгенерировать fallback фото"
  - "этап 07c"
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - landing-wireframe
  - landing-compose
  - landing-go
tags:
  - photos
  - stage-07c
  - pr-b
  - pipeline
---

# /landing-photos — Обработка клиентских фотографий (Stage 07c)

## Что делает

Запускает полный конвейер обработки фотографий клиента: принимает снимки, классифицирует их через AI, подбирает под слоты лендинга, показывает визуальный preview и встраивает одобренные фото в `composed.html`.

## Когда вызывать / в каком этапе

Запускается на этапе **07c** — после утверждения дизайн-системы (05) и выбора вариантов блоков в wireframe (07a). Вызывается вручную командой `/landing-photos` или автоматически через `/landing-go`. Требует два обязательных условия:
- `.landing-state.yaml → stages.05_design.status == approved`
- `07a_WIREFRAME/selections.yaml` существует с выбранными вариантами

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (7 тематических подпапок)
- Опционально: фото в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (для старых проектов)
- `tokens.json` из дизайн-системы (нужен для стилизации AI-генерации)
- `07a_WIREFRAME/selections.yaml` со списком photo-слотов

**Выход:**
- `07c_PHOTOS/catalog.yaml` — каталог фото с AI-тегами
- `07c_PHOTOS/selections.draft.yaml` — черновик расстановки от AI
- `07c_PHOTOS/selections.yaml` — финальная расстановка (заполняется пользователем через `photo-board.html`)
- `07c_PHOTOS/processed/` — обрезанные и оптимизированные фото для сайта
- `07b_COMPOSED/composed.html` — перерендеренная версия с реальными `<img>` вместо placeholders

## Флаги и режимы

| Флаг | Назначение |
|------|-----------|
| `--project <slug>` | Указать папку проекта явно |
| `--force-stage <этап>` | Сбросить и повторить конкретный подэтап (intake / classify / match / preview) |
| `--all-ai` | Пропустить сканирование inbox, использовать generative fallback для всех слотов |
| `--interactive` | Диалоговый режим: агент спрашивает что положить в каждый слот по очереди |

## Связанные концепты

- [[photo-curator]] — главный агент, оркестрирует весь процесс от intake до re-render
- [[photo-classifier]] — AI-классификатор фоток через codex
- [[photo-matcher]] — ранжирует кандидатов на каждый слот прототипа
- [[landing-wireframe]] — предшествующий этап, даёт список photo-слотов через selections.yaml
- [[landing-compose]] — создаёт composed.html с placeholders, которые landing-photos замещает
- [[landing-go]] — рекомендуемый способ запуска через оркестратор

## Источник

- `commands/landing-photos.md`