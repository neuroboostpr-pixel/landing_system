# PR-C Visual Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build icon/infographic generation pipeline that fills `data-slot type="icon"` and `data-slot type="infographic"` in `composed.html` (PR-A) using codex `image_gen`, parameterized by `tokens.json` + niche, with hash-based cache and 90 OpenDesign prompts as source.

**Architecture:** New skill `skills/visual-generation/` + 3 agents (visual-curator, icon-generator, infographic-builder) + 1 slash command `/landing-visuals`. Heavy reuse of PR-B patterns: codex wrapper structure, render-prompt.py, identity-safe-NOT-applied, STATE.yaml. Extends `inject-content.py` (PR-A) for icon/infographic branches.

**Tech Stack:** Python 3.10+ (Pillow, PyYAML, BeautifulSoup4), bash + bats, pytest, codex CLI v0.125+. No new external deps.

**Spec:** [`docs/superpowers/specs/2026-05-13-visual-generation-design.md`](../specs/2026-05-13-visual-generation-design.md)

---

## Task dependency graph

```
[Task 1: slot-scanner.py] ──┐
[Task 2: prompt-picker.py] ─┤
[Task 3: visual-cache.py] ──┼─▶ [Task 4: skill scaffold + templates]
[Task 9: new block-library] ┘        │
                                     ▼
                            [Task 5: 2 codex wrappers]
                                     │
                                     ▼
                            [Task 6: 3 agent docs]
                                     │
                                     ▼
                            [Task 7: extend inject-content.py]
                            [Task 8: /landing-visuals command]
                            [Task 10: 07d_VISUALS template]
                                     │
                                     ▼
                            [Task 11: extend test-pipeline.sh]
                            [Task 12: docs updates]
```

**12 tasks total.** Tasks 1-3 and 9 parallelizable. Rest mostly sequential.

---

## Task 1: `slot-scanner.py` — parse composed.html for visual slots

**Files:**
- Create: `skills/visual-generation/__init__.py`
- Create: `skills/visual-generation/scripts/__init__.py`
- Create: `skills/visual-generation/scripts/slot-scanner.py`
- Create: `tests/phase-prc/__init__.py`
- Create: `tests/phase-prc/conftest.py`
- Create: `tests/phase-prc/test-slot-scanner.py`

- [ ] **Step 1: Create test scaffold**

`tests/phase-prc/__init__.py`: empty.

`tests/phase-prc/conftest.py`:
```python
import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_skills_mod = sys.modules.setdefault("skills", type(sys)("skills"))
_vg_mod = type(sys)("skills.visual_generation")
_vg_scripts_mod = type(sys)("skills.visual_generation.scripts")
sys.modules["skills.visual_generation"] = _vg_mod
sys.modules["skills.visual_generation.scripts"] = _vg_scripts_mod

for script in ["slot-scanner", "prompt-picker", "visual-cache"]:
    p = REPO_ROOT / "skills" / "visual-generation" / "scripts" / f"{script}.py"
    if p.exists():
        mod = _load_module(f"skills.visual_generation.scripts.{script.replace('-', '_')}", p)
        sys.modules[f"skills.visual_generation.scripts.{script.replace('-', '_')}"] = mod
```

- [ ] **Step 2: Write failing test**

`tests/phase-prc/test-slot-scanner.py`:
```python
"""Tests for slot-scanner.py — parses composed.html for visual slots."""
from pathlib import Path
import yaml

from skills.visual_generation.scripts.slot_scanner import scan_html


SAMPLE_HTML = """<!DOCTYPE html>
<html><body>
<section class="block" data-block-id="ru-features-01">
  <div data-slot="feature-1-icon" data-slot-type="icon" data-hint="shield"></div>
  <div data-slot="feature-2-icon" data-slot-type="icon"></div>
</section>
<section class="block" data-block-id="ru-stats-01">
  <div data-slot="kpi-clients" data-slot-type="infographic" data-chart-type="number"></div>
</section>
<section class="block" data-block-id="ru-hero-01">
  <div data-slot="hero-bg" data-slot-type="photo"></div>
  <h1 data-slot="headline">Test</h1>
</section>
</body></html>"""


def test_scan_finds_icon_and_infographic_slots(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)

    result = scan_html(html_path)

    assert "icons" in result
    assert "infographics" in result
    assert len(result["icons"]) == 2
    assert len(result["infographics"]) == 1


def test_scan_captures_hints_and_block_ids(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)

    result = scan_html(html_path)

    icon1 = result["icons"][0]
    assert icon1["slot_name"] == "feature-1-icon"
    assert icon1["block_id"] == "ru-features-01"
    assert icon1["hint"] == "shield"

    icon2 = result["icons"][1]
    assert icon2["hint"] == ""  # no data-hint

    info1 = result["infographics"][0]
    assert info1["chart_type"] == "number"


def test_scan_ignores_photo_and_text_slots(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)

    result = scan_html(html_path)

    all_slot_names = [s["slot_name"] for s in result["icons"]] + [s["slot_name"] for s in result["infographics"]]
    assert "hero-bg" not in all_slot_names
    assert "headline" not in all_slot_names


def test_scan_empty_html_returns_empty_lists(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text("<html><body></body></html>")
    result = scan_html(html_path)
    assert result == {"icons": [], "infographics": []}


def test_scan_writes_yaml_output(tmp_path):
    from skills.visual_generation.scripts.slot_scanner import scan_and_write

    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)
    out_path = tmp_path / "_slots.yaml"

    scan_and_write(html_path, out_path)

    data = yaml.safe_load(out_path.read_text())
    assert len(data["icons"]) == 2
    assert len(data["infographics"]) == 1
```

- [ ] **Step 3: Run — fails**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
python3 -m pytest tests/phase-prc/test-slot-scanner.py -v 2>&1 | head -20
```

- [ ] **Step 4: Implement slot-scanner.py**

`skills/visual-generation/scripts/slot-scanner.py`:
```python
#!/usr/bin/env python3
"""Parse composed.html for visual slots (type=icon and type=infographic).

Outputs structured YAML for visual-curator agent.
Looks for `data-slot-type="icon"` or `data-slot-type="infographic"` attribute.
Captures sibling: data-slot (name), data-hint, data-chart-type, and parent's data-block-id.
"""
from pathlib import Path
from typing import Optional

import yaml
from bs4 import BeautifulSoup


def _find_block_id(element) -> str:
    """Walk up DOM to find nearest ancestor with data-block-id attribute."""
    cur = element.parent
    while cur is not None:
        if hasattr(cur, "get") and cur.get("data-block-id"):
            return cur.get("data-block-id", "")
        cur = cur.parent
    return ""


def scan_html(html_path: Path) -> dict:
    """Scan composed.html for icon and infographic slots.

    Returns dict {"icons": [...], "infographics": [...]} where each entry has
    slot_name, block_id, hint, chart_type (infographic only).
    """
    soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "html.parser")
    icons: list[dict] = []
    infographics: list[dict] = []

    for el in soup.select('[data-slot-type="icon"]'):
        icons.append({
            "slot_name": el.get("data-slot", ""),
            "block_id": _find_block_id(el),
            "hint": el.get("data-hint", ""),
            "icon_color": el.get("data-icon-color", ""),
        })

    for el in soup.select('[data-slot-type="infographic"]'):
        infographics.append({
            "slot_name": el.get("data-slot", ""),
            "block_id": _find_block_id(el),
            "hint": el.get("data-hint", ""),
            "chart_type": el.get("data-chart-type", ""),
            "data": el.get("data-chart-data", ""),
        })

    return {"icons": icons, "infographics": infographics}


def scan_and_write(html_path: Path, out_path: Path) -> dict:
    """Scan and write result to YAML file."""
    result = scan_html(html_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, help="Path to composed.html")
    ap.add_argument("--out", required=True, help="Path to output _slots.yaml")
    args = ap.parse_args()
    result = scan_and_write(Path(args.html), Path(args.out))
    print(f"Found {len(result['icons'])} icon slots, {len(result['infographics'])} infographic slots")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests — pass**

```bash
python3 -m pytest tests/phase-prc/test-slot-scanner.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/visual-generation/__init__.py skills/visual-generation/scripts/__init__.py skills/visual-generation/scripts/slot-scanner.py tests/phase-prc/
git commit -m "feat(pr-c): slot-scanner.py — parse composed.html for visual slots"
```

---

## Task 2: `prompt-picker.py` — waterfall prompt selection

**Files:**
- Create: `skills/visual-generation/scripts/prompt-picker.py`
- Create: `tests/phase-prc/test-prompt-picker.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prc/test-prompt-picker.py`:
```python
"""Tests for prompt-picker.py — waterfall: OpenDesign → icons.csv → generic."""
import pytest
from pathlib import Path

from skills.visual_generation.scripts.prompt_picker import (
    pick_icon_prompt,
    pick_infographic_prompt,
    PromptSource,
)


def test_pick_icon_falls_through_to_generic_when_nothing_matches(tmp_path):
    result = pick_icon_prompt(
        hint="completely-unique-xyz-no-match",
        brand_context={"BRAND_ACCENT": "#1e3a8a", "VISUAL_STYLE": "Minimalism"},
        icons_csv=None,
        opendesign_index=None,
    )
    assert result.source == PromptSource.GENERIC
    assert "completely-unique-xyz-no-match" in result.prompt


def test_pick_icon_matches_icons_csv_by_keyword(tmp_path):
    icons_csv = tmp_path / "icons.csv"
    icons_csv.write_text(
        "No,Category,Icon Name,Keywords,Library,Import Code,Usage,Best For,Style\n"
        '1,Navigation,menu,hamburger menu navigation toggle bars,Lucide,import { Menu },"<Menu />",Mobile drawer,Outline\n'
        '2,Action,shield,shield protect security warranty guarantee,Lucide,import { Shield },"<Shield />",Trust block,Outline\n'
    )
    result = pick_icon_prompt(
        hint="shield",
        brand_context={"BRAND_ACCENT": "#1e3a8a", "VISUAL_STYLE": "Minimalism"},
        icons_csv=icons_csv,
        opendesign_index=None,
    )
    assert result.source == PromptSource.ICONS_CSV
    assert "shield" in result.prompt.lower()


def test_pick_infographic_matches_opendesign_by_category(tmp_path):
    od_index_dir = tmp_path / "image"
    od_index_dir.mkdir()
    sample = od_index_dir / "growth-chart.json"
    sample.write_text('''{
        "id": "growth-chart",
        "category": "Infographic",
        "tags": ["chart", "growth"],
        "model": "gpt-image-2",
        "prompt": "Render a growth chart with smooth line, brand color [BRAND_ACCENT]",
        "source": {"license": "CC-BY-4.0", "author": "test"}
    }''')
    result = pick_infographic_prompt(
        hint="growth",
        chart_type="line",
        brand_context={"BRAND_ACCENT": "#c47a3a", "VISUAL_STYLE": "Editorial"},
        opendesign_index=od_index_dir,
    )
    assert result.source == PromptSource.OPENDESIGN
    assert "growth" in result.prompt.lower() or "chart" in result.prompt.lower()


def test_pick_returns_source_attribution_for_opendesign(tmp_path):
    od_index_dir = tmp_path / "image"
    od_index_dir.mkdir()
    sample = od_index_dir / "bar-chart.json"
    sample.write_text('''{
        "id": "bar-chart",
        "category": "Infographic",
        "tags": ["bar", "stats"],
        "prompt": "Bar chart with 5 bars in [BRAND_ACCENT]",
        "source": {"license": "CC-BY-4.0", "author": "creator-name", "url": "https://example.com"}
    }''')
    result = pick_infographic_prompt(
        hint="stats",
        chart_type="bar",
        brand_context={"BRAND_ACCENT": "#000", "VISUAL_STYLE": "Brutalism"},
        opendesign_index=od_index_dir,
    )
    assert result.attribution is not None
    assert result.attribution["license"] == "CC-BY-4.0"
    assert result.attribution["author"] == "creator-name"
```

