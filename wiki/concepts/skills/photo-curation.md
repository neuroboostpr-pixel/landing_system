---
type: skill
name: photo-curation
sources: ["skills/photo-curation/SKILL.md"]
updated: 2026-05-15
triggers: ["/landing-photos", "обработка фоток", "фото для лендинга", "загрузить фотографии клиента"]
stage: "07c"
uses: ["photo-curator", "photo-classifier", "photo-matcher", "photo-preview-board", "block-composition", "prototype-import", "wireframe-rendering", "design-tokens-generation", "visual-generation"]
tags: ["photo", "pipeline", "codex", "identity-safe", "PR-B"]
---

# Photo Curation — конвейер клиентских фотографий

## Что делает

Превращает «сырую» папку фотографий клиента в готовые изображения для каждого слота лендинга: автоматически классифицирует снимки через AI, подбирает лучшие кандидаты для wireframe-слотов, обрезает под нужное соотношение сторон и вставляет результат в `composed.html`.

## Когда вызывать / в каком этапе

Этап **07c**. Запускается командой `/landing-photos` после того, как утверждены два предыдущих этапа: `05_design` (дизайн-система) и `07a_wireframe` (выбор блоков). Перезапуск продолжает с прерванного шага благодаря `STATE.yaml`.

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (подпапки: портреты, процесс, объекты и т.д.)
- `prototype.yaml` с описанием photo-слотов
- `07a_WIREFRAME/selections.yaml` с выбранными блоками
- `tokens.json` из дизайн-системы (цвета, пропорции)

**Выход:**
- `07c_PHOTOS/catalog.yaml` — каталог с тегами каждого фото
- `07c_PHOTOS/selections.draft.yaml` → `selections.yaml` — топ-3 кандидата на каждый слот
- `07c_PHOTOS/photo-board.html` — drag-drop галерея для пользователя
- `07c_PHOTOS/photo-preview.html` — предпросмотр финального расположения
- Обновлённый `07b_COMPOSED/composed.html` с реальными `<img>` вместо плейсхолдеров

## Ключевые правила

**Identity-safe:** клиентские фотографии никогда не перерисовываются AI. Генерация лиц (testimonial, team-слоты) требует явного флага `ai_approved_by_user: true` в `selections.yaml`.

**Codex pipeline (обязательно с 2026-05-15):** каждое фото проходит `codex-process-photo.sh` → `identity-check.py` (perceptual hash) → resize. Кэш в `07c_PHOTOS/.cache/<hash>.jpg` — повторный прогон не тратит API-вызовы.

**Семь шагов конвейера:** intake → classify → match → approve → process → preview → compose re-render. Если процесс прерван — `/landing-photos` продолжает с нужного шага. Принудительный сброс шага: `--force-stage <name>`.

## Связанные концепты

- [[photo-curator]] — агент-оркестратор этапа 07c, который запускает этот скилл
- [[photo-classifier]] — тегирует одно фото через codex CLI
- [[photo-matcher]] — подбирает топ-3 кандидата для каждого слота
- [[photo-preview-board]] — рендерит финальный preview и применяет изображения
- [[block-composition]] — этап 07b, чей `composed.html` обновляется на выходе
- [[wireframe-rendering]] — этап 07a, чьи selections.yaml используются как вход
- [[design-tokens-generation]] — поставляет `tokens.json` с пропорциями слотов
- [[visual-generation]] — параллельный этап 07d (иконки/инфографика)

## Источник

- `skills/photo-curation/SKILL.md`