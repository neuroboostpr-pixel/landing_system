---
type: test-group
name: phase-prb
sources: ["tests/phase-prb/"]
updated: 2026-05-18
---

# Тесты phase-prb

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-prb/

# Pytest (если есть test_*.py)
pytest tests/phase-prb/
```

## Файлы

- tests/phase-prb/test-agents-frontmatter.bats
- tests/phase-prb/test-codex-wrappers.bats
- tests/phase-prb/test-landing-photos-gate.bats
- tests/phase-prb/test-template-07c.bats

