---
type: rule
name: verify-composed-has-visuals
sources: ["scripts/verify-composed-has-visuals.sh", "scripts/verify-composed-has-visuals.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: "07c, 07d"
uses: ["block-composer", "photo-curator", "visual-curator", "photo-preview-board"]
tags: ["qa", "gate", "visuals", "photos", "composed", "bash"]
---

# verify-composed-has-visuals — проверка placeholder-маркеров в composed.html

## Что делает

Bash-скрипт-верификатор: проверяет, что в финальном `composed.html` не осталось нераскрытых placeholder-меток вида `[SLOT: ...]`. Если маркеры найдены — значит этапы фото (PR-B) или визуала (PR-C) ещё не завершены, и сборка не может идти дальше.

## Когда вызывать / в каком этапе

Запускается как HARD GATE на переходе от этапов **07c** (фото) и **07d** (иконки/инфографика) к сборке **08**. Вызывается вручную или автоматически через `gate-check.sh` и `landing-orchestrator` перед тем, как двигаться к `/landing-build`.

Типичный сценарий: после того как `photo-curator` или `visual-curator` завершили работу — запустить скрипт и убедиться, что все слоты заполнены реальным контентом.

## Что на вход / на выход

**Вход:**
- Путь к файлу `composed.html` (аргумент командной строки)

**Выход (exit codes):**
| Код | Значение |
|-----|----------|
| `0` | Файл чистый — все placeholder-маркеры заменены |
| `1` | Найдены оставшиеся маркеры — PR-B или PR-C не завершены |
| `2` | Файл `composed.html` не найден по указанному пути |

**Типичный вызов:**
```bash
bash scripts/verify-composed-has-visuals.sh 07b_COMPOSED/composed.html
```

## Связанные концепты

- [[photo-curator]] — этап 07c, заменяет фото-слоты в composed.html реальными изображениями
- [[visual-curator]] — этап 07d, заменяет иконки и инфографику в composed.html
- [[photo-preview-board]] — рендерит финальный photo-preview.html и инициирует замену placeholders
- [[block-composer]] — создаёт composed.html с placeholder-метками на этапе 07b
- [[stage-gates]] — система HARD GATE, в которую встроена эта проверка
- [[premium-07b-checklist]] — смежный стандарт качества для composed.html

## Источник

- `scripts/verify-composed-has-visuals.sh`