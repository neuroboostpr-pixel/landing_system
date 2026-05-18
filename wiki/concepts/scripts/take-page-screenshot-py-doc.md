---
type: rule
name: take-page-screenshot
sources: ["scripts/import-blocks/take-page-screenshot.py", "scripts/import-blocks/take-page-screenshot.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "references-collection"]
tags: ["script", "python", "playwright", "screenshot", "import-blocks"]
---

# take-page-screenshot — скриншот страницы (desktop + mobile)

## Что делает
Python-скрипт делает полноэкранный скриншот любой веб-страницы в двух форматах: desktop (1280×800) и mobile (375×812). Результат — два PNG-файла в указанной папке.

## Когда вызывать / в каком этапе
Используется в пайплайне импорта блоков (`scripts/import-blocks/`) — когда нужно зафиксировать визуальный вид страницы-источника перед тем, как вырезать из неё блоки в библиотеку. Вызывается как CLI-утилита из других скриптов или вручную.

## Что на вход / на выход

**Вход:**
- `url` — URL страницы (позиционный аргумент)
- `--out <dir>` — путь к папке для сохранения скриншотов (обязательный флаг)
- Зависимость: `playwright` + `chromium` должны быть установлены (`pip install playwright && playwright install chromium`)

**Выход:**
- `<out>/desktop.png` — полностраничный скриншот при ширине 1280px
- `<out>/mobile.png` — полностраничный скриншот при ширине 375px
- Статус-сообщение `OK Screenshots done` в stdout при успехе
- Exit code `2` если playwright не установлен; `0` при успехе

**Детали поведения:**
- Ждёт `domcontentloaded`, затем пытается дождаться `networkidle` (timeout 20 сек) — игнорирует ошибку тайм-аута, но предупреждает в stderr
- Создаёт папку `--out` автоматически (включая вложенные)

## Связанные концепты
- [[block-library-management]] — скрипт входит в пайплайн импорта новых блоков в библиотеку
- [[references-collection]] — скриншоты могут использоваться при сборе визуальных референсов

## Источник
- `scripts/import-blocks/take-page-screenshot.py`