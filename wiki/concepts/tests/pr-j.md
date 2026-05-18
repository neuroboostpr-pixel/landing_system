---
type: unknown
name: pr-j
sources: ["tests/pr-j/README.md", "tests/pr-j/test_verify_identity.bats", "tests/pr-j/test_threshold_per_type.bats", "tests/pr-j/test_revert_on_violation.bats"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation"]
tags: ["tests", "identity-safe", "bats", "photo-pipeline"]
---

# PR-J: Тесты identity-check и photo-pipeline

## Что делает
Набор bats-тестов, проверяющих механизм **identity-safe** в photo-pipeline: правильно ли скрипты определяют, что лицо/объект на фото не был изменён AI при обработке, и корректно ли поведение при нарушении.

## Когда вызывать / в каком этапе
Запускается как часть CI после изменений в `skills/photo-curation/scripts/` — скриптах `identity-check.py`, `photo-pipeline.py` и `verify-identity-preserved.sh`. Относится к этапу **07c** (обработка фотографий клиента).

## Что на вход / на выход

**Вход:**
- Тестовые JPEG-изображения (создаются хелпером `make_dummy_jpg`)
- Проект с manifest-файлом (создаётся хелпером `make_project_with_manifest`)
- Реальные скрипты: `identity-check.py`, `photo-pipeline.py`, `verify-identity-preserved.sh`

**Выход:**
- Exit 0 / Exit 1 по результатам трёх тест-файлов:
  - `test_verify_identity.bats` — проверяет скрипт `verify-identity-preserved.sh`: нет нарушений → exit 0, есть нарушение → exit 1 с деталями, нет манифеста → exit 0 (no-op)
  - `test_threshold_per_type.bats` — проверяет `identity-check.py`: порог 5 для `portrait`, порог 10 для `vehicle`, ручной `--threshold` перебивает тип слота
  - `test_revert_on_violation.bats` — smoke-проверки кода `photo-pipeline.py`: наличие поля `identity_violation` в выходном dict и передача флага `--slot-type` в identity-check

## Запуск

```bash
# Все bats-тесты PR-J
bats tests/pr-j/
```

## Связанные концепты
- [[photo-curator]] — оркестратор этапа 07c, чьи скрипты тестируются
- [[photo-curation]] — скилл, содержащий `photo-pipeline.py` и `identity-check.py`

## Источник
- `tests/pr-j/README.md`
- `tests/pr-j/test_verify_identity.bats`
- `tests/pr-j/test_threshold_per_type.bats`
- `tests/pr-j/test_revert_on_violation.bats`