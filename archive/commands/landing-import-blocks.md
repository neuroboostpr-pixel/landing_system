---
description: Импорт новых блоков в block-library из URL или скриншота. Проверяет уникальность по layout-сигнатуре, добавляет только структурно уникальные блоки с нейтральным template.html без стилей. Перегенерирует gallery.html.
allowed-tools: Bash, Read
---

# /landing-import-blocks

Импорт новых блоков в `block-library/` из URL или скриншота.

## Использование

```
/landing-import-blocks [--url <URL>] [--screenshot <path>] [--from-chat] [--yes-to-all]
```

- `--url <URL>` — скриншот страницы по URL
- `--screenshot <path>` — локальный файл скриншота
- `--from-chat` — взять скриншот, присланный в чат
- `--yes-to-all` — добавить все блоки без подтверждения дублей

## Steps

1. Run:
   ```bash
   python "skills/landing-import-blocks/scripts/import_blocks.py" {{args}}
   ```
2. При появлении вопроса о дубле — ответь yes/no.
3. По завершении открой `block-library/gallery.html` для просмотра новых блоков.

## Что делает

1. Получает изображение (URL / скриншот из чата / файл).
2. Codex vision анализирует блоки — тип, layout-паттерн, слоты, фоновое фото.
3. Вычисляет сигнатуру каждого блока и проверяет дубли в `catalog.yaml`.
4. При дубле — показывает сравнение и спрашивает yes/no.
5. Генерирует нейтральный `template.html` без стилей (серые тона, system-ui, `data-slot`).
6. Присваивает id вида `hero-004`, обновляет `catalog.yaml` и `gallery.html`.

## Под капотом

Скил `landing-import-blocks`. Таксономия — `block-library/taxonomy.yaml` (10 категорий, 27 типов).
См. [spec](../docs/superpowers/specs/2026-05-29-landing-import-blocks-design.md),
[plan](../docs/superpowers/plans/2026-05-29-landing-import-blocks-plan.md).
