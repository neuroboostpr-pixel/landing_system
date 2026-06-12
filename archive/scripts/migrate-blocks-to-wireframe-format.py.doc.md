---
type: script
name: migrate-blocks-to-wireframe-format
language: python
sources: ["scripts/migrate-blocks-to-wireframe-format.py"]
updated: 2026-05-18
---

# migrate-blocks-to-wireframe-format.py

Конвертирует новые блоки (index.html + styles.css в корне) под старый
формат wireframe-rendering (assets/template.html + assets/template-mobile.html).

Не удаляет index.html/styles.css — создаёт parallel assets/ структуру.

## Источник

- `scripts/migrate-blocks-to-wireframe-format.py`
