---
slug: 07c-photos
type: stage
name: "07c — Фото клиента и Photo Pipeline"
stage: "07c"
tags: [photo-pipeline, pr-b, client-assets, stage]
triggers: [landing-photos, landing-go]
inputs: [05-dizayn-sistema, 07-prototip, 02-materialy-klienta]
outputs: [catalog.yaml, selections.yaml, photo-board.html, photo-preview.html, processed/]
gates: [photo-board-approved]
pre_reqs: [05-dizayn-sistema, 07-prototip]
related: [landing-photos, photo-classifier, photo-curation, photo-curator, photo-matcher, photo-preview-board, photo-styling, photo-stylist]
sources: ["template/07c_PHOTOS/README.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# 07c — Фото клиента и Photo Pipeline

## Что делает

Этап принимает сырые фотографии клиента (любых форматов, включая HEIC с iPhone), автоматически классифицирует их по типам, сопоставляет со слотами прототипа и готовит финальную обрезку под нужные пропорции. Для незаполненных слотов генерирует фото под брендинг проекта. Результат — полный набор обработанных изображений, привязанных к конкретным местам в макете, с визуальным HTML-превью для проверки вёрстки до начала сборки темы.

## Когда вызывается

Запускается вручную командой `/landing-photos` после того, как утверждены этапы 05 (design-system) и 07a (wireframe). Также вызывается оркестратором через `/landing-go` в prototype-first workflow, параллельно с этапом 07e (visuals).

## Вход → выход

**Вход:** утверждённый design-system (`05-dizayn-sistema`), прототип со слотами (`07-prototip`), фотки клиента в подпапках `inbox/` (7 категорий: портреты, процесс, объекты, интерьер, до/после, документы, `_свалка/`).

**Выход:** `catalog.yaml` — каталог фоток с тегами; `selections.yaml` — раскладка фото по слотам (заполняется пользователем через `photo-board.html`); `processed/` — финальные JPEG с обрезкой; `photo-board.html` — drag-drop UI для утверждения; `photo-preview.html` — превью фото в позициях макета; `STATE.yaml` — статусы под-этапов pipeline.

## Чем закрывается этап (gates)

- **photo-board-approved** — пользователь сделал выбор в `photo-board.html`, скачал и положил `selections.yaml` обратно в `07c_PHOTOS/`. После этого `composed.html` перерендерится с реальными фото вместо placeholders.

## Failure modes

- Фотки в корне `inbox/` вместо подпапок — AI не может определить категорию без папки-подсказки; классификация через `_свалка/` работает медленнее и хуже.
- HEIC-конвертация падает если не установлен `imagemagick` или `pillow` — pipeline зависает на шаге `classify`.
- Пустые слоты без AI-генерации (если не выставлен флаг `ai_approved_by_user`) — `selections.yaml` будет неполным, `composed.html` останется с placeholders.
- Попытка ретуши лиц клиентов — система блокирует (identity-safe правило); генерация новых лиц для testimonial/team слотов требует явного разрешения пользователя.
- Перезапуск без `--force-stage` после частичного прогона — pipeline продолжит с последнего пройденного шага; если нужно с начала — передавать флаг явно.

## Related

- [[landing-photos]] — команда, запускающая весь этап
- [[photo-classifier]] — под-агент классификации фото по категориям
- [[photo-curator]] — под-агент подбора фото к слотам прототипа
- [[photo-matcher]] — сопоставление фото ↔ слот по метаданным и теге
- [[photo-preview-board]] — генерация `photo-board.html` и `photo-preview.html`
- [[photo-stylist]] — финальная обрезка и цветокоррекция под brand-kit
- [[05-dizayn-sistema]] — нужен для пропорций кадрирования и brand-токенов
- [[07-prototip]] — источник слотов для раскладки фото