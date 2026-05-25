---
type: agent
name: photo-curator
sources: ["agents/photo-curator.md"]
updated: 2026-05-25
triggers: []
stage: "07c"
uses: ["photo-classifier", "photo-matcher", "photo-preview-board", "landing-photos", "landing-orchestrator"]
tags: ["photos", "pipeline", "stage-07c", "pr-b"]
---

# photo-curator — оркестратор фото-пайплайна (Stage 07c)

## Что делает

Управляет полным циклом обработки клиентских фотографий: принимает фотки из папки `inbox/`, классифицирует их через AI, подбирает фото к слотам макета, показывает интерактивную галерею для ручной расстановки, обрабатывает финальные фото через codex и встраивает их в `composed.html`. Все лица и объекты клиента остаются нетронутыми — AI только улучшает обрамление и пропорции.

## Когда вызывать / в каком этапе

Активируется командой `/landing-photos` как часть stage **07c**. Требует, чтобы:
- этап **05_design** имел статус `approved` (дизайн-система утверждена),
- этап **07a_wireframe** имел `approved` или существовал файл `selections.yaml` из wireframe.

Без этих условий агент завершается с сообщением об ошибке на русском языке. Запускается вручную — не через `landing-orchestrator` (интеграция в оркестратор запланирована на PR-D).

## Что на вход / на выход

**Вход:**
- Клиентские фотографии в `07c_PHOTOS/inbox/` (7 подпапок по типу контента)
- `07_ПРОТОТИП/prototype.yaml` — список слотов для фото
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `tokens.json` и `market-profile.md` — бренд-параметры для codex-обработки

**Выход:**
- `07c_PHOTOS/catalog.yaml` — каталог всех фото с тегами
- `07c_PHOTOS/photo-board.html` — интерактивная галерея для ручной расстановки
- `07c_PHOTOS/selections.yaml` — финальный маппинг слотов (подтверждается пользователем)
- `07c_PHOTOS/photo-preview.html` — превью как фото лягут в макет
- `07c_PHOTOS/processed/<slot>.jpg` — обработанные через codex фото
- Обновлённый `07b_COMPOSED/composed.html` с реальными фотографиями вместо placeholders

## Ключевые правила

Каждое фото проходит обязательный codex post-process: валидация пропорций слота → codex enhancement (без перекраски объекта клиента) → resize → кэш по хэшу. **HARD GATE:** ни один SVG-placeholder не должен оставаться в финальном composed.html — `verify-photo-pipeline.sh` заблокирует закрытие этапа, если найдёт сырые или незаменённые фото.

Агент идемпотентен: при перезапуске читает `07c_PHOTOS/STATE.yaml` и продолжает с первого незавершённого шага.

## Связанные концепты

- [[photo-classifier]] — AI-классификация фото через codex CLI (батчи по 5)
- [[photo-matcher]] — подбор фото к слотам на основе каталога и prototype.yaml
- [[photo-preview-board]] — генерация photo-preview.html и финальная обработка
- [[landing-photos]] — slash-команда, запускающая этого агента
- [[landing-orchestrator]] — главный оркестратор pipeline (интеграция планируется)
- [[landing-compose]] — stage 07b, compose-blocks.py перерендеривает composed.html после approve

## Источник

- `agents/photo-curator.md`