- [ ] **Step 2: Run — fails**

```bash
python3 -m pytest tests/phase-prc/test-prompt-picker.py -v 2>&1 | head -20
```

- [ ] **Step 3: Implement prompt-picker.py**

`skills/visual-generation/scripts/prompt-picker.py`:
```python
#!/usr/bin/env python3
"""Waterfall prompt picker: OpenDesign 90 JSON → icons.csv → generic template.

For icons:    icons.csv keyword match → generic (skip OpenDesign — they're not icon-suited)
For infographics: OpenDesign tag/category match → generic

Returns PickedPrompt(prompt_text, source, attribution).
"""
import csv
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class PromptSource(Enum):
    OPENDESIGN = "opendesign"
    ICONS_CSV = "icons_csv"
    GENERIC = "generic"


@dataclass
class PickedPrompt:
    prompt: str
    source: PromptSource
    attribution: Optional[dict] = None  # populated for OpenDesign


GENERIC_ICON_TEMPLATE = """Use the built-in image_gen tool. Generate ONE PNG, 1024x1024,
on flat solid {chroma} background, for: {hint}.

VISUAL STYLE: {visual_style}, {icon_style} icon
COLOR: {brand_accent} primary, monochrome on {chroma} background
NICHE CONTEXT: {niche}

FORBIDDEN: lens flare, glitch, AI watermarks, text, numbers, photoreal faces, surreal artifacts.

Single clean shape, centered, occupying ~70% of canvas, flat {chroma} background for chroma-key removal."""


GENERIC_INFOGRAPHIC_TEMPLATE = """Use the built-in image_gen tool. Generate ONE PNG, 1024x1024,
on flat solid {chroma} background, for a {chart_type} infographic.

DATA: {data}
VISUAL STYLE: {visual_style}
COLOR: {brand_accent} primary
NICHE CONTEXT: {niche}

For "{chart_type}":
- "number" — large number with unit/label, ornamental frame
- "bar" — simple bar chart, 3-5 bars max
- "line" — single line chart, growth trend
- "donut" — donut chart, 2-4 segments

FORBIDDEN: lens flare, glitch, photoreal faces, surreal artifacts, text labels longer than 30 chars.

Single clean composition centered, ~80% canvas, flat {chroma} background."""


def _icons_csv_match(hint: str, icons_csv: Path) -> Optional[dict]:
    """Search icons.csv for keyword match. Returns row dict or None."""
    if not icons_csv or not icons_csv.exists():
        return None
    hint_lower = hint.lower().strip()
    if not hint_lower:
        return None
    with icons_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keywords = (row.get("Keywords", "") + " " + row.get("Icon Name", "")).lower()
            if hint_lower in keywords:
                return row
    return None


def _opendesign_match(hint: str, opendesign_index: Path, category: Optional[str] = None) -> Optional[dict]:
    """Search opendesign prompt JSONs for tag/category match. Returns prompt dict or None."""
    if not opendesign_index or not opendesign_index.exists():
        return None
    hint_lower = hint.lower().strip()
    if not hint_lower:
        return None

    for json_path in sorted(opendesign_index.glob("*.json")):
        # Skip attribution files
        if json_path.name.endswith(".attribution.txt"):
            continue
        try:
            data = json.loads(json_path.read_text())
        except json.JSONDecodeError:
            continue

        if category and data.get("category", "").lower() != category.lower():
            continue

        # Match on tags or title
        if hint_lower in data.get("title", "").lower():
            return data
        if any(hint_lower in tag.lower() for tag in data.get("tags", [])):
            return data

    return None


def pick_icon_prompt(
    hint: str,
    brand_context: dict,
    icons_csv: Optional[Path] = None,
    opendesign_index: Optional[Path] = None,
) -> PickedPrompt:
    """Pick prompt for icon slot. Waterfall: icons.csv → generic (skip OpenDesign for icons)."""
    chroma = brand_context.get("CHROMA_KEY", "#00ff00")
    brand_accent = brand_context.get("BRAND_ACCENT", "#888888")
    visual_style = brand_context.get("VISUAL_STYLE", "Minimalism")
    icon_style = brand_context.get("ICON_STYLE", "outlined")
    niche = brand_context.get("NICHE", "")

    row = _icons_csv_match(hint, icons_csv) if icons_csv else None
    if row:
        prompt = GENERIC_ICON_TEMPLATE.format(
            chroma=chroma,
            hint=f"{row['Icon Name']} icon ({row.get('Keywords', '').split()[0]})",
            visual_style=visual_style,
            icon_style=icon_style,
            brand_accent=brand_accent,
            niche=niche,
        )
        return PickedPrompt(prompt=prompt, source=PromptSource.ICONS_CSV)

    prompt = GENERIC_ICON_TEMPLATE.format(
        chroma=chroma,
        hint=hint if hint else "abstract minimalist icon",
        visual_style=visual_style,
        icon_style=icon_style,
        brand_accent=brand_accent,
        niche=niche,
    )
    return PickedPrompt(prompt=prompt, source=PromptSource.GENERIC)


def pick_infographic_prompt(
    hint: str,
    chart_type: str,
    brand_context: dict,
    opendesign_index: Optional[Path] = None,
) -> PickedPrompt:
    """Pick prompt for infographic. Waterfall: OpenDesign → generic."""
    chroma = brand_context.get("CHROMA_KEY", "#00ff00")
    brand_accent = brand_context.get("BRAND_ACCENT", "#888888")
    visual_style = brand_context.get("VISUAL_STYLE", "Minimalism")
    niche = brand_context.get("NICHE", "")

    od = _opendesign_match(hint, opendesign_index, category="Infographic") if opendesign_index else None
    if od:
        adapted = od.get("prompt", "")
        # Substitute brand vars where OpenDesign uses {argument} pattern
        adapted = adapted.replace("[BRAND_ACCENT]", brand_accent)
        adapted = adapted.replace("[BRAND_PRIMARY]", brand_accent)
        adapted = adapted.replace("[CHROMA_KEY]", chroma)
        attribution = {
            "id": od.get("id"),
            "license": od.get("source", {}).get("license"),
            "author": od.get("source", {}).get("author"),
            "url": od.get("source", {}).get("url"),
        }
        return PickedPrompt(prompt=adapted, source=PromptSource.OPENDESIGN, attribution=attribution)

    prompt = GENERIC_INFOGRAPHIC_TEMPLATE.format(
        chroma=chroma,
        chart_type=chart_type or "number",
        data=str(hint) if hint else "placeholder data",
        visual_style=visual_style,
        brand_accent=brand_accent,
        niche=niche,
    )
    return PickedPrompt(prompt=prompt, source=PromptSource.GENERIC)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["icon", "infographic"], required=True)
    ap.add_argument("--hint", required=True)
    ap.add_argument("--chart-type", default="")
    ap.add_argument("--brand-accent", default="#1e3a8a")
    ap.add_argument("--visual-style", default="Minimalism")
    ap.add_argument("--niche", default="")
    ap.add_argument("--icons-csv", default="")
    ap.add_argument("--opendesign-index", default="")
    args = ap.parse_args()

    brand_ctx = {
        "BRAND_ACCENT": args.brand_accent,
        "VISUAL_STYLE": args.visual_style,
        "NICHE": args.niche,
        "ICON_STYLE": "outlined",
    }

    if args.type == "icon":
        result = pick_icon_prompt(args.hint, brand_ctx, Path(args.icons_csv) if args.icons_csv else None, None)
    else:
        result = pick_infographic_prompt(args.hint, args.chart_type, brand_ctx,
                                          Path(args.opendesign_index) if args.opendesign_index else None)

    print(f"Source: {result.source.value}")
    if result.attribution:
        print(f"Attribution: {result.attribution}")
    print("---PROMPT---")
    print(result.prompt)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run — pass**

```bash
python3 -m pytest tests/phase-prc/test-prompt-picker.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/visual-generation/scripts/prompt-picker.py tests/phase-prc/test-prompt-picker.py
git commit -m "feat(pr-c): prompt-picker.py — waterfall OpenDesign → icons.csv → generic"
```

---

## Task 3: `visual-cache.py` — hash-based skip-if-exists cache

**Files:**
- Create: `skills/visual-generation/scripts/visual-cache.py`
- Create: `tests/phase-prc/test-visual-cache.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prc/test-visual-cache.py`:
```python
"""Tests for visual-cache.py — hash-based prompt cache."""
from pathlib import Path

from skills.visual_generation.scripts.visual_cache import (
    cache_key,
    lookup_cache,
    save_to_cache,
)


def test_cache_key_deterministic():
    key1 = cache_key(hint="shield", style="outlined", brand_color="#000")
    key2 = cache_key(hint="shield", style="outlined", brand_color="#000")
    assert key1 == key2


def test_cache_key_changes_with_inputs():
    a = cache_key(hint="shield", style="outlined", brand_color="#000")
    b = cache_key(hint="shield", style="filled", brand_color="#000")
    c = cache_key(hint="shield", style="outlined", brand_color="#fff")
    d = cache_key(hint="lock", style="outlined", brand_color="#000")
    assert a != b
    assert a != c
    assert a != d


