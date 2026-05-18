---
type: test-group
name: pr-m
sources: ["tests/pr-m/"]
updated: 2026-05-18
---

# Тесты pr-m

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-m/

# Pytest (если есть test_*.py)
pytest tests/pr-m/
```

## Файлы

- tests/pr-m/test_index_has_4_buttons.bats
- tests/pr-m/test_previews_generated.bats
- tests/pr-m/test_previews_have_iframes.bats

