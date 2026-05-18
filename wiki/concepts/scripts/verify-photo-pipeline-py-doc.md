---
type: rule
name: verify-photo-pipeline
sources: ["scripts/verify_photo_pipeline.py"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-preview-board", "07c-photos", "block-composer"]
tags: ["photo", "hard-gate", "qa", "pr-k"]
---

# verify_photo_pipeline — Верификатор фото-пайплайна

## Что делает
Скрипт проверяет, что все клиентские фотографии корректно вшиты в `composed.html` после этапа 07c (Photo Pipeline). Обеспечивает HARD GATE PR-K: без exit 0 нельзя двигаться дальше.

## Когда вызывать / в каком этапе
Запускается автоматически как hard_check после команды `/landing-photos` (этап 07c) перед переходом к этапу 07d (visuals) или 08 (build). `landing-orchestrator` блокирует следующий этап, если скрипт вернул exit 1 или exit 2.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — финальный HTML с тегами `<img>`
- `07c_PHOTOS/processed/` — папка с обработанными фото
- `07c_PHOTOS/manifest.json` — манифест фото-пайплайна
- `block-library/.../meta.yaml` — метаданные слотов с ожидаемым соотношением сторон

**Проверки:**
1. Все `<img src>` в composed.html ведут на `07c_PHOTOS/processed/` (не на внешние URL и не на inbox)
2. В HTML нет SVG-placeholder'ов (признак незаменённых слотов)
3. Размеры файлов совпадают с атрибутами `width`/`height` в HTML
4. Файл `manifest.json` существует
5. **HARD GATE PR-K:** соотношение сторон `hero-bg` совпадает с ratio из `meta.yaml` в пределах ±5%

**Выход (exit codes):**
- `exit 0` — всё ОК, этап пройден
- `exit 1` — найдены проблемы (битые ссылки, SVG-заглушки, несоответствие размеров)
- `exit 2` — критические файлы отсутствуют (composed.html, manifest.json)

## Связанные концепты
- [[photo-curator]] — оркестратор этапа 07c, запускает этот скрипт как gate-check
- [[photo-preview-board]] — генерирует processed/ фото, которые проверяются скриптом
- [[block-composer]] — создаёт composed.html, в котором проверяются img-теги
- [[stage-gates]] — общий механизм HARD GATE между этапами
- [[07c-photos]] — этап pipeline, к которому относится верификатор

## Источник
- `scripts/verify_photo_pipeline.py`