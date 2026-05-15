---
type: agent
name: photo-classifier
sources: ["agents/photo-classifier.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "visual-curator"]
tags: ["photos", "ai", "codex", "catalog", "classification"]
---

# Photo Classifier — ИИ-тегирование фотографий

## Что делает

Анализирует одну фотографию через codex CLI и создаёт структурированные метаданные: теги, подпись, кадрирование, совместимость с брендом. Сами фотографии не изменяются — агент работает только на чтение.

## Когда вызывать / в каком этапе

Вызывается автоматически агентом [[photo-curator]] на этапе **07c** (Photo Pipeline). Обрабатывает все фото в `07c_PHOTOS/intake/`, у которых в `catalog.yaml` стоит статус `tag_source: pending_ai_classify`. Не вызывается напрямую пользователем — только как субагент в рамках `/landing-photos`.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — абсолютный путь к папке проекта
- `<photo_path>` — путь к одному фото для классификации
- Контекст проекта: `tokens.json`, `market-profile.md` (для составления промпта)

**Выход:**
- Запись в `07c_PHOTOS/catalog.yaml` с полями: `tags`, `caption`, `composition`, `usable_ratios`, `brand_compatible`, `notes`, статус `tag_source: ai_classify`
- Полный лог промпта и ответа codex → `07c_PHOTOS/.logs/`

**Процесс:**
1. Рендерит `templates/classify-prompt.md` с контекстом проекта.
2. Вызывает `codex exec --image <photo_path> "<prompt>"` через обёртку `call-codex.sh`.
3. Парсит YAML-ответ; при невалидном YAML — повторяет до 2 раз с более строгим промптом.
4. При полном провале — помечает фото как `unclassified`, записывает предупреждение в `STATE.yaml`.
5. Добавляет или обновляет запись в `catalog.yaml` по полю `id`.

**Ограничение безопасности:** согласно `IDENTITY_SAFE.md`, агент никогда не перезаписывает пиксели фотографий. Только метаданные.

## Связанные концепты

- [[photo-curator]] — оркестратор этапа 07c, вызывает photo-classifier для каждого фото из intake и агрегирует результаты в catalog.yaml
- [[photo-curation]] — навык-обёртка, содержит скрипты (`codex-classify.sh`, `call-codex.sh`) и шаблоны промптов
- [[landing-photos]] — slash-команда, запускающая весь пайплайн 07c включая этот агент

## Источник

- `agents/photo-classifier.md`