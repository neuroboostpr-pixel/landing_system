---
type: test-group
name: api_validators
sources: ["tests/api_validators/"]
updated: 2026-05-18
---

# Тесты api_validators

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/api_validators/

# Pytest (если есть test_*.py)
pytest tests/api_validators/
```

## Файлы

- tests/api_validators/test_aggregate.py
- tests/api_validators/test_amocrm.py
- tests/api_validators/test_base.py
- tests/api_validators/test_beget_api.py
- tests/api_validators/test_beget_ssh.py
