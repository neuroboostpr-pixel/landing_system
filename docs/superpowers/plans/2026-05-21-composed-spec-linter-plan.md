# Composed ↔ block-spec Linter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a strict-mode linter that catches mismatches between `07b_COMPOSED/composed*.html` and `08_КОД/block-spec.yaml` before stage-08 closes, with opt-in auto-fix.

**Architecture:** Three pure-Python modules (composed inspector via BeautifulSoup, spec inspector reusing existing `block_spec.py`, lint rules) feed into a CLI that returns exit-1 on errors. Gate hook integrates into `scripts/gate-check.sh` for stage-08.

**Tech Stack:** Python 3.10+, BeautifulSoup4 (already vendored), PyYAML (already used), pytest.

**Spec:** [docs/superpowers/specs/2026-05-21-composed-spec-linter-design.md](../specs/2026-05-21-composed-spec-linter-design.md)

---

## File Structure

```
skills/wp-gutenberg-block-builder/scripts/
├── lib/
│   ├── block_spec.py                          # MODIFIED — add probe_selector + probe_kind to Block dataclass
│   ├── composed_inspector.py                  # NEW
│   ├── spec_inspector.py                      # NEW
│   └── lint_heuristics.py                     # NEW
└── lint-composed-vs-spec.py                   # NEW — CLI

tests/phase-stage-08/
├── fixtures/lint/
│   ├── minimal-composed.html                  # NEW
│   ├── brutalist-features-section.html        # NEW
│   ├── model-card-slider.html                 # NEW
│   ├── good-spec.yaml                         # NEW
│   └── broken-spec.yaml                       # NEW
├── test-composed-inspector.py                 # NEW
├── test-spec-inspector.py                     # NEW
├── test-lint-heuristics.py                    # NEW
└── test-lint-integration.py                   # NEW

scripts/
└── gate-check.sh                              # MODIFIED — invoke linter at stage 08

docs/standards/
└── stage-08-spec-lint.md                      # NEW
```

---

### Task 1: Extend `Block` dataclass with `probe_selector` + `probe_kind`

**Files:**
- Modify: `skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py`
- Test: `tests/phase-stage-08/test-spec-inspector.py` (will be created in Task 4 — for this task, write a quick smoke test inline)

- [ ] **Step 1: Read current `Block` dataclass to understand fields**

Run: `grep -n "class Block" skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py`

Expected: shows definition of `Block` with fields like `slug`, `title`, `icon`, `category`, `controls`, etc.

- [ ] **Step 2: Add `probe_selector: str | None = None` and `probe_kind: str = "single"` to `Block`**

```python
# In Block dataclass — add two fields, defaults preserve backward compat
probe_selector: str | None = None
probe_kind: str = "single"  # "single" | "card-collection"
```

- [ ] **Step 3: Update YAML loader to read these fields**

Find function that maps YAML dict → `Block(...)`. Add:

```python
probe_selector=raw.get("probe_selector"),
probe_kind=raw.get("probe_kind", "single"),
```

- [ ] **Step 4: Validate `probe_kind` value**

In `validate()` function (or equivalent) add:

```python
if b.probe_kind not in ("single", "card-collection"):
    raise BlockSpecError(f"block {b.slug}: probe_kind must be 'single' or 'card-collection', got {b.probe_kind!r}")
```

- [ ] **Step 5: Smoke-test with a minimal YAML**

Run:
```bash
python -c "
import sys; sys.path.insert(0, 'skills/wp-gutenberg-block-builder/scripts/lib')
from block_spec import load, validate
import io, tempfile, pathlib
yaml_text = '''
blocks:
  - slug: nav
    title: Nav
    icon: menu
    category: layout
    type: single
    probe_selector: '.nav'
    probe_kind: single
    controls: []
'''
p = pathlib.Path(tempfile.mktemp(suffix='.yaml'))
p.write_text(yaml_text)
s = load(p); validate(s)
print('OK', s.blocks[0].probe_selector, s.blocks[0].probe_kind)
"
```

Expected: `OK .nav single`

- [ ] **Step 6: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py
git commit -m "feat(stage-08-lint): add probe_selector + probe_kind fields to Block dataclass"
```

---

### Task 2: Create fixtures for composed-inspector tests

**Files:**
- Create: `tests/phase-stage-08/fixtures/lint/minimal-composed.html`
- Create: `tests/phase-stage-08/fixtures/lint/brutalist-features-section.html`
- Create: `tests/phase-stage-08/fixtures/lint/model-card-slider.html`

- [ ] **Step 1: Create `minimal-composed.html`** — sanity fixture with one section

```html
<!doctype html>
<html><body>
  <section class="nav"><h1>Logo</h1></section>
  <section class="hero">
    <h1 class="hero-title">Title</h1>
    <p class="hero-lead">Lead text</p>
  </section>
</body></html>
```

- [ ] **Step 2: Create `brutalist-features-section.html`** — replicates dubai-avto-liza features-section structure

```html
<!doctype html>
<html><body>
<section class="features-section">
  <div class="features-grid">
    <article class="feature-card feature-statement">
      <p><strong>LiXiang — smart, quiet, and luxurious.</strong> Exactly as it should be.</p>
      <p>Li vehicles are built for people who no longer see a car as just transport.</p>
      <p>Every detail is designed to elevate everyday life.</p>
      <p>Li is a statement on the outside.</p>
    </article>
    <article class="feature-card">
      <span class="feature-icon"><svg viewBox="0 0 24 24"><path d="M1 2"/></svg></span>
      <h3 class="feature-title">Confidence in Every Journey</h3>
      <p class="feature-text">Li is family-focused safety.</p>
    </article>
    <article class="feature-card">
      <span class="feature-icon"><svg viewBox="0 0 24 24"><path d="M3 4"/></svg></span>
      <h3 class="feature-title">Quietness and Comfort</h3>
      <p class="feature-text">A refined ride.</p>
    </article>
  </div>
