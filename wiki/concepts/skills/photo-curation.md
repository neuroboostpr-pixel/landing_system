---
type: skill
name: photo-curation
sources: ["skills/photo-curation/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "07c"
uses:
  - landing-photos
  - landing-compose
  - landing-orchestrator
  - landing-prototype
  - landing-wireframe
tags: ["photos", "pipeline", "codex", "stage-07c", "pr-b"]
---

# Photo Curation — конвейер клиентских фото (этап 07c)

## Что делает

Обрабатывает клиентские фотографии: классифицирует их через AI, подбирает под слоты макета, нарезает в нужные пропорции и подставляет в `composed.html` вместо визуальных заглушек. Для слотов без подходящих фото генерирует AI-замену.

## Когда вызывать / в каком этапе

Запускается командой `/landing-photos` вручную на этапе **07c**. Обязательные предусловия:

- этап **05** (design-system) — утверждён,
- этап **07a** (wireframe) — утверждён и скачан `selections.yaml`.

Клиентские фотки кладутся в `07c_PHOTOS/inbox/` (7 подпапок по типу) до запуска команды.

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (JPEG/HEIC/PNG, по подпапкам).
- `prototype.yaml` — список photo-слотов с описаниями и пропорциями.
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков.
- `05_ДИЗАЙН/tokens.json` — brand-цвета и параметры стиля.

**Выход:**
- `07c_PHOTOS/photo-board.html` — интерактивная доска для ручного подбора фото (drag-drop).
- `07c_PHOTOS/selections.yaml` — финальный маппинг фото по слотам (после approve пользователем).
- `07c_PHOTOS/photo-preview.html` — превью как фото лягут в макет.
- Обновлённый `07b_COMPOSED/composed.html` — заглушки `[SLOT: ...]` заменены на `<img>`/`<picture>` с mobile-вариантом.
- `07c_PHOTOS/.cache/` — кэш обработанных через codex фото (по hash параметров).

## Ключевые правила

**Identity-safe:** клиентские фото **никогда** не репеинтятся AI. Генерация лиц (testimonial / expert / team слоты) требует явного флага `ai_approved_by_user: true` в конфиге слота.

**Перезапуск:** `07c_PHOTOS/STATE.yaml` фиксирует прогресс. Повторный `/landing-photos` продолжает с прерванного этапа. Сброс: `--force-stage <name>`.

**Кэш codex:** повторный прогон с теми же параметрами (hint + style + brand_color + niche) не вызывает codex API.

## Связанные концепты

- [[landing-photos]] — slash-команда, запускающая этот конвейер
- [[landing-wireframe]] — поставляет `selections.yaml` со слотами для matching
- [[landing-compose]] — PR-A; `inject-content.py` из compose-скилла выполняет финальный re-render `composed.html`
- [[landing-prototype]] — поставляет `prototype.yaml` с описаниями photo-слотов
- [[landing-orchestrator]] — в PR-D интегрирует 07c как автоматический этап pipeline
- [[landing-visuals]] — параллельный этап 07d (иконки и инфографика), запускается одновременно с 07c

## Источник

- `skills/photo-curation/SKILL.md`