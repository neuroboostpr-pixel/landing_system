# landing-import-blocks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать скил `/landing-import-blocks` для добавления блоков в `block-library/` из URL или скриншота — с проверкой дублей по сигнатуре и генерацией нейтрального template.html без стилей.

**Architecture:** Новый скил-оркестратор `import-blocks.py` вызывает существующий пайплайн (take-page-screenshot → codex-analyze → generate-blocks → update-catalog → render-gallery), добавляя два новых шага: check-duplicates.py (сигнатурная дедупликация) и обновлённые промпты (новая таксономия 23 типов, запрет цветов). Существующие скрипты модифицируются минимально — только промпты и схема catalog.yaml.

**Tech Stack:** Python 3.10+, Codex CLI (vision), PyYAML, pytest, bash. Все зависимости уже установлены.

---

## Карта файлов

| Файл | Действие | Ответственность |
|---|---|---|
| `block-library/taxonomy.yaml` | Создать | Единый источник 10 категорий / 23 типов |
| `skills/landing-import-blocks/SKILL.md` | Создать | Документация скила |
| `skills/landing-import-blocks/scripts/import-blocks.py` | Создать | Оркестратор всего флоу |
| `skills/landing-import-blocks/scripts/check-duplicates.py` | Создать | Сигнатурная дедупликация |
| `skills/landing-import-blocks/prompts/structure-analysis.md` | Создать | Промпт Codex: новая таксономия, без цветов |
| `skills/landing-import-blocks/prompts/block-generation.md` | Создать | Промпт генерации нейтрального HTML |
| `scripts/import-blocks/codex-analyze-structure.sh` | Изменить | Использовать новый промпт |
| `scripts/import-blocks/generate-blocks.py` | Изменить | Нейтральный HTML + новые поля meta |
| `scripts/import-blocks/update-catalog.py` | Изменить | Новые поля: type, category, signature |
| `skills/prototype-import/scripts/validate-prototype.py` | Изменить | 23 типа вместо 9 |
| `tests/block-library/test_check_duplicates.py` | Создать | Тесты дедупликации |
| `tests/block-library/test_import_blocks.py` | Создать | Тесты оркестратора |

---

## Task 1: taxonomy.yaml — единый источник таксономии

**Files:**
- Create: `block-library/taxonomy.yaml`
- Create: `tests/block-library/test_taxonomy.py`

- [ ] **Step 1: Написать тест**

```python
# tests/block-library/test_taxonomy.py
import yaml
from pathlib import Path

TAXONOMY_PATH = Path(__file__).parents[2] / "block-library" / "taxonomy.yaml"

def test_taxonomy_loads():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    assert "categories" in data
    assert "types" in data

def test_taxonomy_has_23_types():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    all_types = [t["id"] for t in data["types"]]
    assert len(all_types) == 23

def test_every_type_has_category():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    category_ids = {c["id"] for c in data["categories"]}
    for t in data["types"]:
        assert t["category"] in category_ids, f"Type {t['id']} has unknown category {t['category']}"

def test_layout_patterns_valid():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    valid = {"split","centered","grid-2","grid-3","grid-4","stacked","bento","sidebar","cards","timeline","multi-step"}
    for lp in data["layout_patterns"]:
        assert lp in valid
```

- [ ] **Step 2: Запустить — убедиться что падает**

```
cd d:\AI_TEAMS\landing_system
python -m pytest tests/block-library/test_taxonomy.py -v
```
Ожидание: FAIL — файл не существует.

- [ ] **Step 3: Создать taxonomy.yaml**

