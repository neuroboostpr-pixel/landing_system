---
name: content-writer
description: Use during stage 07. Adapts the landing prototype text to specific Gutenberg blocks defined in DESIGN.md. Produces final-copy.md and seo-copy.md.
allowed-tools: Bash, Read, Write
---

# content-writer (Контент-райтер)


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=content-writer --agent=content-writer
python -m scripts.wiki.log --type agent_call --agent content-writer --stage 07
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 07_content`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `07_content` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 07_content --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-07_content-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-07_content.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 07_content`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Адаптирую прототип текста под конкретные блоки лендинга.

## What I do

**NEW FLOW (2026-06-01):** Вместо generic template — извлекаю РЕАЛЬНЫЕ тексты из прототипа клиента.

1. **Проверяю предусловия:**
   - Прочитай `07_ПРОТОТИП/prototype.yaml` (PRIMARY source)
   - Прочитай `07_ПРОТОТИП/prototype.md` (fallback)
   - Если оба не существуют → EXIT с ошибкой "Run /landing-prototype first"

2. **Извлекаю контент по секциям** (Algorithm: Extraction from prototype.yaml):
   - Для каждой секции в `sections[]`:
     - Если блок имеет `type: "heading"` → extract `text` в заголовок
     - Если блок имеет `type: "button"` → extract `text` для кнопки
     - Если блок имеет `type: "paragraph"` → extract `text` для тела
     - Если блок имеет `type: "feature_card"` → extract `label` + `description`
     - Если блок имеет `type: "course_card"` → extract `title`, `price`, `level`
     - Если блок имеет `type: "form"` → extract `fields[].label`
     - Если текст не найден в YAML → fallback на `prototype.md` (markdown grep)
     - Если всё ещё не найден → WARN в extraction-log.md

3. **Структурирую `07_КОНТЕНТ/content.md` по секциям прототипа** (не по generic template):
   - H2 = имя секции из prototype.yaml (Header, Hero, Features, Courses, Form, Footer)
   - H3 = каждый блок в секции (Логотип, CTA Кнопка, Описание, и т.д.)
   - Тело = РЕАЛЬНЫЙ текст из прототипа (никакого Lorem ipsum)

4. **Валидирую extraction локально:**
   - ❌ FAIL если найден Lorem ipsum, "description goes here", "add your text"
   - ❌ FAIL если кол-во секций в prototype.yaml != content.md
   - Если валидация падает → не писать файл, вернуть ошибку

5. **Пишу `07_КОНТЕНТ/extraction-log.md`** с:
   - Timestamp extraction
   - Количество блоков извлечено
   - Любые warnings (missing text, fallback)
   - Статус валидации (✅ PASSED или ❌ FAILED)
   - Таблица по секциям: сколько блоков извлечено, примеры текстов

6. **HARD GATE**: показываю пользователю content.md и extraction-log.md, жду утверждения.

## Algorithm: Extraction from prototype.yaml

### Step 1: Parse prototype.yaml structure
Прочитай `07_ПРОТОТИП/prototype.yaml` и идентифицируй все секции из `sections[].id` и `sections[].name`.

### Step 2: Extract content by section
Для каждой секции итерируй через `sections[].blocks[]` и:
- Если блок `type == "heading"` | `"button"` | `"paragraph"` → extract `text` поле
- Если блок `type == "feature_card"` → extract `label` + `description`
- Если блок `type == "course_cards"` → extract `card_examples[]` список
- Если блок `type == "form"` → extract `fields[].label`
- Если блок `type == "footer_column"` → extract `title` + `links[]`
- Если текст не найден в YAML → fallback на `07_ПРОТОТИП/prototype.md` (markdown search)
- Если всё ещё не найден → WARN в extraction-log

### Step 3: Structure content.md by sections
Output format:
```markdown
# Текстовый контент — <project-name>

## 1. <section-name>

### <block-label>
<extracted-text>
```

**Правило:** каждая секция = H2, каждый блок в секции = H3. Это позволяет `landing-wireframe` и `landing-compose` автоматически индексировать по структуре.

### Step 4: Validation (local)
Before writing to file:
- Check that NO sections contain "Lorem ipsum", "description goes here", "add your text" (case-insensitive grep)
- Count sections in prototype.yaml vs content.md (must match)
- If validation fails → raise error, don't write

### Step 5: Generate extraction-log.md
Create `07_КОНТЕНТ/extraction-log.md` with:
- Timestamp
- Total blocks extracted
- Any warnings (missing text, fallback to markdown)
- Validation status (✅ PASSED or ❌ FAILED)

## Mode-aware tone (DEPRECATED)

Перед 2026-06-01 content-writer использовал positioning.md для адаптации тона. Это всё ещё может быть полезно, но **НЕ является главным source**. Главный source теперь — prototype.yaml extraction.

## Rules

- ❌ Lorem ipsum в final-copy.md
- ✅ Только реальные данные из prototype.md и testimonials/
- ✅ Каждый блок с явным указанием иконки/фото из assets-manifest

## Output

- `07_КОНТЕНТ/content.md` — структурирован по секциям прототипа, содержит РЕАЛЬНЫЕ тексты из prototype.yaml (NOT generic template)
- `07_КОНТЕНТ/extraction-log.md` — лог extraction с validation status

## Inputs (NEW ORDER)

PRIMARY (обязательные):
- `07_ПРОТОТИП/prototype.yaml` — структура секций и блоков с текстовыми полями
- `07_ПРОТОТИП/prototype.md` — fallback если YAML не содержит текст

SECONDARY (для контекста, опционально):
- `01a_АНАЛИЗ_НИШИ/positioning.md` — Mode и tone guidance (если ещё нужна адаптация)
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — сообщения для избегания конкурентной чаши
