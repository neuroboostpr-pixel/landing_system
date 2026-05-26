---
type: agent
name: photo-curator
sources: ["agents/photo-curator.md"]
updated: 2026-05-26
triggers: []
stage: "07c"
uses:
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - landing-photos
  - block-composition
tags: ["photos", "stage-07c", "pr-b", "identity-safe"]
---

# Photo Curator — оркестратор фото-пайплайна (этап 07c)

## Что делает

Управляет полным циклом обработки клиентских фотографий на этапе 07c: принимает фотки из папки `inbox/`, классифицирует их через AI, подбирает к слотам макета, генерирует интерактивный photo-board для согласования с пользователем, затем обрабатывает утверждённые фото через codex и перерендеривает `composed.html` с реальными изображениями вместо placeholders.

## Когда вызывать / в каком этапе

Запускается командой `/landing-photos` (этап **07c**). Требует два жёстких предусловия:
- этап `05_design` должен быть в статусе `approved` (дизайн-система утверждена);
- этап `07a_wireframe` должен быть `approved` (wireframe selections.yaml существует).

Если хотя бы одно условие не выполнено — агент останавливается с русским сообщением об ошибке.

## Что на вход / на выход

**Вход:**
- Клиентские фото в `<project>/07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс, объекты, интерьер и т.д.)
- Опционально: фото из `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (копируются в `inbox/_свалка/`)
- `07_ПРОТОТИП/prototype.yaml` — слоты макета
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `tokens.json`, `market-profile.md` — бренд и ниша для codex post-process

**Выход:**
- `07c_PHOTOS/catalog.yaml` — классифицированный каталог
- `07c_PHOTOS/selections.draft.yaml` → `selections.yaml` (утверждается пользователем)
- `07c_PHOTOS/photo-board.html` — интерактивная галерея для drag-drop расстановки
- `07c_PHOTOS/photo-preview.html` — превью фото в контексте макета
- `07c_PHOTOS/processed/<slot>.jpg` — обработанные codex'ом фото под каждый слот
- Обновлённый `07b_COMPOSED/composed.html` с реальными фото вместо SVG-placeholders
- `07c_PHOTOS/STATE.yaml` — статус каждого подэтапа (intake / classify / match / approval / process)

## Связанные концепты

- [[photo-classifier]] — субагент: классификация каждой фотографии через codex CLI `--image`
- [[photo-matcher]] — субагент: сопоставление слотов макета с фото из каталога
- [[photo-preview-board]] — субагент: обработка фото + рендер `photo-preview.html`
- [[landing-photos]] — slash-команда, которая запускает этого агента
- [[block-composition]] — скрипт `compose-blocks.py`, перерендеривающий `composed.html` после approve

## Источник

- `agents/photo-curator.md`