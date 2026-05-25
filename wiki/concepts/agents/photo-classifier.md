---
type: agent
name: photo-classifier
sources: ["agents/photo-classifier.md"]
updated: 2026-05-25
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "landing-photos"]
tags: ["photos", "ai", "codex", "catalog", "classification"]
---

# Photo Classifier — AI-классификатор одной фотографии

## Что делает
Анализирует одну клиентскую фотографию через codex CLI и добавляет метаданные в каталог проекта: теги, подпись, композицию, подходящие форматы кадрирования и совместимость с брендом. Сам файл фотографии не изменяется — агент работает исключительно в режиме чтения.

## Когда вызывать / в каком этапе
Это вспомогательный агент — вызывается **только** родительским агентом [[photo-curator]] на этапе **07c** (обработка фото). Не предназначен для прямого запуска пользователем. Обрабатывает фотографии, у которых в `catalog.yaml` стоит статус `tag_source: pending_ai_classify`.

## Что на вход / на выход

**Вход:**
- Абсолютный путь к папке проекта (`<project_dir>`)
- Путь к одной фотографии (`<photo_path>`) из `07c_PHOTOS/intake/`

**Выход:**
- Запись в `<project>/07c_PHOTOS/catalog.yaml` со статусом `tag_source: ai_classify`, содержащая поля: `tags`, `caption`, `composition`, `usable_ratios`, `brand_compatible`, `notes`
- Лог промпта и ответа codex в `07c_PHOTOS/.logs/`

**Процесс:**
1. Рендерит промпт из `templates/classify-prompt.md` с контекстом проекта (tokens.json, ниша)
2. Вызывает `codex exec --image <photo>` через обёртку `call-codex.sh`
3. Парсит YAML-ответ; при ошибке — два повтора со строгим промптом, иначе помечает как `unclassified`
4. Обновляет запись в `catalog.yaml`

**Правило identity-safe:** фото клиентов никогда не перезаписываются и не перерисовываются AI. Агент производит только метаданные.

## Связанные концепты
- [[photo-curator]] — родительский агент, который диспатчит photo-classifier для каждого фото
- [[landing-photos]] — slash-команда этапа 07c, запускающая всю photo pipeline
- [[photo-curation]] — скилл, содержащий скрипты (`codex-classify.sh`, `call-codex.sh`) и шаблоны промптов

## Источник
- `agents/photo-classifier.md`