---
type: rule
name: stage-08-helper
sources: ["scripts/lib/stage_08_helper.py"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["stage-gates", "wp-builder", "wp-gutenberg-block-builder"]
tags: ["gate-check", "lazy-blocks", "validation", "stage-08"]
---

# stage_08_helper — валидатор артефактов этапа 08 (Lazy Blocks)

## Что делает

Python-скрипт, который проверяет корректность сборки WordPress-темы на этапе 08. Убеждается, что все обязательные артефакты Lazy Blocks присутствуют и имеют правильную структуру — до того как проект уйдёт на деплой.

## Когда вызывать / в каком этапе

Вызывается автоматически из `scripts/gate-check.sh` при прохождении HARD GATE этапа 08 (`08_КОД`). Запускается после того, как `wp-builder` сгенерировал тему. Не требует ручного вызова — оркестратор и gate-check вызывают его сами.

Можно вызвать вручную для диагностики:
```
python stage_08_helper.py <project-root>
```
Exit 0 = всё ок, exit 1 = жёсткая ошибка.

## Что на вход / на выход

**Вход:**
- Путь к корню проекта (`<project-root>`)
- `08_КОД/block-spec.yaml` — спецификация блоков (загружается и валидируется через `block_spec.load + validate`)
- `08_КОД/wp-theme/functions.php` — должен содержать строки `lzb/init` и `lazyblocks()->add_block(`
- `08_КОД/wp-theme/blocks/` — папка с хотя бы одним файлом `lazyblock-*/block.php`
- `08_КОД/page-content.html` — HTML-контент страницы

**Выход:**
- Exit 0 — все артефакты на месте, gate проходит
- Exit 1 — жёсткий провал (hard fail): в консоль выводится список отсутствующих/некорректных файлов

**Мягкая проверка (warn-only):**
Если в `block-spec.yaml` есть блоки типа `section-card`, скрипт проверяет наличие маркера `lzb-inner-blocks` в `assets/css/main.css`. Отсутствие даёт предупреждение, но не блокирует gate.

## Связанные концепты

- [[stage-gates]] — система HARD/SOFT гейтов, в рамках которой вызывается этот скрипт
- [[wp-builder]] — агент, который генерирует артефакты, которые проверяет этот скрипт
- [[wp-gutenberg-block-builder]] — скилл сборки Lazy Blocks блоков
- [[08-kod]] — этап, к которому относится проверка

## Источник

- `scripts/lib/stage_08_helper.py`