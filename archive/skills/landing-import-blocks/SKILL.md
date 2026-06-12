---
name: landing-import-blocks
description: Импорт новых блоков в block-library из URL или скриншота. Проверяет уникальность по layout-сигнатуре, добавляет только структурно уникальные блоки с нейтральным template.html без стилей.
---

# landing-import-blocks

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill landing-import-blocks --stage ""
```

## Использование

Папка скила называется `landing-import-blocks` (с дефисами), модуль импортируется
по прямому пути. Запуск через сам файл:

```bash
# Из URL:
python "skills/landing-import-blocks/scripts/import_blocks.py" --url https://example.com

# Из скриншота в чате (пришли скриншот, потом запусти):
python "skills/landing-import-blocks/scripts/import_blocks.py" --from-chat

# Из файла:
python "skills/landing-import-blocks/scripts/import_blocks.py" --screenshot /path/to/img.png

# Добавить все блоки без подтверждения дублей:
python "skills/landing-import-blocks/scripts/import_blocks.py" --url https://... --yes-to-all
```

## Что делает

1. Получает изображение (URL / скриншот из чата / файл).
2. Codex vision анализирует блоки — тип, layout-паттерн, слоты, наличие фонового фото.
3. Вычисляет сигнатуру каждого блока: `{type}|{layout_pattern}|[slots]|bg:{bool}`.
4. Проверяет каждый блок на дубль по сигнатуре в `block-library/catalog.yaml`.
5. При дубле — показывает сравнение существующего и нового блока, спрашивает yes/no.
6. Генерирует нейтральный `template.html` без стилей (серые тона, system-ui, `data-slot`).
7. Присваивает id вида `hero-004` (max+1 по типу).
8. Обновляет `catalog.yaml` и перегенерирует `gallery.html`.
9. Выводит список добавленных блоков и ссылку на `block-library/gallery.html`.

## Таксономия

Единый источник истины — `block-library/taxonomy.yaml` (10 категорий, 27 типов).

## Связанные документы

- [spec](../../docs/superpowers/specs/2026-05-29-landing-import-blocks-design.md)
- [plan](../../docs/superpowers/plans/2026-05-29-landing-import-blocks-plan.md)
