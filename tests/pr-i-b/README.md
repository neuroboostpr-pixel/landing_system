---
type: test-group
name: pr-i-b
sources: ["tests/pr-i-b/"]
updated: 2026-05-18
---

# Тесты pr-i-b

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-i-b/

# Pytest (если есть test_*.py)
pytest tests/pr-i-b/
```

## Файлы

- tests/pr-i-b/test_apply_fix.bats
- tests/pr-i-b/test_review_parse.bats
- tests/pr-i-b/test_screenshots.bats

