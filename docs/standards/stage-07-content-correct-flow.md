# Stage 07_content — CORRECT WORKFLOW

**Date:** 2026-06-01  
**Status:** CRITICAL DOCUMENTATION  
**For:** Landing system agents (content-writer, wireframe-composer, etc.)

---

## The Problem

**Before 2026-06-01:** Agents (content-writer, wireframe-composer) were INVENTING content instead of READING from actual files.

Example of WRONG behavior:
```
content-writer agent:
  ❌ Invents generic texts like "Lorem ipsum", "The Skills You Need", "60+ Online Courses"
  ❌ Doesn't read 07_ПРОТОТИП/prototype.yaml
  ❌ Doesn't read 07_ПРОТОТИП/prototype.md
  ❌ Doesn't read 07_КОНТЕНТ/content.md
```

Example of incident (neurokreator project):
- prototype.docx contained: **REAL course about AI-visual** (НЕЙРОКРЕАТОР)
- content.md generated: **MADE-UP content about learning platform** (60+ Online Courses, etc.)
- wireframe.html showed: **FAKE content** instead of real prototype

---

## The Correct Workflow (MANDATORY)

### Step 1: Agent READS prototype.yaml (NOT INVENTS)

```python
# content-writer agent MUST DO THIS:

with open(f"{project}/07_ПРОТОТИП/prototype.yaml") as f:
    prototype = yaml.safe_load(f)  # ← ACTUALLY READ THE FILE

# Extract from prototype ONLY (no invention):
for section in prototype['sections']:
    section_name = section['name']  # ← USE REAL NAME
    for block in section['blocks']:
        if 'text' in block:
            extracted_text = block['text']  # ← USE REAL TEXT
        elif 'description' in block:
            extracted_text = block['description']  # ← USE REAL DESC
        elif 'title' in block:
            extracted_text = block['title']  # ← USE REAL TITLE

# If text missing in YAML → fallback to prototype.md (also READ, not INVENT):
if not extracted_text:
    with open(f"{project}/07_ПРОТОТИП/prototype.md") as f:
        markdown_content = f.read()
        extracted_text = find_in_markdown(section_name, block_label)  # ← GREP, not INVENT
```

### Step 2: Agent WRITES content.md (ONLY from real sources)

```markdown
# content.md (REAL content only!)

## 1. Section Name (from prototype.yaml section['name'])

### Block Label (from block['label'])
Real text extracted from block['text'] or block['description']
← NOT INVENTED, EXTRACTED FROM FILE
```

**VALIDATION:**
```bash
# Must NOT contain:
❌ "Lorem ipsum"
❌ "description goes here"
❌ "add your text"
❌ "sample text"
❌ Generic "Learn More", "Add to Cart", "Get Started"

# Must contain:
✅ Real text from prototype.yaml
✅ Real headings from prototype.md
✅ Real course/product descriptions
✅ Real target audience segments
```

### Step 3: wireframe-composer READS content.md (NOT INVENTS)

```javascript
// wireframe.html generation (CORRECT):

const fs = require('fs');
const yaml = require('yaml');

// READ THE ACTUAL FILES:
const content_md = fs.readFileSync('07_КОНТЕНТ/content.md', 'utf8');
const prototype_yaml = yaml.parse(fs.readFileSync('07_ПРОТОТИП/prototype.yaml', 'utf8'));

// Extract section by section:
for (const section of prototype_yaml.sections) {
  const section_name = section.name;
  
  // FIND this section in content.md (using regex, grep, or parsing):
  const section_content = content_md.match(
    new RegExp(`## .*${section_name}.*[\\s\\S]*?(?=##|$)`)
  )[0];
  
  // Use REAL content in HTML:
  html += `<h2>${section_name}</h2>`;
  html += `<p>${section_content}</p>`;  // ← REAL content from content.md
}
```

**VALIDATION in wireframe.html:**
```bash
# Must NOT contain:
❌ Generic text like "60+ Online Courses"
❌ Made-up descriptions
❌ Placeholder content

# Must contain:
✅ Real headings from content.md
✅ Real descriptions extracted from content.md
✅ Real block labels and texts
✅ Real course/product names
```

### Step 4: HARD GATE validation

```bash
# scripts/validate-content-extraction.py

# Check 1: content.md exists and is NOT empty
if not os.path.getsize('07_КОНТЕНТ/content.md') > 100:
  FAIL  # "content.md is empty or too small - agent invented nothing"

# Check 2: content.md has real text (NO template patterns)
if grep -i "lorem\|description goes here\|add your text" content.md:
  FAIL  # "content.md contains invented template text"

# Check 3: content.md sections match prototype.yaml sections
yaml_sections = count(prototype.yaml sections[])
md_sections = count(content.md "## " headers)
if yaml_sections != md_sections:
  FAIL  # "Section count mismatch - agent invented sections"

# Check 4: content.md is NOT generic
if grep -c "Learn More\|Add to Cart\|Get Started" content.md > threshold:
  WARN  # "Too many generic CTAs - possibly invented"
