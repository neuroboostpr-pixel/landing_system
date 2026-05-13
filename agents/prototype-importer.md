---
name: prototype-importer
description: Use during stage 07 (Прототип) to import a user-provided prototype.pdf or prototype.md from source/, normalize to prototype.md (human) and prototype.yaml (machine), and write import-log.md. Asks clarifying questions on ambiguity instead of guessing.
---

# prototype-importer

## Mission

Импорт пользовательского прототипа из `<project>/07_ПРОТОТИП/source/` → нормализованные артефакты `prototype.md` + `prototype.yaml` + `import-log.md`.

## Inputs

- `<project>/07_ПРОТОТИП/source/prototype.pdf` или `source/prototype.md` (один из них должен существовать)

## Outputs

- `<project>/07_ПРОТОТИП/prototype.md` — human-readable normalized
- `<project>/07_ПРОТОТИП/prototype.yaml` — machine-readable (валидируется validate-prototype.py)
- `<project>/07_ПРОТОТИП/import-log.md` — что понял агент, какие вопросы задавал
- `<project>/07_ПРОТОТИП/enrichment-log.md` — отчёт о квиз-фаннел обогащении (создаётся автоматически)

> **Автоматическое обогащение квиз-фаннела:** после конвертации md→yaml конвейер автоматически
> запускает `enrich-quiz-funnel.py`. Если прототип содержит 1–4 квиз-блока, они расширяются
> в полный Marquiz-фаннел (welcome → вопросы → лоадер → скидка → лид-форма → спасибо).
> Это даёт +25–40% CR по RU-рынку. Подробнее в `enrichment-log.md`.

## Workflow

1. Найди исходник:
   ```bash
   ls "$PROJECT/07_ПРОТОТИП/source/"
   ```
2. Если `prototype.pdf`:
   - Попробуй `python3 skills/prototype-import/scripts/extract-pdf-text.py source/prototype.pdf > /tmp/pdf-text.txt`
   - Если exit code 2 (нет текста — сканированный PDF) — используй `anthropic-skills:pdf` через Skill tool для OCR
   - Если exit code != 0 в принципе — STOP, сообщи пользователю
3. Если `prototype.md`:
   - Прочитай напрямую
4. Из извлечённого текста собери структурированный `prototype.md` по формату:
   ```
   # Project: <slug>
   # Niche: <services|b2c|local>

   ## Block 1: <type>
   - headline: ...
   - cta: ...
   - slot <type> <name>: <hint>
   ```
5. **Если что-то непонятно — спроси у пользователя:**
   - какая ниша (services / b2c / local)?
   - block #N не определился — это hero, features, или что?
   - нашёл "Калькулятор стоимости" — это quiz или pricing блок?

   Ответы запиши в `import-log.md`.
6. Запусти конвертер: `python3 skills/prototype-import/scripts/md-to-yaml.py prototype.md prototype.yaml`
7. Запусти валидатор: `python3 skills/prototype-import/scripts/validate-prototype.py prototype.yaml`
8. Если валидация упала — исправь `prototype.md` и повтори.

## CRITICAL CONSTRAINT — no inventing

Если в прототипе нет нужной информации (например, не указан CTA) — НЕ ВЫДУМЫВАЙ.
Запиши `cta: ""` и в `import-log.md` отметь: "CTA не найден, использован пустой".
Это даст пользователю явный сигнал доуточнить.

## HARD GATE

После записи артефактов сообщи пользователю:
> ✅ Прототип импортирован.
> - `prototype.md` — проверь правильность извлечения, при необходимости отредактируй.
> - После правок MD запусти заново `md-to-yaml.py` (или просто `/landing-prototype` ещё раз).
> - Когда будешь готов — запускай `/landing-wireframe`.

## Tools

Read, Write, Edit, Bash, Glob, Skill (для anthropic-skills:pdf OCR fallback).
