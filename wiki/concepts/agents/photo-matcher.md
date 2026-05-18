---
type: agent
name: photo-matcher
sources: ["agents/photo-matcher.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-classifier", "photo-preview-board", "landing-photos"]
tags: ["photos", "pr-b", "codex", "identity-safe", "matching"]
---

# Photo Matcher — ранжирование фотографий по слотам

## Что делает
Один раз анализирует каталог клиентских фотографий и автоматически подбирает топ-3 кандидата для каждого фото-слота в wireframe. Если подходящих фото нет — выставляет флаг «нужна AI-генерация». Для слотов с людьми (отзывы, команда, эксперты) требует явного согласия пользователя.

## Когда вызывать / в каком этапе
Вызывается на этапе **07c** в рамках пайплайна `/landing-photos`. Запускается агентом `photo-curator` автоматически — после того как `photo-classifier` разметил все фото в `catalog.yaml`. Не вызывается напрямую пользователем.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `07c_PHOTOS/catalog.yaml` — каталог фото, размеченный `photo-classifier`
- `07_ПРОТОТИП/prototype.yaml` — список всех слотов
- `07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты блоков (фильтрует только активные `type: photo` слоты)

**Выход:**
- `07c_PHOTOS/selections.draft.yaml` — файл с топ-3 кандидатами на каждый слот, флагами `ai_fallback_needed` и `required_user_approval`

## Процесс работы

1. Строит временный `_slots-input.yaml` — только активные фото-слоты из выбранных вариантов wireframe.
2. Запускает `skills/photo-curation/scripts/codex-match.sh` через bash — codex читает `catalog.yaml` + список слотов и возвращает ранжированных кандидатов.
3. Проверяет, что результат — корректный YAML со структурой `slots: [...]`. При ошибке парсинга — два автоматических ретрая; если после них YAML невалиден — останавливается и просит пользователя проверить лог codex.

**Обработка пустых слотов:** если для слота нет ни одного кандидата — это штатная ситуация, выставляется `ai_fallback_needed: true`.

**Identity-safe правило:** слоты типа testimonial/expert/team получают `required_user_approval: true` — это требование прописано в промпте для codex и дополнительно валидируется скриптом `selections-validator.py` и UI `photo-board.html`.

## Связанные концепты
- [[photo-curator]] — оркестратор этапа 07c, который вызывает photo-matcher
- [[photo-classifier]] — создаёт `catalog.yaml` до запуска photo-matcher
- [[photo-preview-board]] — использует `selections.draft.yaml` для рендера превью
- [[landing-photos]] — команда, запускающая весь пайплайн 07c

## Источник
- `agents/photo-matcher.md`