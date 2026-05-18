---
type: test-group
name: gate-check
sources: ["tests/gate-check/"]
updated: 2026-05-18
---

# Тесты gate-check

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/gate-check/

# Pytest (если есть test_*.py)
pytest tests/gate-check/
```

## Файлы

- tests/gate-check/test-gate-check.bats
- tests/gate-check/test-gate-state.bats

