На основе прочитанных файлов формирую wiki-страницу:

---
type: rule
name: gate-check-tests
sources: ["tests/gate-check/README.md", "tests/gate-check/test-gate-check.bats", "tests/gate-check/test-gate-state.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["stage-gates", "landing-orchestrator"]
tags: ["testing", "bats", "gate-check", "gate-state", "ci"]
---

# Тесты gate-check — проверка гейтов между этапами

## Что делает

Набор автотестов (bats), который проверяет, что скрипты `gate-check.sh` и `gate-state.sh` корректно контролируют переходы между этапами лендинг-проекта: нельзя перейти к следующему этапу без явного одобрения предыдущего.

## Когда вызывать / в каком этапе

Тесты запускаются на уровне CI или вручную разработчиком после любых изменений в `scripts/gate-check.sh` или `scripts/gate-state.sh`. Входят в базовый smoke-прогон перед коммитом в основную ветку.

```bash
# Bats-тесты
bats tests/gate-check/

# Pytest (если появятся test_*.py)
pytest tests/gate-check/
```

## Что на вход / на выход

**Вход:**
- Временная папка `$BATS_TEST_TMPDIR/test-project/` — изолированный проект.
- `template/.landing-state.yaml` — копируется в тестовый проект как эталонное состояние.
- `scripts/gate-check.sh` и `scripts/gate-state.sh` — тестируемые скрипты.

**Выход:**
- bats exit 0 — все тесты прошли (инварианты гейтов соблюдены).
- bats exit ≠ 0 — сломан один или несколько сценариев гейтинга.

**Файлы тестов:**
| Файл | Что проверяет |
|------|---------------|
| `test-gate-check.bats` | `gate-check.sh`: блокировка при не-одобренных предшественниках; hard_check file_exists; флаг `--approve` переводит этап в `approved` |
| `test-gate-state.bats` | `gate-state.sh`: get/set/approve операции над `.landing-state.yaml`; `all_approved` возвращает 0/1 корректно |

**Ключевые сценарии:**
- Этап `02_assets` не проходит, если `00_brief` или `01_context` не одобрены.
- Флаг `--approve` в `gate-check.sh` записывает статус `approved` в YAML.
- `gate-state.sh get` возвращает `n/a` для bypass-этапов и `locked` для ещё не начатых.
- `all_approved` возвращает ошибку и печатает имя блокирующего этапа.

## Связанные концепты

- [[stage-gates]] — правило HARD GATE между этапами: стандарт, который эти тесты верифицируют
- [[landing-orchestrator]] — главный агент, вызывающий `gate-check.sh` перед каждым этапом

## Источник

- `tests/gate-check/README.md`
- `tests/gate-check/test-gate-check.bats`
- `tests/gate-check/test-gate-state.bats`