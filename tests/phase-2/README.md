---
type: test-group
name: phase-2
sources: ["tests/phase-2/"]
updated: 2026-05-18
---

# Тесты phase-2

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-2/

# Pytest (если есть test_*.py)
pytest tests/phase-2/
```

## Файлы

- tests/phase-2/test-agents-frontmatter.bats
- tests/phase-2/test-commands-phase2.bats
- tests/phase-2/test-deps.bats
- tests/phase-2/test-orchestrator-phase2.bats

