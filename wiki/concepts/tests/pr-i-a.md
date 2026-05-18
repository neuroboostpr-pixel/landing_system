Теперь у меня достаточно контекста. Формирую wiki-страницу:

---
type: unknown
name: pr-i-a
sources: ["tests/pr-i-a/README.md"]
updated: 2026-05-18
stage: "07c"
uses: ["photo-curator", "photo-curation", "visual-generation", "stage-gates"]
tags: ["tests", "photo-pipeline", "bats", "codex", "identity-safe"]
---

# PR-I-A — Тест-группа: Photo Pipeline (размер + codex + identity)

## Что делает
Набор bats-тестов для проверки фото-пайплайна этапа 07c: что codex-кэш работает, интерактивный подбор фото по слотам завершается корректно, в финальном composed.html не остаётся SVG-плейсхолдеров, а пропорции загруженных фото соответствуют требованиям слотов.

## Когда вызывать / в каком этапе
Запускаются в рамках CI после изменений в `skills/photo-curation/`, `agents/photo-curator.md` и любых скриптов, связанных с этапом **07c**. Вручную — командой `bats tests/pr-i-a/` перед закрытием HARD GATE 07c.

## Что на вход / на выход

**Вход:**
- Тестовые фото в `07c_PHOTOS/inbox/`
- `tokens.json` с бренд-цветами и `market-profile.yaml` с регионом/настроением
- Заготовленные `selections.yaml` (мок-варианты для интерактивного теста)

**Выход:**
- Результат bats: exit 0 = все тесты прошли, exit 1 = есть падения
- Покрываемые сценарии:
  - `test_codex_caches.bats` — повторный прогон на тех же слотах не вызывает codex (hash-кэш работает)
  - `test_interactive_slot_fill.bats` — интерактивный диалог заполняет все слоты без пропуска
  - `test_no_placeholders.bats` — в `composed.html` нет SVG-заглушек после завершения пайплайна
  - `test_photo_ratio_validates.bats` — несовпадение ratio >5% выдаёт warning/flag, <5% → auto crop_center

## Связанные концепты
- [[photo-curator]] — основной агент этапа 07c, который тест-группа покрывает
- [[photo-curation]] — скилл с описанием identity-safe правил и интерактивного диалога
- [[visual-generation]] — паттерн codex hash-кэша, переиспользованный в PR-I-A
- [[stage-gates]] — HARD GATE 07c не закрывается при наличии плейсхолдеров или незаполненных слотов

## Источник
- `tests/pr-i-a/README.md`