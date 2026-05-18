---
type: test-group
name: phase-prd
sources: ["tests/phase-prd/"]
updated: 2026-05-18
---

# Тесты phase-prd

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-prd/

# Pytest (если есть test_*.py)
pytest tests/phase-prd/
```

## Файлы

- tests/phase-prd/test-gate-na-status.bats
- tests/phase-prd/test-install-codex.bats
- tests/phase-prd/test-landing-go.bats
- tests/phase-prd/test-migration.bats
- tests/phase-prd/test-onboarding-update.bats

