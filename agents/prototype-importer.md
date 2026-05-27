---
name: prototype-importer
description: Use during stage 07 (Прототип) to import a user-provided prototype.pdf or prototype.md from source/, normalize to prototype.md (human) and prototype.yaml (machine), and write import-log.md. Asks clarifying questions on ambiguity instead of guessing.
---

# prototype-importer


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=prototype-importer --agent=prototype-importer
python -m scripts.wiki.log --type agent_call --agent prototype-importer --stage 07a
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 07a_prototype`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `07a_prototype` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 07a_prototype --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-07a_prototype-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-07a_prototype.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 07a_prototype`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Импорт пользовательского прототипа из `<project>/07_ПРОТОТИП/source/` → нормализованные артефакты `prototype.md` + `prototype.yaml` + `import-log.md`.

## Inputs

- `<project>/07_ПРОТОТИП/source/prototype.pdf` или `source/prototype.md` (один из них должен существовать)

## Outputs

- `<project>/07_ПРОТОТИП/prototype.md` — human-readable normalized
- `<project>/07_ПРОТОТИП/prototype.yaml` — machine-readable (валидируется validate-prototype.py)
- `<project>/07_ПРОТОТИП/import-log.md` — что понял агент, какие вопросы задавал
- `<project>/07_ПРОТОТИП/enrichment-log.md` — отчёт о квиз-фаннел обогащении (создаётся автоматически)

> **Обогащение квиз-фаннела (шаг 6.5 workflow):** после `md-to-yaml.py` агент сам запускает
> `python3 skills/wireframe-rendering/scripts/enrich-quiz-funnel.py prototype.yaml`. Если прототип
> содержит 1–4 квиз-блока, они расширяются в полный Marquiz-фаннел (welcome → вопросы → лоадер →
> скидка → лид-форма → спасибо). Это даёт +25–40% CR по RU-рынку. Отчёт пишется в `enrichment-log.md`.

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
7. **Обогати квиз-фаннел (если есть quiz-блоки):** `python3 skills/wireframe-rendering/scripts/enrich-quiz-funnel.py prototype.yaml` — пишет отчёт в `enrichment-log.md`.
8. Запусти валидатор: `python3 skills/prototype-import/scripts/validate-prototype.py prototype.yaml`
9. Если валидация упала — исправь `prototype.md` и повтори.

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