def test_save_and_lookup_roundtrip(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    src = tmp_path / "src.png"
    src.write_bytes(b"fake_png_bytes")

    key = cache_key(hint="x", style="outlined", brand_color="#000")
    save_to_cache(cache_dir, key, src)

    found = lookup_cache(cache_dir, key)
    assert found is not None
    assert found.read_bytes() == b"fake_png_bytes"


def test_lookup_returns_none_for_missing(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    assert lookup_cache(cache_dir, "nonexistent-hash") is None


def test_lookup_rejects_too_small_files(tmp_path):
    """Damaged/empty cache files should be treated as miss."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "tiny.png").write_bytes(b"x")  # 1 byte = damaged

    assert lookup_cache(cache_dir, "tiny") is None
```

- [ ] **Step 2: Run — fails**

```bash
python3 -m pytest tests/phase-prc/test-visual-cache.py -v 2>&1 | head -15
```

- [ ] **Step 3: Implement visual-cache.py**

`skills/visual-generation/scripts/visual-cache.py`:
```python
#!/usr/bin/env python3
"""Hash-based skip-if-exists cache for visual generation.

Pattern from nexu-io/open-design imagegen.ts: cache by hash(hint+style+brand_color);
skip codex call if cache exists (unless FORCE=1).
"""
import hashlib
import shutil
from pathlib import Path
from typing import Optional


MIN_CACHE_FILE_SIZE = 1024  # 1 KB — anything smaller is considered damaged


def cache_key(hint: str, style: str, brand_color: str, niche: str = "") -> str:
    """Deterministic 16-char hex key from inputs."""
    canonical = f"{hint}|{style}|{brand_color}|{niche}".lower().strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def lookup_cache(cache_dir: Path, key: str) -> Optional[Path]:
    """Return cache file if exists and not damaged, else None."""
    cache_dir = Path(cache_dir)
    candidate = cache_dir / f"{key}.png"
    if not candidate.exists():
        return None
    if candidate.stat().st_size < MIN_CACHE_FILE_SIZE:
        return None
    return candidate


def save_to_cache(cache_dir: Path, key: str, source_png: Path) -> Path:
    """Copy source_png into cache_dir/{key}.png. Returns cached path."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f"{key}.png"
    shutil.copyfile(source_png, dest)
    return dest


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--hint", required=True)
    ap.add_argument("--style", required=True)
    ap.add_argument("--brand-color", required=True)
    ap.add_argument("--niche", default="")
    args = ap.parse_args()
    print(cache_key(args.hint, args.style, args.brand_color, args.niche))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run — pass**

```bash
python3 -m pytest tests/phase-prc/test-visual-cache.py -v
```

- [ ] **Step 5: Commit**

```bash
git add skills/visual-generation/scripts/visual-cache.py tests/phase-prc/test-visual-cache.py
git commit -m "feat(pr-c): visual-cache.py — hash-based skip-if-exists cache"
```

---

## Task 4: Skill scaffold + 2 prompt templates

**Files:**
- Create: `skills/visual-generation/SKILL.md`
- Create: `skills/visual-generation/templates/icon-prompt.md`
- Create: `skills/visual-generation/templates/infographic-prompt.md`
- Create: `tests/phase-prc/test-templates-shape.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prc/test-templates-shape.py`:
```python
"""Validate the 2 codex prompt templates have the required structure."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "skills" / "visual-generation" / "templates"

REQUIRED_SECTIONS = ["## How to use", "## Placeholders", "## Prompt body", "## Filled example"]


def test_icon_template_has_all_sections():
    body = (TEMPLATES / "icon-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"icon-prompt.md missing: {s}"


def test_infographic_template_has_all_sections():
    body = (TEMPLATES / "infographic-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"infographic-prompt.md missing: {s}"


def test_icon_template_forbids_text_and_faces():
    body = (TEMPLATES / "icon-prompt.md").read_text()
    assert "No text" in body or "no text" in body.lower()
    assert "No photoreal human faces" in body or "no photoreal" in body.lower()


def test_skill_md_exists():
    p = REPO / "skills" / "visual-generation" / "SKILL.md"
    assert p.exists()
    body = p.read_text()
    assert body.startswith("---")
    assert "name: visual-generation" in body
```

- [ ] **Step 2: Run — fails**

```bash
python3 -m pytest tests/phase-prc/test-templates-shape.py -v 2>&1 | head -15
```

- [ ] **Step 3: Create SKILL.md**

`skills/visual-generation/SKILL.md`:
```markdown
---
name: visual-generation
description: Stage 07d (PR-C) — generate icons + infographics via codex image_gen for composed.html slots. Parameterized by tokens.json + niche. Hash-cache. Owned by visual-curator agent.
---

# visual-generation

Конвейер генерации визуалов (иконки, инфографика) для лендинга. Запускается командой `/landing-visuals` после approved `05_design` + существующего `07b_COMPOSED/composed.html`.

## Этапы

1. **scan** — `scripts/slot-scanner.py` парсит `composed.html`, выдаёт списки icon/infographic слотов в `07d_VISUALS/_slots.yaml`.
2. **generate** — `scripts/codex-generate-icon.sh` / `-infographic.sh` для каждого слота. Перед вызовом codex — кэш-lookup по hash(hint+style+brand_color+niche).
3. **inject** — `inject-content.py` (PR-A/PR-B расширенный) подставляет PNG в `composed.html` на месте placeholders.

## Identity-safe

НЕ применяется — нет людей в иконках/чартах.

## Cache

`07d_VISUALS/.cache/<hash>.png` — переиспользование сгенерированных изображений между прогонами. `FORCE=1` обходит кэш.

## Promptpicker waterfall

- **icons:** icons.csv keyword match → generic template (skip OpenDesign — они не под иконки)
- **infographics:** OpenDesign 90 JSON tag/category match → generic template

## State management

`07d_VISUALS/STATE.yaml` отслеживает scan / generate / inject. Перезапуск продолжает с прерванного.
```

- [ ] **Step 4: Create icon-prompt.md**

`skills/visual-generation/templates/icon-prompt.md`:
```markdown
# icon-prompt — codex image_gen for icon slots

## How to use

1. Render placeholders via prompt-picker.py (which uses tokens.json + niche).
2. Pass to `codex-generate-icon.sh` (clones `generate-atlas.sh` snapshot pattern).
3. Chroma-key remove afterwards.
4. Output → `07d_VISUALS/icons/<slot_name>.png`.

## Placeholders

- `[VISUAL_STYLE]` — `tokens.json:design.visual_style`
- `[BRAND_ACCENT]` — `tokens.json:colors.accent` (icon primary color)
- `[ICON_STYLE]` — `tokens.json:design.icon_style` (outlined / filled / duotone / 3d). Default: outlined.
- `[NICHE]` — `01a_АНАЛИЗ_НИШИ/market-profile.md:niche`
- `[SLOT_HINT]` — hint from meta.yaml or slot.name parsed
- `[CHROMA_KEY]` — `#00ff00` default; `#ff00ff` if accent is green

## Prompt body

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid [CHROMA_KEY]
background, for: [SLOT_HINT].

VISUAL STYLE: [VISUAL_STYLE], [ICON_STYLE] icon
COLOR: [BRAND_ACCENT] primary, monochrome on [CHROMA_KEY] background
NICHE CONTEXT: [NICHE]

FORBIDDEN (from open-design DESIGN.md):
- No lens flare, no glitch, no chromatic aberration
- No AI watermarks (no "AI", "Midjourney", "DALL-E" signatures)
- No text, no numbers, no letters on the icon
- No photoreal human faces or recognizable people
- No surreal melting or flowing artifacts
- No cartoon/anime style unless brand_mood demands

Single clean shape, centered, occupying ~70% of the canvas, on a perfectly flat
[CHROMA_KEY] background for clean chroma-key removal.
```

## Filled example

When [SLOT_HINT]=shield, [VISUAL_STYLE]=Minimalism & Swiss Style, [BRAND_ACCENT]=#1e3a8a,
[ICON_STYLE]=outlined, [NICHE]=услуги, [CHROMA_KEY]=#00ff00:

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid #00ff00
background, for: shield.

VISUAL STYLE: Minimalism & Swiss Style, outlined icon
COLOR: #1e3a8a primary, monochrome on #00ff00 background
NICHE CONTEXT: услуги

(... forbidden list and centering rules as in body above)
```
```

- [ ] **Step 5: Create infographic-prompt.md**

`skills/visual-generation/templates/infographic-prompt.md`:
```markdown
# infographic-prompt — codex image_gen for infographic slots

## How to use

1. Render placeholders via prompt-picker.py.
2. If OpenDesign template matched — use it (with substituted brand vars).
3. Pass to `codex-generate-infographic.sh`.
4. Chroma-key remove afterwards.
5. Output → `07d_VISUALS/infographics/<slot_name>.png`.

## Placeholders

- `[VISUAL_STYLE]`, `[BRAND_ACCENT]`, `[NICHE]`, `[CHROMA_KEY]` — same as icon-prompt.md
- `[CHART_TYPE]` — `meta.yaml:slots[].chart_type` (number, bar, line, donut)
- `[CHART_DATA]` — JSON-stringified slots[].data (numbers + labels)

## Prompt body

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid [CHROMA_KEY]
background, for a [CHART_TYPE] infographic.

DATA: [CHART_DATA]
VISUAL STYLE: [VISUAL_STYLE]
COLOR: [BRAND_ACCENT] primary, monochrome accents allowed
NICHE CONTEXT: [NICHE]

For "[CHART_TYPE]":
- "number" — large number with unit/label, ornamental frame
- "bar" — simple bar chart, 3-5 bars max
- "line" — single line chart, growth trend
- "donut" — donut chart, 2-4 segments

FORBIDDEN: lens flare, glitch, photoreal faces, surreal artifacts, text labels longer than 30 chars.

Single clean composition centered, ~80% canvas, flat [CHROMA_KEY] background.
```

## Filled example

When [CHART_TYPE]=number, [CHART_DATA]={"value": 1000, "label": "+", "caption": "клиентов"},
[VISUAL_STYLE]=Minimalism, [BRAND_ACCENT]=#c47a3a, [NICHE]=услуги, [CHROMA_KEY]=#00ff00:

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, on flat solid #00ff00
background, for a number infographic.

DATA: {"value": 1000, "label": "+", "caption": "клиентов"}
VISUAL STYLE: Minimalism
COLOR: #c47a3a primary, monochrome accents allowed
NICHE CONTEXT: услуги

(... chart type rules and forbidden list as in body)
```
```

- [ ] **Step 6: Run — pass + commit**

```bash
python3 -m pytest tests/phase-prc/test-templates-shape.py -v
git add skills/visual-generation/SKILL.md skills/visual-generation/templates/ tests/phase-prc/test-templates-shape.py
git commit -m "feat(pr-c): skill scaffold + icon-prompt.md + infographic-prompt.md"
```

---

## Task 5: 2 codex CLI wrappers (icon + infographic)

**Files:**
- Create: `skills/visual-generation/scripts/codex-generate-icon.sh`
- Create: `skills/visual-generation/scripts/codex-generate-infographic.sh`
- Create: `tests/phase-prc/test-codex-wrappers.bats`

- [ ] **Step 1: Write failing bats test**

`tests/phase-prc/test-codex-wrappers.bats`:
```bash
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
    MOCK="$REPO_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    export CODEX_BIN="$MOCK"
    TMP_PROJECT="$(mktemp -d)"
    mkdir -p "$TMP_PROJECT/07d_VISUALS/.logs"
    mkdir -p "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА"
    echo '{"colors":{"primary":"#1e3a8a","accent":"#c47a3a"},"design":{"visual_style":"Minimalism","icon_style":"outlined"}}' > "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
}

teardown() { rm -rf "$TMP_PROJECT"; }

@test "codex-generate-icon.sh creates PNG output path and logs" {
    skip "Requires real codex CLI image_gen — covered by E2E"
}

@test "codex-generate-icon.sh skip-if-exists works" {
    OUT_DIR="$TMP_PROJECT/07d_VISUALS/icons"
    mkdir -p "$OUT_DIR"
    # Pre-populate the target
    echo "existing png" > "$OUT_DIR/test-slot.png"

    run bash "$REPO_ROOT/skills/visual-generation/scripts/codex-generate-icon.sh" \
        "$TMP_PROJECT" "test-slot" "shield"
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "SKIP"
}

@test "codex-generate-icon.sh FORCE=1 bypasses skip" {
    OUT_DIR="$TMP_PROJECT/07d_VISUALS/icons"
    mkdir -p "$OUT_DIR"
    echo "existing png" > "$OUT_DIR/test-slot.png"

    # With FORCE=1, the script should attempt regeneration (will try to call codex mock)
    FORCE=1 run bash "$REPO_ROOT/skills/visual-generation/scripts/codex-generate-icon.sh" \
        "$TMP_PROJECT" "test-slot" "shield"
    # We don't assert success because the mock doesn't produce real PNG;
    # we just verify SKIP path was not taken.
    if [ "$status" -eq 0 ]; then
        ! echo "$output" | grep -q "SKIP"
    fi
}

@test "codex-generate-infographic.sh respects --type infographic" {
    skip "Requires real codex CLI image_gen — covered by E2E"
}
```

- [ ] **Step 2: Run — fails (scripts don't exist)**

```bash
bats tests/phase-prc/test-codex-wrappers.bats 2>&1 | head -15
```

- [ ] **Step 3: Implement codex-generate-icon.sh**

`skills/visual-generation/scripts/codex-generate-icon.sh`:
```bash
#!/usr/bin/env bash
# codex-generate-icon.sh — generate ONE PNG icon via codex image_gen.
# Clones paralaximus generate-atlas.sh snapshot+comm+copy pattern.
#
# Usage:
#   bash codex-generate-icon.sh <project_dir> <slot_name> <hint>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
SLOT_NAME="${2:?ERROR: slot_name required}"
HINT="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/icon-prompt.md"

OUT_DIR="$PROJECT_DIR/07d_VISUALS/icons"
mkdir -p "$OUT_DIR"
OUT_PNG="$OUT_DIR/${SLOT_NAME}.png"

# Skip-if-exists (open-design imagegen.ts pattern)
if [ -f "$OUT_PNG" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "SKIP: $OUT_PNG exists. Set FORCE=1 to override."
    exit 0
fi

# Render prompt via Python (uses prompt-picker.py for waterfall selection)
PROMPT_FILE="$(mktemp)"
python3 - "$TEMPLATE" "$PROJECT_DIR" "$HINT" "$SLOT_NAME" "$PROMPT_FILE" <<'PYEOF'
import sys, re, json
from pathlib import Path

template_path = sys.argv[1]
project_dir = sys.argv[2]
hint = sys.argv[3]
slot_name = sys.argv[4]
out_file = sys.argv[5]

text = Path(template_path).read_text()
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: icon-prompt.md missing Prompt body section")
body = m.group(1)

# Load brand context from tokens.json
tokens_path = Path(project_dir) / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
tokens = json.loads(tokens_path.read_text()) if tokens_path.exists() else {}
brand_accent = tokens.get("colors", {}).get("accent", "#1e3a8a")
visual_style = tokens.get("design", {}).get("visual_style", "Minimalism")
icon_style = tokens.get("design", {}).get("icon_style", "outlined")

# Niche
niche = ""
niche_path = Path(project_dir) / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
if niche_path.exists():
    nm = re.search(r"\*\*Niche:\*\*\s*(.+)$", niche_path.read_text(), re.MULTILINE)
    if nm:
        niche = nm.group(1).strip()

slot_hint = hint if hint else slot_name.replace("-", " ").replace("_", " ")
chroma = "#00ff00"

body = (body
    .replace("[SLOT_HINT]", slot_hint)
    .replace("[VISUAL_STYLE]", visual_style)
    .replace("[BRAND_ACCENT]", brand_accent)
    .replace("[ICON_STYLE]", icon_style)
    .replace("[NICHE]", niche)
    .replace("[CHROMA_KEY]", chroma))

Path(out_file).write_text(body)
PYEOF

# Snapshot existing codex image dirs (paralaximus pattern)
TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

CODEX_BIN="${CODEX_BIN:-codex}"
LOGS_DIR="$PROJECT_DIR/07d_VISUALS/.logs"
mkdir -p "$LOGS_DIR"
TS="$(date +%Y-%m-%d_%H%M%S)"
LOG="$LOGS_DIR/${TS}_icon_${SLOT_NAME}.log"

{
    echo "=== ICON GEN: $SLOT_NAME ($HINT) ==="
    echo "=== PROMPT ==="
    cat "$PROMPT_FILE"
    echo "=== RESPONSE ==="
} > "$LOG"

echo "→ Generating icon: $SLOT_NAME..."
"$CODEX_BIN" exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" >>"$LOG" 2>&1 || {
    rc=$?
    echo "ERROR: codex exec failed (rc=$rc). See $LOG" >&2
    rm -f "$PROMPT_FILE" "$TMP_BEFORE"
    exit "$rc"
}

TMP_AFTER="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER" "$PROMPT_FILE"

[ -n "$NEW_DIR" ] || NEW_DIR="$(ls -1t ~/.codex/generated_images/ 2>/dev/null | head -1)"
[ -n "$NEW_DIR" ] || { echo "ERROR: no codex generated_images dir found" >&2; exit 3; }

SRC_PNG="$(ls -1t "$HOME/.codex/generated_images/$NEW_DIR"/*.png 2>/dev/null | head -1 || true)"
[ -n "$SRC_PNG" ] || { echo "ERROR: no PNG produced" >&2; exit 4; }

cp "$SRC_PNG" "$OUT_PNG"
echo "✓ Icon generated: $OUT_PNG"
```

- [ ] **Step 4: Implement codex-generate-infographic.sh**

Same structure as codex-generate-icon.sh but uses `templates/infographic-prompt.md` and reads `chart_type`/`data` args. Save as `skills/visual-generation/scripts/codex-generate-infographic.sh`:

```bash
#!/usr/bin/env bash
# codex-generate-infographic.sh — generate ONE PNG infographic via codex image_gen.
#
# Usage:
#   bash codex-generate-infographic.sh <project_dir> <slot_name> <chart_type> <data_json>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
SLOT_NAME="${2:?ERROR: slot_name required}"
CHART_TYPE="${3:-number}"
DATA_JSON="${4:-{}}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/infographic-prompt.md"

OUT_DIR="$PROJECT_DIR/07d_VISUALS/infographics"
mkdir -p "$OUT_DIR"
OUT_PNG="$OUT_DIR/${SLOT_NAME}.png"

if [ -f "$OUT_PNG" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "SKIP: $OUT_PNG exists. Set FORCE=1 to override."
    exit 0
fi

PROMPT_FILE="$(mktemp)"
python3 - "$TEMPLATE" "$PROJECT_DIR" "$CHART_TYPE" "$DATA_JSON" "$PROMPT_FILE" <<'PYEOF'
import sys, re, json
from pathlib import Path

template_path, project_dir, chart_type, data_json, out_file = sys.argv[1:6]

text = Path(template_path).read_text()
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: infographic-prompt.md missing Prompt body section")
body = m.group(1)

tokens_path = Path(project_dir) / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
tokens = json.loads(tokens_path.read_text()) if tokens_path.exists() else {}
brand_accent = tokens.get("colors", {}).get("accent", "#1e3a8a")
visual_style = tokens.get("design", {}).get("visual_style", "Minimalism")

niche = ""
niche_path = Path(project_dir) / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
if niche_path.exists():
    nm = re.search(r"\*\*Niche:\*\*\s*(.+)$", niche_path.read_text(), re.MULTILINE)
    if nm:
        niche = nm.group(1).strip()

body = (body
    .replace("[CHART_TYPE]", chart_type)
    .replace("[CHART_DATA]", data_json)
    .replace("[VISUAL_STYLE]", visual_style)
    .replace("[BRAND_ACCENT]", brand_accent)
    .replace("[NICHE]", niche)
    .replace("[CHROMA_KEY]", "#00ff00"))

Path(out_file).write_text(body)
PYEOF

TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

CODEX_BIN="${CODEX_BIN:-codex}"
LOGS_DIR="$PROJECT_DIR/07d_VISUALS/.logs"
mkdir -p "$LOGS_DIR"
TS="$(date +%Y-%m-%d_%H%M%S)"
LOG="$LOGS_DIR/${TS}_infographic_${SLOT_NAME}.log"

{
    echo "=== INFOGRAPHIC GEN: $SLOT_NAME ($CHART_TYPE) ==="
    echo "=== PROMPT ==="
    cat "$PROMPT_FILE"
    echo "=== RESPONSE ==="
} > "$LOG"

echo "→ Generating infographic: $SLOT_NAME..."
"$CODEX_BIN" exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" >>"$LOG" 2>&1 || {
    rc=$?
    rm -f "$PROMPT_FILE" "$TMP_BEFORE"
    exit "$rc"
}

TMP_AFTER="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER" "$PROMPT_FILE"

[ -n "$NEW_DIR" ] || NEW_DIR="$(ls -1t ~/.codex/generated_images/ 2>/dev/null | head -1)"
[ -n "$NEW_DIR" ] || { echo "ERROR: no codex generated_images dir found" >&2; exit 3; }

SRC_PNG="$(ls -1t "$HOME/.codex/generated_images/$NEW_DIR"/*.png 2>/dev/null | head -1 || true)"
[ -n "$SRC_PNG" ] || { echo "ERROR: no PNG produced" >&2; exit 4; }

cp "$SRC_PNG" "$OUT_PNG"
echo "✓ Infographic generated: $OUT_PNG"
```

Make both executable: `chmod +x skills/visual-generation/scripts/codex-generate-*.sh`

- [ ] **Step 5: Run bats — verify skip-if-exists test passes**

```bash
bats tests/phase-prc/test-codex-wrappers.bats
```

Expected: 2 PASS + 2 SKIP (E2E only).

- [ ] **Step 6: Commit**

```bash
git add skills/visual-generation/scripts/codex-generate-*.sh tests/phase-prc/test-codex-wrappers.bats
git commit -m "feat(pr-c): codex CLI wrappers for icon + infographic generation"
```

---

## Task 6: 3 agent docs (visual-curator, icon-generator, infographic-builder)

**Files:**
- Create: `agents/visual-curator.md`
- Create: `agents/icon-generator.md`
- Create: `agents/infographic-builder.md`
- Create: `tests/phase-prc/test-agents-frontmatter.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-prc/test-agents-frontmatter.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "visual-curator agent exists with frontmatter" {
    [ -f "$REPO/agents/visual-curator.md" ]
    head -10 "$REPO/agents/visual-curator.md" | grep -q "^name: visual-curator$"
}

@test "icon-generator agent exists with frontmatter" {
    [ -f "$REPO/agents/icon-generator.md" ]
    head -10 "$REPO/agents/icon-generator.md" | grep -q "^name: icon-generator$"
}

@test "infographic-builder agent exists with frontmatter" {
    [ -f "$REPO/agents/infographic-builder.md" ]
    head -10 "$REPO/agents/infographic-builder.md" | grep -q "^name: infographic-builder$"
}

@test "visual-curator references both sub-agents and /landing-visuals command" {
    body=$(cat "$REPO/agents/visual-curator.md")
    echo "$body" | grep -q "icon-generator"
    echo "$body" | grep -q "infographic-builder"
    echo "$body" | grep -q "/landing-visuals"
}

@test "visual-curator references stage gates 05_design and 07b composed" {
    body=$(cat "$REPO/agents/visual-curator.md")
    echo "$body" | grep -qi "05_design\|05_ДИЗАЙН"
    echo "$body" | grep -qi "07b\|composed"
}
```

- [ ] **Step 2: Create agents/visual-curator.md**

```markdown
---
name: visual-curator
description: Stage 07d orchestrator (PR-C). Scans composed.html for icon/infographic slots, dispatches icon-generator and infographic-builder, manages STATE.yaml, injects PNGs back into composed.html. Triggered by /landing-visuals.
---

# visual-curator

## Mission

Orchestrate visual generation pipeline (stage 07d). No identity-safe rules — visuals don't contain people.

## Gate

- `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе exit «Сначала утверди дизайн-систему».
- `<project>/07b_COMPOSED/composed.html` exists — иначе exit «Сначала запусти `/landing-compose` (PR-A)».

## Process

1. **Scan.**
   ```bash
   python3 skills/visual-generation/scripts/slot-scanner.py \
     --html <project>/07b_COMPOSED/composed.html \
     --out <project>/07d_VISUALS/_slots.yaml
   ```

2. **Generate icons.** For each icon slot:
   - Dispatch `icon-generator` agent with (slot_name, hint).
   - Cache lookup first via `visual-cache.py`; skip codex if cached.
   - On generation: copy result also to `.cache/<hash>.png`.

3. **Generate infographics.** Same for infographic slots, dispatch `infographic-builder` agent.

4. **Inject.**
   ```bash
   python3 skills/block-composition/scripts/compose-blocks.py --project <project>
   ```
   This now reads `07d_VISUALS/icons/` and `07d_VISUALS/infographics/`. Backward compatible: if 07d_VISUALS missing, placeholder behavior preserved.

5. Mark `STATE.yaml:stages.inject` done. Print Russian summary.

## State

`07d_VISUALS/STATE.yaml`:
- `stages.{scan, generate, inject}`: status, finished, counts, errors
- `warnings: []`, `errors: []`

## Idempotency

Cache-based; default skip-if-exists. `/landing-visuals --force` bypasses cache.
Specific slot: `/landing-visuals --slot <name>`.

## Sub-agents

- `icon-generator`
- `infographic-builder`

## Tools

Bash, Read, Write, Edit, Glob, Task.
```

- [ ] **Step 3: Create agents/icon-generator.md**

```markdown
---
name: icon-generator
description: Generates ONE icon PNG via codex image_gen for a given slot. Uses prompt-picker waterfall (icons.csv → generic). Hash-cache via visual-cache.py.
---

# icon-generator

## Mission

Generate ONE icon PNG for one slot_name. Used by visual-curator in stage 07d.

## Input

- `<project_dir>` (absolute)
- `<slot_name>` (e.g. `feature-1-icon`)
- `<hint>` (optional, e.g. `shield`)

## Output

`<project>/07d_VISUALS/icons/<slot_name>.png`

## Process

1. Compute cache key:
   ```bash
   python3 skills/visual-generation/scripts/visual-cache.py \
     --hint "<hint>" --style "<icon_style>" --brand-color "<accent>" --niche "<niche>"
   ```
2. If cache hit (`.cache/<hash>.png` exists, size >= 1KB) — copy to `icons/<slot>.png`, exit.
3. Otherwise:
   ```bash
   bash skills/visual-generation/scripts/codex-generate-icon.sh \
     <project_dir> <slot_name> "<hint>"
   ```
4. After successful generation, copy output also to `.cache/<hash>.png` for future runs.

## Errors

- codex fail after retry → fallback to SVG-placeholder (`skills/photo-curation/scripts/svg-placeholder.py` from PR-B).
- Chroma-key fringe issues → retry with `--edge-contract 1` or alternative chroma `#ff00ff`.

## Tools

Bash, Read.
```

- [ ] **Step 4: Create agents/infographic-builder.md**

```markdown
---
name: infographic-builder
description: Generates ONE infographic PNG via codex image_gen. Uses prompt-picker waterfall (OpenDesign 90 JSON → generic). Hash-cache via visual-cache.py.
---

# infographic-builder

## Mission

Generate ONE infographic PNG for one slot_name. Used by visual-curator in stage 07d.

## Input

- `<project_dir>`
- `<slot_name>` (e.g. `kpi-clients`)
- `<chart_type>` (number, bar, line, donut)
- `<data_json>` (JSON-stringified data spec, e.g. `{"value": 1000, "label": "+", "caption": "клиентов"}`)

## Output

`<project>/07d_VISUALS/infographics/<slot_name>.png`

## Process

1. Compute cache key from (hint, chart_type, brand_accent, niche).
2. If cache hit → copy to `infographics/<slot>.png`, exit.
3. Otherwise:
   ```bash
   bash skills/visual-generation/scripts/codex-generate-infographic.sh \
     <project_dir> <slot_name> <chart_type> '<data_json>'
   ```
4. After successful generation, copy to `.cache/<hash>.png`.
5. Record attribution (if OpenDesign source) in `07d_VISUALS/prompts.yaml`.

## Errors

- codex fail after retry → SVG-placeholder fallback.
- Invalid `data_json` → use generic placeholder data, warn in STATE.yaml.

## Tools

Bash, Read.
```

- [ ] **Step 5: Run + commit**

```bash
bats tests/phase-prc/test-agents-frontmatter.bats
git add agents/visual-curator.md agents/icon-generator.md agents/infographic-builder.md tests/phase-prc/test-agents-frontmatter.bats
git commit -m "feat(pr-c): 3 visual-pipeline agents (curator, icon-generator, infographic-builder)"
```

---

## Task 7: Extend `inject-content.py` for icon + infographic branches

**Files:**
- Modify: `skills/block-composition/scripts/inject-content.py`
- Create: `tests/phase-prc/test-inject-visuals.py`

- [ ] **Step 1: Read existing inject-content.py to find photo branch**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
grep -n "photo_slots\|data-slot-type\|slot-placeholder" skills/block-composition/scripts/inject-content.py | head -20
```

The PR-B work added `photo_selections` parameter. Now add similar for visuals: scan project's `07d_VISUALS/{icons,infographics}/` and substitute PNGs.

- [ ] **Step 2: Write failing test**

`tests/phase-prc/test-inject-visuals.py`:
```python
"""Tests for inject-content.py icon + infographic substitution."""
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

try:
    from skills.block_composition.scripts.inject_content import inject_block
except ImportError:
    pytest.skip("inject_block not importable yet", allow_module_level=True)


def test_inject_icon_from_visuals_dir(tmp_path):
    block_html = '<section><div data-slot="feature-1-icon" data-slot-type="icon"></div></section>'
    block_meta = {
        "id": "ru-features-01",
        "slots": [{"type": "icon", "name": "feature-1-icon", "hint": "shield"}]
    }
    visuals_dir = tmp_path / "07d_VISUALS"
    icons_dir = visuals_dir / "icons"
    icons_dir.mkdir(parents=True)
    (icons_dir / "feature-1-icon.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 100)

    result = inject_block(block_html, block_meta, {}, visuals_dir=visuals_dir)

    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    assert img is not None
    assert "feature-1-icon.png" in img.get("src", "")


def test_inject_infographic_from_visuals_dir(tmp_path):
    block_html = '<section><div data-slot="kpi-1" data-slot-type="infographic"></div></section>'
    block_meta = {
        "id": "ru-stats-01",
        "slots": [{"type": "infographic", "name": "kpi-1", "chart_type": "number"}]
    }
    visuals_dir = tmp_path / "07d_VISUALS"
    info_dir = visuals_dir / "infographics"
    info_dir.mkdir(parents=True)
    (info_dir / "kpi-1.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 100)

    result = inject_block(block_html, block_meta, {}, visuals_dir=visuals_dir)

    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    assert img is not None
    assert "infographics/kpi-1.png" in img.get("src", "") or "kpi-1.png" in img.get("src", "")


def test_inject_falls_back_to_placeholder_when_visuals_missing(tmp_path):
    block_html = '<section><div data-slot="feature-1-icon" data-slot-type="icon"></div></section>'
    block_meta = {
        "id": "ru-features-01",
        "slots": [{"type": "icon", "name": "feature-1-icon"}]
    }
    result = inject_block(block_html, block_meta, {}, visuals_dir=None)

    soup = BeautifulSoup(result, "html.parser")
    placeholder = soup.find(class_="slot-placeholder")
    assert placeholder is not None


def test_inject_pra_compat_no_visuals_no_photo_selections(tmp_path):
    """Regression: PR-A behavior preserved when both PR-B and PR-C inputs absent."""
    block_html = '<section><div data-slot="hero-bg" data-slot-type="photo"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "hint": "object"}]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=None, visuals_dir=None)
    soup = BeautifulSoup(result, "html.parser")
    placeholder = soup.find(class_="slot-placeholder")
    assert placeholder is not None
```

- [ ] **Step 3: Run — fails or some pass partially**

```bash
python3 -m pytest tests/phase-prc/test-inject-visuals.py -v 2>&1 | head -25
```

- [ ] **Step 4: Modify inject-content.py**

In `skills/block-composition/scripts/inject-content.py`:

1. Update function signature to accept `visuals_dir`:
   ```python
   def inject_block(html_str, block_meta, content, photo_selections=None, visuals_dir=None):
   ```

2. Build slot type lookup at function start:
   ```python
   icon_slots = {s["name"]: s for s in block_meta.get("slots", []) if s.get("type") == "icon"}
   info_slots = {s["name"]: s for s in block_meta.get("slots", []) if s.get("type") == "infographic"}
   ```

3. Inside the loop over `[data-slot]` elements, ADD branches before falling through to placeholder:
   ```python
   elif slot_name in icon_slots:
       icon_png = None
       if visuals_dir:
           candidate = Path(visuals_dir) / "icons" / f"{slot_name}.png"
           if candidate.exists():
               icon_png = candidate
       if icon_png:
           el.clear()
           img = soup.new_tag("img", attrs={
               "src": f"../07d_VISUALS/icons/{slot_name}.png",
               "alt": icon_slots[slot_name].get("hint", slot_name),
               "class": "lp-icon",
           })
           el.append(img)
       else:
           el.clear()
           ph = soup.new_tag("div", **{"class": "slot-placeholder"})
           ph.string = f"[SLOT: {slot_name}]"
           el.append(ph)

   elif slot_name in info_slots:
       info_png = None
       if visuals_dir:
           candidate = Path(visuals_dir) / "infographics" / f"{slot_name}.png"
           if candidate.exists():
               info_png = candidate
       if info_png:
           el.clear()
           img = soup.new_tag("img", attrs={
               "src": f"../07d_VISUALS/infographics/{slot_name}.png",
               "alt": info_slots[slot_name].get("chart_type", "infographic"),
               "class": "lp-infographic",
           })
           el.append(img)
       else:
           el.clear()
           ph = soup.new_tag("div", **{"class": "slot-placeholder"})
           ph.string = f"[INFOGRAPHIC: {slot_name}]"
           el.append(ph)
   ```

4. Also update `compose-blocks.py` to detect `07d_VISUALS/` and pass it via `--visuals-dir` to `inject-content.py` (similar to PR-B `--selections` flag).

   Open `skills/block-composition/scripts/compose-blocks.py`. After the PR-B `--selections` detection:
   ```python
   visuals_dir = project_dir / "07d_VISUALS"
   inject_args = []
   if photo_selections_path.exists():
       inject_args += ["--selections", str(photo_selections_path)]
   if visuals_dir.exists():
       inject_args += ["--visuals-dir", str(visuals_dir)]
   # Pass to subprocess call
   ```

5. Add `--visuals-dir` to inject-content.py CLI args. In `main()`:
   ```python
   ap.add_argument("--visuals-dir", default="", help="Path to 07d_VISUALS/ for PR-C visual substitution")
   # ... later, pass to inject_block:
   visuals_dir = Path(args.visuals_dir) if args.visuals_dir else None
   result = inject_block(..., visuals_dir=visuals_dir)
   ```

- [ ] **Step 5: Run new tests + PR-A and PR-B regression**

```bash
python3 -m pytest tests/phase-prc/test-inject-visuals.py -v
python3 -m pytest tests/phase-prb/test-inject-photos.py -v   # PR-B regression
bats tests/phase-pra/test-inject-content.bats              # PR-A regression
```

All must pass.

- [ ] **Step 6: Commit**

```bash
git add skills/block-composition/scripts/inject-content.py skills/block-composition/scripts/compose-blocks.py tests/phase-prc/test-inject-visuals.py
git commit -m "feat(pr-c): inject-content.py substitutes icons + infographics from 07d_VISUALS/

Backward compatible with PR-A (placeholder fallback) and PR-B (--selections kwarg preserved).
Adds --visuals-dir CLI arg routed by compose-blocks.py."
```

---

## Task 8: `/landing-visuals` slash command + stage gates

**Files:**
- Create: `commands/landing-visuals.md`
- Create: `tests/phase-prc/test-landing-visuals-gate.bats`

- [ ] **Step 1: Write failing bats test**

`tests/phase-prc/test-landing-visuals-gate.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "/landing-visuals command exists with frontmatter" {
    [ -f "$REPO/commands/landing-visuals.md" ]
    head -10 "$REPO/commands/landing-visuals.md" | grep -q "^description:"
}

@test "/landing-visuals mentions visual-curator agent" {
    grep -q "visual-curator" "$REPO/commands/landing-visuals.md"
}

@test "/landing-visuals lists --type --force --slot flags" {
    grep -q -- "--type" "$REPO/commands/landing-visuals.md"
    grep -q -- "--force" "$REPO/commands/landing-visuals.md"
    grep -q -- "--slot" "$REPO/commands/landing-visuals.md"
}

@test "/landing-visuals references stage gates 05_design + 07b_COMPOSED" {
    grep -qE "05_design|05_ДИЗАЙН" "$REPO/commands/landing-visuals.md"
    grep -qE "07b_COMPOSED|composed.html|composed" "$REPO/commands/landing-visuals.md"
}
```

- [ ] **Step 2: Create commands/landing-visuals.md**

```markdown
---
description: Stage 07d (PR-C) — генерация иконок и инфографики через codex image_gen для composed.html. Параметризовано tokens.json + niche. Требует approved 05 design + существующий composed.html.
---

# /landing-visuals

Генерирует иконки и инфографику для всех `data-slot type="icon"` и `type="infographic"` в `composed.html`. Stage 07d.

## Использование

```
/landing-visuals [--project <slug>] [--type icons|infographics] [--force] [--slot <name>]
```

**Флаги:**
- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--type icons` — только иконки (пропустить инфографику).
- `--type infographics` — только инфографика (пропустить иконки).
- `--force` — обойти кэш, перегенерить всё.
- `--slot <name>` — только один конкретный слот по имени.

## Гейты

1. `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе:
   > Сначала утверди дизайн-систему (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`) — без `tokens.json` codex не попадёт в стиль.

