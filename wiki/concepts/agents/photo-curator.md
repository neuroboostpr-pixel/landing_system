---
type: agent
name: photo-curator
sources: ["agents/photo-curator.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses: ["photo-classifier", "photo-matcher", "photo-preview-board", "landing-photos", "block-composition", "07c-photos", "07b-composed"]
tags: ["photos", "pipeline", "orchestrator", "identity-safe"]
---

# photo-curator — Оркестратор фото-pipeline (этап 07c)

## Что делает

Управляет полным процессом работы с клиентскими фотографиями от приёмки до готового макета: принимает фотки из папки `inbox/`, классифицирует через AI, автоматически подбирает кандидатов к слотам wireframe, показывает маркетологу галерею для ручного подтверждения и вставляет утверждённые фото в `composed.html`. С версии PR-I.a каждая фотка обязательно проходит codex post-processing под бренд (цвета, ниша, регион) — сырые фото в макет не попадают.

## Когда вызывать / в каком этапе

Этап **07c**. Вызывается командой `/landing-photos`.

Перед запуском обязательно должны быть утверждены два предыдущих этапа:
- `05_design.status == approved` — дизайн-система готова
- `07a_wireframe.status == approved` — варианты блоков выбраны, `selections.yaml` существует

При нарушении любого из условий агент завершает работу с русским сообщением об ошибке.

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс, объекты и т.д.)
- Дополнительно: `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (обратная совместимость)
- `07_ПРОТОТИП/prototype.yaml` + `07a_WIREFRAME/selections.yaml` — для определения слотов
- `tokens.json` + `market-profile.md` — параметры для codex обработки

**Выход:**
- `07c_PHOTOS/catalog.yaml` — классифицированный каталог фотографий
- `07c_PHOTOS/selections.draft.yaml` — топ-3 кандидата на каждый слот
- `07c_PHOTOS/photo-board.html` — интерактивная галерея для ручного подтверждения
- `07c_PHOTOS/selections.yaml` — финальный выбор пользователя
- `07c_PHOTOS/photo-preview.html` — предпросмотр фото в макете
- `07c_PHOTOS/processed/<slot>.jpg` — обработанные фото под размеры слота
- `07b_COMPOSED/composed.html` — перерендеренный макет с реальными фото вместо плейсхолдеров
- `07c_PHOTOS/STATE.yaml` — трекинг статуса всех стадий pipeline

## Связанные концепты

- [[photo-classifier]] — диспатчится батчами по 5 фото, классифицирует каждое через codex CLI
- [[photo-matcher]] — подбирает топ-3 кандидатов для каждого слота wireframe
- [[photo-preview-board]] — обрабатывает утверждённые фото и рендерит `photo-preview.html`
- [[landing-photos]] — команда-триггер, запускающая этого агента
- [[block-composition]] — скилл, перерендеривающий `composed.html` с реальными фото
- [[07c-photos]] — этап pipeline, которым управляет агент
- [[07b-composed]] — предшествующий этап; его `composed.html` обновляется на выходе

## Источник

- `agents/photo-curator.md`