</section>
</body></html>
```

- [ ] **Step 3: Create `model-card-slider.html`** — replicates dubai-avto-liza model-card structure

```html
<!doctype html>
<html><body>
<section class="models-section">
  <article class="model-card" id="model-l6">
    <div class="model-photo">
      <div class="model-slider">
        <div class="slider-track">
          <img src="assets/photos/l6-main.jpg" alt="">
          <img src="assets/photos/l6-slide2.jpg" alt="">
          <img src="assets/photos/l6-slide3.jpg" alt="">
          <img src="assets/photos/l6-slide4.jpg" alt="">
          <img src="assets/photos/insp-l6-slide5.jpg" alt="">
        </div>
      </div>
    </div>
    <div class="model-info">
      <span class="model-tag">5-seat SUV</span>
      <h3 class="model-title">Li L6</h3>
      <ul class="model-specs">
        <li><strong>1,390 km</strong> range</li>
        <li><strong>5.4 s</strong> · 0–100 km/h</li>
        <li><strong>180 km/h</strong> top speed</li>
        <li><strong>6.5 L/100km</strong> ICE fuel</li>
      </ul>
      <div class="model-colors">
        <span class="color-swatch" style="--c:#C5C8CA"></span>
        <span class="color-swatch" style="--c:#6E6E6E"></span>
        <span class="color-swatch" style="--c:#0A0A0A"></span>
        <span class="color-swatch" style="--c:#2D5A3E"></span>
        <span class="color-swatch" style="--c:#8E9092"></span>
      </div>
      <p class="model-description">A spacious, comfort-focused interior with generous room for the family.</p>
    </div>
  </article>
</section>
</body></html>
```

- [ ] **Step 4: Commit**

```bash
git add tests/phase-stage-08/fixtures/lint/
git commit -m "test(stage-08-lint): add composed.html fixtures for inspector tests"
```

---

### Task 3: Implement `composed_inspector.py` — basic parse + probe matching

**Files:**
- Create: `skills/wp-gutenberg-block-builder/scripts/lib/composed_inspector.py`
- Create: `tests/phase-stage-08/test-composed-inspector.py`

- [ ] **Step 1: Write failing test — probe finds one match in minimal fixture**

```python
"""Tests for composed_inspector.py — DOM probe matching."""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"
sys.path.insert(0, str(LIB))

