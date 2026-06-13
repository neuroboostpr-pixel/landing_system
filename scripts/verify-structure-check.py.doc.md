---
type: script
name: verify-structure-check
language: python
sources: ["scripts/verify-structure-check.py"]
updated: 2026-05-18
---

# verify-structure-check.py

A2-гейт: поблочная сверка composed.html ↔ prototype.md действительно сделана.

Раньше гейт 07c проверял лишь НАЛИЧИЕ structure-check.md (type:file_exists) —
block-composer мог записать пустой файл и закрыть этап без реальной сверки.
Теперь требуется явный машинный вердикт.

Контракт structure-check.md (см. docs/standards/reference-driven-rules.md):
  - в конце файла строка `STRUCTURE_MATCH: PASS` (или `FAIL`);
  - PASS допустим только если нет нерешённых расхождений.

Exit: 0 — файл есть, вердикт PASS, есть содержательная сверка (таблица/строки);
      1 — файла нет / пустой / вердикт FAIL / вердикт отсутствует.

Usage: verify-structure-check.py <project-dir>

## Источник

- `scripts/verify-structure-check.py`