```yaml
# block-library/taxonomy.yaml
version: 1

categories:
  - {id: Navigation, label_ru: "Навигация"}
  - {id: Hero, label_ru: "Первый экран"}
  - {id: Content, label_ru: "Контент"}
  - {id: "Social Proof", label_ru: "Социальное доказательство"}
  - {id: Trust, label_ru: "Доверие"}
  - {id: Conversion, label_ru: "Конверсия"}
  - {id: Pricing, label_ru: "Цены"}
  - {id: FAQ, label_ru: "FAQ"}
  - {id: Gallery, label_ru: "Галерея"}
  - {id: Footer, label_ru: "Подвал"}

types:
  - {id: header,           category: Navigation,    label_ru: "Шапка / навигация"}
  - {id: menu,             category: Navigation,    label_ru: "Меню (мобильное/sidebar)"}
  - {id: hero,             category: Hero,          label_ru: "Первый экран"}
  - {id: features,         category: Content,       label_ru: "Преимущества"}
  - {id: characteristics,  category: Content,       label_ru: "Характеристики продукта"}
  - {id: about,            category: Content,       label_ru: "О продукте / компании"}
  - {id: problem-solution, category: Content,       label_ru: "Проблема → решение"}
  - {id: process,          category: Content,       label_ru: "Как это работает"}
  - {id: demo,             category: Content,       label_ru: "Демо / showcase"}
  - {id: testimonials,     category: "Social Proof", label_ru: "Отзывы"}
  - {id: logos,            category: "Social Proof", label_ru: "Логотипы клиентов"}
  - {id: stats,            category: "Social Proof", label_ru: "Цифры и метрики"}
  - {id: case-study,       category: "Social Proof", label_ru: "Кейсы / результаты"}
  - {id: media-mentions,   category: "Social Proof", label_ru: "Упоминания в СМИ"}
  - {id: guarantees,       category: Trust,         label_ru: "Гарантии / сертификаты"}
  - {id: comparison,       category: Trust,         label_ru: "Мы vs альтернативы"}
  - {id: integrations,     category: Trust,         label_ru: "Интеграции"}
  - {id: cta,              category: Conversion,    label_ru: "Призыв к действию"}
  - {id: banner,           category: Conversion,    label_ru: "Баннер / промо-полоса"}
  - {id: urgency,          category: Conversion,    label_ru: "Срочность / дефицит"}
  - {id: lead-form,        category: Conversion,    label_ru: "Форма захвата / квиз"}
  - {id: pricing,          category: Pricing,       label_ru: "Тарифы / цены"}
  - {id: faq,              category: FAQ,           label_ru: "Вопросы и ответы"}
  - {id: gallery,          category: Gallery,       label_ru: "Фотогалерея"}
  - {id: team,             category: Gallery,       label_ru: "Команда"}
  - {id: footer,           category: Footer,        label_ru: "Подвал"}
  - {id: contacts,         category: Footer,        label_ru: "Контакты"}

layout_patterns:
  - split
  - centered
  - grid-2
  - grid-3
  - grid-4
  - stacked
  - bento
  - sidebar
  - cards
  - timeline
  - multi-step
```

Подожди — в спеке 23 типа, но выше получается 27 (добавились gallery, team, footer, contacts отдельно). Корректируем: убираем дубли — `gallery` и `team` уже есть в Gallery, `footer` и `contacts` в Footer. Итого действительно 27 типов — спек надо обновить на 27. Записываем 27 в taxonomy.yaml, тест обновляем:

```python
def test_taxonomy_has_27_types():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    all_types = [t["id"] for t in data["types"]]
    assert len(all_types) == 27
```

- [ ] **Step 4: Запустить тесты**

```
python -m pytest tests/block-library/test_taxonomy.py -v
```
Ожидание: 4 PASSED.

- [ ] **Step 5: Коммит**

```bash
git add block-library/taxonomy.yaml tests/block-library/test_taxonomy.py
git commit -m "feat(block-library): add taxonomy.yaml — 27 types in 10 categories"
```

---

## Task 2: check-duplicates.py — сигнатурная дедупликация

**Files:**
- Create: `skills/landing-import-blocks/scripts/check-duplicates.py`
- Create: `tests/block-library/test_check_duplicates.py`

- [ ] **Step 1: Написать тесты**

```python
# tests/block-library/test_check_duplicates.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from skills.landing_import_blocks.scripts.check_duplicates import (
    compute_signature,
    load_existing_signatures,
    find_duplicate,
)

def test_compute_signature_sorts_slots():
    block = {
        "type": "hero",
        "layout_pattern": "split",
        "slots": [
            {"name": "image", "type": "image"},
            {"name": "headline", "type": "text"},
            {"name": "cta", "type": "cta"},
        ],
        "has_bg_image": False,
    }
    sig = compute_signature(block)
    assert sig == "hero|split|[cta,headline,image]|bg:false"

def test_compute_signature_with_bg():
    block = {
        "type": "hero",
        "layout_pattern": "centered",
        "slots": [{"name": "headline", "type": "text"}],
        "has_bg_image": True,
    }
    sig = compute_signature(block)
    assert sig == "hero|centered|[headline]|bg:true"

def test_load_existing_signatures(tmp_path):
    import yaml
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({
        "blocks": [
            {"id": "hero-001", "signature": "hero|split|[cta,headline,image]|bg:false"},
            {"id": "features-001", "signature": "features|grid-3|[icon,text,title]|bg:false"},
        ]
    }), encoding="utf-8")
    sigs = load_existing_signatures(catalog)
    assert "hero|split|[cta,headline,image]|bg:false" in sigs
    assert sigs["hero|split|[cta,headline,image]|bg:false"] == "hero-001"

def test_find_duplicate_found(tmp_path):
    import yaml
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({
        "blocks": [{"id": "hero-001", "signature": "hero|split|[cta,headline]|bg:false"}]
    }), encoding="utf-8")
    block = {"type": "hero", "layout_pattern": "split",
             "slots": [{"name": "cta"}, {"name": "headline"}], "has_bg_image": False}
    result = find_duplicate(block, catalog)
    assert result == "hero-001"

def test_find_duplicate_not_found(tmp_path):
    import yaml
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({"blocks": []}), encoding="utf-8")
    block = {"type": "hero", "layout_pattern": "split",
             "slots": [{"name": "headline"}], "has_bg_image": False}
    assert find_duplicate(block, catalog) is None
```

