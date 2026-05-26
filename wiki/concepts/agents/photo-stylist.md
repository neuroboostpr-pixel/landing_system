---
slug: photo-stylist
type: agent
name: "Photo Stylist"
stage: "02"
tags: [photos, identity-safe, cutout, compositing, processing]
triggers: [photo-curator]
inputs: [02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original]
outputs: [02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed, 02_МАТЕРИАЛЫ_КЛИЕНТА/photos/stylesheet.md]
gates: []
pre_reqs: []
related: [photo-curator, photo-classifier, photo-matcher]
sources: ["agents/photo-stylist.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Photo Stylist

## Что делает
Обрабатывает сырые фотографии клиента для использования в лендинге: вырезает фон, чистит края, накладывает тени и текстуры бумаги, кадрирует под сцену и конвертирует формат. Все операции строго identity-safe — лица, возраст и пропорции тела не трогаются ни при каких условиях. Единственный разрешённый инструмент — `skills/photo-styling/scripts/style.py`. Результаты фиксируются в `stylesheet.md`.

## Когда вызывается
Диспатчится родительским агентом `photo-curator` в рамках этапа 02. Прямой вызов пользователем не предусмотрен — агент является вспомогательным и не управляет Stage Execution Protocol самостоятельно.

## Вход → выход
**Вход:** оригинальные фото клиента в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`; уточнение от пользователя об intended use каждого фото (hero / about / proof).

**Выход:** обработанные фото в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/`; обновлённый `stylesheet.md` с описанием применённых правил к каждому файлу; обновлённая `assets-gallery.html` с оригиналом и обработанной версией рядом — для ревью пользователем перед этапом 03.

## Failure modes
- Попытка обойти ограничение `style.py` и вызвать PIL, curl или внешний AI-сервис — архитектурное нарушение, которое делает «Forbidden»-список неконтролируемым.
- Пропуск уточняющего вопроса об intended use — агент обрабатывает фото в неверном режиме (cutout для «about» вместо hero-кадрирования).
- Обработка файлов без обновления `stylesheet.md` — теряется трассируемость: непонятно, какие правила применены к какому фото.
- Запуск до того, как `photo-curator` передал управление — агент не имеет контекста о слотах и может обработать лишние или неправильные фото.
- Отсутствие HARD GATE: выход на этап 03 без ревью `assets-gallery.html` пользователем — gallery показывает оба варианта (оригинал / обработка) специально для этого момента одобрения.

## Related
- [[photo-curator]] — родительский агент, который диспатчит photo-stylist и владеет Stage Execution Protocol этапа 02
- [[photo-classifier]] — классифицирует фото по типу до передачи в photo-stylist
- [[photo-matcher]] — сопоставляет обработанные фото со слотами макета после этапа photo-stylist