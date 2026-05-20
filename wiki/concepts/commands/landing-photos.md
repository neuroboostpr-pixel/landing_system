---
type: command
name: landing-photos
sources: ["commands/landing-photos.md"]
updated: 2026-05-20
triggers:
  - "обработать фотографии клиента"
  - "загрузить фото на лендинг"
  - "запустить фото-пайплайн"
  - "подобрать фото к слотам"
  - "stage 07c"
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - landing-go
  - landing-compose
tags: [photos, stage-07c, pr-b, pipeline, intake, classify, match]
---

# /landing-photos — Обработка клиентских фото (Stage 07c)

## Что делает

Запускает полный конвейер обработки клиентских фотографий: принимает фото из папки `inbox/`, классифицирует их через AI, подбирает лучших кандидатов к каждому photo-слоту прототипа, даёт пользователю интерактивный UI для финального выбора, обрезает фото под нужный формат и перерендерит `composed.html` с реальными изображениями вместо placeholders.

## Когда вызывать / в каком этапе

Этап **07c** — после того как утверждены:
1. `05_ДИЗАЙН-СИСТЕМА` (статус `approved` в `.landing-state.yaml`) — нужен `tokens.json` для стилизации промптов codex.
2. `07a_WIREFRAME/selections.yaml` — нужно знать, какие photo-слоты войдут в финальный лендинг.

Вызывается вручную командой `/landing-photos` или автоматически через `/landing-go`. Принимает флаги `--project <slug>`, `--force-stage <этап>`, `--all-ai` (generative fallback на все слоты), `--interactive` (диалоговый режим по каждому слоту).

## Что на вход / на выход

**Вход:**
- `07c_PHOTOS/inbox/` — папка с фотографиями клиента (7 подпапок по типу: портреты, процессы и т.д.)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` — альтернативный источник (legacy)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — бренд-стиль
- `07a_WIREFRAME/selections.yaml` — выбранные блоки и photo-слоты

**Выход:**
- `catalog.yaml` — каталог фото с AI-тегами
- `selections.draft.yaml` — AI-черновик расстановки по слотам
- `selections.yaml` — финальная расстановка (утверждает пользователь)
- `processed/` — готовые кадрированные JPEG/WebP для сайта
- `photo-board.html` — drag-drop UI для выбора фото
- `photo-preview.html` — превью «фото в контексте блоков»
- `STATE.yaml` — статусы под-этапов пайплайна
- `.logs/` — логи AI-вызовов
- Обновлённый `07b_COMPOSED/composed.html` — placeholders заменены на `<img>` / `<picture>`

## Связанные концепты

- [[photo-curator]] — главный оркестратор этапа, диспатчит все под-агенты
- [[photo-classifier]] — тегирует фотки из `_свалка/` через codex
- [[photo-matcher]] — ранжирует кандидатов на каждый photo-слот
- [[photo-preview-board]] — обрезает под слоты, генерирует fallback, рендерит preview
- [[landing-go]] — вызывает `/landing-photos` автоматически в нужный момент pipeline
- [[landing-compose]] — предшествующий этап 07b, чей `composed.html` перерендерится с реальными фото

## Источник

- `commands/landing-photos.md`