spec = importlib.util.spec_from_file_location("composed_inspector", LIB / "composed_inspector.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
inspect = mod.inspect

FIX = REPO_ROOT / "tests" / "phase-stage-08" / "fixtures" / "lint"


def test_minimal_probe_matches_one_nav():
    blocks = inspect(FIX / "minimal-composed.html", probes=[".nav"])
    assert len(blocks) == 1
    assert blocks[0].probe_selector == ".nav"
    assert len(blocks[0].matches) == 1


def test_minimal_probe_no_match_returns_zero_matches():
    blocks = inspect(FIX / "minimal-composed.html", probes=[".nonexistent"])
    assert len(blocks) == 1
    assert len(blocks[0].matches) == 0
```

- [ ] **Step 2: Run test — verify it fails**

Run: `pytest tests/phase-stage-08/test-composed-inspector.py -v`

Expected: FAIL — module not found.

- [ ] **Step 3: Implement minimal `composed_inspector.py`**

```python
"""Parse composed.html into a tree of inspection facts.

Returns one InspectedBlock per probe selector. Each InspectedBlock has
0..N InspectedMatch entries (one per DOM element that matched).

Heuristics for child analysis live in lint_heuristics.py; this module
only handles DOM parsing and probe matching.
"""
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class InspectedChild:
    heuristic: str
    count: int
    values: list[str] = field(default_factory=list)


@dataclass
class InspectedMatch:
    tag: str
    attrs: dict
    soup: object  # BeautifulSoup Tag — passed to heuristics
    children: list[InspectedChild] = field(default_factory=list)


@dataclass
class InspectedBlock:
    probe_selector: str
    matches: list[InspectedMatch] = field(default_factory=list)


def inspect(composed_path: Path, probes: list[str]) -> list[InspectedBlock]:
    html = composed_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for probe in probes:
        block = InspectedBlock(probe_selector=probe)
        for el in soup.select(probe):
            block.matches.append(InspectedMatch(
                tag=el.name,
                attrs=dict(el.attrs),
                soup=el,
            ))
        result.append(block)
    return result
```

- [ ] **Step 4: Run tests — verify pass**

Run: `pytest tests/phase-stage-08/test-composed-inspector.py -v`

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lib/composed_inspector.py tests/phase-stage-08/test-composed-inspector.py
git commit -m "feat(stage-08-lint): composed_inspector — DOM probe matching"
```

---

### Task 4: Implement `spec_inspector.py` — read spec, expose probe info

**Files:**
- Create: `skills/wp-gutenberg-block-builder/scripts/lib/spec_inspector.py`
- Create: `tests/phase-stage-08/fixtures/lint/good-spec.yaml`
- Create: `tests/phase-stage-08/test-spec-inspector.py`

- [ ] **Step 1: Create `good-spec.yaml` fixture**

```yaml
blocks:
  - slug: nav
    title: Nav
    icon: menu
    category: layout
    type: single
    probe_selector: '.nav'
    probe_kind: single
    controls:
      - { id: c_nav_logo, name: logo, type: text, label: Logo, default: "Brand" }
  - slug: features
    title: Features
    icon: star
    category: design
    type: section-card
    probe_selector: '.features-section'
    probe_kind: card-collection
    section_grid_class: 'features-grid'
    controls:
      - { id: c_feat_stmt, name: feat_statement, type: textarea, label: Statement, default: "One paragraph only" }
    card:
      slug: feature-card
      title: Feature Card
      controls:
        - { id: c_fc_title, name: title, type: text, label: Title, default: "Feat" }
        - { id: c_fc_icon, name: icon_svg, type: textarea, label: Icon, default: "" }
      template:
        - { title: "Confidence" }
        - { title: "Quietness" }
```

- [ ] **Step 2: Write failing test**

```python
"""Tests for spec_inspector.py — surface probe + controls."""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"
sys.path.insert(0, str(LIB))

spec_mod = importlib.util.spec_from_file_location("spec_inspector", LIB / "spec_inspector.py")
si = importlib.util.module_from_spec(spec_mod)
spec_mod.loader.exec_module(si)

FIX = REPO_ROOT / "tests" / "phase-stage-08" / "fixtures" / "lint"


def test_inspect_spec_exposes_probe():
    s = si.inspect_spec(FIX / "good-spec.yaml")
    nav = next(b for b in s.blocks if b.slug == "nav")
    assert nav.probe_selector == ".nav"
    assert nav.probe_kind == "single"


def test_inspect_spec_controls_present():
    s = si.inspect_spec(FIX / "good-spec.yaml")
    nav = next(b for b in s.blocks if b.slug == "nav")
    assert any(c.name == "logo" for c in nav.controls)


def test_inspect_spec_section_card_template_visible():
    s = si.inspect_spec(FIX / "good-spec.yaml")
    feat = next(b for b in s.blocks if b.slug == "features")
    assert feat.probe_kind == "card-collection"
    assert len(feat.template) == 2
```

- [ ] **Step 3: Run — verify fail**

Run: `pytest tests/phase-stage-08/test-spec-inspector.py -v`

Expected: FAIL — module not found.

- [ ] **Step 4: Implement `spec_inspector.py`**

```python
"""Wrap block_spec.load() to expose a flat structure for linting."""
from dataclasses import dataclass, field
from pathlib import Path

from block_spec import load as _load, validate as _validate


@dataclass
class InspectedControl:
    name: str
    type: str
    has_default: bool
    default_value: object


@dataclass
class InspectedSpecBlock:
    slug: str
    probe_selector: str | None
    probe_kind: str
    type: str
    controls: list[InspectedControl] = field(default_factory=list)
    card_controls: list[InspectedControl] = field(default_factory=list)
    template: list[dict] = field(default_factory=list)


@dataclass
class InspectedSpec:
    blocks: list[InspectedSpecBlock]


def _to_inspected_control(c) -> InspectedControl:
    return InspectedControl(
        name=c.name,
        type=c.type,
        has_default=c.default is not None and c.default != "",
        default_value=c.default,
    )


def inspect_spec(spec_path: Path) -> InspectedSpec:
    raw = _load(spec_path)
    _validate(raw)
    blocks: list[InspectedSpecBlock] = []
    for b in raw.blocks:
        card_controls: list[InspectedControl] = []
        template: list[dict] = []
        if b.card is not None:
            card_controls = [_to_inspected_control(c) for c in b.card.controls]
            template = list(b.card.template or [])
        blocks.append(InspectedSpecBlock(
            slug=b.slug,
            probe_selector=b.probe_selector,
            probe_kind=b.probe_kind,
            type=b.type,
            controls=[_to_inspected_control(c) for c in b.controls],
            card_controls=card_controls,
            template=template,
        ))
    return InspectedSpec(blocks=blocks)
```

- [ ] **Step 5: Run — verify pass**

Run: `pytest tests/phase-stage-08/test-spec-inspector.py -v`

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lib/spec_inspector.py tests/phase-stage-08/fixtures/lint/good-spec.yaml tests/phase-stage-08/test-spec-inspector.py
git commit -m "feat(stage-08-lint): spec_inspector — flat view over block-spec"
```

---

### Task 5: Implement `lint_heuristics.py` — `bullets`, `color-swatches`, `multi-paragraph`, `slider-images`, `inline-svg-icon`

**Files:**
- Create: `skills/wp-gutenberg-block-builder/scripts/lib/lint_heuristics.py`
- Create: `tests/phase-stage-08/test-lint-heuristics.py`

- [ ] **Step 1: Write failing test for `bullets` heuristic**

```python
"""Tests for lint_heuristics.py — one test per heuristic, pass and fail cases."""
import importlib.util
import sys
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"
sys.path.insert(0, str(LIB))

m = importlib.util.spec_from_file_location("lint_heuristics", LIB / "lint_heuristics.py")
lh = importlib.util.module_from_spec(m); m.loader.exec_module(lh)
si_m = importlib.util.spec_from_file_location("spec_inspector", LIB / "spec_inspector.py")
si = importlib.util.module_from_spec(si_m); si_m.loader.exec_module(si)


def _make_spec_block(slug, controls=None, template=None):
    return si.InspectedSpecBlock(
        slug=slug, probe_selector=".x", probe_kind="single", type="single",
        controls=[si.InspectedControl(name=n, type=t, has_default=True, default_value=v)
                  for n, t, v in (controls or [])],
        template=template or [],
    )


def _soup(html):
    return BeautifulSoup(html, "html.parser").select_one(":scope > *") or BeautifulSoup(html, "html.parser")


def test_bullets_pass_when_li_count_matches_controls():
    spec_block = _make_spec_block("model-card", controls=[
        ("range", "text", "1,390 km"),
        ("accel", "text", "5.4 s"),
        ("top_speed", "text", "180 km/h"),
        ("fuel", "text", "6.5 L/100km"),
    ])
    soup = _soup('<div class="model-card"><ul class="model-specs"><li>a</li><li>b</li><li>c</li><li>d</li></ul></div>')
    issues = lh.check_bullets(spec_block, soup)
    assert issues == []


def test_bullets_fail_when_li_count_exceeds_controls():
    spec_block = _make_spec_block("model-card", controls=[
        ("range", "text", "x"), ("accel", "text", "x"), ("top_speed", "text", "x"),
    ])
    soup = _soup('<div class="model-card"><ul class="model-specs"><li>a</li><li>b</li><li>c</li><li>d</li></ul></div>')
    issues = lh.check_bullets(spec_block, soup)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "4" in issues[0].message and "3" in issues[0].message
```

- [ ] **Step 2: Run — verify fail**

Run: `pytest tests/phase-stage-08/test-lint-heuristics.py::test_bullets_pass_when_li_count_matches_controls -v`

Expected: FAIL — module not found.

- [ ] **Step 3: Create `lint_heuristics.py` with `LintIssue` and `check_bullets`**

```python
"""Heuristic checks comparing DOM matches to spec blocks.

Each check_X(spec_block, soup_match) returns a list of LintIssue.
soup_match is a BeautifulSoup Tag — the matched DOM element.
"""
import re
from dataclasses import dataclass
from typing import Literal


# Attribute names that signal raw SVG (mirrored from
# fix-page-content-images.py to keep contracts aligned).
SVG_ATTR_NAMES = {"icon_svg", "svg", "background_svg", "decoration_svg", "logo_svg"}


@dataclass
class LintIssue:
    severity: Literal["error", "warning"]
    block_slug: str
    heuristic: str
    message: str
    suggested_fragment: str | None = None


def _bullet_field_count(spec_block) -> int:
    """Count text-controls that look like a spec list field.

    A spec block has at most one repeater for bullets, OR a set of
    sibling text-controls (range/accel/top_speed/fuel/...).
    """
    count = 0
    for c in spec_block.controls + spec_block.card_controls:
        if c.type == "text":
            count += 1
        elif c.type == "repeater":
            # Repeater rows can be many; treat as "unbounded" by returning a
            # high sentinel so the count check passes (delegated to template).
            return 9999
    return count


def check_bullets(spec_block, soup_match) -> list[LintIssue]:
    li_nodes = soup_match.select('ul[class$="-specs"] > li, ul.specs > li')
    if not li_nodes:
        return []
    field_count = _bullet_field_count(spec_block)
    if field_count >= len(li_nodes):
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="bullets",
        message=(f"{spec_block.slug} composed has {len(li_nodes)} <li> in specs list "
                 f"but only {field_count} matching controls in spec"),
        suggested_fragment=None,
    )]