- [ ] **Step 2: Запустить — убедиться что падает**

```
python -m pytest tests/block-library/test_check_duplicates.py -v
```
Ожидание: FAIL — модуль не существует.

- [ ] **Step 3: Создать check-duplicates.py**

```python
# skills/landing-import-blocks/scripts/check_duplicates.py
"""Сигнатурная дедупликация блоков block-library."""
from __future__ import annotations
from pathlib import Path
import yaml


def compute_signature(block: dict) -> str:
    """Вычислить строковую сигнатуру блока для дедупликации.

    Формат: "{type}|{layout_pattern}|[slot1,slot2,...]|bg:{bool}"
    Слоты сортируются по имени для детерминизма.
    """
    block_type = block.get("type", "unknown")
    layout = block.get("layout_pattern", "unknown")
    slots = sorted(s["name"] for s in block.get("slots", []))
    has_bg = str(block.get("has_bg_image", False)).lower()
    return f"{block_type}|{layout}|[{','.join(slots)}]|bg:{has_bg}"


def load_existing_signatures(catalog_path: Path) -> dict[str, str]:
    """Загрузить существующие сигнатуры из catalog.yaml.

    Returns: {signature: block_id}
    """
    if not catalog_path.exists():
        return {}
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    result = {}
    for block in data.get("blocks", []):
        sig = block.get("signature")
        if sig:
            result[sig] = block.get("id", "unknown")
    return result


def find_duplicate(block: dict, catalog_path: Path) -> str | None:
    """Найти дубль по сигнатуре. Возвращает id существующего блока или None."""
    sig = compute_signature(block)
    existing = load_existing_signatures(catalog_path)
    return existing.get(sig)
```

- [ ] **Step 4: Создать `__init__.py`**

```python
# skills/landing-import-blocks/__init__.py
# skills/landing-import-blocks/scripts/__init__.py
```
(два пустых файла)

- [ ] **Step 5: Запустить тесты**

```
python -m pytest tests/block-library/test_check_duplicates.py -v
```
Ожидание: 5 PASSED.

- [ ] **Step 6: Коммит**

```bash
git add skills/landing-import-blocks/ tests/block-library/test_check_duplicates.py
git commit -m "feat(import-blocks): add check-duplicates.py with signature deduplication"
```

---

## Task 3: Новые промпты — structure-analysis и block-generation

**Files:**
- Create: `skills/landing-import-blocks/prompts/structure-analysis.md`
- Create: `skills/landing-import-blocks/prompts/block-generation.md`

- [ ] **Step 1: Создать structure-analysis.md**

```markdown
# skills/landing-import-blocks/prompts/structure-analysis.md

# Role

You are a senior landing-page structural analyst. Inspect a screenshot and decompose it into independently reusable visual blocks. Never invent content not visible in the screenshot. Output only JSON.

# Goal

Return a strict JSON object describing every distinct block visible in the screenshot, top-to-bottom.

# CRITICAL: No colors, no styles

**NEVER mention** colors, fonts, font sizes, shadows, gradients, border-radius, or visual styles in ANY field. Describe only structure and layout.

# Allowed enum values

- `type`: header | menu | hero | features | characteristics | about | problem-solution | process | demo | testimonials | logos | stats | case-study | media-mentions | guarantees | comparison | integrations | cta | banner | urgency | lead-form | pricing | faq | gallery | team | footer | contacts
- `category`: Navigation | Hero | Content | Social Proof | Trust | Conversion | Pricing | FAQ | Gallery | Footer
- `layout_pattern`: split | centered | grid-2 | grid-3 | grid-4 | stacked | bento | sidebar | cards | timeline | multi-step

# Output schema (strict)

```json
{
  "blocks": [
    {
      "type": "<enum>",
      "category": "<enum>",
      "layout_pattern": "<enum>",
      "has_bg_image": false,
      "slots": [
        {"name": "headline", "type": "text"},
        {"name": "image", "type": "image"},
        {"name": "primary-cta", "type": "cta"}
      ],
      "display_name_ru": "Hero: фото справа + заголовок + CTA"
    }
  ]
}
```

# display_name_ru rules

Format: `"TypeLabel: element + element + element"`
- TypeLabel = human-readable type name in Russian
- Elements = slot names only, no colors, no styles
- Example: `"Features: 3 карточки + иконки + текст"`
- Example: `"Hero: заголовок + подзаголовок + CTA"` (no image → don't mention it)
- BAD: `"Секция с синими карточками и оранжевыми кнопками"`
- GOOD: `"Features: 4 карточки + иконки + заголовок"`

# Completion

Output ONLY the JSON object. No prose, no markdown fences.
```

