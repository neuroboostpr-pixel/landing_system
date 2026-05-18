---
type: unknown
name: pr-l-tests
sources: ["tests/pr-l/README.md", "tests/pr-l/test_final_check_fail.bats", "tests/pr-l/test_final_check_pass.bats", "tests/pr-l/test_report_file_created.bats", "tests/pr-l/helpers.bash"]
updated: 2026-05-18
triggers: []
stage: "10"
uses: ["landing-final-check", "qa-auditor", "10-qa"]
tags: ["tests", "bats", "final-check", "qa", "pr-l"]
---

# PR-L Tests — тесты финальной проверки лендинга

## Что делает

Группа bats-тестов, которая проверяет корректность работы скрипта `landing-final-check.sh`: правильно ли он агрегирует результаты шести verify-скриптов, когда возвращает PASS/FAIL, и создаёт ли итоговый отчёт `10_QA/final-check-report.md`.

## Когда вызывать / в каком этапе

Запускаются вручную (или CI) после изменений в `scripts/landing-final-check.sh` или любом из проверочных скриптов. Покрывают этап **10 QA** — последнюю обязательную проверку перед деплоем.

```bash
bats tests/pr-l/
```

## Что на вход / на выход

**Вход:**
- `helpers.bash` — создаёт sandbox-репо с shim-скриптами и пустой project-skeleton (`07b_COMPOSED/`, `10_QA/`)
- Параметры exit-кодов для каждого из 6 проверочных скриптов: `wiki-sync`, `composed-premium`, `content-preserved`, `photo-pipeline`, `identity-preserved`, `visual-qa`

**Выход / что проверяют:**
- `test_final_check_pass.bats` — все verify exit 0 → `landing-final-check.sh` возвращает exit 0 и выводит `"Final check: PASS"`
- `test_final_check_fail.bats` — обязательный verify (`composed-premium`) exit 1 → итог exit 1 + `"Final check: FAIL"`; опциональный (`visual-qa`) exit 1 → всё равно exit 0
- `test_report_file_created.bats` — файл `10_QA/final-check-report.md` создаётся и содержит все 6 секций (`wiki-sync`, `composed-premium`, `content-preserved`, `photo-pipeline`, `identity-preserved`, `visual-qa`) и строку `"ВСЕ обязательные проверки прошли"`

## Ключевые детали

| Проверка | Тип |
|---|---|
| `check-wiki-sync.sh` | обязательная |
| `verify-composed-premium.sh` | обязательная |
| `verify-content-preserved.sh` | обязательная |
| `verify-photo-pipeline.sh` | обязательная |
| `verify-identity-preserved.sh` | обязательная |
| `verify-visual-qa.sh` | **опциональная** — падение не блокирует |

Shim-подход в `helpers.bash` позволяет изолированно протестировать логику агрегации без зависимости от реального состояния проекта.

## Связанные концепты

- [[landing-final-check]] — команда, чей скрипт тестируется
- [[qa-auditor]] — агент этапа QA, использующий те же verify-скрипты
- [[10-qa]] — этап pipeline, на котором запускается финальная проверка
- [[stage-gates]] — механизм hard gate, на который влияет exit-код `landing-final-check.sh`

## Источник

- `tests/pr-l/README.md`
- `tests/pr-l/helpers.bash`
- `tests/pr-l/test_final_check_pass.bats`
- `tests/pr-l/test_final_check_fail.bats`
- `tests/pr-l/test_report_file_created.bats`