---
type: rule
name: verify-content-preserved
sources: ["scripts/verify_content_preserved.py"]
updated: 2026-05-18
triggers: []
stage: "07b"
uses: ["prototype-importer", "block-composer"]
tags: ["qa", "verify", "prototype", "composed"]
---

# verify_content_preserved.py — Проверка сохранности текстов прототипа

## Что делает
Скрипт проверяет, что все текстовые строки из `prototype.yaml` присутствуют в финальном `composed.html` и порядок блоков не нарушился. Это страховка от случайного пропуска или перестановки контента при сборке страницы.

## Когда вызывать / в каком этапе
Запускается на этапе **07b (Block Compose)** — после того, как `block-composer` собрал `composed.html` с подставленными токенами и текстами прототипа. Является частью HARD GATE 07b: пока скрипт не вернёт exit 0, этап не считается закрытым. Также можно запускать вручную в любой момент для диагностики.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — машиночитаемая версия прототипа (создаётся `prototype-importer`)
- `composed.html` — финальная сборка блоков (создаётся `block-composer`)

**Выход:**
- **Exit code 0** — все строки прототипа найдены в composed.html, порядок блоков сохранён
- **Exit code 1** — обнаружены расхождения; детали выводятся в stderr
- **Exit code 2** — один из входных файлов (`prototype.yaml` или `composed.html`) не найден

## Связанные концепты
- [[prototype-importer]] — создаёт `prototype.yaml`, который скрипт читает как эталон
- [[block-composer]] — генерирует `composed.html`, который скрипт проверяет
- [[premium-07b-checklist]] — более широкий чеклист качества этапа 07b, частью которого является этот скрипт
- [[stage-gates]] — HARD GATE 07b требует exit 0 перед переходом к следующему этапу

## Источник
- `scripts/verify_content_preserved.py`