---
name: photo-curation
description: Stage 07c (PR-B) photo pipeline — intake, AI-classification via codex, AI-matching to wireframe slots, processing under design-system tokens, generative fallback. Owned by photo-curator agent.
---

# photo-curation

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill photo-curation --stage 07c
```

Конвейер обработки клиентских фоток для лендинга. Запускается командой `/landing-photos` после approved `05_design` + `07a_wireframe`.

## Этапы

1. **intake** — `scripts/intake.py` копирует фотки из `07c_PHOTOS/inbox/` подпапок в `07c_PHOTOS/intake/`. HEIC→JPEG, EXIF strip, dedupe, folder-tag.
2. **classify** — `scripts/codex-classify.sh` тегирует фотки из `_свалка/` через codex CLI (фото в подпапках уже имеют folder-tag).
3. **match** — `scripts/codex-match.sh` ранжирует кандидатов на каждый photo-слот из prototype.yaml + wireframe selections.
4. **approve** — пользователь открывает `photo-board.html` (рендерит `scripts/gallery-render.py`), правит выбор, скачивает `selections.yaml`.
5. **process** — `scripts/style.py` (расширенный) обрезает под `slots[].ratio` + `mobile_ratio`. Для AI-fallback слотов — `scripts/codex-generate-fallback.sh`.
6. **preview** — `scripts/preview-render.py` собирает `photo-preview.html` для финального approve.
7. **compose re-render** — `inject-content.py` (PR-A) читает `07c_PHOTOS/selections.yaml` и подставляет реальные фотки в `composed.html`.

## Pipeline через codex (PR-I.a, обязательно с 2026-05-15)

Каждое фото перед попаданием в composed.html проходит:
1. `codex-process-photo.sh` — codex image_gen с brand параметрами
2. `identity-check.py` — perceptual hash контроль (не репеинтнули ли объект)
3. Resize в точные размеры слота
4. Сохранение + manifest.json

Cache: `07c_PHOTOS/.cache/<hash>.jpg`. Повторный прогон с теми же параметрами не зовёт codex.

## Identity-safe

См. [`IDENTITY_SAFE.md`](IDENTITY_SAFE.md). Кратко: клиентские фото никогда не репеинтятся; AI-генерация лиц требует явного `ai_approved_by_user: true`.

## State management

`07c_PHOTOS/STATE.yaml` отслеживает каждый этап. Перезапуск `/landing-photos` продолжает с прерванного. Принудительный сброс: `/landing-photos --force-stage <name>`.

## Templates

Три codex шаблона в `templates/` — повторяют формат `paralaximus-codex/templates/atlas-prompt.md`:
- `classify-prompt.md` — одна фотка → YAML с тегами
- `match-prompt.md` — каталог + слоты → ранжированные кандидаты
- `generate-fallback.md` — генерация под brand-tokens

## Стандарт пайплайна картинок (D1, обязательный)

Каждое визуальное место обрабатывается по
[`docs/standards/image-pipeline.md`](../docs/standards/image-pipeline.md):
анализ места → цель → спецификация → референсы (число = составу композиции) →
генерация на вырезаемом фоне → rembg → вставка; адаптация под палитру —
полупрозрачным оверлеем акцента, не отдельной картинкой на каждый цвет.
