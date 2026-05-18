---
type: rule
name: pr-g-tests
sources: ["tests/pr-g/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["stage-gates", "wiki", "landing-orchestrator"]
tags: ["testing", "bats", "gate-check", "post-commit", "wiki-sync"]
---

# Тесты PR-G — автосинхронизация wiki и stage-gates

## Что делает

Покрывает bats-тестами два ключевых механизма PR-G: **post-commit хук wiki-синхронизации** и **gate-check блокировки этапов** (hard + soft). Запускается командами `bats tests/pr-g/` или `pytest tests/pr-g/`.

## Когда вызывать / в каком этапе

Запускается автоматически при CI или вручную разработчиком при изменении:
- `.githooks/post-commit` — логики хука;
- `scripts/gate-check.sh` — скрипта проверки гейтов;
- `config/*.yaml` — конфигурации stage-gates.

Не привязан к конкретному этапу pipeline — это системный тест инфраструктуры.

## Что на вход / на выход

**Вход:**
- Скрипт `scripts/gate-check.sh` (тестируемый объект).
- `.githooks/post-commit` (хук, логика которого проверяется инлайн).
- `helpers.bash` — вспомогательные фикстуры (`make_fake_project`, `set_status`).

**Выход:**
- `bats` exit 0 если все тесты прошли, exit 1 с описанием упавших кейсов.

**Что именно проверяется (4 файла):**

| Файл | Что тестирует |
|---|---|
| `test_post_commit_hook.bats` | Хук НЕ запускает `compile.py` при изменении несвязанных файлов; ЗАПУСКАЕТ при изменении `agents/` и других источников wiki |
| `test_gate_check_updates_graph.bats` | После прохода `gate-check.sh` файл `wiki/log.md` в проекте обновляется (авто-обновление project-graph) |
| `test_stage_lock_hard.bats` | Hard-блокировки: `07b_wireframe` закрыт без `04_brand approved`; `08_build` без `07c_composed`; `09_deploy` без `10_qa` |
| `test_stage_lock_soft.bats` | Soft-предупреждения: `04_brand` печатает `⚠️ Soft warning` при незакрытом `03_references`, но не блокирует с флагом `--auto` |

## Связанные концепты

- [[stage-gates]] — правила hard/soft блокировок, которые тесты верифицируют
- [[wiki]] — механизм wiki-синхронизации через post-commit хук
- [[landing-orchestrator]] — использует `gate-check.sh` перед переходом между этапами

## Источник

- `tests/pr-g/README.md`