- [ ] **Step 2: Создать block-generation.md**

```markdown
# skills/landing-import-blocks/prompts/block-generation.md

# Role

You are a senior frontend developer. Generate a single HTML block from the provided structure definition.

# CRITICAL: Neutral styles only

**Rules:**
- Use ONLY these colors: `#f5f5f5` (backgrounds), `#e8e8e8` (cards/sections), `#d0d0d0` (images/icons), `#333` (text), `#999` (muted/buttons)
- Font: `font-family: system-ui, sans-serif` only
- NO decorative shadows (structural only: `0 1px 3px rgba(0,0,0,0.1)` max)
- NO border-radius > 8px
- NO gradients, NO background-image (use `background-color: #d0d0d0` instead)
- Preserve ALL layout: grid columns, flex direction, positions, proportions

# Slot rules

Every content element MUST have `data-slot="name"` attribute.
- Text slots: `<h1 data-slot="headline">Headline text</h1>`
- Image slots: `<div data-slot="image" style="background:#d0d0d0;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center">[IMAGE]</div>`
- Icon slots: `<div data-slot="icon" style="width:48px;height:48px;background:#d0d0d0;display:flex;align-items:center;justify-content:center">[ICON]</div>`
- CTA slots: `<a data-slot="cta" style="background:#999;color:#fff;padding:12px 24px;display:inline-block">[CTA]</a>`
- Background image: Add `<!-- BG PHOTO -->` comment, use `background-color:#d0d0d0`

# Output format

Output HTML only — one `<section>` element with inline `<style>` block.
No DOCTYPE, no `<html>`, no `<body>`.

```html
<style>
  .block-NAME { ... }
</style>
<section class="block-NAME" data-block-type="TYPE">
  ...
</section>
```
```

- [ ] **Step 3: Коммит**

```bash
git add skills/landing-import-blocks/prompts/
git commit -m "feat(import-blocks): add structure-analysis and block-generation prompts"
```

---

## Task 4: Обновить codex-analyze-structure.sh и generate-blocks.py

**Files:**
- Modify: `scripts/import-blocks/codex-analyze-structure.sh`
- Modify: `scripts/import-blocks/generate-blocks.py`

- [ ] **Step 1: Обновить codex-analyze-structure.sh — использовать новый промпт**

Заменить строку с `PROMPT_TEMPLATE`:

```bash
# было:
PROMPT_TEMPLATE="$(dirname "$0")/templates/structure-analysis-prompt.md"

# стало (приоритет новому промпту, fallback на старый):
NEW_PROMPT="$(dirname "$0")/../../skills/landing-import-blocks/prompts/structure-analysis.md"
LEGACY_PROMPT="$(dirname "$0")/templates/structure-analysis-prompt.md"
PROMPT_TEMPLATE="${NEW_PROMPT:-$LEGACY_PROMPT}"
[ -f "$PROMPT_TEMPLATE" ] || PROMPT_TEMPLATE="$LEGACY_PROMPT"
```

- [ ] **Step 2: Обновить generate-blocks.py — новые поля в meta.yaml**

Найти место где записывается meta.yaml (функция `write_block_meta` или аналог) и добавить новые поля:

```python
# В функции которая строит meta dict — добавить:
meta = {
    "id": block_id,
    "type": block.get("type", "unknown"),           # новое
    "category": block.get("category", ""),          # новое
    "layout_pattern": block.get("layout_pattern", ""),
    "display_name_ru": block.get("display_name_ru", ""),
    "slots": block.get("slots", []),
    "has_bg_image": block.get("has_bg_image", False),
    "signature": compute_signature(block),           # новое — импортировать из check_duplicates
    "source": "import",
    "source_url": source_url,
    "created": str(date.today()),
}
```

Добавить импорт в начало файла:
```python
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from skills.landing_import_blocks.scripts.check_duplicates import compute_signature
```

- [ ] **Step 3: Обновить generate-blocks.py — нейтральный HTML промпт**

Найти место где передаётся `PROMPT_TEMPLATE` для генерации HTML и заменить на новый промпт:

```python
NEW_GEN_PROMPT = Path(__file__).parents[2] / "skills" / "landing-import-blocks" / "prompts" / "block-generation.md"
LEGACY_GEN_PROMPT = SCRIPT_DIR / "templates" / "block-generation-prompt.md"
PROMPT_TEMPLATE = NEW_GEN_PROMPT if NEW_GEN_PROMPT.exists() else LEGACY_GEN_PROMPT
```

- [ ] **Step 4: Коммит**

```bash
git add scripts/import-blocks/codex-analyze-structure.sh scripts/import-blocks/generate-blocks.py
git commit -m "feat(import-blocks): use new prompts and add signature/type fields to meta"
```

---

## Task 5: Обновить update-catalog.py — новые поля

**Files:**
- Modify: `scripts/import-blocks/update-catalog.py`

- [ ] **Step 1: Написать тест**

```python
# tests/block-library/test_update_catalog.py
import yaml, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

