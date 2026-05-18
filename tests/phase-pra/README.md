---
type: test-group
name: phase-pra
sources: ["tests/phase-pra/"]
updated: 2026-05-18
---

# Тесты phase-pra

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-pra/

# Pytest (если есть test_*.py)
pytest tests/phase-pra/
```

## Файлы

- tests/phase-pra/test-agents-exist.bats
- tests/phase-pra/test-compose-blocks.bats
- tests/phase-pra/test-design-md-sections.bats
- tests/phase-pra/test-enrich-quiz-funnel.bats
- tests/phase-pra/test-extract-pdf-text.bats

