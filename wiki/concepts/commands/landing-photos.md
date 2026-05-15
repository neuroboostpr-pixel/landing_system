---
type: command
name: landing-photos
sources: ["commands/landing-photos.md"]
updated: 2026-05-15
triggers:
  - "обработай фотки клиента"
  - "запусти фото-конвейер"
  - "расставь фото по слотам"
  - "сгенерируй fallback для фото"
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
tags: ["photos", "stage-07c", "pr-b", "visual", "command"]
---

# /landing-photos — Конвейер клиентских фотографий

## Что делает

Запускает полный pipeline обработки клиентских фотографий: AI-классификация снимков, подбор лучших кандидатов под каждый слот лендинга, ручная галерея для расстановки и генеративный fallback если фоток нет. После выполнения перерендерит `composed.html` с реальными фото вместо плейсхолдеров.

## Когда вызывать / в каком этапе

**Stage 07c** — после того как утверждены:
- этап `05_ДИЗАЙН-СИСТЕМА` (статус `approved` в `.landing-state.yaml`) — нужен `tokens.json` для стиля промптов
- `07a_WIREFRAME/selections.yaml` с выбранными вариантами блоков — нужно знать какие photo-слоты будут в лендинге

Запускается **вручную** командой `/landing-photos`. В автоматический оркестратор (`landing-orchestrator`) не встроен — это задача PR-D.

**Флаги:**
- `--project <slug>` — указать папку проекта явно
- `--force-stage <intake|classify|match|preview>` — сбросить конкретный шаг при повторном прогоне
- `--all-ai` — пропустить inbox, генерировать все фото через codex (требует подтверждения)

## Что на вход / на выход

**Вход:**
- Фотки клиента в `07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс работы и т.д.)
- Или архивные фото из `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (для старых проектов)
- `07a_WIREFRAME/selections.yaml` — список photo-слотов
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета и стиль бренда

**Выход (в `07c_PHOTOS/`):**
- `intake/` — обработанные JPEG + миниатюры (HEIC→JPEG, EXIF strip, dedupe)
- `catalog.yaml` — каталог с AI-тегами
- `selections.draft.yaml` — AI-черновик расстановки
- `selections.yaml` — финальная расстановка (утверждается пользователем)
- `processed/` — финальные кадрированные фото под слоты
- `photo-board.html` — UI для drag-drop расстановки
- `photo-preview.html` — превью «фото в макете»
- `STATE.yaml` — статусы этапов
- Обновлённый `07b_COMPOSED/composed.html` с реальными `<img>`/`<picture>`

## Связанные концепты

- [[photo-curator]] — оркестратор всего pipeline, диспатчит под-агентов
- [[photo-classifier]] — тегирует фотки через codex (один снимок за вызов)
- [[photo-matcher]] — ранжирует кандидатов по каждому слоту, формирует `selections.draft.yaml`
- [[photo-preview-board]] — кадрирует фото под слоты и генерирует fallback через codex image_gen
- [[block-composition]] — предыдущий этап 07b, создаёт `composed.html` с плейсхолдерами
- [[landing-visuals]] — параллельный этап 07d для иконок и инфографики

## Источник

- `commands/landing-photos.md`