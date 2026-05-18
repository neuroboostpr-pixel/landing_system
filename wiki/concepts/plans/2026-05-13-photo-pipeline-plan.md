---
type: stage
name: photo-pipeline-plan
sources: ["docs/superpowers/plans/2026-05-13-photo-pipeline-plan.md"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - photo-curation
  - landing-photos
  - block-composition
  - photo-styling
  - visual-generation
tags: [pr-b, photos, pipeline, stage-07c, codex, identity-safe]
---

# PR-B Photo Pipeline — план реализации (этап 07c)

## Что делает

Полный конвейер обработки клиентских фоток: от загрузки из папки `inbox/` до подстановки реальных фото в `composed.html`. Включает HEIC→JPEG-конвертацию, AI-классификацию через codex CLI, автоматический подбор фоток на слоты прототипа, HTML-галерею для ручной правки расстановки, обрезку под нужные пропорции и AI-генерацию заглушек для пустых слотов.

## Когда вызывать / в каком этапе

Этап 07c. Запускается командой `/landing-photos` после того, как утверждены:
- `stages.05_design.status == approved` (нужен `tokens.json` для бренд-контекста codex)
- `07a_WIREFRAME/selections.yaml` (нужно знать финальные photo-слоты)

## Что на вход / на выход

**Вход:**
- `07c_PHOTOS/inbox/<подпапка>/` — фотки клиента (JPEG/PNG/HEIC), разложенные по 7 тематическим подпапкам
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — бренд-цвета, визуальный стиль
- `07_ПРОТОТИП/prototype.yaml` + `07a_WIREFRAME/selections.yaml` — список photo-слотов

**Выход:**
- `07c_PHOTOS/intake/` — нормализованные JPEG + миниатюры 256px
- `07c_PHOTOS/catalog.yaml` — каталог фоток с тегами от AI
- `07c_PHOTOS/selections.draft.yaml` → `selections.yaml` — расстановка фоток по слотам (после approve пользователя)
- `07c_PHOTOS/photo-board.html` — split-view drag-drop UI для выбора расстановки
- `07c_PHOTOS/photo-preview.html` — превью «фото в макетных местах»
- `07c_PHOTOS/processed/<slot_id>/{desktop,mobile}.jpg` — финальные кадрированные фотки
- Обновлённый `07b_COMPOSED/composed.html` — placeholders заменены на реальные `<img>` / `<picture>`

## Ключевые компоненты (по задачам плана)

| Задача | Артефакт | Описание |
|--------|----------|----------|
| Task 0 | `research/codex-image-input.md` | Исследование механизма передачи изображений в codex CLI |
| Task 1 | `render-prompt.py` | Подстановка `[PLACEHOLDER]` в codex-промптах |
| Task 2 | `intake.py` | HEIC→JPEG, EXIF-strip, дедупликация по SHA-256, folder-tags |
| Task 3 | `SKILL.md`, 3 prompt-шаблона | Scaffold скилла + classify/match/generate-fallback промпты |
| Task 4 | `svg-placeholder.py` | SVG-заглушка под `.png` (порт open-design placeholder.ts) |
| Task 5 | `codex-classify.sh`, `codex-match.sh`, `codex-generate-fallback.sh` | Три обёртки codex CLI |
| Task 6 | `gallery-render.py` + `gallery-template.html` | `photo-board.html` с drag-drop |
| Task 7 | `preview-render.py` | `photo-preview.html` — финальный approve |
| Task 8 | `selections-validator.py` | Валидация schema + identity-safe гейт |
| Task 9 | `style.py --target-ratio` | Расширение обрезки под нужные пропорции слота |
| Task 10 | `inject-content.py` | Подстановка фото в `composed.html` |
| Task 11–12 | 4 agent docs + `/landing-photos` команда | Полный комплект агентов + slash-команда |
| Task 13 | `template/07c_PHOTOS/` | Структура inbox: 7 подпапок с русскими README |

## Identity-safe правило

Клиентские фотки **никогда** не перерисовываются AI. Для слотов с лицами (`testimonial-*`, `expert-*`, `team-*`) стратегия `generate` требует явного `ai_approved_by_user: true` через чекбокс в `photo-board.html`. Без галочки — слот получает SVG-плейсхолдер, не AI.

## Связанные концепты

- [[photo-curator]] — оркестратор этапа 07c, диспатчит все 4 суб-агента
- [[photo-classifier]] — классификация одной фотки через codex (только чтение, не изменяет фото)
- [[photo-matcher]] — ранжирование кандидатов по слотам
- [[photo-preview-board]] — обработка после approve: crop/resize + AI-fallback + SVG-плейсхолдеры
- [[photo-curation]] — скилл-скаффолд с prompt-шаблонами и IDENTITY_SAFE.md
- [[landing-photos]] — slash-команда `/landing-photos`, точка входа
- [[block-composition]] — `inject-content.py` расширяется для подстановки реальных фото
- [[photo-styling]] — `style.py` расширяется режимом `--target-ratio`
- [[07b-composed]] — предыдущий этап; его `composed.html` перерендерится с реальными фото

## Источник

- `docs/superpowers/plans/2026-05-13-photo-pipeline-plan.md`