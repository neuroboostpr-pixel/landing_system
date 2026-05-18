---
type: script
name: verify_content_preserved
language: python
sources: ["scripts/verify_content_preserved.py"]
updated: 2026-05-18
---

# verify_content_preserved.py

Проверяет что текст из prototype.yaml присутствует в composed.html.

Exit codes:
  0 — все строки прототипа найдены, порядок блоков сохранён
  1 — есть расхождения (детали в stderr)
  2 — файл prototype.yaml или composed.html не найден

## Источник

- `scripts/verify_content_preserved.py`
