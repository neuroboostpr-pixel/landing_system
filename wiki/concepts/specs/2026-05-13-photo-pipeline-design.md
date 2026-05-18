---
type: stage
name: 07c-photos
sources: ["docs/superpowers/specs/2026-05-13-photo-pipeline-design.md"]
updated: 2026-05-18
triggers: ["/landing-photos"]
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - photo-curation
  - photo-styling
  - landing-photos
  - 07b-composed
  - 07a-wireframe
  - 05-dizayn-sistema
tags: ["photos", "pipeline", "identity-safe", "codex", "intake", "generative-fallback"]
---

# 07c — Photo Pipeline (PR-B)

## Что делает
Превращает папку сырых клиентских фотографий в обработанные изображения, расставленные по слотам лендинга. После этапа в `composed.html` вместо серых плейсхолдеров стоят реальные (или AI-сгенерированные) фото, подогнанные под нужные пропорции и цветовой стиль бренда.

## Когда вызывать / в каком этапе
Запускается командой `/landing-photos` **строго после** двух обязательных гейтов: утверждённой дизайн-системы (этап 05) и утверждённого wireframe с выбранными вариантами блоков (этап 07a). Без этих гейтов команда завершается с ошибкой и понятным сообщением на русском.

Место в пайплайне: `07a_WIREFRAME (approved)` → **`07c_PHOTOS`** → повторный рендер `07b_COMPOSED`.

## Что на вход / на выход

**Вход:**
- `07c_PHOTOS/inbox/` — клиентские фотографии (JPG, PNG, HEIC) в 7 тематических под-папках или в `_свалка/`
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков со слотами
- `tokens.json` + `DESIGN.md` — палитра и стиль бренда для параметризации AI-промптов
- `prototype.yaml` — описание photo-слотов с подсказками (hints) и соотношениями сторон

**Выход:**
- `catalog.yaml` — каталог всех фоток с тегами, соотношением сторон, числом лиц, совместимостью с брендом
- `selections.draft.yaml` — AI-рекомендации: топ-3 кандидата на каждый слот + флаг `ai_fallback_needed`
- `selections.yaml` — финальный выбор пользователя после approve в `photo-board.html`
- `processed/` — обрезанные JPG под нужные пропорции (desktop + mobile варианты)
- `photo-board.html` — drag-drop галерея для ручной корректировки раскладки
- `photo-preview.html` — «фото в макетных местах» для финального подтверждения
- `STATE.yaml` — статус каждого подэтапа (intake / classify / match / approval / process)
- Обновлённый `07b_COMPOSED/composed.html` — placeholders заменены тегами `<img>`

**Идемпотентность:** повторный запуск читает `STATE.yaml` и продолжает с прерванного подэтапа.

**Identity-safe:** клиентские фото никогда не изменяются AI. Генерация лиц для слотов testimonial/expert/team разблокируется только явной галочкой пользователя в `photo-board.html`; без галочки — SVG-placeholder.

## Связанные концепты
- [[photo-curator]] — главный оркестратор: запускает intake, координирует остальных агентов, рендерит HTML-галерею, управляет `STATE.yaml`
- [[photo-classifier]] — тегирует фотки через `codex exec` с image input, заполняет `catalog.yaml`
- [[photo-matcher]] — подбирает топ-3 кандидата на каждый слот, формирует `selections.draft.yaml`
- [[photo-preview-board]] — обрезает фото под пропорции слотов, запускает AI-fallback через `codex image_gen`, собирает `photo-preview.html`
- [[photo-curation]] — скилл: шаблоны промптов classify/match/generate, скрипты `intake.py`, `render-prompt.py`, `gallery-render.py`
- [[photo-styling]] — существующий скилл, расширяется флагом `--target-ratio` для обрезки под конкретный ratio
- [[landing-photos]] — slash-команда, точка входа в этап
- [[07b-composed]] — артефакт-получатель: перерендерится с реальными фото после approve `selections.yaml`
- [[07a-wireframe]] — обязательный гейт-предшественник; его `selections.yaml` определяет слоты
- [[05-dizayn-sistema]] — обязательный гейт-предшественник; `tokens.json` параметризует все AI-промпты

## Источник
- `docs/superpowers/specs/2026-05-13-photo-pipeline-design.md`