---
type: script
name: verify_photo_pipeline
language: python
sources: ["scripts/verify_photo_pipeline.py"]
updated: 2026-05-18
---

# verify_photo_pipeline.py

Verify photo pipeline для hard_check.

Проверяет:
- Все <img src> в composed.html ведут на 07c_PHOTOS/processed/
- Нет SVG placeholder'ов
- Размеры файлов соответствуют атрибутам width/height в HTML
- manifest.json существует
- HARD GATE PR-K: hero-bg не должен обрезаться — ratio файла должен совпадать
  с ratio слота из meta.yaml в пределах 5%.

Exit 0 — OK, exit 1 — issues, exit 2 — files missing.

## Источник

- `scripts/verify_photo_pipeline.py`
