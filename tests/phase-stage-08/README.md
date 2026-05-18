---
type: test-group
name: phase-stage-08
sources: ["tests/phase-stage-08/"]
updated: 2026-05-18
---

# Тесты phase-stage-08

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-stage-08/

# Pytest (если есть test_*.py)
pytest tests/phase-stage-08/
```

## Файлы

- tests/phase-stage-08/test-backport-legacy.bats
- tests/phase-stage-08/test-gate-check-stage-08.bats
- tests/phase-stage-08/test-generate-wp-blocks.bats
- tests/phase-stage-08/test-mark-legacy-projects.bats