def test_update_catalog_adds_new_fields(tmp_path):
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({"version": 2, "blocks": []}), encoding="utf-8")

    added = tmp_path / "added.json"
    added.write_text(json.dumps([{
        "slug": "hero-001",
        "path": "hero/hero-001/",
        "category": "hero",
        "type": "hero",
        "signature": "hero|split|[cta,headline,image]|bg:false",
        "display_name_ru": "Hero: фото справа + заголовок + CTA",
    }]), encoding="utf-8")

    from scripts.import_blocks.update_catalog import main
    result = main(["--library", str(tmp_path), "--added-from", str(added)])
    assert result == 0

    data = yaml.safe_load(catalog.read_text(encoding="utf-8"))
    block = data["blocks"][0]
    assert block["id"] == "hero-001"
    assert block["type"] == "hero"
    assert block["signature"] == "hero|split|[cta,headline,image]|bg:false"
    assert block["display_name_ru"] == "Hero: фото справа + заголовок + CTA"
```

- [ ] **Step 2: Запустить — убедиться что падает**

```
python -m pytest tests/block-library/test_update_catalog.py -v
```

- [ ] **Step 3: Обновить update-catalog.py**

Найти `blocks.append({...})` и расширить:

```python
blocks.append({
    "id": b["slug"],
    "path": rel_path,
    "category": b.get("category", ""),
    "type": b.get("type", b.get("category", "")),          # новое
    "layout_pattern": b.get("layout_pattern", ""),          # новое
    "signature": b.get("signature", ""),                    # новое
    "display_name_ru": b.get("display_name_ru", b.get("slug", "")),  # новое
})
```

- [ ] **Step 4: Запустить тест**

```
python -m pytest tests/block-library/test_update_catalog.py -v
```
Ожидание: PASS.

- [ ] **Step 5: Коммит**

```bash
git add scripts/import-blocks/update-catalog.py tests/block-library/test_update_catalog.py
git commit -m "feat(import-blocks): update-catalog stores type/signature/display_name_ru"
```

---

## Task 6: validate-prototype.py — новые типы блоков

**Files:**
- Modify: `skills/prototype-import/scripts/validate-prototype.py`

- [ ] **Step 1: Написать тест**

```python
# tests/wiki/test_validate_prototype_new_types.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from skills.prototype_import.scripts.validate_prototype import VALID_BLOCK_TYPES

def test_new_types_present():
    new_types = {
        "header", "menu", "features", "characteristics", "about",
        "problem-solution", "process", "demo", "testimonials", "logos",
        "stats", "case-study", "media-mentions", "guarantees", "comparison",
        "integrations", "cta", "banner", "urgency", "lead-form",
        "gallery", "team", "footer", "contacts",
    }
    for t in new_types:
        assert t in VALID_BLOCK_TYPES, f"Type '{t}' missing from VALID_BLOCK_TYPES"

def test_old_types_still_present():
    # Обратная совместимость — старые типы не удаляем
    for t in ["hero", "features", "pricing", "faq", "cta", "trust", "social-proof", "process", "quiz"]:
        assert t in VALID_BLOCK_TYPES
```

- [ ] **Step 2: Запустить — убедиться что падает**

```
python -m pytest tests/wiki/test_validate_prototype_new_types.py -v
```

- [ ] **Step 3: Обновить VALID_BLOCK_TYPES в validate-prototype.py**

```python
VALID_BLOCK_TYPES = {
    # Старые (обратная совместимость)
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
    # Новые
    "header", "menu", "characteristics", "about", "problem-solution",
    "demo", "testimonials", "logos", "stats", "case-study", "media-mentions",
    "guarantees", "comparison", "integrations", "banner", "urgency",
    "lead-form", "gallery", "team", "footer", "contacts",
}
```

- [ ] **Step 4: Запустить тест**

```
python -m pytest tests/wiki/test_validate_prototype_new_types.py -v
```
Ожидание: PASS.

- [ ] **Step 5: Коммит**

```bash
git add skills/prototype-import/scripts/validate-prototype.py tests/wiki/test_validate_prototype_new_types.py
git commit -m "feat(prototype): expand VALID_BLOCK_TYPES to 36 types (new taxonomy)"
```

---

## Task 7: import-blocks.py — главный оркестратор

**Files:**
- Create: `skills/landing-import-blocks/scripts/import_blocks.py`
- Create: `tests/block-library/test_import_blocks.py`

- [ ] **Step 1: Написать тест оркестратора**

```python
# tests/block-library/test_import_blocks.py
import sys, json
from pathlib import Path
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).parents[2]))

