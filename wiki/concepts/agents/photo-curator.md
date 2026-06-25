---
slug: photo-curator
type: agent
name: "Photo Curator"
stage: "07c"
tags: [photo, pipeline, orchestrator, pr-b, stage-07c]
triggers: [landing-photos]
inputs: [07c-photos, 02-materialy-klienta, 05-dizayn-sistema, 07b-composed]
outputs: [07c-photos]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [photo-classifier, photo-matcher, photo-preview-board, photo-curation, landing-photos, landing-compose]
sources: ["agents/photo-curator.md"]
updated: 2026-06-19
---

# Photo Curator

## Что делает

Оркестрирует весь фото-пайплайн на этапе 07c (PR-B): принимает клиентские фотографии из `07c_PHOTOS/inbox/` (или из `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/`), классифицирует их через sub-агент `photo-classifier`, сопоставляет со слотами прототипа через `photo-matcher`, рендерит интерактивную галерею `photo-board.html` для ручного расставления, валидирует выбор, запускает codex post-process для каждой фотки (identity-safe), и финально перерендерит `composed.html` с реальными фото вместо SVG-плейсхолдеров. Идемпотентен: при рестарте читает `STATE.yaml` и продолжает с незавершённого шага.

## Когда вызывается

Запускается вручную командой `/landing-photos` внутри папки проекта. До запуска обязательно: этап 05 (дизайн-система) в статусе `approved` и существующий `07b_COMPOSED/composed.html`. Если хотя бы одно условие не выполнено — агент завершается с русским сообщением об ошибке.

## Вход → выход

**Вход:** клиентские фото в `07c_PHOTOS/inbox/` (7 подпапок по типу контента), `07_ПРОТОТИП/prototype.yaml` (список слотов), `tokens.json` и `market-profile.md` (для codex post-process параметров), `07b_COMPOSED/composed.html`.

**Выход:** `07c_PHOTOS/catalog.yaml`, `selections.draft.yaml`, `selections.yaml` (после пользовательского approve), `photo-board.html`, `photo-preview.html`, `processed/<slot>.jpg` для каждого слота + `processed/manifest.json`, обновлённый `composed.html` с подставленными реальными фото, обновлённый `07c_PHOTOS/STATE.yaml`.

## Failure modes

- **Не пройдены hard-gates предшественников** — агент остановится при старте, если 05 или 07b не в статусе `approved`; пользователь получит сообщение но не трассировку ошибки.
- **Пользователь не кладёт `selections.yaml` обратно** — агент зависнет на шаге 8, ожидая файл; нет тайм-аута.
- **Codex post-process падает на отдельной фотке** — manifest.json будет неполным; `verify-photo-pipeline.sh` заблокирует закрытие этапа, пока хоть один слот не обработан.
- **SVG-плейсхолдеры в composed.html после перерендера** — HARD GATE 07c и 07f поймает это; причина — отсутствие processed-фото для слота.
- **Несоответствие ratio фото к слоту** — codex-process-photo.sh должен валидировать до обработки, но при ошибке валидации фото молча может остаться необработанным.

## Related

- [[photo-classifier]] — sub-агент AI-классификации фото по тегам и типу
- [[photo-matcher]] — sub-агент сопоставления фото со слотами прототипа
- [[photo-preview-board]] — sub-агент финальной обработки и рендера preview HTML
- [[photo-curation]] — скилл-контейнер со скриптами пайплайна (intake, gallery-render, validator)
- [[landing-photos]] — slash-команда, запускающая photo-curator
- [[landing-compose]] — предшествующий этап 07b, создающий composed.html с плейсхолдерами