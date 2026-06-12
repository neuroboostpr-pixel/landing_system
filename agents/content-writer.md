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

**CRITICAL (2026-06-01):** I MUST READ FILES, NOT INVENT CONTENT!

See: [`docs/standards/stage-07-content-correct-flow.md`](../standards/stage-07-content-correct-flow.md)

### Step 1: CHECK PREREQUISITES (MUST READ FILES)

```python
import yaml
import os

# ✅ ACTUALLY OPEN AND READ THE FILE:
prototype_yaml_path = f"{project}/07_ПРОТОТИП/prototype.yaml"
if not os.path.exists(prototype_yaml_path):
    FAIL("prototype.yaml not found. Run /landing-prototype first")

with open(prototype_yaml_path) as f:
    prototype = yaml.safe_load(f)  # ← ACTUALLY READ & PARSE

prototype_md_path = f"{project}/07_ПРОТОТИП/prototype.md"
prototype_md_content = ""
if os.path.exists(prototype_md_path):
    with open(prototype_md_path) as f:
        prototype_md_content = f.read()  # ← FALLBACK SOURCE
```

### Step 2: EXTRACT CONTENT (FROM ACTUAL FILES)

**❌ WRONG:** "The Skills You Need" (invented)  
**✅ CORRECT:** Extract ONLY from `prototype['sections'][...]['blocks'][...]['text']`

```python
extracted_sections = []

for section in prototype['sections']:
    section_name = section['name']  # ← FROM YAML
    section_blocks = []
    
    for block in section['blocks']:
        block_label = block.get('label', block.get('type', 'Unknown'))
        
        # TRY TO EXTRACT TEXT IN THIS ORDER:
        block_text = None
        
        if 'text' in block:
            block_text = block['text']  # ← PRIMARY
        elif 'title' in block:
            block_text = block['title']
        elif 'description' in block:
            block_text = block['description']
        elif 'label' in block:
            block_text = block['label']
        
        # FALLBACK: If no text in YAML, search prototype.md
        if not block_text and prototype_md_content:
            # GREP for this block in markdown:
            import re
            pattern = rf"### {re.escape(block_label)}.*?(?=###|##|$)"
            match = re.search(pattern, prototype_md_content, re.DOTALL)
            if match:
                block_text = match.group(0)
        
        # If STILL no text found, WARN (don't invent):
        if not block_text:
            warnings.append(f"No text found for block '{block_label}' in section '{section_name}'")
            block_text = f"[TEXT NOT FOUND IN PROTOTYPE]"  # ← MARK AS MISSING, DON'T INVENT
        
        section_blocks.append({
            'label': block_label,
            'text': block_text
        })
    
    extracted_sections.append({
        'name': section_name,
        'blocks': section_blocks
    })
```

### Step 3: WRITE content.md (ONLY REAL TEXT)

**Structure:**
```markdown
## Section Name (from prototype['sections'][i]['name'])

### Block Label (from block['label'])
Block text (from block['text'] or block['description'] or block['title'])
← MUST BE FROM YAML, NOT INVENTED
```

### Step 4: VALIDATE (NO INVENTION ALLOWED)

```python
def validate_extraction(content_md_path):
    with open(content_md_path) as f:
        content = f.read().lower()
    
    # ❌ FAIL if contains template patterns:
    bad_patterns = [
        "lorem ipsum",
        "description goes here",
        "add your text",
        "your text here",
        "sample text",
        "[placeholder]"
    ]
    
    for pattern in bad_patterns:
        if pattern in content:
            return FAIL(f"Found template pattern: '{pattern}' - content was INVENTED, not extracted!")
    
    # ✅ PASS:
    return PASS("All content extracted from REAL prototype")
```

### Step 5: CREATE extraction-log.md

Document EXACTLY what was extracted:
- Sections extracted (count)
- Blocks extracted (count)
- Any warnings (missing text, fallbacks)
- Validation result

### Step 6: HARD GATE

Don't approve stage 07 until gate-check passes ALL hard-checks:
- ✅ content_md_exists
- ✅ content_no_lorem (no template patterns)
- ✅ content_sections_match
- ✅ extraction_log_passed

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

**Правило:** каждая секция = H2, каждый блок в секции = H3. Это позволяет `landing-compose` автоматически индексировать по структуре.

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
