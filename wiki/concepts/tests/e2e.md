---
type: rule
name: e2e-tests
sources: ["tests/e2e/README.md", "tests/e2e/test-skip-prevention.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["stage-gates", "landing-orchestrator"]
tags: ["testing", "bats", "e2e", "gate-check"]
---

# E2E-тесты: защита от пропуска этапов

## Что делает
Группа end-to-end тестов, которая проверяет, что система не позволяет перепрыгнуть через этапы — например, запустить деплой без утверждённой сборки. Тесты запускаются через `bats` (Bash Automated Testing System).

## Когда вызывать / в каком этапе
Запускаются вручную или в CI перед коммитом, особенно при изменениях в `scripts/gate-check.sh`, `.landing-state.yaml`, `landing-orchestrator` или любых HARD GATE проверках. Не привязаны к конкретному этапу pipeline — это сквозная защита всей цепочки.

```bash
# Запуск bats-тестов
bats tests/e2e/

# Запуск pytest (если появятся Python-тесты)
pytest tests/e2e/
```

## Что на вход / на выход

**Вход:**
- Временная структура проекта (`$BATS_TEST_TMPDIR/skip-prevention`) с каталогами `00_БРИФ`, `05_ДИЗАЙН-СИСТЕМА`, `07_КОНТЕНТ`, `08_КОД/wp-theme`
- Скопированный `template/.landing-state.yaml` (все этапы НЕ утверждены)
- Переменная окружения `GATE_AUTO=1`

**Выход:**
- Статус 0 (все тесты прошли) или ненулевой статус с описанием падения
- Проверяются два сценария:
  1. **08_build** отказывает, если этапы 02–07 не утверждены
  2. **09_deploy** отказывает, если 08_build не утверждён

## Связанные концепты
- [[stage-gates]] — правила HARD GATE, которые тесты верифицируют
- [[landing-orchestrator]] — агент, который вызывает `gate-check.sh` в реальном pipeline

## Источник
- `tests/e2e/README.md`
- `tests/e2e/test-skip-prevention.bats`