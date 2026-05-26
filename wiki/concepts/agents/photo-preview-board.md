---
slug: photo-preview-board
type: agent
name: "Photo Preview Board — обработка слотов и рендер превью"
stage: "07c"
tags: [photos, preview, identity-safe, codex, image-processing]
triggers: []
inputs: ["07c_PHOTOS/selections.yaml"]
outputs: ["07c_PHOTOS/processed/<slot_id>/desktop.jpg", "07c_PHOTOS/processed/<slot_id>/mobile.jpg", "07c_PHOTOS/photo-preview.html"]
gates: []
pre_reqs: [photo-curator]
related: [landing-photos]
sources: ["agents/photo-preview-board.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# Photo Preview Board — обработка слотов и рендер превью

## Что делает

Хелпер-агент, вызываемый родительским агентом `photo-curator` после того, как пользователь утвердил `selections.yaml`. Для каждого слота из этого файла выполняет одно из трёх действий: кроппинг/ресайз клиентской фотографии, AI-генерацию изображения через codex (fallback), или создание SVG-заглушки. Затем рендерит `photo-preview.html` — финальный экран для проверки перед продолжением пайплайна. Принудительно применяет identity-safe политику: если слот помечен как идентификационный (testimonial, expert, team-member и т.п.) и флаг `ai_approved_by_user` не выставлен, стратегия `generate` молча понижается до `placeholder`.

## Когда вызывается

Диспатчится агентом `photo-curator` после того, как пользователь скачал и положил `selections.yaml` обратно в `07c_PHOTOS/`. Не вызывается напрямую пользователем — это внутренний хелпер этапа 07c.

## Вход → выход

**Вход:** Директория проекта с валидным `07c_PHOTOS/selections.yaml` (утверждённые пользователем слоты, каждый с указанной стратегией: `bring-your-own`, `generate` или `placeholder`).

**Выход:** Обработанные изображения в `07c_PHOTOS/processed/<slot_id>/desktop.jpg` (и `mobile.jpg` при наличии `mobile_ratio` в мета-блока), а также `07c_PHOTOS/photo-preview.html` — HTML-страница для финальной визуальной проверки всех слотов.

## Failure modes

- `selections.yaml` не проходит валидацию (`selections-validator.py` → abort) — агент останавливается и не обрабатывает ни одного слота.
- Недоступен codex CLI при стратегии `generate` — скрипт `codex-generate-fallback.sh` упадёт; нужна проверка установки через `scripts/install-codex.sh`.
- `style.py` получает фото с нестандартным соотношением сторон и не может нормально кропнуть — результат может не совпасть с ожидаемым ratio.
- Identity-safe downgrade происходит молча — пользователь не получает явного предупреждения, что слот переключён в placeholder; может вызвать удивление при просмотре превью.
- Отсутствует `mobile_ratio` в `meta.yaml` блока, хотя блок адаптивный — мобильная версия не генерируется, что вскроется на этапе 08 Build.

## Related

- [[landing-photos]] — slash-команда этапа 07c, которая запускает весь photo-pipeline, включая вызов `photo-curator` → `photo-preview-board`
- [[photo-curator]] — родительский агент, диспатчащий этот хелпер после approve `selections.yaml`