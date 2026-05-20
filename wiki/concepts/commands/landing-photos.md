---
type: command
name: landing-photos
sources: ["commands/landing-photos.md"]
updated: 2026-05-20
triggers:
  - "обработать фотки клиента"
  - "добавить фото на лендинг"
  - "photo pipeline"
  - "расставить фото по слотам"
  - "stage 07c"
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - landing-go
  - landing-compose
  - landing-wireframe
tags: [photos, stage-07c, pr-b, ai-classify, generative-fallback]
---

# /landing-photos — конвейер клиентских фотографий

## Что делает

Запускает полный цикл обработки фото клиента: сортирует снимки из папки `inbox/`, классифицирует их через AI, подбирает лучший кадр к каждому слоту макета, позволяет расставить фото через визуальный drag-drop интерфейс и наконец встраивает итоговые фото в `composed.html`, убирая плейсхолдеры.

## Когда вызывать / в каком этапе

**Stage 07c** — между `07b_COMPOSED` и финальным production-рендером.

Обязательные гейты перед запуском:
1. Этап 05 (дизайн-система) утверждён — `status == approved` в `.landing-state.yaml`. Без `tokens.json` AI не знает стиль.
2. Файл `07a_WIREFRAME/selections.yaml` существует и содержит выбранные варианты блоков — без него неизвестно, какие photo-слоты войдут в лендинг.

Рекомендуется запускать через `/landing-go` (оркестратор сам отследит гейты). Допустим ручной вызов этой командой напрямую.

**Флаги:**
- `--project <slug>` — указать папку проекта явно
- `--force-stage <intake|classify|match|preview>` — пересброс конкретного этапа
- `--all-ai` — пропустить inbox, все слоты генерируются через codex fallback (требует подтверждения)
- `--interactive` — агент спрашивает по очереди что положить в каждый слот

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс, объекты и т.д.)
- Дополнительный путь: `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (старые проекты)
- `07a_WIREFRAME/selections.yaml` — список photo-слотов
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета и стиль для промптов codex

**Выход (в `07c_PHOTOS/`):**
- `catalog.yaml` — каталог всех фото с AI-тегами
- `selections.draft.yaml` — черновик расстановки от AI
- `selections.yaml` — финальная расстановка (утверждает пользователь)
- `processed/` — готовые к вёрстке файлы (crop + resize)
- `photo-board.html` — UI для drag-drop расстановки
- `photo-preview.html` — предпросмотр «фото в макете»
- `STATE.yaml` — статусы внутренних этапов
- Обновлённый `07b_COMPOSED/composed.html` — плейсхолдеры `[photo slot: ...]` заменены на `<img>` / `<picture>`

## Связанные концепты

- [[photo-curator]] — главный агент-оркестратор всего stage 07c
- [[photo-classifier]] — тегирует фотки через codex CLI (1 фото = 1 вызов)
- [[photo-matcher]] — ранжирует кандидатов на каждый слот, выдаёт top-3
- [[photo-preview-board]] — финальная нарезка и generative fallback для пустых слотов
- [[landing-go]] — рекомендуемый способ вызова через оркестратор
- [[landing-compose]] — предшествующий этап, создаёт composed.html с плейсхолдерами
- [[landing-wireframe]] — этап 07a, должен быть завершён до старта

## Источник

- `commands/landing-photos.md`