---
type: agent
name: photo-classifier
sources: ["agents/photo-classifier.md"]
updated: 2026-05-26
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation"]
tags: ["photos", "ai", "codex", "classification", "stage-07c"]
---

# Photo Classifier — AI-классификатор фотографий

## Что делает
Автоматически анализирует одну фотографию через codex CLI и записывает метаданные (теги, подпись, композицию, совместимость с брендом) в каталог проекта. Сам файл фотографии никогда не изменяется.

## Когда вызывать / в каком этапе
Вызывается **только родительским агентом** [`photo-curator`](photo-curator) на этапе **07c** (Photo Pipeline). Прямой вызов не предусмотрен — агент является вспомогательным (helper). Обрабатывает фотографии со статусом `tag_source: pending_ai_classify` из папки `07c_PHOTOS/intake/`.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — абсолютный путь к папке проекта
- `<photo_path>` — путь к одной конкретной фотографии для классификации

**Выход:**
- Запись в `<project>/07c_PHOTOS/catalog.yaml` со статусом `tag_source: ai_classify`
- Поля записи: `tags`, `caption`, `composition`, `usable_ratios`, `brand_compatible`, `notes`
- Логи запроса и ответа в `07c_PHOTOS/.logs/`

**Процесс под капотом:**
1. Рендеринг промпта из шаблона `templates/classify-prompt.md` с контекстом проекта (tokens.json, ниша)
2. Вызов `codex exec --image <photo_path>` через `call-codex.sh`
3. Парсинг YAML-ответа; при ошибке — 2 повтора со строгим промптом, иначе `tags: [unclassified]`
4. Запись/обновление записи в `catalog.yaml`

## Identity-safe правило
Агент работает **только на чтение** файлов фотографий. Никаких изменений в байты изображения не вносится. Это требование зафиксировано в [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md) и не может быть нарушено ни при каких условиях.

## Обработка ошибок
- Невалидный YAML от codex → 2 повтора с более строгим промптом → пометка `unclassified` + предупреждение в `STATE.yaml`
- Тихий сбой codex → обрабатывается скриптом `call-codex.sh` (retry + exit code)

## Связанные концепты
- [[photo-curator]] — родительский агент, который диспатчит photo-classifier для каждой фотографии
- [[photo-curation]] — скилл, содержащий скрипты (`codex-classify.sh`, `call-codex.sh`) и шаблоны промптов

## Источник
- `agents/photo-classifier.md`