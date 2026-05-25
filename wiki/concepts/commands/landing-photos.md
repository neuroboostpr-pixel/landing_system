---
type: command
name: landing-photos
sources: ["commands/landing-photos.md"]
updated: 2026-05-25
triggers:
  - "обработать фотки клиента"
  - "запустить фото-пайплайн"
  - "расставить фото по слотам"
  - "сгенерировать фото для лендинга"
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
  - media
---

# /landing-photos — Фото-пайплайн (Stage 07c)

## Что делает

Принимает клиентские фотографии, автоматически классифицирует их через AI, подбирает нужное фото под каждый слот лендинга и подготавливает финальный `composed.html` с реальными изображениями вместо плейсхолдеров. Если фоток нет — генерирует fallback через codex.

## Когда вызывать / в каком этапе

Stage **07c** — запускается после того как утверждены:
- этап **05** (design-system, `tokens.json` существует),
- этап **07a** (wireframe, `selections.yaml` от пользователя готов).

Вызывается вручную командой `/landing-photos` или автоматически через `/landing-go`. При пустой папке `inbox/` агент спросит: положить фотки вручную или использовать флаг `--all-ai`.

**Флаги:**
- `--project <slug>` — указать папку проекта явно
- `--force-stage <intake|classify|match|preview>` — сбросить конкретный этап
- `--all-ai` — generative fallback на все слоты (требует подтверждения)
- `--interactive` — агент спрашивает по каждому слоту что подложить

## Что на вход / на выход

**Вход:**
- `07c_PHOTOS/inbox/` — 7 подпапок с фотками клиента (портреты, процесс, офис и т.д.)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` — совместимость со старыми проектами
- `07a_WIREFRAME/selections.yaml` — список photo-слотов из выбранных блоков
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета бренда для промптов codex

**Выход:**
- `07c_PHOTOS/catalog.yaml` — каталог фоток с тегами (авто)
- `07c_PHOTOS/selections.draft.yaml` — AI-черновик расстановки (авто)
- `07c_PHOTOS/selections.yaml` — финальная расстановка (подтверждается пользователем)
- `07c_PHOTOS/processed/` — обрезанные финальные фото
- `07c_PHOTOS/photo-board.html` — интерактивный drag-drop UI
- `07c_PHOTOS/photo-preview.html` — превью «фото в местах макета»
- `07b_COMPOSED/composed.html` — перерендерится с реальными `<img>` вместо плейсхолдеров

## Связанные концепты

- [[photo-curator]] — агент-оркестратор всего фото-пайплайна, вызывается командой
- [[photo-classifier]] — тегирует фотки из `_свалка/` через codex
- [[photo-matcher]] — ранжирует кандидатов по слотам
- [[landing-wireframe]] — формирует `selections.yaml` с перечнем photo-слотов
- [[landing-compose]] — создаёт `composed.html`, который перерендерится после фото
- [[landing-go]] — главный оркестратор, запускает этот этап автоматически

## Источник

- `commands/landing-photos.md`