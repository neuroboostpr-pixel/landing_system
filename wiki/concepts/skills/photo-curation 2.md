---
slug: photo-curation
type: skill
name: "Конвейер обработки клиентских фото (Photo Curation)"
stage: "07c"
tags: [photos, pipeline, codex, ai-classification, compose]
triggers: [landing-photos]
inputs:
  - 07c_PHOTOS/inbox/
  - 05_ДИЗАЙН/design-system (approved)
  - 07a_WIREFRAME/selections.yaml
  - prototype.yaml
outputs:
  - 07c_PHOTOS/selections.yaml
  - 07c_PHOTOS/photo-board.html
  - 07c_PHOTOS/photo-preview.html
  - 07b_COMPOSED/composed.html (re-render с реальными фото)
  - 07c_PHOTOS/manifest.json
gates: []
pre_reqs: [design-system-generator, prototype-importer, ux-composer]
related:
  - photo-curator
  - photo-classifier
  - photo-matcher
  - photo-stylist
  - photo-preview-board
  - block-composer
  - visual-curator
  - prototype-importer
sources: ["skills/photo-curation/SKILL.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# Конвейер обработки клиентских фото (Photo Curation)

## Что делает

Скилл реализует семиэтапный конвейер подготовки клиентских фотографий для лендинга. Он принимает сырые фото из `inbox/`, прогоняет их через AI-классификацию и матчинг к wireframe-слотам, даёт пользователю интерактивную доску для финального выбора, затем обрабатывает снимки под токены дизайн-системы (кадрирование по ratio, mobile-вариант) и перерендеривает `composed.html` с реальными фотографиями вместо placeholder'ов. Для слотов без клиентских фото запускается codex-генерация fallback-изображений при условии явного согласия (`ai_approved_by_user: true`).

## Когда вызывается

Команда `/landing-photos` после того, как этапы 05 (design-system) и 07a (wireframe selections) получили approve. Повторный запуск продолжает с прерванного этапа согласно `07c_PHOTOS/STATE.yaml`; принудительный сброс — флаг `--force-stage <name>`.

## Вход → выход

**Вход:** фотографии клиента в подпапках `07c_PHOTOS/inbox/`, утверждённые `05_ДИЗАЙН/tokens.json` и `07a_WIREFRAME/selections.yaml`, `prototype.yaml` со списком photo-слотов.

**Выход:** обработанные фото в `07c_PHOTOS/processed/`, `selections.yaml` с финальным маппингом слот→файл, `photo-board.html` и `photo-preview.html` для пользовательского просмотра, обновлённый `composed.html` с реальными `<img>` вместо placeholders, `manifest.json` с хэшами и параметрами обработки.

## Failure modes

- **codex-classify зависает** — нет codex CLI или превышен лимит API; прогон прерывается, `STATE.yaml` фиксирует стадию `classify`, повторный запуск продолжит.
- **Несоответствие ratio** — `style.py` не находит в `tokens.json` значение `slots[].ratio`; блок падает с KeyError.
- **Дубли не дедуплицированы** — при разных именах файлов с одинаковым содержимым `intake.py` может пропустить дубликат, что приведёт к двум кандидатам на один слот.
- **Identity-safe нарушено** — если `ai_approved_by_user` не выставлен, а в слоте обнаружено лицо, генерация fallback прерывается; слот остаётся с placeholder'ом в composed.html.
- **Кэш устарел** — при смене brand-tokens хэш меняется, но старые `07c_PHOTOS/.cache/` файлы не удаляются автоматически; размер кэша растёт неограниченно.

## Related

- [[photo-curator]] — агент-владелец скилла, оркестрирует все семь этапов
- [[photo-classifier]] — отвечает за codex-тегирование (этап classify)
- [[photo-matcher]] — ранжирует кандидатов по wireframe-слотам (этап match)
- [[photo-stylist]] — кадрирование и обработка под design-tokens (этап process)
- [[photo-preview-board]] — рендер photo-board.html и photo-preview.html (этапы approve/preview)
- [[block-composer]] — принимает итоговый composed.html после re-render
- [[visual-curator]] — параллельный этап 07d (AI-генерация иконок и инфографики)
- [[prototype-importer]] — поставляет prototype.yaml со списком photo-слотов