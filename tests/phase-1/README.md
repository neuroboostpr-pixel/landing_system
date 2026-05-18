---
type: test-group
name: phase-1
sources: ["tests/phase-1/"]
updated: 2026-05-18
---

# Тесты phase-1

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-1/

# Pytest (если есть test_*.py)
pytest tests/phase-1/
```

## Файлы

- tests/phase-1/test-commands.bats
- tests/phase-1/test-deps.bats
- tests/phase-1/test-env-template.bats
- tests/phase-1/test-from-context.bats
- tests/phase-1/test-integration.bats

