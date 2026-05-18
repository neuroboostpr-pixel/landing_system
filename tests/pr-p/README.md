---
type: test-group
name: pr-p
sources: ["tests/pr-p/"]
updated: 2026-05-18
---

# Тесты pr-p

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-p/

# Pytest (если есть test_*.py)
pytest tests/pr-p/
```

## Файлы

- tests/pr-p/test_build_patterns_library.bats
- tests/pr-p/test_extract_patterns.bats
- tests/pr-p/test_premium_checklist_extended.bats

