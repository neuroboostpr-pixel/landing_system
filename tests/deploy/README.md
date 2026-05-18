---
type: test-group
name: deploy
sources: ["tests/deploy/"]
updated: 2026-05-18
---

# Тесты deploy

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/deploy/

# Pytest (если есть test_*.py)
pytest tests/deploy/
```

## Файлы

- tests/deploy/test_deploy_lazy_blocks.bats

