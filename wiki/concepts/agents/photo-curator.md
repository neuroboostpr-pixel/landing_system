---
slug: photo-curator
type: agent
name: "Куратор фотографий — оркестратор этапа 07c"
stage: "07c"
tags: [photos, pipeline, orchestrator, pr-b, identity-safe, codex]
triggers: [landing-photos]
inputs:
  - .landing-state.yaml
  - 07c_PHOTOS/inbox/
  - 07_ПРОТОТИП/prototype.yaml
  - 07a_WIREFRAME/selections.yaml
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/
outputs:
  - 07c_PHOTOS/STATE.yaml
  - 07c_PHOTOS/catalog.yaml
  - 07c_PHOTOS/selections.draft.yaml
  - 07c_PHOTOS/photo-board.html
  - 07c_PHOTOS/photo-preview.html
  - 07b_COMPOSED/composed.html
gates:
  - photo-board-user-approve
  - photo-preview-user-approve
pre_reqs:
  - landing-design
  - landing-wireframe
related:
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - landing-photos
  - landing-compose
sources: ["agents/photo-curator.md"]
updated: 2026-05-26
confidence:
  stage: low
---

# Куратор фотографий — оркестратор этапа 07c

## Что делает

`photo-curator` управляет всем фото-пайплайном этапа 07c (PR-B): принимает клиентские фотографии из inbox, классифицирует их через `photo-classifier`, сопоставляет с wireframe-слотами через `photo-matcher`, генерирует интерактивную галерею `photo-board.html` для ручного расстановки, обрабатывает утверждённые фото через codex (resize + бренд-постобработка), рендерит `photo-preview.html` и — после финального approve — перегенерирует `composed.html`, заменяя все placeholder-слоты реальными изображениями.

## Когда вызывается

Запускается командой `/landing-photos`. Требует двух жёстких предусловий: этап `05_design` должен быть в статусе `approved`, а wireframe (`07a_wireframe`) — тоже утверждён (или присутствует `selections.yaml`). Если хотя бы одно условие не выполнено — агент останавливается с сообщением об ошибке на русском языке.

## Вход → выход

**Вход:** фотографии в `07c_PHOTOS/inbox/` (или `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`), `prototype.yaml` с описанием слотов, `selections.yaml` из wireframe-этапа, `tokens.json` с бренд-цветами, `market-profile.md` с нишей/регионом.

**Выход:** `catalog.yaml` с классифицированными фото, `photo-board.html` для пользовательского выбора, `selections.yaml` после approve, обработанные фото в `07c_PHOTOS/processed/`, `photo-preview.html` для финальной проверки, обновлённый `composed.html` без SVG-placeholder'ов.

## Чем закрывается этап (gates)

- **photo-board-user-approve** — пользователь расставил фото drag-drop в `photo-board.html`, скачал и положил `selections.yaml` в `07c_PHOTOS/`; `selections-validator.py` вернул exit 0.
- **photo-preview-user-approve** — пользователь открыл `photo-preview.html` и подтвердил, что фото корректно легли в макет; `scripts/verify-photo-pipeline.sh` возвращает exit 0 (нет сырых inbox-фото и SVG-placeholder'ов).

## Failure modes

- **Гейт-предшественник не закрыт** — `enforce_stage_gate.py` физически блокирует Write/Edit; агент не может обойти это, нужно закрыть 05_design или 07a_wireframe.
- **`selections-validator.py` падает** — несовпадение слот-идентификаторов или пустые обязательные слоты; агент возвращается к шагу 7 (повторный approve через photo-board.html).
- **Codex-постобработка зависает или меняет identity** — встроенная identity-проверка ловит репейнт объекта клиента (машина/лицо/товар); при срабатывании — слот остаётся без обработки и логируется в `STATE.yaml:errors`.
- **Фото не соответствует ratio слота** — `validate ratio` отклоняет фото до codex-вызова; ошибка фиксируется, пользователю нужно заменить изображение.
- **Перезапуск на полуслове** — `STATE.yaml` хранит статус каждого подэтапа; агент идемпотентен и продолжит с первого незавершённого шага. При сбое конкретного подэтапа — `--force-stage <name>`.

## Related

- [[photo-classifier]] — диспатчится батчами по 5 фото для AI-классификации через codex CLI
- [[photo-matcher]] — сопоставляет классифицированный каталог со слотами из wireframe
- [[photo-preview-board]] — финальная обработка + рендер photo-preview.html
- [[landing-photos]] — slash-команда, запускающая данного агента
- [[landing-compose]] — скилл compose-blocks.py, который перегенерирует composed.html на шаге 11