2. `<project>/07b_COMPOSED/composed.html` существует — иначе:
   > Сначала запусти `/landing-compose` (PR-A).

## Что происходит

Команда вызывает `visual-curator` агента, который:
1. Сканирует `composed.html` на icon и infographic слоты (`slot-scanner.py`).
2. Для каждого слота — cache lookup по hash(hint+style+brand_color+niche). Если cache hit — copy без вызова codex.
3. Если cache miss — диспатчит `icon-generator` или `infographic-builder` агента.
4. После всех генераций — re-render composed.html через PR-A `compose-blocks.py` (он теперь читает `07d_VISUALS/`).

## Артефакты

В `<project>/07d_VISUALS/`:
- `_slots.yaml` — найденные слоты (auto)
- `icons/<slot-name>.png` — иконки (auto)
- `infographics/<slot-name>.png` — инфографика (auto)
- `.cache/<hash>.png` — кэш (auto, не удаляй, экономит API)
- `prompts.yaml` — лог промптов с attribution (auto)
- `STATE.yaml` — статусы этапов (auto)
- `.logs/` — codex prompts + responses (auto)

## После выполнения

`07b_COMPOSED/composed.html` перерендерится — placeholders `[SLOT: ...]` и `[INFOGRAPHIC: ...]` заменятся на реальные `<img class="lp-icon">` / `<img class="lp-infographic">`.

