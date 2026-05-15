---
type: skill
name: photo-curation
sources: ["skills/photo-curation/SKILL.md"]
updated: 2026-05-15
triggers: ["/landing-photos", "обработка фоток", "фото для лендинга", "расставить фотографии"]
stage: "07c"
uses: ["photo-curator", "prototype-import", "wireframe-rendering", "block-composition", "design-tokens-generation", "visual-generation"]
tags: ["photos", "PR-B", "codex", "identity-safe", "stage-07c"]
---

# photo-curation — Конвейер клиентских фотографий

## Что делает

Автоматически обрабатывает фотографии клиента: классифицирует их через AI, подбирает лучшие фото к каждому слоту макета, кадрирует и готовит финальный вариант для вставки в лендинг. Если фото не хватает — генерирует замену через codex.

## Когда вызывать / в каком этапе

Этап **07c**. Запускается командой `/landing-photos` вручную после того, как утверждены этап `05_design` (дизайн-система) и `07a_wireframe` (вайрфрейм). Фотографии клиента должны быть заранее загружены в `07c_PHOTOS/inbox/` по подпапкам.

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (подпапки по типу: портреты, процесс работы и т.д.)
- `prototype.yaml` с описанием photo-слотов
- `07a_WIREFRAME/selections.yaml` с выбранными блоками
- `tokens.json` (цвета и стиль для AI-fallback)

**Выход:**
- `07c_PHOTOS/catalog.yaml` — каталог всех фотографий с тегами
- `07c_PHOTOS/photo-board.html` — интерактивная доска для ручного одобрения выбора
- `07c_PHOTOS/selections.yaml` — утверждённое соответствие фото ↔ слот
- `07c_PHOTOS/photo-preview.html` — финальный превью перед вставкой
- `07c_PHOTOS/STATE.yaml` — состояние конвейера (для возобновления)
- Обновлённый `07b_COMPOSED/composed.html` — с реальными фото вместо плейсхолдеров

**Семь шагов конвейера:**
1. **intake** — копирует фото из inbox, конвертирует HEIC→JPEG, убирает EXIF, дедублирует
2. **classify** — codex тегирует фото из `_свалки/` (фото в подпапках получают folder-tag)
3. **match** — codex ранжирует кандидатов под каждый слот макета
4. **approve** — пользователь правит выбор через `photo-board.html`, скачивает `selections.yaml`
5. **process** — кадрирование под `slots[].ratio` и `mobile_ratio`; для пустых слотов — codex-fallback
6. **preview** — сборка `photo-preview.html` для финального одобрения
7. **compose re-render** — `inject-content.py` заменяет плейсхолдеры на `<img>`/`<picture>` в `composed.html`

Перезапуск `/landing-photos` продолжает с прерванного шага. Принудительный сброс: `/landing-photos --force-stage <name>`.

**Identity-safe правило:** клиентские фото никогда не перерисовываются AI. AI-генерация лиц (для testimonial/team слотов) требует явного `ai_approved_by_user: true` в `selections.yaml`.

## Связанные концепты

- [[photo-curator]] — агент-оркестратор, который запускает этот конвейер
- [[wireframe-rendering]] — предшествующий этап 07a, даёт список слотов
- [[block-composition]] — предшествующий этап 07b, создаёт composed.html
- [[design-tokens-generation]] — токены (цвета, стиль) используются для codex-fallback
- [[visual-generation]] — параллельный этап 07d для иконок и инфографики
- [[prototype-import]] — prototype.yaml используется как источник описания photo-слотов

## Источник

- `skills/photo-curation/SKILL.md`