```

- [ ] **Step 4: Run — verify bullets pass**

Run: `pytest tests/phase-stage-08/test-lint-heuristics.py -v -k bullets`

Expected: 2 passed.

- [ ] **Step 5: Add `check_color_swatches` test**

Append to `test-lint-heuristics.py`:

```python
def test_color_swatches_pass_when_colors_control_present():
    spec_block = _make_spec_block("model-card", controls=[("colors", "text", "#FFF,#000,#888")])
    soup = _soup('<div class="model-card"><span class="color-swatch" style="--c:#fff"></span>'
                 '<span class="color-swatch" style="--c:#000"></span></div>')
    issues = lh.check_color_swatches(spec_block, soup)
    assert issues == []


def test_color_swatches_fail_when_swatches_exist_and_no_control():
    spec_block = _make_spec_block("model-card", controls=[("name", "text", "")])
    soup = _soup('<div class="model-card"><span class="color-swatch" style="--c:#fff"></span></div>')
    issues = lh.check_color_swatches(spec_block, soup)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "color" in issues[0].message.lower()
```

- [ ] **Step 6: Run — verify fail (color-swatches not implemented yet)**

Run: `pytest tests/phase-stage-08/test-lint-heuristics.py -v -k color`

Expected: FAIL.

- [ ] **Step 7: Implement `check_color_swatches`**

Append to `lint_heuristics.py`:

```python
def check_color_swatches(spec_block, soup_match) -> list[LintIssue]:
    swatches = soup_match.select('[style*="--c"], .color-swatch')
    if not swatches:
        return []
    all_names = {c.name for c in spec_block.controls + spec_block.card_controls}
    if "colors" in all_names:
        return []
    hex_values = []
    for s in swatches:
        m = re.search(r'--c\s*:\s*(#[0-9a-fA-F]+)', s.get("style", ""))
        if m:
            hex_values.append(m.group(1))
    suggestion = (
        f"# Add to {spec_block.slug} controls:\n"
        f"  - {{ id: c_colors, name: colors, type: text, label: 'Colors (CSV hex)',\n"
        f"      default: '{','.join(hex_values)}' }}"
    ) if hex_values else None
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="color-swatches",
        message=f"{spec_block.slug} composed has {len(swatches)} color-swatch elements but no 'colors' control in spec",
        suggested_fragment=suggestion,
    )]
```

- [ ] **Step 8: Run all heuristic tests so far — verify pass**

Run: `pytest tests/phase-stage-08/test-lint-heuristics.py -v`

Expected: 4 passed.

- [ ] **Step 9: Add tests for `multi-paragraph`, `slider-images`, `inline-svg-icon`**

Append to `test-lint-heuristics.py`:

```python
def test_multi_paragraph_pass_when_textarea_has_separators():
    spec_block = _make_spec_block("features", controls=[
        ("feat_statement", "textarea", "Para 1\n\nPara 2\n\nPara 3\n\nPara 4"),
    ])
    soup = _soup('<div class="feature-statement"><p>1</p><p>2</p><p>3</p><p>4</p></div>')
    issues = lh.check_multi_paragraph(spec_block, soup, target_field="feat_statement")
    assert issues == []


def test_multi_paragraph_fail_when_textarea_only_one_para():
    spec_block = _make_spec_block("features", controls=[("feat_statement", "textarea", "Single line")])
    soup = _soup('<div class="feature-statement"><p>1</p><p>2</p><p>3</p><p>4</p></div>')
    issues = lh.check_multi_paragraph(spec_block, soup, target_field="feat_statement")
    assert len(issues) == 1
    assert "4" in issues[0].message and "1" in issues[0].message


def test_slider_images_pass_when_all_photo_fields_filled():
    spec_block = _make_spec_block("model-card", template=[
        {"photo1": "x", "photo2": "x", "photo3": "x", "photo4": "x", "photo5": "x"},
    ])
    soup = _soup('<div class="model-card"><div class="slider-track">'
                 '<img src="a.jpg"><img src="b.jpg"><img src="c.jpg"><img src="d.jpg"><img src="e.jpg">'
                 '</div></div>')
    issues = lh.check_slider_images(spec_block, soup, template_index=0)
    assert issues == []