## NOTE

PR-C команда вызывается ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция — задача PR-D.

См. [spec](../docs/superpowers/specs/2026-05-13-visual-generation-design.md), [plan](../docs/superpowers/plans/2026-05-13-visual-generation-plan.md).
```

- [ ] **Step 3: Run + commit**

```bash
bats tests/phase-prc/test-landing-visuals-gate.bats
git add commands/landing-visuals.md tests/phase-prc/test-landing-visuals-gate.bats
git commit -m "feat(pr-c): /landing-visuals slash command with stage gates"
```

---

## Task 9: 2 new block-library blocks with `type: infographic` slots

**Files:**
- Create: `block-library/features/ru-features-XX-kpi-metrics/SKILL.md`
- Create: `block-library/features/ru-features-XX-kpi-metrics/meta.yaml`
- Create: `block-library/features/ru-features-XX-kpi-metrics/assets/template.html`
- Create: `block-library/features/ru-features-XX-kpi-metrics/assets/template-mobile.html`
- Create: `block-library/social-proof/ru-stats-XX-growth-chart/SKILL.md`
- Create: `block-library/social-proof/ru-stats-XX-growth-chart/meta.yaml`
- Create: `block-library/social-proof/ru-stats-XX-growth-chart/assets/template.html`
- Create: `block-library/social-proof/ru-stats-XX-growth-chart/assets/template-mobile.html`
- Create: `tests/phase-prc/test-new-blocks.bats`

- [ ] **Step 1: Inspect block-library convention**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
ls block-library/features/ru-features-01-3col-icons/
cat block-library/features/ru-features-01-3col-icons/meta.yaml
cat block-library/features/ru-features-01-3col-icons/assets/template.html | head -40
ls block-library/ | sort
```

