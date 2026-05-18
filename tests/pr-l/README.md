---
type: test-group
name: pr-l
sources: ["tests/pr-l/"]
updated: 2026-05-18
---

# Тесты pr-l

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/pr-l/

# Pytest (если есть test_*.py)
pytest tests/pr-l/
```

## Файлы

- tests/pr-l/test_final_check_fail.bats
- tests/pr-l/test_final_check_pass.bats
- tests/pr-l/test_report_file_created.bats

