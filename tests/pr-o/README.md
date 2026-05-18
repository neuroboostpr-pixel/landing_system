---
type: test-group
name: pr-o
sources: ["tests/pr-o/"]
updated: 2026-05-18
---

# Тесты pr-o

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-o/

# Pytest (если есть test_*.py)
pytest tests/pr-o/
```

## Файлы

- tests/pr-o/test_block_generation_skips_existing.bats
- tests/pr-o/test_screenshot_works.bats
- tests/pr-o/test_structure_parse_works.bats

