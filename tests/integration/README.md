---
type: test-group
name: integration
sources: ["tests/integration/"]
updated: 2026-05-18
---

# Тесты integration

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/integration/

# Pytest (если есть test_*.py)
pytest tests/integration/
```

## Файлы

- tests/integration/test_landing_style_gate.bats

