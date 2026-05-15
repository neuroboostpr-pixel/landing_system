---
type: agent
name: photo-preview-board
sources: ["agents/photo-preview-board.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-matcher", "selections-validator", "photo-stylist", "identity-safe"]
tags: ["photos", "preview", "identity-safe", "processing", "stage-07c"]
---

# Photo Preview Board — рендер превью обработанных фото

## Что делает

Берёт утверждённый пользователем файл `selections.yaml` и превращает каждый слот в реальное изображение: обрезает и масштабирует клиентские фото, генерирует изображения через codex или создаёт SVG-заглушку. После обработки всех слотов рендерит HTML-страницу `photo-preview.html` для финального просмотра перед сборкой.

## Когда вызывать / в каком этапе

Вызывается на этапе **07c** агентом-оркестратором `photo-curator` — автоматически после того, как пользователь одобрил `selections.yaml` в интерактивной фото-доске (`photo-board.html`). Вручную не вызывается напрямую — только через `/landing-photos`.

## Что на вход / на выход

**Вход:**
- Директория проекта с готовым `07c_PHOTOS/selections.yaml` (каноничный, утверждённый пользователем)
- Обработанные фото в `07c_PHOTOS/intake/`

**Выход:**
- `07c_PHOTOS/processed/<slot_id>/desktop.jpg` — обрезанное фото под десктоп
- `07c_PHOTOS/processed/<slot_id>/mobile.jpg` — мобильный вариант (если блок задаёт `mobile_ratio`)
- `07c_PHOTOS/photo-preview.html` — финальная страница для просмотра и утверждения

**Три стратегии обработки слота:**
1. `bring-your-own` — обрезка/масштаб клиентского фото через `style.py`
2. `generate` — генерация через `codex-generate-fallback.sh` (с identity-safe проверкой)
3. `placeholder` — SVG-заглушка через `svg-placeholder.py`

## Identity-safe enforcement

Критическое правило: если слот относится к типу `testimonial`, `expert`, `team-member` или `avatar` (т.е. может изображать реального человека) и при этом `ai_approved_by_user: false` — стратегия `generate` **молча понижается** до `placeholder`. Агент никогда не генерирует лица без явного разрешения пользователя. Эта проверка закреплена в шаге 2 процесса и является точкой принудительного соблюдения политики идентичности.

## Связанные концепты

- [[photo-curator]] — оркестратор этапа 07c, вызывает этот агент после approve `selections.yaml`
- [[photo-matcher]] — предшественник: формирует `selections.draft.yaml`, из которого пользователь делает `selections.yaml`
- [[photo-stylist]] — предоставляет скрипт `style.py` для обрезки клиентских фото
- [[selections-validator]] — валидирует `selections.yaml` перед обработкой; при ошибке агент прерывается
- [[identity-safe]] — политика, запрещающая AI-репейнт людей без разрешения

## Источник

- `agents/photo-preview-board.md`