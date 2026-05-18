---
type: test-group
name: pr-i-a
sources: ["tests/pr-i-a/"]
updated: 2026-05-18
---

# Тесты pr-i-a

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-i-a/

# Pytest (если есть test_*.py)
pytest tests/pr-i-a/
```

## Файлы

- tests/pr-i-a/test_codex_caches.bats
- tests/pr-i-a/test_interactive_slot_fill.bats
- tests/pr-i-a/test_no_placeholders.bats
- tests/pr-i-a/test_photo_ratio_validates.bats