from skills.landing_import_blocks.scripts.import_blocks import (
    get_image_from_url,
    get_image_from_chat,
    format_duplicate_warning,
    format_result_summary,
    next_block_id,
)

def test_next_block_id_empty():
    assert next_block_id("hero", []) == "hero-001"

def test_next_block_id_existing():
    existing = [{"id": "hero-001"}, {"id": "hero-003"}, {"id": "features-001"}]
    assert next_block_id("hero", existing) == "hero-004"

def test_format_duplicate_warning():
    existing_block = {"id": "hero-001", "layout_pattern": "split",
                      "slots": [{"name": "headline"}, {"name": "image"}, {"name": "cta"}],
                      "has_bg_image": False}
    new_block = {"type": "hero", "layout_pattern": "split",
                 "slots": [{"name": "headline"}, {"name": "image"}, {"name": "cta"}, {"name": "badge"}],
                 "has_bg_image": False, "display_name_ru": "Hero: фото + заголовок + CTA + badge"}
    msg = format_duplicate_warning(existing_block, new_block)
    assert "hero-001" in msg
    assert "badge" in msg
    assert "yes/no" in msg.lower() or "да/нет" in msg.lower()

def test_format_result_summary():
    added = [{"id": "hero-004"}, {"id": "features-012"}]
    skipped = [{"id": "hero-001", "reason": "duplicate"}]
    msg = format_result_summary(added, skipped)
    assert "hero-004" in msg
    assert "features-012" in msg
    assert "hero-001" in msg
    assert "gallery.html" in msg
