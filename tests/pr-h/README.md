---
type: test-group
name: pr-h
sources: ["tests/pr-h/"]
updated: 2026-05-18
---

# Тесты pr-h

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-h/

# Pytest (если есть test_*.py)
pytest tests/pr-h/
```

## Файлы

- tests/pr-h/test_fail_cta.bats
- tests/pr-h/test_fail_order.bats
- tests/pr-h/test_fail_title.bats
- tests/pr-h/test_pass.bats

