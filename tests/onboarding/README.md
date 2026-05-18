---
type: test-group
name: onboarding
sources: ["tests/onboarding/"]
updated: 2026-05-18
---

# Тесты onboarding

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/onboarding/

# Pytest (если есть test_*.py)
pytest tests/onboarding/
```

## Файлы

- tests/onboarding/test-setup-flag.bats
- tests/onboarding/test-validate-all.bats
- tests/onboarding/test-wizard.bats

