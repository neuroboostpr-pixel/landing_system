---
type: agent
name: photo-preview-board
sources: ["agents/photo-preview-board.md"]
updated: 2026-05-25
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "photo-styling", "identity-safe"]
tags: ["photos", "preview", "image-processing", "stage-07c"]
---

# Photo Preview Board — рендер превью фотографий

## Что делает
Обрабатывает каждый слот из утверждённого `selections.yaml`: кроппит/ресайзит клиентские фото, генерирует изображения через Codex или создаёт SVG-плейсхолдеры. Результат — файлы `desktop.jpg`/`mobile.jpg` и финальная страница `photo-preview.html` для проверки заказчиком.

## Когда вызывать / в каком этапе
Вызывается **только автоматически** агентом `photo-curator` после того, как пользователь подтвердил `selections.yaml`. Не предназначен для прямого вызова. Относится к этапу **07c (Photos)**.

## Что на вход / на выход

**Вход:**
- `<project>/07c_PHOTOS/selections.yaml` — канонический файл с выбором пользователя (должен пройти валидацию)

**Выход:**
- `<project>/07c_PHOTOS/processed/<slot_id>/desktop.jpg` — обработанное изображение для десктопа
- `<project>/07c_PHOTOS/processed/<slot_id>/mobile.jpg` — версия для мобильных (если блок задаёт `mobile_ratio`)
- `<project>/07c_PHOTOS/photo-preview.html` — интерактивный HTML-превью для финального одобрения

## Ключевые правила обработки

Каждый слот обрабатывается согласно стратегии из `selections.yaml`:

| Стратегия | Действие |
|---|---|
| `bring-your-own` | Кроп/ресайз через `photo-styling/scripts/style.py` с целевым ratio |
| `generate` | Генерация через Codex (`codex-generate-fallback.sh`), если прошла identity-safe проверка |
| `placeholder` | SVG-плейсхолдер через `svg-placeholder.py` с брендовым цветом |

**Identity-safe gate:** если слот типа `testimonial`, `expert`, `team-member` или `avatar` имеет стратегию `generate` при `ai_approved_by_user: false` — стратегия автоматически понижается до `placeholder` без уведомления. Это главная точка принудительного соблюдения политики безопасности идентичности.

## Связанные концепты
- [[photo-curator]] — родительский агент, который диспатчит этого хелпера
- [[photo-curation]] — скилл с валидатором `selections-validator.py` и Codex-скриптами
- [[photo-styling]] — скилл с `style.py` для ресайза/кропа
- [[identity-safe]] — политика запрета AI-генерации лиц без явного разрешения

## Источник
- `agents/photo-preview-board.md`