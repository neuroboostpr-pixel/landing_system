---
type: test-group
name: pr-j
sources: ["tests/pr-j/"]
updated: 2026-05-18
---

# Тесты pr-j

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-j/

# Pytest (если есть test_*.py)
pytest tests/pr-j/
```

## Файлы

- tests/pr-j/test_revert_on_violation.bats
- tests/pr-j/test_threshold_per_type.bats
- tests/pr-j/test_verify_identity.bats

