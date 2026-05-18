---
type: test-group
name: preflight
sources: ["tests/preflight/"]
updated: 2026-05-18
---

# Тесты preflight

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/preflight/

# Pytest (если есть test_*.py)
pytest tests/preflight/
```

## Файлы

- tests/preflight/test_preflight_lazy_blocks.bats

