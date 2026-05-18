---
type: test-group
name: phase-prc
sources: ["tests/phase-prc/"]
updated: 2026-05-18
---

# Тесты phase-prc

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-prc/

# Pytest (если есть test_*.py)
pytest tests/phase-prc/
```

## Файлы

- tests/phase-prc/test-agents-frontmatter.bats
- tests/phase-prc/test-codex-wrappers.bats
- tests/phase-prc/test-landing-visuals-gate.bats
- tests/phase-prc/test-new-blocks.bats
- tests/phase-prc/test-template-07d.bats