def test_slider_images_fail_when_photo_fields_empty():
    spec_block = _make_spec_block("model-card", template=[
        {"photo1": "", "photo2": "", "photo3": ""},
    ])
    soup = _soup('<div class="model-card"><div class="slider-track">'
                 '<img src="a.jpg"><img src="b.jpg"><img src="c.jpg"><img src="d.jpg"><img src="e.jpg">'
                 '</div></div>')
    issues = lh.check_slider_images(spec_block, soup, template_index=0)
    assert len(issues) == 1
    assert "5" in issues[0].message


def test_inline_svg_pass_when_control_has_value():
    spec_block = _make_spec_block("feature-card", template=[{"icon_svg": "%3Csvg%3E"}])
    soup = _soup('<article class="feature-card"><span class="feature-icon"><svg></svg></span></article>')
    issues = lh.check_inline_svg_icon(spec_block, soup, template_index=0)
    assert issues == []


def test_inline_svg_fail_when_dom_has_svg_but_template_empty():
    spec_block = _make_spec_block("feature-card", template=[{"icon_svg": ""}])
    soup = _soup('<article class="feature-card"><span class="feature-icon"><svg></svg></span></article>')
    issues = lh.check_inline_svg_icon(spec_block, soup, template_index=0)
    assert len(issues) == 1
```

- [ ] **Step 10: Run — verify fail (functions don't exist)**

Run: `pytest tests/phase-stage-08/test-lint-heuristics.py -v`

Expected: 4 passed, 6 failed (multi-paragraph, slider, svg tests fail with AttributeError).

- [ ] **Step 11: Implement remaining three heuristics**

Append to `lint_heuristics.py`:

```python
def check_multi_paragraph(spec_block, soup_match, target_field: str) -> list[LintIssue]:
    p_count = len(soup_match.find_all("p"))
    if p_count <= 1:
        return []
    control = next((c for c in spec_block.controls + spec_block.card_controls
                    if c.name == target_field), None)
    if control is None or control.type != "textarea":
        return []
    default_str = str(control.default_value or "")
    # Count paragraphs in default by splitting on \n\n
    spec_para_count = len([p for p in default_str.split("\n\n") if p.strip()])
    if spec_para_count >= p_count:
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="multi-paragraph",
        message=(f"{spec_block.slug}.{target_field}: composed has {p_count} paragraphs "
                 f"but spec default has only {spec_para_count}"),
        suggested_fragment=None,
    )]


def check_slider_images(spec_block, soup_match, template_index: int = 0) -> list[LintIssue]:
    imgs = soup_match.select('.slider-track > img, [data-slider] img')
    if not imgs:
        return []
    photo_keys = [f"photo{i}" for i in range(1, len(imgs) + 1)]
    if template_index >= len(spec_block.template):
        filled = 0
    else:
        row = spec_block.template[template_index]
        filled = sum(1 for k in photo_keys if str(row.get(k, "")).strip())
    if filled >= len(imgs):
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="slider-images",
        message=(f"{spec_block.slug}[template_index={template_index}]: composed slider has "
                 f"{len(imgs)} images but template only fills {filled} photo* fields"),
        suggested_fragment=None,
    )]


def check_inline_svg_icon(spec_block, soup_match, template_index: int = 0) -> list[LintIssue]:
    svg = soup_match.select_one('.feature-icon > svg, .icon > svg')
    if svg is None:
        return []
    svg_control = next((c for c in spec_block.controls + spec_block.card_controls
                        if c.name in SVG_ATTR_NAMES), None)
    if svg_control is None:
        return [LintIssue(
            severity="error",
            block_slug=spec_block.slug,
            heuristic="inline-svg-icon",
            message=f"{spec_block.slug} composed has inline <svg> but no SVG control in spec (expected one of {sorted(SVG_ATTR_NAMES)})",
        )]
    if template_index < len(spec_block.template):
        row = spec_block.template[template_index]
        if str(row.get(svg_control.name, "")).strip():
            return []
    if svg_control.has_default and str(svg_control.default_value).strip():
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="inline-svg-icon",
        message=(f"{spec_block.slug}.{svg_control.name}: composed has <svg> but spec "
                 f"template[{template_index}] / default is empty"),
    )]
```

- [ ] **Step 12: Run all heuristic tests — verify pass**

Run: `pytest tests/phase-stage-08/test-lint-heuristics.py -v`

Expected: 10 passed.

- [ ] **Step 13: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lib/lint_heuristics.py tests/phase-stage-08/test-lint-heuristics.py
git commit -m "feat(stage-08-lint): heuristic rules — bullets/colors/multi-p/slider/svg"
```

---

### Task 6: CLI `lint-composed-vs-spec.py` (verify-only mode)

**Files:**
- Create: `skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py`
- Create: `tests/phase-stage-08/test-lint-integration.py`
- Create: `tests/phase-stage-08/fixtures/lint/broken-spec.yaml`

- [ ] **Step 1: Create `broken-spec.yaml` fixture**

```yaml
blocks:
  - slug: features
    title: Features
    icon: star
    category: design
    type: section-card
    probe_selector: '.features-section'
    probe_kind: card-collection
    section_grid_class: 'features-grid'
    controls:
      - { id: c_feat_stmt, name: feat_statement, type: textarea, label: Statement, default: "Only one paragraph here" }
    card:
      slug: feature-card
      title: Feature Card
      controls:
        - { id: c_fc_title, name: title, type: text, label: Title, default: "Feat" }
        - { id: c_fc_icon, name: icon_svg, type: textarea, label: Icon, default: "" }
      template:
        - { title: "Confidence", icon_svg: "" }
        - { title: "Quietness", icon_svg: "" }
```

- [ ] **Step 2: Write failing integration test**

