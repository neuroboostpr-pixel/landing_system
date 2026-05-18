---
type: test-group
name: e2e
sources: ["tests/e2e/"]
updated: 2026-05-18
---

# Тесты e2e

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/e2e/

# Pytest (если есть test_*.py)
pytest tests/e2e/
```

## Файлы

- tests/e2e/test-skip-prevention.bats