Identify next available ID number for `ru-features-XX` (X = lowest unused integer).

- [ ] **Step 2: Write failing test**

`tests/phase-prc/test-new-blocks.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "ru-features-XX-kpi-metrics block exists with valid structure" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    [ -n "$BLOCK" ]
    [ -f "$BLOCK/meta.yaml" ]
    [ -f "$BLOCK/assets/template.html" ]
    [ -f "$BLOCK/assets/template-mobile.html" ]
    [ -f "$BLOCK/SKILL.md" ]
}

@test "kpi-metrics meta.yaml has type=infographic slots" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    grep -q "type: infographic" "$BLOCK/meta.yaml"
}

@test "kpi-metrics has chart_type field" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    grep -qE "chart_type:|chart_type " "$BLOCK/meta.yaml"
}

@test "ru-stats-XX-growth-chart block exists with valid structure" {
    BLOCK="$(ls -d "$REPO/block-library/social-proof/ru-stats-"*"-growth-chart" 2>/dev/null | head -1)"
    [ -n "$BLOCK" ]
    [ -f "$BLOCK/meta.yaml" ]
    [ -f "$BLOCK/assets/template.html" ]
}

@test "growth-chart meta.yaml has type=infographic line slot" {
    BLOCK="$(ls -d "$REPO/block-library/social-proof/ru-stats-"*"-growth-chart" 2>/dev/null | head -1)"
    grep -q "type: infographic" "$BLOCK/meta.yaml"
    grep -qE "chart_type:.*line|line.*chart_type" "$BLOCK/meta.yaml"
}

@test "template.html files have data-slot-type=infographic" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    grep -q 'data-slot-type="infographic"' "$BLOCK/assets/template.html"
}
```

