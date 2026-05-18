---
type: test-group
name: phase-pre
sources: ["tests/phase-pre/"]
updated: 2026-05-18
---

# Тесты phase-pre

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-pre/

# Pytest (если есть test_*.py)
pytest tests/phase-pre/
```

## Файлы

- tests/phase-pre/test-landing-start.bats
- tests/phase-pre/test-migrate-readmes.bats
- tests/phase-pre/test-template-readmes.bats
- tests/phase-pre/test-wizard-agent.bats

