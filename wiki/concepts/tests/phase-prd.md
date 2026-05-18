---
type: rule
name: phase-prd-tests
sources: ["tests/phase-prd/README.md", "tests/phase-prd/test-gate-na-status.bats", "tests/phase-prd/test-landing-go.bats", "tests/phase-prd/test-migration.bats", "tests/phase-prd/test-install-codex.bats", "tests/phase-prd/test-onboarding-update.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-go", "landing-orchestrator", "landing-onboarding", "stage-gates"]
tags: ["tests", "bats", "pr-d", "gate", "migration", "codex"]
---

# Тесты phase-prd

## Что делает
Набор автоматизированных bats-тестов, который проверяет корректность реализации PR-D — интеграции оркестратора с prototype-first workflow. Покрывает 5 сценариев: статус `n/a` в gate-скриптах, команду `/landing-go`, миграцию `.landing-state.yaml`, установку codex CLI и актуальность скилла onboarding.

## Когда вызывать / в каком этапе
Запускается вручную при разработке PR-D или после любых изменений в скриптах `gate-check.sh`, `gate-state.sh`, `migrate-state-for-prd.sh`, `install-codex.sh`, файле `commands/landing-go.md` и скилле `landing-onboarding`. Обязателен перед коммитом, затрагивающим эти артефакты.

```bash
bats tests/phase-prd/
```

## Что на вход / на выход

**Вход:**
- Репозиторий `landing-system/` с установленным `bats-core`
- Скрипты: `scripts/gate-check.sh`, `scripts/gate-state.sh`, `scripts/migrate-state-for-prd.sh`, `scripts/install-codex.sh`
- Файлы: `commands/landing-go.md`, `skills/landing-onboarding/SKILL.md`

**Выход:**
- Отчёт bats: количество прошедших/упавших тестов
- Exit 0 — всё в порядке, PR-D можно коммитить

**Покрытие по файлам:**

| Файл | Что проверяет |
|---|---|
| `test-gate-na-status.bats` | `gate-check.sh` и `gate-state.sh` корректно принимают статус `n/a` для этапов 00–02 (prototype-first: эти этапы проходят до системы) |
| `test-landing-go.bats` | `commands/landing-go.md` содержит frontmatter, флаги `--auto-fix`/`--skip-gate`, ссылку на `landing-orchestrator`, документацию prototype-first входа |
| `test-migration.bats` | `migrate-state-for-prd.sh` добавляет новые PR-D этапы без перезаписи существующих, идемпотентен, поднимает `schema_version` до 2 |
| `test-install-codex.bats` | `install-codex.sh` исполняем, `--check` правильно определяет наличие codex, `--dry-run` печатает npm-команду без выполнения |
| `test-onboarding-update.bats` | Скилл `landing-onboarding` упоминает `install-codex.sh`, `/landing-go`, prototype-first flow, команды `/landing-photos` и `/landing-visuals` |

## Связанные концепты
- [[landing-go]] — команда, корректность которой проверяет `test-landing-go.bats`
- [[landing-orchestrator]] — агент, на который должен ссылаться `/landing-go`
- [[landing-onboarding]] — скилл, актуальность которого проверяет `test-onboarding-update.bats`
- [[stage-gates]] — механизм gate-check, тестируемый на статус `n/a` в `test-gate-na-status.bats`

## Источник
- `tests/phase-prd/README.md`
- `tests/phase-prd/test-gate-na-status.bats`
- `tests/phase-prd/test-install-codex.bats`
- `tests/phase-prd/test-landing-go.bats`
- `tests/phase-prd/test-migration.bats`
- `tests/phase-prd/test-onboarding-update.bats`