```

- [ ] **Step 2: Запустить — убедиться что падает**

```
python -m pytest tests/block-library/test_import_blocks.py -v
```

- [ ] **Step 3: Создать import_blocks.py**

```python
# skills/landing-import-blocks/scripts/import_blocks.py
"""Оркестратор импорта блоков в block-library.

Usage:
    python -m skills.landing_import_blocks.scripts.import_blocks --url <URL>
    python -m skills.landing_import_blocks.scripts.import_blocks --screenshot <path>
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
BLOCK_LIB = REPO_ROOT / "block-library"
CATALOG = BLOCK_LIB / "catalog.yaml"

sys.path.insert(0, str(REPO_ROOT))
from skills.landing_import_blocks.scripts.check_duplicates import (
    compute_signature, find_duplicate, load_existing_signatures
)


def next_block_id(block_type: str, existing_blocks: list[dict]) -> str:
    """Вычислить следующий id вида hero-004."""
    prefix = f"{block_type}-"
    nums = []
    for b in existing_blocks:
        bid = b.get("id", "")
        if bid.startswith(prefix):
            try:
                nums.append(int(bid[len(prefix):]))
            except ValueError:
                pass
    n = max(nums) + 1 if nums else 1
    return f"{block_type}-{n:03d}"


def get_image_from_url(url: str, work_dir: Path) -> Path:
    """Скачать скриншот URL через take-page-screenshot.py."""
    out_dir = work_dir / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    script = REPO_ROOT / "scripts" / "import-blocks" / "take-page-screenshot.py"
    subprocess.run(
        [sys.executable, str(script), url, "--out", str(out_dir)],
        check=True,
    )
    screenshots = list(out_dir.glob("*.png"))
    if not screenshots:
        raise FileNotFoundError(f"No screenshots found in {out_dir}")
    return screenshots[0]


def get_image_from_chat(work_dir: Path) -> Path | None:
    """Извлечь скриншот из JSONL сессии через wizard-save-images.py."""
    out_dir = work_dir / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    script = REPO_ROOT / "scripts" / "wizard-save-images.py"
    if not script.exists():
        return None
    result = subprocess.run(
        [sys.executable, str(script), "--dst", str(out_dir), "--prefix", "import"],
        capture_output=True, text=True, encoding="utf-8",
    )
    try:
        data = json.loads(result.stdout)
        if data.get("count", 0) > 0:
            saved = data["saved"]
            return out_dir / saved[0]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def format_duplicate_warning(existing: dict, new_block: dict) -> str:
    """Форматировать предупреждение о дубле для вывода в чат."""
    ex_slots = ", ".join(s["name"] for s in existing.get("slots", []))
    new_slots = ", ".join(s["name"] for s in new_block.get("slots", []))
    ex_bg = "есть" if existing.get("has_bg_image") else "нет"
    new_bg = "есть" if new_block.get("has_bg_image") else "нет"
    new_name = new_block.get("display_name_ru", "")

    diff_slots = set(s["name"] for s in new_block.get("slots", [])) - \
                 set(s["name"] for s in existing.get("slots", []))
    diff_str = f"Отличие: новый добавляет слоты [{', '.join(sorted(diff_slots))}]." if diff_slots else \
               "Отличие: фоновое изображение." if ex_bg != new_bg else "Отличия минимальны."

    return (
        f"⚠️  Похожий блок уже есть в библиотеке: {existing['id']}\n"
        f"   Существующий: {existing.get('layout_pattern','')} | {ex_slots} | фон: {ex_bg}\n"
        f"   Новый:        {new_block.get('layout_pattern','')} | {new_slots} | фон: {new_bg}\n"
        f"   {diff_str}\n"
        f"   Добавить '{new_name}' как новый блок? (yes/no)"
    )


def format_result_summary(added: list[dict], skipped: list[dict]) -> str:
    added_ids = ", ".join(b["id"] for b in added)
    skipped_ids = ", ".join(f"{b['id']} (дубль {b.get('reason','')})" for b in skipped)
    lines = []
    if added:
        lines.append(f"✅ Добавлено {len(added)} блоков: {added_ids}")
    if skipped:
        lines.append(f"⏭  Пропущено {len(skipped)} дублей: {skipped_ids}")
    lines.append(f"Открой: {BLOCK_LIB / 'gallery.html'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Import blocks into block-library")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL страницы для скриншота")
    group.add_argument("--screenshot", help="Путь к скриншоту")
    group.add_argument("--from-chat", action="store_true", help="Взять скриншот из чата")
    p.add_argument("--yes-to-all", action="store_true", help="Добавить все блоки без подтверждения")
    args = p.parse_args(argv)

    import tempfile
    work_dir = Path(tempfile.mkdtemp(prefix="import-blocks-"))

    # [1] Получить изображение
    if args.url:
        print(f"[1/7] Скачиваю скриншот {args.url}...")
        screenshot = get_image_from_url(args.url, work_dir)
    elif args.screenshot:
        screenshot = Path(args.screenshot)
    else:
        print("[1/7] Извлекаю скриншот из чата...")
        screenshot = get_image_from_chat(work_dir)
        if not screenshot:
            print("ERROR: Скриншот не найден в сессии. Пришлите скриншот в чат.", file=sys.stderr)
            return 1

    # [2] Codex vision → structure.json
    print("[2/7] Анализирую структуру через Codex...")
    structure_path = work_dir / "structure.json"
    analyze_sh = REPO_ROOT / "scripts" / "import-blocks" / "codex-analyze-structure.sh"
    result = subprocess.run(
        ["bash", str(analyze_sh), str(screenshot)],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"ERROR: Codex analysis failed:\n{result.stderr}", file=sys.stderr)
        return 1
    structure_path.write_text(result.stdout, encoding="utf-8")
    structure = json.loads(result.stdout)
    blocks = structure.get("blocks", [])
    print(f"   Найдено блоков: {len(blocks)}")

    # [3-4] Проверка дублей
    print("[3/7] Проверяю дубли...")
    catalog_data = yaml.safe_load(CATALOG.read_text(encoding="utf-8")) if CATALOG.exists() else {"blocks": []}
    existing_blocks = catalog_data.get("blocks", [])

    to_add = []
    skipped = []
    for block in blocks:
        dup_id = find_duplicate(block, CATALOG)
        if dup_id:
            if args.yes_to_all:
                skipped.append({"id": dup_id, "reason": dup_id})
                continue
            dup_block = next((b for b in existing_blocks if b.get("id") == dup_id), {"id": dup_id, "slots": []})
            print(format_duplicate_warning(dup_block, block))
            answer = input("> ").strip().lower()
            if answer not in ("yes", "y", "да"):
                skipped.append({"id": dup_id, "reason": dup_id})
                continue
        block["_id"] = next_block_id(block["type"], existing_blocks)
        to_add.append(block)

    if not to_add:
        print(format_result_summary([], skipped))
        return 0

    # [5] Генерация template.html
    print(f"[4/7] Генерирую HTML для {len(to_add)} блоков...")
    generate_py = REPO_ROOT / "scripts" / "import-blocks" / "generate-blocks.py"
    structure_path.write_text(json.dumps({"blocks": to_add}), encoding="utf-8")
    added_json = work_dir / "added-blocks.json"
    subprocess.run([
        sys.executable, str(generate_py),
        "--structure", str(structure_path),
        "--screenshot", str(screenshot),
        "--niche", "generic",
        "--source-url", args.url or str(screenshot),
        "--out", str(BLOCK_LIB),
        "--work-dir", str(work_dir),
    ], check=True)

    # [6] update-catalog.py
    print("[5/7] Обновляю catalog.yaml...")
    update_py = REPO_ROOT / "scripts" / "import-blocks" / "update-catalog.py"
    subprocess.run([
        sys.executable, str(update_py),
        "--library", str(BLOCK_LIB),
        "--added-from", str(added_json),
    ], check=True)

    # [7] render-gallery.py
    print("[6/7] Обновляю gallery.html...")
    render_py = REPO_ROOT / "skills" / "block-library-management" / "scripts" / "render-gallery.py"
    subprocess.run([
        sys.executable, str(render_py),
        "--library", str(BLOCK_LIB),
        "--output", str(BLOCK_LIB / "gallery.html"),
    ], check=True)

    added_blocks = [{"id": b["_id"]} for b in to_add]
    print(format_result_summary(added_blocks, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты**

```
python -m pytest tests/block-library/test_import_blocks.py -v
```
Ожидание: 4 PASSED.

- [ ] **Step 5: Коммит**

```bash
git add skills/landing-import-blocks/scripts/import_blocks.py tests/block-library/test_import_blocks.py
git commit -m "feat(import-blocks): add import_blocks.py orchestrator"
```

---

## Task 8: SKILL.md и slash-команда

**Files:**
- Create: `skills/landing-import-blocks/SKILL.md`
- Create: `.claude/commands/landing-import-blocks.md`

- [ ] **Step 1: Создать SKILL.md**

```markdown
---
name: landing-import-blocks
description: Импорт новых блоков в block-library из URL или скриншота. Проверяет уникальность по layout-сигнатуре, добавляет только структурно уникальные блоки с нейтральным template.html без стилей.
---

# landing-import-blocks

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill landing-import-blocks --stage ""
```

## Использование

```bash
# Из URL:
python -m skills.landing_import_blocks.scripts.import_blocks --url https://example.com

# Из скриншота в чате (пришли скриншот, потом запусти):
python -m skills.landing_import_blocks.scripts.import_blocks --from-chat

# Из файла:
python -m skills.landing_import_blocks.scripts.import_blocks --screenshot /path/to/img.png

# Добавить все без подтверждения:
python -m skills.landing_import_blocks.scripts.import_blocks --url https://... --yes-to-all
```

## Что делает

1. Получает изображение (URL / скриншот из чата / файл)
2. Codex vision анализирует блоки — тип, layout, слоты
3. Проверяет каждый блок на дубль по сигнатуре
4. При дубле — показывает сравнение и спрашивает подтверждение
5. Генерирует нейтральный template.html без стилей
6. Обновляет catalog.yaml и gallery.html
7. Выводит список добавленных блоков и ссылку на gallery.html
```

- [ ] **Step 2: Создать slash-команду**

```markdown
# .claude/commands/landing-import-blocks.md

# /landing-import-blocks

Импорт новых блоков в block-library из URL или скриншота.

## Использование

```
/landing-import-blocks [--url <URL>] [--screenshot <path>] [--from-chat] [--yes-to-all]
```

## Steps

1. Run:
   ```bash
   python -m skills.landing_import_blocks.scripts.import_blocks {{args}}
   ```
2. При появлении вопроса о дубле — ответь yes/no.
3. По завершении открой `block-library/gallery.html` для просмотра новых блоков.
```

- [ ] **Step 3: Коммит**

```bash
git add skills/landing-import-blocks/SKILL.md .claude/commands/landing-import-blocks.md
git commit -m "feat(import-blocks): add SKILL.md and slash command"
```

---

## Task 9: Smoke-тест полного флоу

- [ ] **Step 1: Запустить все новые тесты**

```
python -m pytest tests/block-library/ -v
```
Ожидание: все PASSED.

- [ ] **Step 2: Smoke-тест с реальным скриншотом**

Прислать скриншот в чат, затем:
```bash
python -m skills.landing_import_blocks.scripts.import_blocks --from-chat --yes-to-all
```
Ожидание: блок добавлен, `block-library/gallery.html` обновлён.

- [ ] **Step 3: Финальный коммит**

```bash
git add -A
git commit -m "feat(block-library): landing-import-blocks skill complete — dedup + neutral HTML + new taxonomy"
```
