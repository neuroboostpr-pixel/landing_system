---
type: test-group
name: pr-g
sources: ["tests/pr-g/"]
updated: 2026-05-18
---

# Тесты pr-g

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-g/

# Pytest (если есть test_*.py)
pytest tests/pr-g/
```

## Файлы

- tests/pr-g/test_gate_check_updates_graph.bats
- tests/pr-g/test_post_commit_hook.bats
- tests/pr-g/test_stage_lock_hard.bats
- tests/pr-g/test_stage_lock_soft.bats

