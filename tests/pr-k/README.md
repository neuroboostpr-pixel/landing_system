---
type: test-group
name: pr-k
sources: ["tests/pr-k/"]
updated: 2026-05-18
---

# Тесты pr-k

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-k/

# Pytest (если есть test_*.py)
pytest tests/pr-k/
```

## Файлы

- tests/pr-k/test_classify_caches.bats
- tests/pr-k/test_hero_no_crop.bats
- tests/pr-k/test_match_greedy.bats

