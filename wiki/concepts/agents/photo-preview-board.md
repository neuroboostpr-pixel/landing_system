---
slug: photo-preview-board
type: agent
name: "Photo Preview Board — рендер превью фотографий"
stage: "07c"
tags: [photos, preview, identity-safe, codex, photo-processing]
triggers: []
inputs: [07c-photos]
outputs: [07c-photos]
gates: []
pre_reqs: [photo-curator, photo-matcher]
related: [photo-curator, photo-classifier, photo-stylist, photo-curation, photo-styling, landing-photos, 07c-photos]
sources: ["agents/photo-preview-board.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Photo Preview Board — рендер превью фотографий

## Что делает

Агент-помощник, вызываемый `photo-curator` после того, как пользователь одобрил `selections.yaml`. Обрабатывает каждый слот из этого файла: кадрирует и ресайзит клиентские фотографии, при необходимости вызывает Codex для генерации изображения-замены, а для слотов без фото создаёт SVG-плейсхолдер. В финале рендерит `photo-preview.html` для финального просмотра маркетологом. Самостоятельно не управляет этапом — это вспомогательная единица внутри pipeline `landing-photos`.

## Когда вызывается

Диспатчится агентом `photo-curator` автоматически после того, как пользователь разместил одобренный `selections.yaml` в папку `07c_PHOTOS/`. Не предназначен для прямого ручного вызова.

## Вход → выход

**Вход:** директория проекта с валидным `07c_PHOTOS/selections.yaml` (слоты с полями `strategy`, `slot_id`, `ratio`, `hint`, `ai_approved_by_user`).

**Выход:**
- `07c_PHOTOS/processed/<slot_id>/desktop.jpg` — обработанное изображение
- `07c_PHOTOS/processed/<slot_id>/mobile.jpg` — мобильный вариант (если блок требует `mobile_ratio`)
- `07c_PHOTOS/photo-preview.html` — HTML-превью для финального просмотра

## Failure modes

- **Невалидный `selections.yaml`** — скрипт `selections-validator.py` вернёт ошибку, агент прерывает выполнение, не трогая файлы.
- **Недоступен Codex API** — слоты со `strategy: generate` зависнут; нужен fallback до `placeholder` вручную или повтор.
- **Нарушение identity-safe** — слот `testimonial|expert|team-member` с `ai_approved_by_user: false` молча деградирует до `placeholder`. Если логика не сработала — генерируется лицо без согласия пользователя (критичный дефект).
- **Отсутствует `mobile_ratio` в meta.yaml блока** — мобильная версия не создаётся, блок может выглядеть некорректно на смартфонах.
- **Повреждён или отсутствует исходник фото** — `style.py` упадёт с ошибкой чтения файла; нужно проверить путь в `intake/`.

## Related

- [[photo-curator]] — родительский агент, который диспатчит photo-preview-board
- [[photo-curation]] — скилл, содержащий скрипты валидации, генерации и рендера
- [[photo-styling]] — скилл кадрирования/ресайза клиентских фото
- [[photo-classifier]] — предшествует: классифицирует фото клиента по слотам
- [[photo-matcher]] — предшествует: сопоставляет фото со слотами в `selections.yaml`
- [[07c-photos]] — этап, которому принадлежит весь photo-pipeline
- [[landing-photos]] — команда верхнего уровня, запускающая весь photo-pipeline