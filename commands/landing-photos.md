---
description: Stage 07c (PR-B) — обработка клиентских фоток: AI-классификация, matching к слотам прототипа, generative fallback. Требует approved 05 design + 07a wireframe.
---

# /landing-photos

Запускает полный конвейер обработки клиентских фоток для лендинга. Это **stage 07c** между `07b_COMPOSED/` и финальным re-render для production.

## Использование

```
/landing-photos [--project <slug>] [--force-stage <name>] [--all-ai]
```

**Флаги:**
- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--force-stage <intake|classify|match|preview>` — принудительный сброс конкретного этапа (для повторного прогона если что-то пошло не так).
- `--all-ai` — пропустить inbox-сканирование, на все слоты использовать generative fallback. Требует подтверждения от пользователя.

## Гейты (что должно быть готово до запуска)

1. `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе:
   > Сначала утверди дизайн-систему (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`) — без `tokens.json` промпты codex не могут попасть в стиль.

2. `<project>/07a_WIREFRAME/selections.yaml` существует AND содержит выбранные варианты — иначе:
   > Сначала выбери варианты блоков в `wireframe.html` — нужно знать какие photo-слоты будут в финальном лендинге.

## Что происходит

Команда вызывает `photo-curator` агента, который оркестрирует весь процесс:

1. **Bootstrap** — `07c_PHOTOS/inbox/` с 7 подпапками (если их ещё нет).
2. **Dual-path intake** — сканирует ещё и `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (старые проекты).
3. **Intake** — HEIC→JPEG, EXIF strip, dedupe, folder-tag detection (`intake/`).
4. **Classify** — `photo-classifier` тегирует фотки из `_свалка/` через codex.
5. **Match** — `photo-matcher` ранжирует кандидатов на каждый слот.
6. **Gallery render** — пользователь открывает `photo-board.html`, расставляет фото.
7. **Process** — `photo-preview-board` обрезает под слоты + генерирует fallback.
8. **Preview** — пользователь смотрит `photo-preview.html` и approves.
9. **Compose re-render** — `composed.html` рендерится с реальными фото.

Если `inbox/` пустой (нет фоток клиента), агент уточнит: «Папка `07c_PHOTOS/inbox/` пустая — положи туда фотки клиента или запусти с `--all-ai` чтобы использовать generative fallback для всех слотов».

См. [`agents/photo-curator.md`](../agents/photo-curator.md) для деталей.

## Артефакты

В `<project>/07c_PHOTOS/`:
- `inbox/` (7 подпапок) — куда положить фотки клиента
- `intake/` — обработанные JPEG + миниатюры (auto)
- `catalog.yaml` — каталог фоток с тегами (auto)
- `selections.draft.yaml` — AI-черновик расстановки (auto)
- `selections.yaml` — финальная расстановка (от тебя через photo-board.html)
- `processed/` — финальные фото для сайта (auto)
- `photo-board.html` — UI для раскладывания
- `photo-preview.html` — preview «фото в местах»
- `STATE.yaml` — статусы этапов
- `.logs/` — логи всех AI-вызовов

## После выполнения

`07b_COMPOSED/composed.html` перерендерится — placeholders `[photo slot: ...]` заменятся на реальные `<img>` (или `<picture>` с mobile-вариантом, если у блока есть `mobile_ratio`).

## Запуск

Автоматически через `/landing-go` (рекомендуется) или вручную этой командой. Этап интегрирован в `landing-orchestrator` и `config/stage-gates.yaml`.

См. [spec](../docs/superpowers/specs/2026-05-13-photo-pipeline-design.md) и [plan](../docs/superpowers/plans/2026-05-13-photo-pipeline-plan.md).

## Интерактивный режим (PR-I.a)

```
/landing-photos --interactive
```

Агент по очереди спрашивает у пользователя что положить в каждый
photo-слот, показывает подсказку (что должно быть на фото в этом
контексте, какой ratio), потом пропускает фото через pipeline:
codex обработка + resize + identity check.

Альтернатива — drag-drop UI в `07c_PHOTOS/photo-board.html`
(остаётся из PR-B). Если предпочитаешь визуально расставить —
открой HTML, drag фото в слоты, скачай selections.yaml, положи
обратно в проект.
