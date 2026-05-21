---
type: agent
name: photo-classifier
sources: ["agents/photo-classifier.md"]
updated: 2026-05-20
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "visual-curator"]
tags: ["photos", "ai", "codex", "catalog", "identity-safe"]
---

# photo-classifier — AI-классификатор фотографий

## Что делает

Берёт одну фотографию из папки входящих и через codex CLI определяет теги, подпись, кадрирование, пригодные соотношения сторон и совместимость с брендом. Результат записывается в `catalog.yaml` — никакие пиксели оригинала не меняются.

## Когда вызывать / в каком этапе

Вспомогательный агент этапа **07c (Photos)**. Вызывается **только** родительским агентом [[photo-curator]] — не напрямую пользователем. Запускается для каждой фотографии со статусом `tag_source: pending_ai_classify` в `07c_PHOTOS/intake/`.

## Что на вход / на выход

**Вход:**
- Абсолютный путь к папке проекта (`<project_dir>`)
- Абсолютный путь к одной фотографии (`<photo_path>`)

**Выход:**
- Новая или обновлённая запись в `<project>/07c_PHOTOS/catalog.yaml` с полями: `tags`, `caption`, `composition`, `usable_ratios`, `brand_compatible`, `notes`, `tag_source: ai_classify`
- Полный лог промпта и ответа в `07c_PHOTOS/.logs/`

**Процесс внутри:**
1. Рендерит промпт из `templates/classify-prompt.md` с контекстом проекта (`tokens.json`, анализ ниши).
2. Вызывает `codex exec --image <photo_path>` через `call-codex.sh`.
3. Парсит YAML-ответ; при невалидном YAML — два retry со строгим промптом, затем помечает фото `unclassified` и записывает предупреждение в `STATE.yaml`.
4. Дописывает/обновляет запись в `catalog.yaml`.

**Identity-safe:** агент работает строго read-only на фото — читает пиксели, но никогда не перезаписывает и не изменяет изображение. Правило закреплено в `IDENTITY_SAFE.md`.

## Связанные концепты

- [[photo-curator]] — родительский агент, диспатчит photo-classifier для каждого фото
- [[photo-matcher]] — использует `catalog.yaml`, созданный этим агентом, для подбора фото к слотам
- [[photo-curation]] — скилл-оболочка, содержит скрипты `codex-classify.sh` и `call-codex.sh`
- [[07c-photos]] — этап pipeline, которому принадлежит классификация

## Источник

- `agents/photo-classifier.md`