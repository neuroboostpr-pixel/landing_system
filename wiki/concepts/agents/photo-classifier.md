---
slug: photo-classifier
type: agent
name: "Классификатор фото"
stage: "07c"
tags: [photo, classifier, codex, ai, metadata, identity-safe]
triggers: []
inputs: [07c_PHOTOS/intake]
outputs: [07c_PHOTOS/catalog.yaml]
gates: []
pre_reqs: [photo-curator]
related: [photo-curator]
sources: ["agents/photo-classifier.md"]
updated: 2026-05-26
confidence: {pre_reqs: low}
---

# Классификатор фото

## Что делает

Вспомогательный агент, который запускается родительским агентом `photo-curator`. Для каждого фото из папки `07c_PHOTOS/intake/` со статусом `tag_source: pending_ai_classify` вызывает codex CLI с передачей изображения. Получает в ответ структурированные метаданные: теги, подпись, состав кадра, подходящие соотношения сторон, совместимость с брендом и примечания. Результат записывается в `catalog.yaml` — существующая запись обновляется по `id`, новая — добавляется.

## Когда вызывается

Агент не вызывается напрямую. Его диспатчит `photo-curator` на этапе 07c, когда в каталоге есть фото с незаполненной AI-классификацией (`tag_source: pending_ai_classify`). Stage Execution Protocol контролирует родитель.

## Вход → выход

**Вход:** абсолютный путь к папке проекта (`<project_dir>`) и путь к одному фото (`<photo_path>`); `tokens.json` и анализ ниши нужны для рендера промпта.

**Выход:** запись в `<project>/07c_PHOTOS/catalog.yaml` с полями `tags`, `caption`, `composition`, `usable_ratios`, `brand_compatible`, `notes`, `tag_source: ai_classify`; полный лог промпта и ответа в `07c_PHOTOS/.logs/`.

## Failure modes

- **Невалидный YAML от codex** — агент делает два повтора с более строгим промптом; если всё равно ошибка, фото помечается `tags: [unclassified]`, в `STATE.yaml` записывается предупреждение.
- **Тихий сбой codex** — обрабатывается враппером `call-codex.sh` (retry + exit code).
- **Отсутствие `tokens.json` или анализа ниши** — промпт рендерится неполным, качество тегов снижается без явной ошибки.
- **Прямой вызов агента** — не поддерживается: агент не владеет этапом и не знает состояния пайплайна.
- **Изменение байт фото** — принципиально заблокировано правилом identity-safe; агент работает только на чтение.

## Related

- [[photo-curator]] — родительский агент, диспатчит классификатор и агрегирует результаты в `catalog.yaml`