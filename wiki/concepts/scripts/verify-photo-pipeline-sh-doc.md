---
type: rule
name: verify-photo-pipeline
sources: ["scripts/verify-photo-pipeline.sh", "scripts/verify_photo_pipeline.py"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-preview-board", "block-composer", "stage-gates"]
tags: ["photo", "gate", "qa", "07c", "hard-check"]
---

# verify-photo-pipeline — проверка фото-пайплайна (HARD GATE)

## Что делает
Проверяет, что все фотографии в `composed.html` корректно обработаны и вставлены из `07c_PHOTOS/processed/` — нет оставшихся placeholder-ов, нет обрезанного hero-изображения. Возвращает exit 0 (всё ок), exit 1 (найдены проблемы) или exit 2 (файлы не найдены).

## Когда вызывать / в каком этапе
Запускается как HARD GATE на этапе **07c (photos)** — после того как `photo-curator` и `photo-preview-board` завершили работу и `composed.html` обновлён с реальными фото. Вызывается через `gate-check.sh` или вручную:
```bash
bash scripts/verify-photo-pipeline.sh <путь/к/проекту>
```

## Что на вход / на выход

**Вход:**
- Путь к проекту (аргумент командной строки)
- `<project>/07b_COMPOSED/composed.html` — итоговый HTML с фотографиями
- `<project>/07c_PHOTOS/processed/manifest.json` — манифест обработанных фото
- `block-library/<category>/<block-id>/meta.yaml` — метаданные слотов (ratio для hero)

**Выход:**
- `stdout`: `✅ Photo pipeline OK` — при успехе
- `stderr`: список найденных проблем (до 10 штук) — при ошибке
- Exit code: `0` / `1` / `2`

**Что именно проверяется:**
1. Все `<img src>` в `composed.html` ведут в `processed/` (не внешние, не placeholder)
2. Нет SVG placeholder-ов
3. Существует `manifest.json`
4. **PR-K HARD GATE:** ratio hero-фото (data-slot="hero-bg" или class="lp-hero") совпадает с ratio слота из `meta.yaml` с точностью 5% — hero не должен обрезаться

## Связанные концепты
- [[photo-curator]] — orchestrator этапа 07c, запускает пайплайн обработки фото
- [[photo-preview-board]] — финально вставляет фото в `composed.html`, после чего запускается гейт
- [[block-composer]] — собирает `composed.html`, где живут img-слоты
- [[stage-gates]] — механизм HARD/SOFT проверок между этапами; этот скрипт является одной из hard-check функций этапа 07c

## Источник
- `scripts/verify-photo-pipeline.sh`
- `scripts/verify_photo_pipeline.py`