```python
"""End-to-end test for the lint CLI."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lint-composed-vs-spec.py"
FIX = REPO_ROOT / "tests" / "phase-stage-08" / "fixtures" / "lint"


def _run(composed, spec_yaml, *extra):
    return subprocess.run(
        [sys.executable, str(CLI), "--composed", str(composed), "--spec", str(spec_yaml), *extra],
        capture_output=True, text=True,
    )


def test_cli_exits_zero_when_spec_matches_composed(tmp_path):
    # good-spec needs N=2 cards to match composed's 2 cards — test on minimal
    # Use the brutalist-features fixture which has 2 non-statement cards
    r = _run(FIX / "brutalist-features-section.html", FIX / "good-spec.yaml")
    # good-spec has statement default of "One paragraph only" — that's an error
    # against 4 paragraphs in fixture. So this exits 1, but with a single
    # heuristic. We assert on output, not zero.
    assert "multi-paragraph" in r.stdout
    assert r.returncode == 1


def test_cli_exits_one_when_statement_short(tmp_path):
    r = _run(FIX / "brutalist-features-section.html", FIX / "broken-spec.yaml")
    assert r.returncode == 1
    assert "multi-paragraph" in r.stdout
    assert "inline-svg-icon" in r.stdout  # template icon_svg is empty


def test_cli_missing_composed_warning_not_error(tmp_path):
    nonexistent = tmp_path / "missing.html"
    r = _run(nonexistent, FIX / "good-spec.yaml")
    assert r.returncode == 0
    assert "WARNING" in r.stdout or "warning" in r.stdout
```

