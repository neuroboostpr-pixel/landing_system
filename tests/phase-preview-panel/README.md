---
type: test-group
name: phase-preview-panel
sources: ["tests/phase-preview-panel/"]
updated: 2026-05-18
---

# Тесты phase-preview-panel

Тесты для PR этого направления (bats/pytest).

## Запуск

```bash
# Bats-тесты
bats tests/phase-preview-panel/

# Pytest (если есть test_*.py)
pytest tests/phase-preview-panel/
```

## Файлы

- tests/phase-preview-panel/test-export-palettes.bats
- tests/phase-preview-panel/test-generate-axes-filter.bats
- tests/phase-preview-panel/test-generate-palette-css.bats
- tests/phase-preview-panel/test-migrate-to-preview-panel.bats
- tests/phase-preview-panel/test-palette-schema.bats