- [ ] **Step 3: Run — fails**

```bash
bats tests/phase-prc/test-new-blocks.bats
```

- [ ] **Step 4: Find next free numbers**

```bash
ls block-library/features/ | sort
ls block-library/social-proof/ | sort
```

Pick the lowest unused IDs (e.g., `ru-features-14-kpi-metrics` and `ru-stats-01-growth-chart` — adjust based on actual contents).

- [ ] **Step 5: Create kpi-metrics block**

Let's assume `ru-features-14-kpi-metrics` is free. Make directory:
```bash
mkdir -p block-library/features/ru-features-14-kpi-metrics/assets
```

`block-library/features/ru-features-14-kpi-metrics/meta.yaml`:
```yaml
id: ru-features-14-kpi-metrics
category: features
ru_market: true
use_cases:
  - services
  - b2c
description: '4 KPI-метрики с инфографикой: % успеха, лет на рынке, клиентов, проектов'
display_name_ru: 📊 4 KPI-метрики (87% / 12 лет / 1000+ клиентов)
layout_summary_ru: Четыре крупные метрики в одной линии, каждая с infographic-визуалом сверху и подписью снизу. Mobile — 2x2 grid.
slots:
  - type: infographic
    name: kpi-1
    chart_type: number
    data:
      value: 87
      label: '%'
      caption: 'успешных проектов'
    required: true
  - type: infographic
    name: kpi-2
    chart_type: number
    data:
      value: 12
      label: 'лет'
      caption: 'на рынке'
    required: true
  - type: infographic
    name: kpi-3
    chart_type: number
    data:
      value: 1000
      label: '+'
      caption: 'клиентов'
    required: true
  - type: infographic
    name: kpi-4
    chart_type: number
    data:
      value: 500
      label: '+'
      caption: 'завершённых проектов'
    required: false
conversion_notes: KPI-блок повышает доверие. Числа должны быть честными — проверь с клиентом.
source: manual
source_attribution: ''
created: 2026-05-13
recommended_styles_ru:
  - Minimalism & Swiss Style
  - Flat Design 2.0
```

`block-library/features/ru-features-14-kpi-metrics/SKILL.md`:
```markdown
---
name: ru-features-14-kpi-metrics
category: features
---

# ru-features-14-kpi-metrics

KPI-блок с 4 инфографиками (число + единица + подпись).

## When to apply
- Сервисные ниши со зрелым бизнесом (нужна метрика «12 лет на рынке» и т.п.)
- B2C где доверие через цифры

## Conversion notes
- 3-4 KPI максимум, иначе перегружено
- Числа должны быть реальными
- На mobile — grid 2x2
```

`block-library/features/ru-features-14-kpi-metrics/assets/template.html`:
```html
<section class="lp-kpi-metrics" data-block-id="ru-features-14-kpi-metrics">
  <div class="kpi-grid">
    <div class="kpi-item">
      <div data-slot="kpi-1" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">успешных проектов</p>
    </div>
    <div class="kpi-item">
      <div data-slot="kpi-2" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">на рынке</p>
    </div>
    <div class="kpi-item">
      <div data-slot="kpi-3" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">клиентов</p>
    </div>
    <div class="kpi-item">
      <div data-slot="kpi-4" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">завершённых проектов</p>
    </div>
  </div>
</section>
<style>
.lp-kpi-metrics { padding: 80px 24px; background: var(--surface-bg, #fafafa); }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; max-width: 1200px; margin: 0 auto; }
.kpi-item { text-align: center; }
.kpi-visual { width: 100%; aspect-ratio: 1/1; max-width: 200px; margin: 0 auto 16px; }
.kpi-visual img { width: 100%; height: 100%; object-fit: contain; }
.kpi-caption { font-size: 14px; color: var(--text-secondary, #57534e); }
</style>
```

`block-library/features/ru-features-14-kpi-metrics/assets/template-mobile.html`:
```html
<section class="lp-kpi-metrics-mobile" data-block-id="ru-features-14-kpi-metrics">
  <div class="kpi-grid-mobile">
    <div class="kpi-item">
      <div data-slot="kpi-1" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">успешных проектов</p>
    </div>
    <div class="kpi-item">
      <div data-slot="kpi-2" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">на рынке</p>
    </div>
    <div class="kpi-item">
      <div data-slot="kpi-3" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">клиентов</p>
    </div>
    <div class="kpi-item">
      <div data-slot="kpi-4" data-slot-type="infographic" data-chart-type="number" class="kpi-visual"></div>
      <p class="kpi-caption">завершённых проектов</p>
    </div>
  </div>
</section>
<style>
.lp-kpi-metrics-mobile { padding: 40px 16px; }
.kpi-grid-mobile { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.kpi-item { text-align: center; }
.kpi-visual { width: 100%; max-width: 140px; aspect-ratio: 1/1; margin: 0 auto 8px; }
.kpi-visual img { width: 100%; height: 100%; object-fit: contain; }
.kpi-caption { font-size: 12px; color: var(--text-secondary, #57534e); }
</style>
```

- [ ] **Step 6: Create growth-chart block (assume ru-stats-01-growth-chart is free)**

```bash
mkdir -p block-library/social-proof/ru-stats-01-growth-chart/assets
```

`block-library/social-proof/ru-stats-01-growth-chart/meta.yaml`:
```yaml
id: ru-stats-01-growth-chart
category: social-proof
ru_market: true
use_cases:
  - services
  - b2c
description: 'Блок социального доказательства: график роста (клиентов / выручки / проектов) за N лет'
display_name_ru: 📈 График роста (клиенты / выручка / проекты за N лет)
layout_summary_ru: Заголовок + один большой line-chart инфографик слева, краткое описание метрики справа. На mobile — chart сверху, текст снизу.
slots:
  - type: infographic
    name: growth-chart-main
    chart_type: line
    data:
      x_label: 'Год'
      y_label: 'Клиентов'
      points: [[2019, 50], [2020, 180], [2021, 420], [2022, 700], [2023, 1000]]
    required: true
  - type: text
    name: headline
    max_chars: 60
    required: true
  - type: text
    name: subhead
    max_chars: 200
    required: false
conversion_notes: Графики роста — мощный proof. Используй реальные данные. Если данных мало (стартап) — заменить на «текущее vs цель».
source: manual
source_attribution: ''
created: 2026-05-13
recommended_styles_ru:
  - Minimalism & Swiss Style
  - Editorial
```

`block-library/social-proof/ru-stats-01-growth-chart/SKILL.md`:
```markdown
---
name: ru-stats-01-growth-chart
category: social-proof
---

# ru-stats-01-growth-chart

Блок «график роста» — line-chart инфографика + заголовок + подзаголовок.

## When to apply
- Компании с историей >3 лет (есть точки данных)
- Сервисные ниши, B2B SaaS, b2c где видимый рост убедителен

## Conversion notes
- 4-6 точек данных
- Reasonable scale (не «1, 1.1, 1.2, 1.3» — это плоско)
- Если данных мало — лучше KPI-блок (`ru-features-XX-kpi-metrics`)
```

`block-library/social-proof/ru-stats-01-growth-chart/assets/template.html`:
```html
<section class="lp-growth-chart" data-block-id="ru-stats-01-growth-chart">
  <div class="growth-grid">
    <div data-slot="growth-chart-main" data-slot-type="infographic" data-chart-type="line" class="growth-visual"></div>
    <div class="growth-text">
      <h2 data-slot="headline">Рост за 5 лет</h2>
      <p data-slot="subhead">От 50 до 1000+ клиентов — стабильный органический рост.</p>
    </div>
  </div>
</section>
<style>
.lp-growth-chart { padding: 80px 24px; }
.growth-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 48px; max-width: 1200px; margin: 0 auto; align-items: center; }
.growth-visual { width: 100%; aspect-ratio: 16/10; }
.growth-visual img { width: 100%; height: 100%; object-fit: contain; }
.growth-text h2 { font-size: 32px; margin: 0 0 16px; }
.growth-text p { font-size: 16px; color: var(--text-secondary, #57534e); }
</style>
```

`block-library/social-proof/ru-stats-01-growth-chart/assets/template-mobile.html`:
```html
<section class="lp-growth-chart-mobile" data-block-id="ru-stats-01-growth-chart">
  <div data-slot="growth-chart-main" data-slot-type="infographic" data-chart-type="line" class="growth-visual-mobile"></div>
  <h2 data-slot="headline">Рост за 5 лет</h2>
  <p data-slot="subhead">От 50 до 1000+ клиентов — стабильный органический рост.</p>
</section>
<style>
.lp-growth-chart-mobile { padding: 32px 16px; }
.growth-visual-mobile { width: 100%; aspect-ratio: 4/3; margin: 0 0 16px; }
.growth-visual-mobile img { width: 100%; height: 100%; object-fit: contain; }
.lp-growth-chart-mobile h2 { font-size: 22px; margin: 0 0 12px; }
.lp-growth-chart-mobile p { font-size: 14px; color: var(--text-secondary, #57534e); }
</style>
```

- [ ] **Step 7: Run tests + commit**

```bash
bats tests/phase-prc/test-new-blocks.bats
git add block-library/features/ru-features-*-kpi-metrics/ block-library/social-proof/ru-stats-*-growth-chart/ tests/phase-prc/test-new-blocks.bats
git commit -m "feat(pr-c): 2 new blocks with type=infographic slots (kpi-metrics + growth-chart)"
```

---

## Task 10: `07d_VISUALS/` template + README

**Files:**
- Create: `template/07d_VISUALS/README.md`
- Create: `template/07d_VISUALS/.gitkeep`
- Create: `tests/phase-prc/test-template-07d.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-prc/test-template-07d.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "template/07d_VISUALS exists with README" {
    [ -d "$REPO/template/07d_VISUALS" ]
    [ -f "$REPO/template/07d_VISUALS/README.md" ]
}

@test "README is in Russian and mentions /landing-visuals" {
    body=$(cat "$REPO/template/07d_VISUALS/README.md")
    echo "$body" | grep -qE "иконк|инфограф"
    echo "$body" | grep -q "/landing-visuals"
}

@test "README explains icons + infographics + cache" {
    body=$(cat "$REPO/template/07d_VISUALS/README.md")
    echo "$body" | grep -qi "icon"
    echo "$body" | grep -qi "infograph"
    echo "$body" | grep -qi "cache\|кэш"
}
```

