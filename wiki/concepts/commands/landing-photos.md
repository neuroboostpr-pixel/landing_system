---
slug: landing-photos
type: command
name: "/landing-photos — Конвейер клиентских фото (stage 07c)"
stage: "07c"
tags: [photos, media, pipeline, client-assets, ai-classify]
triggers: [landing-photos, landing-go]
inputs:
  - 07c_PHOTOS/inbox/
  - 07a_WIREFRAME/selections.yaml
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - .landing-state.yaml
outputs:
  - 07c_PHOTOS/catalog.yaml
  - 07c_PHOTOS/selections.yaml
  - 07c_PHOTOS/processed/
  - 07c_PHOTOS/photo-board.html
  - 07c_PHOTOS/photo-preview.html
  - 07b_COMPOSED/composed.html
gates: []
pre_reqs:
  - design-tokens-generation
  - wireframe-rendering
related:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-preview-board
  - photo-curation
  - block-composer
  - visual-generation
  - prototype-import
sources: ["commands/landing-photos.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# /landing-photos — Конвейер клиентских фото (stage 07c)

## Что делает

Команда запускает полный конвейер обработки фотоматериалов клиента: конвертирует и дедуплицирует сырые фотки (HEIC→JPEG, EXIF-strip), классифицирует их через codex по содержимому, сопоставляет с фото-слотами прототипа и передаёт пользователю интерактивный drag-drop UI для финальной расстановки. После подтверждения расположения — обрезает фото под нужные соотношения сторон, генерирует fallback-изображения для пустых слотов и перерендерит `composed.html`, заменяя все `[photo slot: ...]` на реальные `<img>` / `<picture>`.

## Когда вызывается

Вызывается вручную командой `/landing-photos` или автоматически через `/landing-go` когда оркестратор доходит до этапа 07c. Обязательные условия: этап 05 (design-system) в статусе `approved` и наличие `07a_WIREFRAME/selections.yaml` с выбранными вариантами блоков — без этих данных команда останавливается с поясняющим сообщением.

## Вход → выход

**Вход:** папка `07c_PHOTOS/inbox/` с фотками клиента (поддерживается HEIC/JPEG/PNG), `07a_WIREFRAME/selections.yaml` со списком фото-слотов финального лендинга, `tokens.json` с цветами бренда (для промптов codex-генерации). При пустом inbox предлагает режим `--all-ai` — generative fallback для всех слотов.

**Выход:** `catalog.yaml` — каталог фоток с тегами классификации; `selections.yaml` — финальная расстановка (фото→слот); `processed/` — обрезанные под слоты фото, готовые для деплоя; `photo-board.html` и `photo-preview.html` — интерактивные UI; обновлённый `07b_COMPOSED/composed.html` с реальными изображениями.

## Failure modes

- **Отсутствует `selections.yaml` wireframe** — команда падает на гейте: нельзя знать какие photo-слоты будут в лендинге без выбранных вариантов блоков.
- **Пустой inbox без флага `--all-ai`** — агент ждёт фотки; забытый флаг приводит к тому, что все слоты остаются пустыми заглушками.
- **Codex недоступен (classify/fallback)** — классификация через `_свалка/` падает; нужна установка codex CLI (`bash scripts/install-codex.sh`).
- **HEIC без конвертера** — intake-этап требует `imagemagick` или `sips`; на Windows конвертация может не пройти.
- **Composed не перерендерился** — если `composed.html` заблокирован или изменён вручную после stage 07b, re-render может не применить фото-замены.

## Related

- [[photo-curator]] — агент-оркестратор всего photo-конвейера, вызывается этой командой
- [[photo-classifier]] — codex-классификация фоток из `_свалка/`
- [[photo-matcher]] — ранжирование кандидатов на каждый фото-слот
- [[photo-preview-board]] — рендер `photo-preview.html` и обрезка под слоты
- [[photo-curation]] — концепт полного процесса курирования фото
- [[block-composer]] — производит `composed.html`, который перерендерится с реальными фото
- [[visual-generation]] — параллельный этап 07d: иконки и инфографика через codex
- [[prototype-import]] — stage 07a, поставляет список photo-слотов через `selections.yaml`