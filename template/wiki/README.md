# wiki/ — граф структуры проекта

Эта папка автоматически наполняется компайлером `landing-system/scripts/wiki/`
после каждого этапа pipeline.

**Не редактируй вручную** — содержимое перезаписывается.

## Структура
- `index.md` — главный индекс (читай первым)
- `log.md` — хронология обновлений
- `concepts/` — концепты по этому проекту:
  - `stage-current.md` — текущий этап
  - `blocks.md` — выбранные блоки
  - `brand.md` — цвета и шрифты
  - `photos.md` — карта фото-слотов

## Как обновляется

Автоматически:
- После `gate-check.sh exit 0` (закрытие этапа)
- Можно вручную: `python -m scripts.wiki.compile --source-mode=project-graph --project=<slug>`

Подробнее: `landing-system/docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md`.