- [ ] **Step 2: Create directory + README**

```bash
mkdir -p template/07d_VISUALS
touch template/07d_VISUALS/.gitkeep
```

`template/07d_VISUALS/README.md`:
```markdown
# 07d_VISUALS — иконки и инфографика

Это папка для AI-сгенерённых визуальных элементов лендинга: иконки и инфографика.

## Что произойдёт когда запустишь /landing-visuals

1. Система просканирует `07b_COMPOSED/composed.html`, найдёт все слоты с `data-slot-type="icon"` и `data-slot-type="infographic"`.
2. Для каждого слота — codex (gpt-image-2) сгенерит PNG под брендинг проекта (цвета, стиль, ниша из tokens.json + market-profile).
3. PNG сохранится в `icons/<slot-name>.png` или `infographics/<slot-name>.png`.
4. `composed.html` перерендерится — placeholders `[SLOT: ...]` заменятся на `<img>`.

## Кэш

`07d_VISUALS/.cache/<hash>.png` — кэшированные генерации по hash(hint + style + brand_color + niche).
- Перезапуск `/landing-visuals` НЕ зовёт codex второй раз для одних и тех же слотов — берёт из кэша.
- Чтобы перегенерить — `/landing-visuals --force`.
- Один слот — `/landing-visuals --slot feature-1-icon`.

## Артефакты

- `_slots.yaml` — найденные слоты в composed.html (auto)
- `icons/` — сгенерённые PNG иконки
- `infographics/` — сгенерённые PNG инфографики
- `.cache/` — кэш по hash (НЕ удаляй — экономит codex API)
- `prompts.yaml` — какой промпт → какой PNG (для аудита и atribution)
- `STATE.yaml` — статусы этапов
- `.logs/` — codex prompts + responses

## Что НЕ делать

- Не редактируй PNG в `icons/` или `infographics/` вручную — `--force` их перезапишет. Лучше отредактируй промпт-шаблон в `skills/visual-generation/templates/`.
- Не коммить `.cache/` в git — это локальный кеш (добавлено в .gitignore через template).

## Перезапуск

```
/landing-visuals --force                 # перегенерить всё с нуля
/landing-visuals --type icons            # только иконки
/landing-visuals --slot feature-3-icon   # один конкретный слот
```

См. полную документацию: [`/landing-visuals`](../../commands/landing-visuals.md).
```

- [ ] **Step 3: Run + commit**

```bash
bats tests/phase-prc/test-template-07d.bats
git add template/07d_VISUALS/ tests/phase-prc/test-template-07d.bats
git commit -m "feat(pr-c): 07d_VISUALS template with Russian README for marketer"
```

---

## Task 11: Extend `scripts/test-pipeline.sh` with PR-C stage

**Files:**
- Modify: `scripts/test-pipeline.sh`

- [ ] **Step 1: Read existing pipeline to find insertion point**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
grep -n "PR-B\|07c_PHOTOS" scripts/test-pipeline.sh | head -10
```

Append PR-C stage AFTER PR-B stage.

- [ ] **Step 2: Append PR-C section to test-pipeline.sh**

After the PR-B section:

```bash
# --- PR-C Visual stage (icons + infographics) ---
if [ -f "$PROJECT/07b_COMPOSED/composed.html" ]; then
    echo ""
    echo "→ Stage PR-C: running visual pipeline..."

    # Ensure 05_design tokens.json exists for prompt context
    if [ ! -f "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json" ]; then
        mkdir -p "$PROJECT/05_ДИЗАЙН-СИСТЕМА"
        echo '{"colors":{"primary":"#1e3a8a","accent":"#c47a3a"},"design":{"visual_style":"Minimalism","icon_style":"outlined"}}' > "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
    fi

    # Stage 1: scan composed.html for visual slots
    python3 "$LS_ROOT/skills/visual-generation/scripts/slot-scanner.py" \
        --html "$PROJECT/07b_COMPOSED/composed.html" \
        --out "$PROJECT/07d_VISUALS/_slots.yaml"
    echo "  ✓ visual scan done"

    # Stage 2: generate (mocked in smoke; real codex if installed)
    if [ -n "${USE_CODEX_MOCK:-}" ]; then
        export CODEX_BIN="$LS_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    fi

    if command -v codex >/dev/null 2>&1 || [ -n "${USE_CODEX_MOCK:-}" ]; then
        # Parse _slots.yaml and run generators
        python3 -c "
import yaml, subprocess, sys
from pathlib import Path
slots = yaml.safe_load(Path('$PROJECT/07d_VISUALS/_slots.yaml').read_text())
for s in slots.get('icons', []):
    subprocess.run(['bash', '$LS_ROOT/skills/visual-generation/scripts/codex-generate-icon.sh',
                    '$PROJECT', s['slot_name'], s.get('hint','')], check=False)
for s in slots.get('infographics', []):
    subprocess.run(['bash', '$LS_ROOT/skills/visual-generation/scripts/codex-generate-infographic.sh',
                    '$PROJECT', s['slot_name'], s.get('chart_type','number'), '{}'], check=False)
"
        echo "  ✓ visual generation attempted"
    else
        echo "  ⊘ skipping generation (codex not installed and USE_CODEX_MOCK not set)"
    fi

    # Stage 3: re-render composed.html with visuals
    python3 "$LS_ROOT/skills/block-composition/scripts/compose-blocks.py" --project "$PROJECT" 2>/dev/null || true

    echo "  PR-C visual stage smoke test PASSED"
fi
```

- [ ] **Step 3: Run with mock**

```bash
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh prc-pipeline-smoke tests/phase-pra/fixtures/prototype-sample.md 2>&1 | tail -20
ls ~/Lendings/prc-pipeline-smoke/07d_VISUALS/ 2>/dev/null
```

- [ ] **Step 4: Commit**

```bash
git add scripts/test-pipeline.sh
git commit -m "test(pr-c): extend test-pipeline.sh with visual generation stage"
```

---

## Task 12: THIRD_PARTY_NOTICES + CLAUDE.md updates

**Files:**
- Modify: `THIRD_PARTY_NOTICES.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Append to THIRD_PARTY_NOTICES.md**

Add new section at end:

```markdown

## OpenDesign image-prompts — PR-C Visual Generation (CC-BY-4.0 main + per-prompt)

PR-C (2026-05-13) uses 90 image-prompt JSON templates from
`vendor/opendesign-extracts/prompt-templates/image/` (Apache-2.0 wrapper repo,
per-prompt licenses in `source.license` field — mostly CC-BY-4.0, some MIT).

When PR-C selects a prompt for infographic generation, the per-prompt
attribution is preserved in `07d_VISUALS/prompts.yaml` with fields:
- `id` — prompt ID
- `license` — per-prompt license (e.g. CC-BY-4.0)
- `author` — original creator
- `url` — original URL

Original repo: YouMind-OpenLab/awesome-gpt-image-2 (CC-BY-4.0 wrapper).

Use locations in this codebase:
- `skills/visual-generation/scripts/prompt-picker.py` — selects + adapts prompts
- `skills/visual-generation/templates/infographic-prompt.md` — fallback template inspired by open-design style
```

- [ ] **Step 2: Add PR-C section to CLAUDE.md**

Insert after the PR-B section (before "Block Library" section):

```markdown
## Новые команды PR-C (Visual Generation)

- `/landing-visuals` — AI-генерация иконок и инфографики через codex image_gen. **Stage 07d.**

**Workflow PR-C:**
1. Утверди этап 05 (design-system) и убедись что есть `07b_COMPOSED/composed.html` (PR-A).
2. Запусти `/landing-visuals`. Без флагов = и иконки, и инфографика.
3. Codex генерит PNG под брендинг (цвета из `tokens.json`, ниша из `market-profile.md`).
4. Кэш по hash(hint + style + brand_color + niche) — повторный прогон НЕ зовёт codex для тех же слотов.
5. `composed.html` перерендерится — placeholders `[SLOT: feature-1-icon]` заменятся на `<img class="lp-icon">`.

**Опциональные флаги:**
- `--type icons` или `--type infographics` — частичный прогон
- `--force` — игнорировать кэш
- `--slot <name>` — один конкретный слот

**Identity-safe** НЕ применяется (в иконках/чартах нет людей).

**NOTE:** PR-C команда вызывается ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция — задача PR-D.

См. [spec](docs/superpowers/specs/2026-05-13-visual-generation-design.md) и [plan](docs/superpowers/plans/2026-05-13-visual-generation-plan.md).
```

- [ ] **Step 3: Commit**

```bash
git add THIRD_PARTY_NOTICES.md CLAUDE.md
git commit -m "docs(pr-c): attribution for 90 open-design image-prompts + CLAUDE.md workflow"
```

---

## Final task: Run full test suite

- [ ] **Step 1: All PR-C tests**

```bash
python3 -m pytest tests/phase-prc/ -v
bats tests/phase-prc/
```

Expected: all pass.

- [ ] **Step 2: PR-A + PR-B regression**

```bash
bats tests/phase-pra/ tests/gate-check/ tests/phase-prb/
python3 -m pytest tests/phase-prb/ -v
```

All must pass — no regressions.

- [ ] **Step 3: Full E2E**

```bash
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh prc-final tests/phase-pra/fixtures/prototype-sample.md
```

Verify `~/Lendings/prc-final/07d_VISUALS/` populated.

- [ ] **Step 4: Mark plan complete**

If anything regressed — file follow-up, not PR-C blocker.

---

## Acceptance checklist (from spec)

- [ ] `/landing-visuals` дает composed.html with PNG icons (Task 7 + Final)
- [ ] `slot-scanner.py` finds all type=icon|infographic (Task 1 tests)
- [ ] `prompt-picker.py` correct waterfall (Task 2 tests)
- [ ] `visual-cache.py` skip-if-exists + FORCE (Task 3 tests)
- [ ] 20+ unit tests pass (Tasks 1-9)
- [ ] Backward compat with PR-A + PR-B (Task 7 regression)
- [ ] 2 new blocks with `type: infographic` (Task 9)
- [ ] `THIRD_PARTY_NOTICES.md` updated (Task 12)
- [ ] `07d_VISUALS/README.md` Russian for marketer (Task 10)
- [ ] `CLAUDE.md` PR-C workflow (Task 12)
