---
type: unknown
name: generate-axes-filter
sources: ["scripts/generate-axes-filter.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: []
tags: ["script", "python", "wordpress", "php-codegen"]
---

# generate-axes-filter.py — генератор PHP-фильтра осей превью-панели

## Что делает
Скрипт генерирует PHP-файл `inc/lp-preview-panel-axes.php`, который регистрирует WordPress-фильтр `lp_preview_panel_axes`. Этот фильтр позволяет подключаемым модулям и темам переопределять конфигурацию осей (axes) в панели превью лендинга — без правки кода вручную.

## Когда вызывать / в каком этапе
Запускается как часть scaffold-процесса сборки темы (ориентировочно этап 08 — Код). Выполняется один раз при генерации или обновлении структуры WordPress-темы. Может перезапускаться при изменении конфигурации осей.

## Что на вход / на выход

**Вход:**
- Конфигурация осей (параметры axes — предположительно из `tokens.json` или аргументов командной строки)

**Выход:**
- `inc/lp-preview-panel-axes.php` — PHP-файл, регистрирующий фильтр `lp_preview_panel_axes` в WordPress

## Связанные концепты
- [[wp-builder]] — основной агент сборки WordPress-темы, в рамках которого вероятно вызывается этот скрипт
- [[wp-theme-assembler]] — скилл сборки темы, управляет генерацией PHP-файлов
- [[wp-gutenberg-block-builder]] — смежный скилл генерации блоков Gutenberg
- [[08-kod]] — этап pipeline, в котором генерируются PHP-артефакты темы

## Источник
- `scripts/generate-axes-filter.py`