```

---

## Real Example: neurokreator Project

### ✅ CORRECT (2026-06-01 fixed):

**prototype.yaml (from prototype.docx):**
```yaml
sections:
  - id: "hero"
    blocks:
      - type: "heading"
        text: "НЕЙРОКРЕАТОР"  # ← REAL
      - type: "paragraph"
        text: "Научитесь создавать визуальный контент с ИИ..."  # ← REAL
```

**content.md (extracted from prototype.yaml):**
```markdown
## Hero Section

### Main Heading
НЕЙРОКРЕАТОР

### Description
Научитесь создавать визуальный контент с ИИ...
```

**wireframe.html (from content.md):**
```html
<h1>НЕЙРОКРЕАТОР</h1>
<p>Научитесь создавать визуальный контент с ИИ...</p>
```

### ❌ WRONG (before 2026-06-01):

**prototype.yaml (actual: ИИ-визуал курс)**
```yaml
sections:
  - id: "hero"
    blocks:
      - type: "heading"
        text: "НЕЙРОКРЕАТОР"
```

**content.md (agent INVENTED):**
```markdown
## Hero Section

### Main Heading
The Skills You Need, The Success You Deserve  ← FAKE!

### Description
Join thousands of professionals mastering new skills...  ← FAKE!
```

**wireframe.html (from invented content):**
```html
<h1>The Skills You Need, The Success You Deserve</h1>
<p>Join thousands of professionals...</p>  ← WRONG CONTENT!
```

---

## Implementation Checklist

### For content-writer agent:

- [ ] **Read** `07_ПРОТОТИП/prototype.yaml` ← REQUIRED FILE
- [ ] **Parse** sections and blocks from YAML
- [ ] **Extract** text from block fields: `text`, `title`, `label`, `description`
- [ ] **Fallback** to `07_ПРОТОТИП/prototype.md` if YAML text missing
- [ ] **Write** `07_КОНТЕНТ/content.md` with REAL extracted text
- [ ] **Validate** that content.md has NO Lorem ipsum
- [ ] **Create** `07_КОНТЕНТ/extraction-log.md` with extraction summary
- [ ] **Validate** section count: `len(prototype.yaml.sections) == len(content.md.headers)`

### For wireframe-composer agent:

- [ ] **Read** `07_КОНТЕНТ/content.md` ← REQUIRED FILE
- [ ] **Parse** sections and blocks from markdown
- [ ] **Extract** real heading and description for each section
- [ ] **Generate** wireframe.html using REAL content (not invented)
- [ ] **Validate** that wireframe.html shows content from content.md
- [ ] **Test** that generic patterns are MINIMAL (not many "Learn More", "Get Started")

### For landing orchestrator:

- [ ] **Gate-check** before stage 07 completion:
  ```bash
  bash scripts/gate-check.sh --stage 07_content --project <project>
  ```
- [ ] **Pass** all hard-checks:
  - content_md_exists
  - content_no_lorem (no template patterns)
  - content_sections_match (section count match)
  - extraction_log_exists
  - extraction_log_passed

---

## Key Rules (NO EXCEPTIONS)

1. **NO INVENTION**: Agent must read files, never invent content
2. **SOURCE PRIORITY**: prototype.yaml (primary) → prototype.md (fallback) → FAIL if not found
3. **VALIDATION**: Every stage validates that content is REAL (gate-check + extraction-log)
4. **TRACEABILITY**: extraction-log.md documents which sections/blocks were extracted
5. **GATE-CHECK**: Stage 07 does NOT complete if content.md contains Lorem or generic templates

---

## What Went Wrong (neurokreator incident)

| Step | What Happened | Why Wrong | What Should Happen |
|------|---------------|----------|-------------------|
| 1. prototype.docx | REAL course about AI-visual | (OK) | (OK) |
| 2. prototype-importer | Parsed to prototype.yaml | (OK) | (OK) |
| 3. content-writer | **INVENTED** fake content | ❌ Didn't read prototype.yaml | **MUST READ** prototype.yaml |
| 4. wireframe-composer | **GENERATED** fake wireframe | ❌ Didn't read content.md | **MUST READ** content.md |
| 5. Result | Wrong lendingpage content | ❌ Entirely invented | ✅ Should show real course |

---

## Testing the Workflow

```bash
# Test that content-writer reads files correctly:
./test-content-extraction.bats

# Verify content.md has real text:
bash scripts/gate-check.sh --stage 07_content --project neurokreator

# Check wireframe shows real content:
grep "НЕЙРОКРЕАТОР" 07a_WIREFRAME/wireframe.html  # Should find REAL heading
grep "60+ Online Course" 07a_WIREFRAME/wireframe.html  # Should NOT find (fake)
```

---

## Summary

**Agent responsibility:** READ files, EXTRACT real text, NEVER INVENT.

**gate-check responsibility:** VALIDATE that content.md is real (no Lorem, no generic templates).

**wireframe responsibility:** DISPLAY content.md text in HTML, not invented content.

This ensures the landing page shows the **client's real content**, not agent hallucinations.