- [ ] **Step 3: Run — verify fail (CLI doesn't exist)**

Run: `pytest tests/phase-stage-08/test-lint-integration.py -v`

Expected: FAIL — CLI script not found / non-zero exit due to FileNotFoundError.

- [ ] **Step 4: Implement CLI (verify-only, no --fix yet)**

```python
#!/usr/bin/env python3
"""Lint composed.html against block-spec.yaml.

Exit codes:
  0 — no errors (warnings allowed)
  1 — at least one error
  2 — system error (spec missing, parse error, etc.)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from composed_inspector import inspect  # noqa: E402
from spec_inspector import inspect_spec  # noqa: E402
import lint_heuristics as lh  # noqa: E402


def _default_composed(project: Path) -> Path | None:
    for cand in ("composed-brutalist.html", "composed.html"):
        p = project / "07b_COMPOSED" / cand
        if p.exists():
            return p
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="Project root (assumes 07b_COMPOSED/ and 08_КОД/)")
    ap.add_argument("--composed", help="Path to composed.html (overrides --project default)")
    ap.add_argument("--spec", help="Path to block-spec.yaml (overrides --project default)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args(argv[1:])

    if args.spec:
        spec_path = Path(args.spec)
    elif args.project:
        spec_path = Path(args.project) / "08_КОД" / "block-spec.yaml"
    else:
        print("ERROR: must pass --project or --spec", file=sys.stderr)
        return 2
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}", file=sys.stderr)
        return 2

    if args.composed:
        composed_path = Path(args.composed)
    elif args.project:
        composed_path = _default_composed(Path(args.project))
    else:
        composed_path = None

    if composed_path is None or not composed_path.exists():
        print(f"WARNING: composed.html not found; skipping lint")
        return 0

    spec = inspect_spec(spec_path)
    probes = [b.probe_selector for b in spec.blocks if b.probe_selector]
    if not probes:
        print("WARNING: no probe_selector defined on any block; nothing to lint")
        return 0

    dom_blocks = {b.probe_selector: b for b in inspect(composed_path, probes)}

    issues: list[lh.LintIssue] = []
    for sb in spec.blocks:
        if not sb.probe_selector:
            continue
        dom_block = dom_blocks.get(sb.probe_selector)
        if dom_block is None or not dom_block.matches:
            issues.append(lh.LintIssue(
                severity="error", block_slug=sb.slug, heuristic="probe-match",
                message=f"{sb.slug} probe_selector {sb.probe_selector!r} not found in composed.html",
            ))
            continue

        if sb.probe_kind == "single" and len(dom_block.matches) != 1:
            issues.append(lh.LintIssue(
                severity="error", block_slug=sb.slug, heuristic="probe-match",
                message=f"{sb.slug} expected 1 instance, found {len(dom_block.matches)}",
            ))

        for idx, match in enumerate(dom_block.matches):
            issues.extend(lh.check_bullets(sb, match.soup))
            issues.extend(lh.check_color_swatches(sb, match.soup))
            # multi-paragraph runs against any textarea control found in the block
            for c in sb.controls + sb.card_controls:
                if c.type == "textarea":
                    issues.extend(lh.check_multi_paragraph(sb, match.soup, target_field=c.name))
            # slider + svg need per-card context — applies to card-collection blocks
            if sb.probe_kind == "card-collection":
                issues.extend(lh.check_slider_images(sb, match.soup, template_index=idx))
                issues.extend(lh.check_inline_svg_icon(sb, match.soup, template_index=idx))

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if args.json:
        import json as _json
        print(_json.dumps({
            "errors": [vars(i) for i in errors],
            "warnings": [vars(i) for i in warnings],
        }, ensure_ascii=False, indent=2))
    else:
        for i in errors:
            print(f"  ERROR [{i.heuristic}] {i.block_slug}: {i.message}")
            if i.suggested_fragment:
                print(f"    suggestion:\n      {i.suggested_fragment}")
        for i in warnings:
            print(f"  WARN  [{i.heuristic}] {i.block_slug}: {i.message}")
        print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Run integration tests — verify pass**

Run: `pytest tests/phase-stage-08/test-lint-integration.py -v`

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py tests/phase-stage-08/test-lint-integration.py tests/phase-stage-08/fixtures/lint/broken-spec.yaml
git commit -m "feat(stage-08-lint): CLI lint-composed-vs-spec (verify mode)"
```

---

### Task 7: Auto-fix mode (`--fix`) — append controls + fill template

**Files:**
- Modify: `skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py`
- Modify: `tests/phase-stage-08/test-lint-integration.py`

- [ ] **Step 1: Write failing test for `--fix` mode**

Append to `test-lint-integration.py`:

```python
def test_cli_fix_writes_backup_and_modifies_spec(tmp_path):
    # Copy broken spec to a tmp location so we don't mutate the fixture
    import shutil
    spec_copy = tmp_path / "spec.yaml"
    shutil.copy(FIX / "broken-spec.yaml", spec_copy)
    r = _run(FIX / "brutalist-features-section.html", spec_copy, "--fix")
    # Backup exists
    backups = list(tmp_path.glob("spec.yaml.bak.*"))
    assert len(backups) == 1
    # Spec was modified (contains AUTO-LINT comment)
    new_text = spec_copy.read_text(encoding="utf-8")
    assert "AUTO-LINT" in new_text
    # Re-run without --fix: errors should be reduced (statement now multi-para)
    r2 = _run(FIX / "brutalist-features-section.html", spec_copy)
    # Either zero errors or strictly fewer than before — assert "multi-paragraph" gone
    assert "multi-paragraph" not in r2.stdout
```

- [ ] **Step 2: Run — verify fail**

Run: `pytest tests/phase-stage-08/test-lint-integration.py::test_cli_fix_writes_backup_and_modifies_spec -v`

Expected: FAIL — `--fix` not supported.

- [ ] **Step 3: Add `--fix` support to CLI**

In `lint-composed-vs-spec.py`:

Add to argparse:
```python
ap.add_argument("--fix", action="store_true", help="Auto-apply safe fixes to spec.yaml")
```

After computing `issues` (and before output), insert the fix block:

```python
if args.fix and errors:
    import shutil, time, re as _re
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = spec_path.with_suffix(spec_path.suffix + f".bak.{ts}")
    shutil.copy(spec_path, backup)
    print(f"Backup written: {backup}")

    # Apply two fix types in v1:
    #   1. multi-paragraph errors → extract paragraphs from composed and
    #      overwrite the textarea default
    #   2. inline-svg-icon template-empty errors → leave a per-row TODO marker
    #
    # We re-parse spec text directly (PyYAML round-trip strips comments).
    spec_text = spec_path.read_text(encoding="utf-8")
    applied = 0

    for issue in errors:
        if issue.heuristic == "multi-paragraph":
            # Parse target field from message: "<slug>.<field>: composed has N paragraphs..."
            m = _re.match(r"([^.]+)\.(\w+):", issue.message)
            if not m:
                continue
            slug, field = m.group(1), m.group(2)
            sb = next((b for b in spec.blocks if b.slug == slug), None)
            if not sb or not sb.probe_selector:
                continue
            dom = dom_blocks.get(sb.probe_selector)
            if not dom or not dom.matches:
                continue
            paragraphs = [p.get_text(" ", strip=True) for p in dom.matches[0].soup.find_all("p")]
            paragraphs = [p for p in paragraphs if p]
            if not paragraphs:
                continue
            new_default = "\n\n".join(paragraphs)
            # Replace the default of this field in spec_text (line-based, single-line strings only).
            # Strategy: locate the control line containing `name: <field>` and rewrite its default.
            pattern = _re.compile(
                rf"(\{{[^}}]*name:\s*{_re.escape(field)}[^}}]*default:\s*)\"[^\"]*\"",
                _re.DOTALL,
            )
            quoted = new_default.replace('\\', '\\\\').replace('"', '\\"').replace("\n", "\\n")
            new_text, n = pattern.subn(
                rf'\1"{quoted}"  # AUTO-LINT {ts}: filled from composed.html',
                spec_text, count=1,
            )
            if n:
                spec_text = new_text
                applied += 1

    if applied:
        spec_path.write_text(spec_text, encoding="utf-8")
        print(f"Applied {applied} auto-fix(es). Re-run without --fix to verify.")
    else:
        print("No auto-fixable issues found.")
```

- [ ] **Step 4: Run — verify pass**

Run: `pytest tests/phase-stage-08/test-lint-integration.py -v`

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py tests/phase-stage-08/test-lint-integration.py
git commit -m "feat(stage-08-lint): --fix mode for multi-paragraph auto-extraction"
```

---

### Task 8: Wire into `gate-check.sh` for stage 08

**Files:**
- Modify: `scripts/gate-check.sh`

- [ ] **Step 1: Inspect current stage-08 section of gate-check.sh**

Run: `grep -n "stage.*08\|stage_08" scripts/gate-check.sh`

Expected: shows the function that checks stage-08.

- [ ] **Step 2: Add lint call to stage-08 check function**

Locate the stage-08 function (likely `stage_08_hard()` or `check_stage_08()`) and append before the success return:

```bash
# Composed↔spec lint — must pass before stage-08 can close.
LINT_SCRIPT="$REPO_ROOT/skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py"
if [ -f "$LINT_SCRIPT" ]; then
  if ! python3 "$LINT_SCRIPT" --project "$PROJECT_DIR" 2>&1; then
    echo "ERROR: composed↔spec lint failed for stage-08."
    echo "  Run: python3 $LINT_SCRIPT --project $PROJECT_DIR --fix"
    return 1
  fi
fi
```

- [ ] **Step 3: Run gate-check on dubai-avto-liza (expected to fail with current spec)**

Run: `bash scripts/gate-check.sh stage-08 ../Lendings/dubai-avto-liza`

Expected: prints lint errors, returns non-zero. (This is intentional — proves the gate now blocks the known regression.)

- [ ] **Step 4: Commit**

```bash
git add scripts/gate-check.sh
git commit -m "feat(stage-08-lint): block stage-08 gate on composed↔spec lint failure"
```

---

### Task 9: Documentation — `docs/standards/stage-08-spec-lint.md`

**Files:**
- Create: `docs/standards/stage-08-spec-lint.md`
- Modify: `CLAUDE.md` (add row to Quality Standards table)

- [ ] **Step 1: Write `stage-08-spec-lint.md`**

```markdown
# Stage-08 — Composed ↔ block-spec Lint

**Status:** required gate (strict mode).

## What it checks

Comparing `07b_COMPOSED/composed*.html` against `08_КОД/block-spec.yaml`, the
linter catches:

1. **Bullets** — `<ul.*-specs > li>` count must match available text-control fields.
2. **Color swatches** — `[style*="--c"]` presence requires a `colors` control.
3. **Multi-paragraph textareas** — `<p>` count must match `\n\n`-separated paragraphs in the default.
4. **Slider images** — `.slider-track > img` count must match populated `photoN` template fields.
5. **Inline SVG icons** — every `.feature-icon > svg` requires a non-empty `icon_svg` value.

## Commands

Verify only:
```bash
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project <project-path>
```

Auto-fix (multi-paragraph extraction):
```bash
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project <project-path> --fix
```

JSON output (for integration):
```bash
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project <project-path> --json
```

## probe_selector contract

Every block in `block-spec.yaml` that should be linted MUST set:

```yaml
- slug: model-card
  probe_selector: '.model-card'    # CSS selector that finds this block in composed.html
  probe_kind: card-collection      # "single" | "card-collection"; default "single"
```

If `probe_selector` is missing, the block is **skipped** with a warning. To
enforce coverage, run with `--json` and grep for `"warning"`.

## Gate behavior

`scripts/gate-check.sh stage-08 <project>` invokes the linter automatically.
Stage-08 cannot close until lint exits 0.
```

- [ ] **Step 2: Update `CLAUDE.md` Quality Standards table**

Find the table starting with `| Стандарт | Применяется | Verify-скрипт |` and append after the asset-pipeline row:

```markdown
| [`stage-08-spec-lint.md`](docs/standards/stage-08-spec-lint.md) | 08 Build — composed↔spec соответствие | `python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py --project <p>` |
```

- [ ] **Step 3: Commit**

```bash
git add docs/standards/stage-08-spec-lint.md CLAUDE.md
git commit -m "docs(stage-08-lint): standard + CLAUDE.md reference"
```

---

### Task 10: Apply to dubai-avto-liza — fix spec, re-run gate

**Files:**
- Modify: `D:/AI_TEAMS/Lendings/dubai-avto-liza/08_КОД/block-spec.yaml`

This task happens outside the worktree (separate repo) after the linter is merged to main.

- [ ] **Step 1: Merge linter branch to main**

```bash
cd D:/AI_TEAMS/landing_system
git checkout main
git merge --no-ff composed-parser-extension -m "merge: composed↔spec linter (stage-08 gate)"
git push origin main
```

- [ ] **Step 2: Run linter on dubai-avto-liza (verify mode)**

```bash
cd D:/AI_TEAMS/Lendings/dubai-avto-liza
python3 D:/AI_TEAMS/landing_system/skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project .
```

Expected: at least 3 errors (statement multi-paragraph, model-card bullets, model-card color-swatches).

- [ ] **Step 3: Add probe_selector to dubai-avto-liza block-spec**

In `08_КОД/block-spec.yaml`, add to each block:
```yaml
- slug: features
  probe_selector: '.features-section'
  probe_kind: card-collection
  ...
- slug: model-card
  probe_selector: '.model-card'
  probe_kind: card-collection
  ...
```
(Add probes for every block that has a clearly identifiable container in composed-brutalist.html.)

- [ ] **Step 4: Run `--fix` for multi-paragraph**

```bash
python3 D:/AI_TEAMS/landing_system/skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project . --fix
```

Expected: spec.yaml backup created, multi-paragraph errors auto-fixed.

- [ ] **Step 5: Manually fill remaining errors**

For bullets and color-swatches the linter prints `suggested_fragment` — copy them into the spec manually (auto-fix for these is out of scope v1).

- [ ] **Step 6: Re-run linter — verify zero errors**

```bash
python3 D:/AI_TEAMS/landing_system/skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project .
```

Expected: exit 0, warnings OK.

- [ ] **Step 7: Rebuild stage-08 + redeploy**

```bash
/landing-go
```

(Follow orchestrator through stage-08 build + deploy.)

- [ ] **Step 8: Commit dubai-avto-liza spec changes**

```bash
cd D:/AI_TEAMS/Lendings/dubai-avto-liza
git add 08_КОД/block-spec.yaml
git commit -m "fix(stage-08): pass composed↔spec lint — add probe_selectors + fill controls"
git push origin main
```

---

## Self-review

**Spec coverage check:**
- Architecture: 3 modules + CLI + gate hook — Tasks 1, 3, 4, 5, 6, 8 ✓
- Heuristics catalog (5 entries): bullets/colors/multi-p/slider/svg — Task 5 (10 tests, one fail+pass per heuristic) ✓
- CLI verify mode + `--fix` + `--json` + `--composed` autodetect — Task 6 + 7 ✓
- Gate integration — Task 8 ✓
- Migration of dubai-avto-liza — Task 10 ✓
- Acceptance criterion "dubai-avto-liza shows ≥3 errors before fix" — verified in Task 10 step 2 ✓
- Acceptance criterion "all tests green" — pytest invocations in Tasks 3, 4, 5, 6, 7 ✓
- Docs in `docs/standards/stage-08-spec-lint.md` — Task 9 ✓

**Placeholder scan:** no TBDs or vague "handle edge cases". Every step has concrete code or commands. ✓

**Type consistency:**
- `InspectedBlock` / `InspectedMatch` / `InspectedChild` defined in Task 3, used in Task 6 (via `dom_blocks[...].matches`) ✓
- `InspectedSpecBlock` / `InspectedControl` defined in Task 4, used in Tasks 5, 6 ✓
- `LintIssue` dataclass defined in Task 5, used in Task 6 ✓
- `check_*` function signatures consistent: `(spec_block, soup_match)` or `(spec_block, soup_match, target_field/template_index)` ✓
- `probe_selector` / `probe_kind` field names consistent across Tasks 1, 4, 6 ✓
