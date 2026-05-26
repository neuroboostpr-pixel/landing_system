---
type: agent
name: photo-preview-board
sources: ["agents/photo-preview-board.md"]
updated: 2026-05-26
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "photo-styling", "selections-validator"]
tags: ["photos", "preview", "identity-safe", "stage-07c"]
---

# Photo Preview Board — обработка фото и рендер превью

## Что делает
Принимает утверждённый файл `selections.yaml`, обрабатывает каждый фото-слот (кроп, ресайз, AI-генерация или SVG-заглушка) и собирает `photo-preview.html` для финального утверждения маркетологом. Строго соблюдает правило identity-safe: не генерирует лица людей без явного разрешения клиента.

## Когда вызывать / в каком этапе
Этап **07c** (обработка фото). Вызывается **только как helper-агент** из `photo-curator` — не диспатчится напрямую. Запускается после того, как пользователь утвердил расстановку фото в drag-drop интерфейсе и положил `selections.yaml` в `07c_PHOTOS/`.

## Что на вход / на выход

**Вход:**
- `<project>/07c_PHOTOS/selections.yaml` — утверждённый пользователем файл с маппингом слотов на фото и стратегиями.
- Клиентские фото в `07c_PHOTOS/intake/`.

**Выход:**
- `<project>/07c_PHOTOS/processed/<slot_id>/desktop.jpg` — обработанная версия для десктопа.
- `<project>/07c_PHOTOS/processed/<slot_id>/mobile.jpg` — мобильная версия (если у блока задан `mobile_ratio`).
- `<project>/07c_PHOTOS/photo-preview.html` — финальный HTML-превью для проверки перед деплоем.

**Три стратегии обработки слота:**
| Стратегия | Что происходит |
|---|---|
| `bring-your-own` | Кроп и ресайз клиентского фото через `style.py` |
| `generate` | Генерация через codex-fallback (с identity-safe фильтром) |
| `placeholder` | SVG-заглушка с брендовым цветом и подсказкой |

**Identity-safe правило:** если слот типа `testimonial`, `expert`, `team-member` или `avatar` помечен стратегией `generate`, но `ai_approved_by_user == false` — стратегия **молча** понижается до `placeholder`. Лица людей никогда не генерируются без явного разрешения.

## Связанные концепты
- [[photo-curator]] — родительский агент, диспатчит photo-preview-board; владеет этапом 07c целиком
- [[photo-curation]] — скилл с `selections-validator.py`, `codex-generate-fallback.sh`, `svg-placeholder.py`, `preview-render.py`
- [[photo-styling]] — скилл с `style.py` для кропа и ресайза

## Источник
- `agents/photo-preview-board.md`