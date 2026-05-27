---
name: prototype-import
description: Import user-provided prototype (PDF or MD) at stage 07 — parse, normalize to prototype.md (human) and prototype.yaml (machine). Used by /landing-prototype command and prototype-importer agent.
---

# prototype-import

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill prototype-import --stage 07a
```

Импорт пользовательского прототипа.

## Сценарий

1. Пользователь кладёт `prototype.pdf` или `prototype.md` в `<project>/07_ПРОТОТИП/source/`.
2. `/landing-prototype` запускает агента `prototype-importer`.
3. Агент использует скрипты:
   - `scripts/extract-pdf-text.py <input.pdf>` — извлечь текст (с OCR fallback через `anthropic-skills:pdf`)
   - `scripts/md-to-yaml.py <prototype.md>` — конвертировать структурированный MD в YAML
   - `scripts/validate-prototype.py <prototype.yaml>` — проверить схему
4. Пишет `prototype.md` + `prototype.yaml` + `import-log.md`.

## Schema

Полная schema — `scripts/validate-prototype.py`. Кратко:
- `project`: slug, niche (services|b2c|local), source_file
- `blocks[]`: position (unique int), type (hero|features|...), headline, subhead, cta, slots, items, mobile_notes
