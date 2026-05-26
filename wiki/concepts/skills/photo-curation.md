---
type: skill
name: photo-curation
sources: ["skills/photo-curation/SKILL.md"]
updated: 2026-05-26
triggers: ["обработать фотки клиента", "запустить фото-пайплайн", "подобрать фото под слоты", "сгенерировать фото-заглушки"]
stage: "07c"
uses: ["landing-photos", "landing-wireframe", "landing-compose", "landing-design", "photo-curator"]
tags: ["photos", "codex", "ai-classify", "stage-07c", "pr-b"]
---

# Photo Curation — конвейер клиентских фотографий

## Что делает

Принимает папку с клиентскими фотографиями, классифицирует их через AI, автоматически подбирает каждое фото к нужному слоту в макете лендинга, обрабатывает под параметры дизайна и генерирует заглушки там, где клиентских фото не хватает.

## Когда вызывать / в каком этапе

Этап **07c**. Запускается командой `/landing-photos` после того, как утверждены:
- этап 05 (`design-system`) — нужны brand-токены для обработки,
- этап 07a (`wireframe`) — нужны `selections.yaml` с описанием photo-слотов.

Фотки клиента должны лежать в `07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс работы и т.д.).

## Что на вход / на выход

**Вход:**
- Клиентские фото в `07c_PHOTOS/inbox/<категория>/`
- `prototype.yaml` — описание слотов
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `05_design-system/tokens.json` — brand-цвета и параметры

**Выход:**
- `07c_PHOTOS/photo-board.html` — интерактивная доска для ручной правки назначений (drag-drop)
- `07c_PHOTOS/selections.yaml` — финальные назначения фото по слотам (после approve)
- `07c_PHOTOS/photo-preview.html` — превью как фото лягут в макет
- Обновлённый `07b_COMPOSED/composed.html` — placeholders заменены на реальные `<img>`/`<picture>`
- `07c_PHOTOS/manifest.json` + кэш в `07c_PHOTOS/.cache/`

**Промежуточный шаг пользователя:** открыть `photo-board.html`, расставить фото drag-drop, нажать «Подтвердить и скачать selections.yaml», положить файл обратно в `07c_PHOTOS/`.

## Связанные концепты

- [[landing-photos]] — slash-команда, запускающая этот скилл
- [[photo-curator]] — агент-владелец пайплайна
- [[landing-wireframe]] — поставляет `selections.yaml` со слотами для matching
- [[landing-design]] — поставляет `tokens.json` для обработки фото под бренд
- [[landing-compose]] — `inject-content.py` читает `07c_PHOTOS/selections.yaml` и перерендеривает `composed.html`

## Источник

- `skills/photo-curation/SKILL.md`