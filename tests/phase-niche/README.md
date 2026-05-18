---
type: test-group
name: phase-niche
sources: ["tests/phase-niche/"]
updated: 2026-05-18
---

# Тесты phase-niche

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-niche/

# Pytest (если есть test_*.py)
pytest tests/phase-niche/
```

## Файлы

- tests/phase-niche/test-e2e-skip-prevention.bats
- tests/phase-niche/test-migrate-niche-to-v2.bats
- tests/phase-niche/test-niche-stage.bats
- tests/phase-niche/test-positioning-modes.bats
- tests/phase-niche/test-visual-rules.bats

