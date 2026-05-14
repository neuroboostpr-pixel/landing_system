# PR-B Photo Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build photo intake + AI-classification + AI-matching + processing + generative-fallback pipeline that fills photo slots in `composed.html` (PR-A artifact) under the project's design-system tokens.

**Architecture:** New skill `skills/photo-curation/` + 4 agents (curator, classifier, matcher, preview-board) + 1 slash command `/landing-photos`. All AI calls through `codex` CLI (proven pattern from `paralaximus-codex`). HTML split-view UI for human selection. Extends existing `inject-content.py` to substitute real photos for placeholders. Backward compatible: projects without PR-B output continue to render placeholders.

**Tech Stack:** Python 3.10+ (Pillow, PyYAML, BeautifulSoup4 — already in project), bash + bats, pytest, codex CLI v0.125+, sips (macOS HEIC). No new external dependencies.

**Spec:** [`docs/superpowers/specs/2026-05-13-photo-pipeline-design.md`](../specs/2026-05-13-photo-pipeline-design.md)

---

## Task dependency graph

```
[Task 0: codex image-input research] (UNBLOCKS classifier design)
       │
       ▼
[Task 1: render-prompt.py] ──┐
[Task 2: intake.py] ─────────┼──▶ [Task 3-5: codex wrappers]
[Task 3: skill scaffold]  ───┤        │
[Task 4: SVG placeholder] ───┘        ▼
                              [Task 6: gallery-render.py]
                              [Task 7: preview-render.py]
                                      │
                                      ▼
                              [Task 8: 4 agent docs]
                                      │
                                      ▼
                              [Task 9: extend style.py]
                              [Task 10: extend inject-content.py]
                              [Task 11: slash command + gates]
                              [Task 12: 07c_PHOTOS/ template + READMEs]
                                      │
                                      ▼
                              [Task 13: extend test-pipeline.sh]
                              [Task 14: THIRD_PARTY_NOTICES + CLAUDE.md]
```

**Parallelizable groups:**
- Group A (after Task 0): Tasks 1, 2, 3, 4 in parallel
- Group B (after Group A): Tasks 5, 6, 7 in parallel (each depends on different bits of Group A)
- Group C (sequential review): Tasks 8, 9, 10, 11, 12, 13, 14

---

## Task 0: Research codex CLI image-input mechanism

**Why first:** spec known risk R1 — without confirmed image input mechanism, `photo-classifier` can't be designed.

**Files:**
- Create: `docs/superpowers/research/codex-image-input.md`

- [ ] **Step 1: Check codex CLI version and image-related flags**

```bash
codex --version
codex exec --help 2>&1 | grep -i -E "image|attach|file|input" | head -20
codex --help 2>&1 | grep -i -E "image|attach|file" | head -20
```

Document each output verbatim.

- [ ] **Step 2: Test image input via three potential paths**

Test A — direct image flag:
```bash
codex exec --skip-git-repo-check --image /tmp/test.jpg "Describe this image in one sentence" 2>&1 | head -20
# Or: codex exec --skip-git-repo-check --attach /tmp/test.jpg "..."
```

Test B — file path in prompt (let codex read via its filesystem tool):
```bash
codex exec --skip-git-repo-check "Read the image file at /tmp/test.jpg using your read tool and describe it in one sentence" 2>&1 | head -20
```

Test C — markdown image reference:
```bash
codex exec --skip-git-repo-check "Analyze this image: ![](/tmp/test.jpg). One sentence description." 2>&1 | head -20
```

Create `/tmp/test.jpg` first: `sips -s format jpeg /System/Library/Desktop\ Pictures/Solar\ Gradients.heic --out /tmp/test.jpg 2>/dev/null || curl -s -o /tmp/test.jpg https://picsum.photos/200`

- [ ] **Step 3: Write research findings**

Create `docs/superpowers/research/codex-image-input.md` with:

```markdown
# Codex CLI image input — research findings (2026-05-13)

## codex --version
<paste output>

## Tested mechanisms

### A: --image / --attach flag
<paste output + verdict: works / not supported / partial>

### B: filesystem read in prompt
<paste output + verdict>

### C: markdown image reference
<paste output + verdict>

## Decision

**Chosen mechanism for photo-classifier:** <A | B | C | Anthropic SDK fallback>

**Rationale:** <one paragraph>

**Implication for plan:** Task 5 (codex-classify.sh) uses the chosen mechanism. If Anthropic SDK fallback chosen, see Task 5b below.
```

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/research/codex-image-input.md
git commit -m "research(pr-b): document codex CLI image input mechanism for photo-classifier"
```

---

## Task 1: `render-prompt.py` — placeholder substitution (foundational utility)

**Why:** Every codex template (classify, match, generate-fallback) contains `[VISUAL_STYLE]`, `[BRAND_PRIMARY]`, etc. placeholders. This is the single substitution point — TDD-tested, used everywhere.

**Files:**
- Create: `skills/photo-curation/scripts/render-prompt.py`
- Create: `tests/phase-prb/test-render-prompt.py`
- Create: `tests/phase-prb/__init__.py` (empty)
- Create: `tests/phase-prb/conftest.py`

- [ ] **Step 1: Create test scaffold**

`tests/phase-prb/__init__.py`:
```python
```

`tests/phase-prb/conftest.py`:
```python
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
```

- [ ] **Step 2: Write failing test**

`tests/phase-prb/test-render-prompt.py`:
```python
"""Tests for skills/photo-curation/scripts/render-prompt.py"""
from pathlib import Path
import pytest

from skills.photo_curation.scripts.render_prompt import render, MissingPlaceholderError


def test_render_substitutes_single_placeholder():
    template = "Brand primary is [BRAND_PRIMARY]."
    context = {"BRAND_PRIMARY": "#c47a3a"}
    assert render(template, context) == "Brand primary is #c47a3a."


def test_render_substitutes_multiple_placeholders():
    template = "[VISUAL_STYLE] | [BRAND_PRIMARY] | [NICHE]"
    context = {"VISUAL_STYLE": "Minimalism", "BRAND_PRIMARY": "#000", "NICHE": "services"}
    assert render(template, context) == "Minimalism | #000 | services"


def test_render_leaves_unknown_placeholders_alone_by_default():
    template = "Known [BRAND_PRIMARY] unknown [MYSTERY]"
    context = {"BRAND_PRIMARY": "#fff"}
    # Strict=False default → unknown stays
    assert render(template, context) == "Known #fff unknown [MYSTERY]"


def test_render_strict_raises_on_unknown_placeholder():
    template = "Known [BRAND_PRIMARY] unknown [MYSTERY]"
    context = {"BRAND_PRIMARY": "#fff"}
    with pytest.raises(MissingPlaceholderError, match="MYSTERY"):
        render(template, context, strict=True)


def test_render_does_not_substitute_inside_brackets_of_unsupported_pattern():
    # Only [UPPER_SNAKE] style is recognized — Markdown links and others left alone.
    template = "[link text](http://x) and [BRAND_PRIMARY]"
    context = {"BRAND_PRIMARY": "#abc"}
    assert render(template, context) == "[link text](http://x) and #abc"


def test_render_handles_repeated_placeholder():
    template = "[BRAND_PRIMARY] and again [BRAND_PRIMARY]"
    context = {"BRAND_PRIMARY": "#0f0"}
    assert render(template, context) == "#0f0 and again #0f0"


def test_load_context_merges_tokens_design_niche(tmp_path):
    from skills.photo_curation.scripts.render_prompt import load_context

    project = tmp_path / "proj"
    (project / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (project / "01a_АНАЛИЗ_НИШИ").mkdir(parents=True)
    (project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(
        '{"colors": {"primary": "#c47a3a", "accent": "#1e3a8a"}, "design": {"visual_style": "Minimalism"}}'
    )
    (project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").write_text("# Design\n\n**Mood:** premium and calm\n")
    (project / "01a_АНАЛИЗ_НИШИ" / "market-profile.md").write_text("# Profile\n\n**Niche:** услуги\n")
    (project / "01a_АНАЛИЗ_НИШИ" / "positioning.md").write_text("# Positioning\n\n**Audience:** owners 35-50\n")

    ctx = load_context(project)
    assert ctx["BRAND_PRIMARY"] == "#c47a3a"
    assert ctx["BRAND_ACCENT"] == "#1e3a8a"
    assert ctx["VISUAL_STYLE"] == "Minimalism"
    assert "premium and calm" in ctx["BRAND_MOOD"]
    assert ctx["NICHE"] == "услуги"
    assert "owners 35-50" in ctx["AUDIENCE"]
```

- [ ] **Step 3: Run tests — verify they fail**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
python3 -m pytest tests/phase-prb/test-render-prompt.py -v
```

Expected: `ModuleNotFoundError: No module named 'skills.photo_curation'`.

- [ ] **Step 4: Implement render-prompt.py**

Create `skills/photo-curation/__init__.py` (empty) and `skills/photo-curation/scripts/__init__.py` (empty).

Create `skills/photo-curation/scripts/render-prompt.py`:
```python
#!/usr/bin/env python3
"""Render codex prompt templates: substitute [PLACEHOLDER] tokens from context.

Used by all 3 PR-B codex wrappers (classify, match, generate-fallback) as the
SINGLE substitution point so prompts stay consistent across the pipeline.
"""
import json
import re
import sys
from pathlib import Path
from typing import Mapping


# Match [UPPER_SNAKE_CASE] — at least 2 chars, uppercase + digits + underscore.
PLACEHOLDER_RE = re.compile(r"\[([A-Z][A-Z0-9_]{1,})\]")


class MissingPlaceholderError(ValueError):
    """Raised when strict=True and a placeholder has no value in context."""


def render(template: str, context: Mapping[str, str], strict: bool = False) -> str:
    """Substitute every [TOKEN] in template with context[TOKEN].

    Unknown tokens are left intact when strict=False (default).
    """
    def _sub(match: re.Match) -> str:
        key = match.group(1)
        if key in context:
            return str(context[key])
        if strict:
            raise MissingPlaceholderError(f"Placeholder [{key}] has no value in context")
        return match.group(0)

    return PLACEHOLDER_RE.sub(_sub, template)


def load_context(project_dir: Path) -> dict:
    """Read tokens.json + DESIGN.md + market-profile.md + positioning.md into context dict.

    Returns dict with keys: BRAND_PRIMARY, BRAND_ACCENT, VISUAL_STYLE, BRAND_MOOD,
    LIGHTING, COLOR_GRADING, NICHE, AUDIENCE.
    """
    project_dir = Path(project_dir)

    ctx: dict[str, str] = {}

    tokens_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    if tokens_path.exists():
        tokens = json.loads(tokens_path.read_text())
        ctx["BRAND_PRIMARY"] = tokens.get("colors", {}).get("primary", "")
        ctx["BRAND_ACCENT"] = tokens.get("colors", {}).get("accent", "")
        ctx["VISUAL_STYLE"] = tokens.get("design", {}).get("visual_style", "")

    design_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    if design_path.exists():
        design = design_path.read_text()
        m = re.search(r"\*\*Mood:\*\*\s*(.+)$", design, re.MULTILINE)
        if m:
            ctx["BRAND_MOOD"] = m.group(1).strip()

    profile_path = project_dir / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
    if profile_path.exists():
        profile = profile_path.read_text()
        m = re.search(r"\*\*Niche:\*\*\s*(.+)$", profile, re.MULTILINE)
        if m:
            ctx["NICHE"] = m.group(1).strip()

    pos_path = project_dir / "01a_АНАЛИЗ_НИШИ" / "positioning.md"
    if pos_path.exists():
        pos = pos_path.read_text()
        m = re.search(r"\*\*Audience:\*\*\s*(.+)$", pos, re.MULTILINE)
        if m:
            ctx["AUDIENCE"] = m.group(1).strip()

    # Derived
    ctx.setdefault("LIGHTING", _derive_lighting(ctx.get("BRAND_MOOD", "")))
    ctx.setdefault("COLOR_GRADING", _derive_color_grading(ctx.get("BRAND_PRIMARY", ""), ctx.get("BRAND_ACCENT", ""), ctx.get("BRAND_MOOD", "")))

    return ctx


def _derive_lighting(mood: str) -> str:
    mood_l = mood.lower()
    if "premium" in mood_l or "editorial" in mood_l:
        return "Soft studio with controlled rim light"
    if "vibrant" in mood_l or "bold" in mood_l:
        return "Bright daylight, high contrast"
    if "calm" in mood_l or "minimal" in mood_l:
        return "Even diffuse natural light"
    return "Natural daylight, soft shadows"


def _derive_color_grading(primary: str, accent: str, mood: str) -> str:
    parts = []
    if primary:
        parts.append(f"primary accent {primary}")
    if accent:
        parts.append(f"secondary accent {accent}")
    if "premium" in mood.lower():
        parts.append("low saturation, deep blacks")
    return ", ".join(parts) if parts else "neutral grading"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("template", help="Path to template .md file")
    ap.add_argument("project", help="Path to project root")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    template_text = Path(args.template).read_text()
    ctx = load_context(Path(args.project))
    sys.stdout.write(render(template_text, ctx, strict=args.strict))


if __name__ == "__main__":
    main()
```

Note: Python module name must be `photo_curation` not `photo-curation` (dashes invalid). The directory is `skills/photo-curation/` but import via `sys.path` trick. Create symlink or use importlib path-based load. Simplest: add to `tests/phase-prb/conftest.py`:

```python
import sys, importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Map dashed dir to underscored module name
_RP_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "render-prompt.py"
_spec = importlib.util.spec_from_file_location("skills.photo_curation.scripts.render_prompt", _RP_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
sys.modules["skills.photo_curation"] = type(sys)("skills.photo_curation")
sys.modules["skills.photo_curation.scripts"] = type(sys)("skills.photo_curation.scripts")
sys.modules["skills.photo_curation.scripts.render_prompt"] = _mod
```

This lets tests `from skills.photo_curation.scripts.render_prompt import render` even though directory has dashes.

- [ ] **Step 5: Run tests — verify they pass**

```bash
python3 -m pytest tests/phase-prb/test-render-prompt.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/photo-curation/scripts/render-prompt.py skills/photo-curation/__init__.py skills/photo-curation/scripts/__init__.py tests/phase-prb/
git commit -m "feat(pr-b): render-prompt.py — codex template placeholder substitution"
```

---

## Task 2: `intake.py` — HEIC→JPEG, EXIF strip, dedupe, folder-tag detection

**Files:**
- Create: `skills/photo-curation/scripts/intake.py`
- Create: `tests/phase-prb/test-intake.py`
- Create: `tests/phase-prb/fixtures/sample.jpg` (will create in step 1)

- [ ] **Step 1: Create test fixture**

```bash
mkdir -p tests/phase-prb/fixtures
python3 -c "
from PIL import Image
img = Image.new('RGB', (100, 100), (255, 0, 0))
img.save('tests/phase-prb/fixtures/red.jpg')
img2 = Image.new('RGB', (200, 200), (0, 255, 0))
img2.save('tests/phase-prb/fixtures/green.jpg')
"
```

- [ ] **Step 2: Write failing test**

`tests/phase-prb/test-intake.py`:
```python
"""Tests for skills/photo-curation/scripts/intake.py"""
import json
import shutil
from pathlib import Path

import pytest
import yaml

from skills.photo_curation.scripts.intake import (
    run_intake,
    SUBFOLDER_TO_TAG,
    INTAKE_SUBFOLDERS,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_subfolder_constants_match_spec():
    # Spec D10: 7 subfolders + _свалка
    assert len(INTAKE_SUBFOLDERS) == 8
    assert "_свалка" in INTAKE_SUBFOLDERS
    assert "портреты_и_команда" in INTAKE_SUBFOLDERS
    assert SUBFOLDER_TO_TAG["портреты_и_команда"] == ["portrait", "team"]


def test_intake_copies_subfolder_photo_with_folder_tag(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "портреты_и_команда"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "ceo.jpg")

    intake_dir = src / "intake"
    report = run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    # 1 file in intake/, named by hash, no _orig metadata
    jpgs = list(intake_dir.glob("*.jpg"))
    assert len([p for p in jpgs if not p.name.endswith(".thumb.jpg")]) == 1
    assert (intake_dir / "intake-report.yaml").exists()

    rpt = yaml.safe_load((intake_dir / "intake-report.yaml").read_text())
    assert len(rpt["photos"]) == 1
    photo = rpt["photos"][0]
    assert photo["original_name"] == "ceo.jpg"
    assert photo["folder_origin"] == "портреты_и_команда"
    assert photo["tag_source"] == "folder"
    assert sorted(photo["tags"]) == ["portrait", "team"]


def test_intake_dumps_unsorted_photo_as_unclassified(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "green.jpg", inbox / "random.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    rpt = yaml.safe_load((intake_dir / "intake-report.yaml").read_text())
    photo = rpt["photos"][0]
    assert photo["folder_origin"] == "_свалка"
    assert photo["tag_source"] == "pending_ai_classify"
    assert photo["tags"] == []


def test_intake_dedupes_by_hash(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "first.jpg")
    shutil.copy(FIXTURES / "red.jpg", inbox / "duplicate.jpg")
    shutil.copy(FIXTURES / "green.jpg", inbox / "unique.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    rpt = yaml.safe_load((intake_dir / "intake-report.yaml").read_text())
    assert len(rpt["photos"]) == 2  # red deduped
    red_entry = next(p for p in rpt["photos"] if "first.jpg" in p["duplicates"] + [p["original_name"]])
    assert "duplicate.jpg" in red_entry["duplicates"] or "first.jpg" in red_entry["duplicates"]


def test_intake_creates_thumbnail(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "x.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    thumbs = list(intake_dir.glob("*.thumb.jpg"))
    assert len(thumbs) == 1
    from PIL import Image
    with Image.open(thumbs[0]) as img:
        assert max(img.size) == 256


def test_intake_idempotent(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "x.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)
    first_files = sorted(p.name for p in intake_dir.iterdir())

    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)
    second_files = sorted(p.name for p in intake_dir.iterdir())

    assert first_files == second_files
```

Add the same `conftest.py` import mapping for `intake` as for `render_prompt`.

- [ ] **Step 3: Run tests — verify they fail**

```bash
python3 -m pytest tests/phase-prb/test-intake.py -v
```

Expected: `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 4: Implement intake.py**

`skills/photo-curation/scripts/intake.py`:
```python
#!/usr/bin/env python3
"""Photo intake: copy from inbox/ subfolders into intake/, dedupe, generate thumbnails.

- HEIC→JPEG via `sips` (macOS); on other OS, skip with warning.
- EXIF strip (removes GPS, camera serial, etc.).
- SHA-256 dedupe.
- Folder-tag detection: file in inbox/X/ inherits X's folder-tag.
- Generates 256px thumbnails for HTML gallery.
- Idempotent: re-runs skip already-processed files (by hash).
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import yaml
from PIL import Image, ExifTags


INTAKE_SUBFOLDERS = [
    "_свалка",
    "портреты_и_команда",
    "процесс_работы",
    "объекты_и_продукты",
    "интерьер_экстерьер",
    "до_после",
    "документы_сертификаты",
]


SUBFOLDER_TO_TAG = {
    "портреты_и_команда": ["portrait", "team"],
    "процесс_работы": ["process"],
    "объекты_и_продукты": ["object"],
    "интерьер_экстерьер": ["interior", "exterior"],
    "до_после": ["before-after"],
    "документы_сертификаты": ["document"],
    "_свалка": [],
}


THUMB_SIZE = 256
MAX_DIMENSION = 4096
SUPPORTED_INPUTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _heic_to_jpeg(src: Path, dst: Path) -> bool:
    """Use macOS sips. Returns True on success, False if sips not available."""
    try:
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(src), "--out", str(dst)],
            check=True, capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _strip_exif_and_save(src: Path, dst: Path) -> None:
    img = Image.open(src)
    # Resize if too large
    if max(img.size) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    # Save without EXIF
    data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(data)
    img_no_exif.save(dst, "JPEG", quality=88)


def _make_thumb(src: Path, dst: Path) -> None:
    img = Image.open(src)
    img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
    img.save(dst, "JPEG", quality=80)


def _enumerate_input_files(inbox_root: Path) -> Iterable[tuple[Path, str]]:
    """Yield (file_path, folder_name) for every supported file in inbox subfolders."""
    if not inbox_root.exists():
        return
    for sub in INTAKE_SUBFOLDERS:
        sub_dir = inbox_root / sub
        if not sub_dir.exists():
            continue
        for f in sub_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in SUPPORTED_INPUTS:
                yield f, sub


def run_intake(inbox_root: Path, intake_dir: Path) -> dict:
    """Process all files in inbox_root subfolders → intake_dir.

    Returns the intake report dict (also written to intake_dir/intake-report.yaml).
    Idempotent: files whose hash already appears in existing report are skipped.
    """
    inbox_root = Path(inbox_root)
    intake_dir = Path(intake_dir)
    intake_dir.mkdir(parents=True, exist_ok=True)

    report_path = intake_dir / "intake-report.yaml"
    if report_path.exists():
        report = yaml.safe_load(report_path.read_text()) or {"photos": []}
    else:
        report = {"photos": []}

    known_hashes = {p["hash"]: p for p in report["photos"]}

    for src, sub in _enumerate_input_files(inbox_root):
        h = _hash_file(src)

        if h in known_hashes:
            # Already processed — add as duplicate if originating filename differs.
            entry = known_hashes[h]
            if src.name not in entry.get("duplicates", []) and src.name != entry["original_name"]:
                entry.setdefault("duplicates", []).append(src.name)
            continue

        intake_id = f"photo_{h}"
        intake_jpg = intake_dir / f"{intake_id}.jpg"
        intake_thumb = intake_dir / f"{intake_id}.thumb.jpg"

        # Convert HEIC if needed
        if src.suffix.lower() in {".heic", ".heif"}:
            tmp_jpg = intake_dir / f"_tmp_{intake_id}.jpg"
            if not _heic_to_jpeg(src, tmp_jpg):
                print(f"WARN: HEIC conversion failed for {src} (sips unavailable). Skipping.", file=sys.stderr)
                continue
            _strip_exif_and_save(tmp_jpg, intake_jpg)
            tmp_jpg.unlink()
        else:
            _strip_exif_and_save(src, intake_jpg)

        _make_thumb(intake_jpg, intake_thumb)

        with Image.open(intake_jpg) as img:
            w, h_img = img.size

        tags = SUBFOLDER_TO_TAG[sub]
        entry = {
            "id": intake_id,
            "hash": h,
            "path": str(intake_jpg.relative_to(intake_dir.parent)),
            "thumb_path": str(intake_thumb.relative_to(intake_dir.parent)),
            "original_name": src.name,
            "folder_origin": sub,
            "tag_source": "folder" if tags else "pending_ai_classify",
            "tags": tags,
            "dimensions": [w, h_img],
            "duplicates": [],
        }
        report["photos"].append(entry)
        known_hashes[h] = entry

    report_path.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False))
    return report


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", required=True, help="Path to inbox/ root (contains subfolders)")
    ap.add_argument("--intake", required=True, help="Path to intake/ output dir")
    args = ap.parse_args()

    report = run_intake(Path(args.inbox), Path(args.intake))
    print(f"Intake done: {len(report['photos'])} unique photos")


if __name__ == "__main__":
    main()
```

Add intake module mapping in `tests/phase-prb/conftest.py` (same pattern as render_prompt).

- [ ] **Step 5: Run tests — verify they pass**

```bash
python3 -m pytest tests/phase-prb/test-intake.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/photo-curation/scripts/intake.py tests/phase-prb/test-intake.py tests/phase-prb/fixtures/
git commit -m "feat(pr-b): intake.py — HEIC/EXIF/dedupe/folder-tag for photo pipeline"
```

---

## Task 3: Skill scaffold — SKILL.md, IDENTITY_SAFE.md, 3 prompt templates

**Files:**
- Create: `skills/photo-curation/SKILL.md`
- Create: `skills/photo-curation/IDENTITY_SAFE.md`
- Create: `skills/photo-curation/templates/classify-prompt.md`
- Create: `skills/photo-curation/templates/match-prompt.md`
- Create: `skills/photo-curation/templates/generate-fallback.md`
- Create: `tests/phase-prb/test-templates-shape.py`

- [ ] **Step 1: Write test that validates template files exist and have required sections**

`tests/phase-prb/test-templates-shape.py`:
```python
"""Validate the 3 codex prompt templates have the required structure."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "skills" / "photo-curation" / "templates"

REQUIRED_SECTIONS = ["## How to use", "## Placeholders", "## Prompt body", "## Filled example"]


def test_classify_template_has_all_sections():
    body = (TEMPLATES / "classify-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"classify-prompt.md missing section: {s}"


def test_match_template_has_all_sections():
    body = (TEMPLATES / "match-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"match-prompt.md missing section: {s}"


def test_generate_fallback_has_all_sections():
    body = (TEMPLATES / "generate-fallback.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"generate-fallback.md missing section: {s}"


def test_generate_fallback_includes_anti_patterns_from_open_design():
    body = (TEMPLATES / "generate-fallback.md").read_text()
    # Anti-pattern list (D11) — at least these phrases must be present
    for phrase in ["No lens flare", "No glitch", "No AI watermarks", "No surreal"]:
        assert phrase in body, f"generate-fallback.md missing anti-pattern: {phrase}"


def test_identity_safe_md_exists():
    p = REPO / "skills" / "photo-curation" / "IDENTITY_SAFE.md"
    assert p.exists()
    body = p.read_text()
    for phrase in ["NEVER alter the face", "NEVER AI-repaint", "ai_approved_by_user"]:
        assert phrase in body
```

- [ ] **Step 2: Run test — verify it fails**

```bash
python3 -m pytest tests/phase-prb/test-templates-shape.py -v
```

Expected: 5 tests FAIL (files don't exist).

- [ ] **Step 3: Create SKILL.md**

`skills/photo-curation/SKILL.md`:
```markdown
---
name: photo-curation
description: Stage 07c (PR-B) photo pipeline — intake, AI-classification via codex, AI-matching to wireframe slots, processing under design-system tokens, generative fallback. Owned by photo-curator agent.
---

# photo-curation

Конвейер обработки клиентских фоток для лендинга. Запускается командой `/landing-photos` после approved `05_design` + `07a_wireframe`.

## Этапы

1. **intake** — `scripts/intake.py` копирует фотки из `07c_PHOTOS/inbox/` подпапок в `07c_PHOTOS/intake/`. HEIC→JPEG, EXIF strip, dedupe, folder-tag.
2. **classify** — `scripts/codex-classify.sh` тегирует фотки из `_свалка/` через codex CLI (фото в подпапках уже имеют folder-tag).
3. **match** — `scripts/codex-match.sh` ранжирует кандидатов на каждый photo-слот из prototype.yaml + wireframe selections.
4. **approve** — пользователь открывает `photo-board.html` (рендерит `scripts/gallery-render.py`), правит выбор, скачивает `selections.yaml`.
5. **process** — `scripts/style.py` (расширенный) обрезает под `slots[].ratio` + `mobile_ratio`. Для AI-fallback слотов — `scripts/codex-generate-fallback.sh`.
6. **preview** — `scripts/preview-render.py` собирает `photo-preview.html` для финального approve.
7. **compose re-render** — `inject-content.py` (PR-A) читает `07c_PHOTOS/selections.yaml` и подставляет реальные фотки в `composed.html`.

## Identity-safe

См. [`IDENTITY_SAFE.md`](IDENTITY_SAFE.md). Кратко: клиентские фото никогда не репеинтятся; AI-генерация лиц требует явного `ai_approved_by_user: true`.

## State management

`07c_PHOTOS/STATE.yaml` отслеживает каждый этап. Перезапуск `/landing-photos` продолжает с прерванного. Принудительный сброс: `/landing-photos --force-stage <name>`.

## Templates

Три codex шаблона в `templates/` — повторяют формат `paralaximus-codex/templates/atlas-prompt.md`:
- `classify-prompt.md` — одна фотка → YAML с тегами
- `match-prompt.md` — каталог + слоты → ранжированные кандидаты
- `generate-fallback.md` — генерация под brand-tokens
```

- [ ] **Step 4: Create IDENTITY_SAFE.md**

`skills/photo-curation/IDENTITY_SAFE.md`:
```markdown
# Identity-safe rules for PR-B Photo Pipeline

## Absolute forbiddens (cannot be overridden)

- NEVER alter the face, age, body proportions, or skin of a real client photo.
- NEVER AI-repaint a person who appears in a client photo.
- NEVER swap a face.
- NEVER apply beauty retouching to client photos.

These rules apply to all agents: `photo-curator`, `photo-classifier`, `photo-matcher`, `photo-preview-board`, and the existing `photo-stylist`.

## AI fallback for portrait slots (testimonial / expert / team)

Default: AI fallback is BLOCKED unless `selections.yaml:ai_approved_by_user == true` for that slot.

The `photo-board.html` UI presents an explicit modal:

> Этот слот требует AI-сгенерированного лица человека. Согласен на использование AI? Это будет видно посетителям сайта как настоящий человек.
> 
> [ ] Да, согласен

Without the checkbox: the slot is processed with `strategy: placeholder` (an SVG placeholder, not AI).

## Future PR-B.1 (paralaximus client-photo)

When PR-B.1 lands:
- Subject layer = client cutout PNG, composited byte-for-byte. No AI modification.
- Background / far / near layers = AI-generated (environment around the subject only).
- If AI-generated background implicitly contains a person — regenerate without person.

## Audit

All AI-generated portrait slots have `log_ref` in `selections.yaml` pointing to `.logs/<timestamp>_generate.log` with the full prompt sent to codex. This enables post-hoc review.
```

- [ ] **Step 5: Create classify-prompt.md**

`skills/photo-curation/templates/classify-prompt.md`:
```markdown
# classify-prompt — photo tagging template

## How to use

1. Pass via codex CLI image input (mechanism per Task 0 research).
2. Substitute `[NICHE]`, `[AUDIENCE]`, `[VISUAL_STYLE]`, `[BRAND_PRIMARY]` via `render-prompt.py`.
3. Expect strict YAML output. Validate with `yaml.safe_load`.

## Placeholders

- `[NICHE]` — niche label from `01a_АНАЛИЗ_НИШИ/market-profile.md`
- `[AUDIENCE]` — audience description from `01a_АНАЛИЗ_НИШИ/positioning.md`
- `[VISUAL_STYLE]` — `tokens.json:design.visual_style`
- `[BRAND_PRIMARY]` — `tokens.json:colors.primary`

## Prompt body

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ ДО И ПОСЛЕ. НЕ ИСПОЛЬЗУЙ MARKDOWN CODE FENCES.

Ты анализируешь фотографию для лендинга в нише [NICHE], целевая аудитория [AUDIENCE].
Brand style: [VISUAL_STYLE], primary color [BRAND_PRIMARY].

Верни строго YAML со следующими ключами:
tags: список из набора [portrait, group, object, process, interior, exterior, before-after, document, team, abstract]
caption: одна строка на русском, до 100 символов, описывающая что на фото
face_count: число лиц на фото
composition: одно из [tight-portrait, medium-shot, wide-shot, object-only]
usable_ratios: список из [1:1, 4:3, 3:4, 16:9, 9:16] — где фото обрежется без потери сюжета
brand_compatible: одно из [yes, no, maybe] — насколько цвета/настроение фото подходят к brand style
notes: технические дефекты (размытие, шум, плохой свет) или пустая строка

Пример валидного ответа:
tags: [portrait, team]
caption: "Женщина 35 лет, улыбается, светлый офис на фоне"
face_count: 1
composition: medium-shot
usable_ratios: ["1:1", "3:4"]
brand_compatible: yes
notes: ""
```

## Filled example

(when [NICHE]=услуги, [AUDIENCE]=владельцы малого бизнеса 35-50, [VISUAL_STYLE]=Minimalism & Swiss Style, [BRAND_PRIMARY]=#1e3a8a):

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ ДО И ПОСЛЕ. НЕ ИСПОЛЬЗУЙ MARKDOWN CODE FENCES.

Ты анализируешь фотографию для лендинга в нише услуги, целевая аудитория владельцы малого бизнеса 35-50.
Brand style: Minimalism & Swiss Style, primary color #1e3a8a.

(... rest as above)
```
```

- [ ] **Step 6: Create match-prompt.md**

`skills/photo-curation/templates/match-prompt.md`:
```markdown
# match-prompt — photo-to-slot matcher template

## How to use

1. Build context: read `catalog.yaml`, `prototype.yaml` slots, `07a_WIREFRAME/selections.yaml`, `tokens.json`, market-profile, positioning.
2. Build `[CATALOG_YAML]` (dump catalog photos list) and `[SLOTS_YAML]` (dump active slots with hints).
3. Substitute via render-prompt.py.
4. Pass via codex CLI (text-only, no image input).
5. Validate output as YAML.

## Placeholders

- `[CATALOG_YAML]` — JSON/YAML dump of `catalog.yaml:photos`
- `[SLOTS_YAML]` — YAML dump of active photo slots (id, block_id, ratio, mobile_ratio, hint)
- `[BRAND_PRIMARY]`, `[VISUAL_STYLE]`, `[NICHE]`, `[AUDIENCE]` — from `render-prompt.load_context`

## Prompt body

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ.

Тебе дан каталог фотографий клиента и список photo-слотов из прототипа лендинга.
Подбери top-3 фото на каждый слот. Если для слота ни одна фотка не подходит — candidates=[] и ai_fallback_needed=true.

Каталог:
[CATALOG_YAML]

Слоты:
[SLOTS_YAML]

Brand context:
- primary: [BRAND_PRIMARY]
- visual_style: [VISUAL_STYLE]
- niche: [NICHE]
- audience: [AUDIENCE]

Правила matching:
- ratio фото (после crop) должно совпадать или близко к slot.ratio
- tag фото должен соответствовать hint слота
- testimonial-* / expert-* / team-* слоты (identity-safe) требуют tag=portrait или group, face_count>=1
- hero-bg требует composition=wide-shot, usable_ratios содержит 16:9
- безопасные слоты (background, process, abstract, interior) — AI-fallback по умолчанию ok
- identity-safe слоты — AI-fallback только если явно нет фотки; required_user_approval=true
- если ai_fallback_needed=true → собери ai_prompt под design-system и slot.hint (1-2 предложения на английском)

Верни YAML:
slots:
  - slot_id: <string>
    candidates:
      - {photo_id: <string>, score: <float 0-1>, reason: <string>}
    ai_fallback_needed: <bool>
    required_user_approval: <bool>
    ai_prompt: <string or null>
```

## Filled example

```
(slots from a small services landing with 1 hero, 2 testimonials, 1 process step photo,
catalog with 12 photos — see tests/phase-prb/fixtures/match-example/)
```
```

- [ ] **Step 7: Create generate-fallback.md**

`skills/photo-curation/templates/generate-fallback.md`:
```markdown
# generate-fallback — codex image_gen for missing slots

## How to use

1. Pass to `codex-generate-fallback.sh` (which clones `generate-atlas.sh` pattern: snapshot ~/.codex/generated_images/, exec codex, copy fresh PNG).
2. Substitute placeholders via render-prompt.py.
3. Output PNG → `processed/<slot_id>/ai-generated.jpg`. Also save the rendered prompt as `ai-prompt.txt` next to it.

## Placeholders

- `[WIDTH]`, `[HEIGHT]` — pixel dimensions
- `[RATIO]` — e.g. "16:9"
- `[SLOT_HINT]` — block-library `meta.yaml:slots[].name` + photo_hint
- `[VISUAL_STYLE]`, `[BRAND_MOOD]`, `[LIGHTING]`, `[COLOR_GRADING]` — from `tokens.json` + `DESIGN.md`
- `[NICHE]`, `[AUDIENCE]` — from niche analysis

## Prompt body

```
Use the built-in image_gen tool. Generate ONE PNG, size [WIDTH]x[HEIGHT] (ratio [RATIO]),
for slot "[SLOT_HINT]" on a landing page in [NICHE] niche, audience [AUDIENCE].

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: [VISUAL_STYLE]
BRAND MOOD: [BRAND_MOOD]
LIGHTING: [LIGHTING]
COLOR GRADING: [COLOR_GRADING]

FORBIDDEN (anti-patterns adapted from nexu-io/open-design DESIGN.md, Apache-2.0):
- No lens flare
- No glitch effects, no chromatic aberration
- No photoreal human faces UNLESS this is explicitly a portrait slot AND user has approved AI face generation (see IDENTITY_SAFE.md)
- No AI watermarks (no "AI", "Midjourney", "DALL-E" visual signatures)
- No cartoonish or anime style unless brand mood demands it
- No surreal melting or flowing artifacts
- No double exposures
- Photoreal premium editorial / commercial digital art quality
```

## Filled example

For a services landing's hero-bg slot, 1920x1080, 16:9, Minimalism style:

```
Use the built-in image_gen tool. Generate ONE PNG, size 1920x1080 (ratio 16:9),
for slot "hero-bg" on a landing page in услуги niche, audience владельцы малого бизнеса 35-50.

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: Minimalism & Swiss Style
BRAND MOOD: premium and calm
LIGHTING: Soft studio with controlled rim light
COLOR GRADING: primary accent #1e3a8a, low saturation, deep blacks

FORBIDDEN (...full list...)
```
```

- [ ] **Step 8: Run test — verify it passes**

```bash
python3 -m pytest tests/phase-prb/test-templates-shape.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add skills/photo-curation/SKILL.md skills/photo-curation/IDENTITY_SAFE.md skills/photo-curation/templates/ tests/phase-prb/test-templates-shape.py
git commit -m "feat(pr-b): skill scaffold + 3 codex prompt templates + IDENTITY_SAFE.md"
```

---

## Task 4: SVG placeholder generator (open-design pattern port)

**Files:**
- Create: `skills/photo-curation/scripts/svg-placeholder.py`
- Create: `tests/phase-prb/test-svg-placeholder.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prb/test-svg-placeholder.py`:
```python
"""Tests for SVG placeholder generator (ports open-design placeholder.ts pattern)."""
from pathlib import Path

from skills.photo_curation.scripts.svg_placeholder import (
    make_placeholder_svg,
    write_placeholder,
)


def test_make_placeholder_returns_svg_string():
    svg = make_placeholder_svg(
        slot_id="hero-bg",
        width=1920, height=1080,
        hint="Фото объекта услуги",
        brand_primary="#1e3a8a",
    )
    assert svg.startswith("<svg")
    assert "</svg>" in svg
    assert "hero-bg" in svg
    assert "Фото объекта услуги" in svg
    assert "#1e3a8a" in svg


def test_make_placeholder_includes_dimensions(tmp_path):
    svg = make_placeholder_svg(slot_id="x", width=400, height=300, hint="h", brand_primary="#000")
    assert 'width="400"' in svg
    assert 'height="300"' in svg


def test_write_placeholder_saves_under_png_filename(tmp_path):
    # Port of open-design trick: svg content saved with .png extension.
    out = tmp_path / "slot.png"
    write_placeholder(
        out_path=out,
        slot_id="testimonial-1",
        width=500, height=500,
        hint="Аватар клиента",
        brand_primary="#c47a3a",
    )
    assert out.exists()
    content = out.read_bytes()
    assert content.startswith(b"<svg") or content.startswith(b"<?xml")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
python3 -m pytest tests/phase-prb/test-svg-placeholder.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement svg-placeholder.py**

`skills/photo-curation/scripts/svg-placeholder.py`:
```python
#!/usr/bin/env python3
"""SVG placeholder generator. Ports nexu-io/open-design placeholder.ts pattern
(Apache-2.0) — writes SVG content under a .png filename so `<img src="x.png">`
keeps working in HTML without an actual raster image.
"""
from pathlib import Path
from html import escape


SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <pattern id="paper" patternUnits="userSpaceOnUse" width="40" height="40">
      <rect width="40" height="40" fill="{bg}" />
      <circle cx="10" cy="10" r="1" fill="{fg}" opacity="0.15" />
      <circle cx="30" cy="30" r="1" fill="{fg}" opacity="0.15" />
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#paper)" />
  <rect x="2" y="2" width="{wm2}" height="{hm2}" fill="none" stroke="{fg}" stroke-width="2" stroke-dasharray="8 8" opacity="0.4" />
  <text x="{cx}" y="{cy_id}" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI" font-size="{fs_id}" fill="{fg}" text-anchor="middle" font-weight="600">{slot_id}</text>
  <text x="{cx}" y="{cy_hint}" font-family="ui-sans-serif, system-ui" font-size="{fs_hint}" fill="{fg}" text-anchor="middle" opacity="0.7">{hint}</text>
  <text x="{cx}" y="{cy_size}" font-family="ui-monospace, monospace" font-size="{fs_size}" fill="{fg}" text-anchor="middle" opacity="0.4">{width}×{height}</text>
</svg>"""


def make_placeholder_svg(
    slot_id: str,
    width: int,
    height: int,
    hint: str,
    brand_primary: str = "#888888",
) -> str:
    cx = width // 2
    cy_id = int(height * 0.4)
    cy_hint = int(height * 0.5)
    cy_size = int(height * 0.62)
    fs_id = max(14, int(min(width, height) * 0.06))
    fs_hint = max(11, int(min(width, height) * 0.035))
    fs_size = max(10, int(min(width, height) * 0.025))

    bg = "#f5f5f4"
    return SVG_TEMPLATE.format(
        width=width, height=height,
        wm2=width - 4, hm2=height - 4,
        cx=cx, cy_id=cy_id, cy_hint=cy_hint, cy_size=cy_size,
        fs_id=fs_id, fs_hint=fs_hint, fs_size=fs_size,
        slot_id=escape(slot_id), hint=escape(hint),
        bg=bg, fg=brand_primary,
    )


def write_placeholder(out_path: Path, slot_id: str, width: int, height: int, hint: str, brand_primary: str = "#888888") -> None:
    svg = make_placeholder_svg(slot_id, width, height, hint, brand_primary)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(svg, encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot-id", required=True)
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--hint", default="")
    ap.add_argument("--brand-primary", default="#888888")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    write_placeholder(Path(args.out), args.slot_id, args.width, args.height, args.hint, args.brand_primary)


if __name__ == "__main__":
    main()
```

Add module mapping in conftest.py.

- [ ] **Step 4: Run test — verify it passes**

```bash
python3 -m pytest tests/phase-prb/test-svg-placeholder.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/photo-curation/scripts/svg-placeholder.py tests/phase-prb/test-svg-placeholder.py
git commit -m "feat(pr-b): SVG placeholder generator (port of open-design placeholder.ts, Apache-2.0)"
```

---

## Task 5: 3 codex CLI wrappers (classify / match / generate-fallback)

**Files:**
- Create: `skills/photo-curation/scripts/call-codex.sh` (shared base)
- Create: `skills/photo-curation/scripts/codex-classify.sh`
- Create: `skills/photo-curation/scripts/codex-match.sh`
- Create: `skills/photo-curation/scripts/codex-generate-fallback.sh`
- Create: `tests/phase-prb/test-codex-wrappers.bats`
- Create: `tests/phase-prb/fixtures/codex-mock.sh`

- [ ] **Step 1: Create codex mock fixture**

`tests/phase-prb/fixtures/codex-mock.sh`:
```bash
#!/usr/bin/env bash
# codex-mock — captures arguments and prints canned response based on env $CODEX_MOCK_RESPONSE
echo "MOCK_CODEX_CALLED" >&2
echo "ARGS: $*" >&2
if [ -n "${CODEX_MOCK_RESPONSE:-}" ]; then
    echo "$CODEX_MOCK_RESPONSE"
else
    echo "tags: [portrait]"
    echo "caption: \"Mock photo description\""
    echo "face_count: 1"
fi
exit 0
```

```bash
chmod +x tests/phase-prb/fixtures/codex-mock.sh
```

- [ ] **Step 2: Write failing bats test**

`tests/phase-prb/test-codex-wrappers.bats`:
```bash
#!/usr/bin/env bats
# Tests for codex CLI wrappers.

setup() {
    REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
    MOCK="$REPO_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    export CODEX_BIN="$MOCK"
    TMP_PROJECT="$(mktemp -d)"
    mkdir -p "$TMP_PROJECT/07c_PHOTOS/.logs"
    mkdir -p "$TMP_PROJECT/07c_PHOTOS/intake"
    mkdir -p "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА"
    echo '{"colors":{"primary":"#1e3a8a"},"design":{"visual_style":"Minimalism"}}' > "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
}

teardown() {
    rm -rf "$TMP_PROJECT"
}

@test "codex-classify.sh calls codex and writes catalog entry" {
    # Create dummy photo
    cp "$REPO_ROOT/tests/phase-prb/fixtures/red.jpg" "$TMP_PROJECT/07c_PHOTOS/intake/photo_test.jpg"

    export CODEX_MOCK_RESPONSE='tags: [portrait]
caption: "Test"
face_count: 1
composition: medium-shot
usable_ratios: ["1:1"]
brand_compatible: yes
notes: ""'

    run bash "$REPO_ROOT/skills/photo-curation/scripts/codex-classify.sh" \
        "$TMP_PROJECT" "$TMP_PROJECT/07c_PHOTOS/intake/photo_test.jpg"
    [ "$status" -eq 0 ]
    # Catalog entry appended
    [ -f "$TMP_PROJECT/07c_PHOTOS/catalog.yaml" ]
    grep -q "photo_test" "$TMP_PROJECT/07c_PHOTOS/catalog.yaml"
}

@test "codex-match.sh produces selections.draft.yaml" {
    # Stub catalog + slots
    cat > "$TMP_PROJECT/07c_PHOTOS/catalog.yaml" <<'EOF'
photos:
  - id: photo_001
    tags: [portrait]
    caption: ""
    usable_ratios: ["1:1"]
EOF
    cat > "$TMP_PROJECT/07c_PHOTOS/_slots-input.yaml" <<'EOF'
slots:
  - slot_id: hero-bg
    block_id: ru-hero-01
    ratio: "16:9"
    hint: object photo
EOF

    export CODEX_MOCK_RESPONSE='slots:
  - slot_id: hero-bg
    candidates: []
    ai_fallback_needed: true
    required_user_approval: false
    ai_prompt: "test prompt"'

    run bash "$REPO_ROOT/skills/photo-curation/scripts/codex-match.sh" \
        "$TMP_PROJECT" \
        "$TMP_PROJECT/07c_PHOTOS/catalog.yaml" \
        "$TMP_PROJECT/07c_PHOTOS/_slots-input.yaml"
    [ "$status" -eq 0 ]
    [ -f "$TMP_PROJECT/07c_PHOTOS/selections.draft.yaml" ]
    grep -q "hero-bg" "$TMP_PROJECT/07c_PHOTOS/selections.draft.yaml"
}

@test "codex-generate-fallback.sh creates PNG output" {
    skip "Requires real codex CLI with image_gen — covered by E2E only"
}

@test "all 3 wrappers log to 07c_PHOTOS/.logs/" {
    cp "$REPO_ROOT/tests/phase-prb/fixtures/red.jpg" "$TMP_PROJECT/07c_PHOTOS/intake/photo_x.jpg"
    export CODEX_MOCK_RESPONSE='tags: [object]
caption: "x"
face_count: 0
composition: object-only
usable_ratios: ["1:1"]
brand_compatible: yes
notes: ""'
    bash "$REPO_ROOT/skills/photo-curation/scripts/codex-classify.sh" \
        "$TMP_PROJECT" "$TMP_PROJECT/07c_PHOTOS/intake/photo_x.jpg"
    [ "$(ls -1 "$TMP_PROJECT/07c_PHOTOS/.logs/" | wc -l)" -gt 0 ]
}
```

- [ ] **Step 3: Run test — verify it fails**

```bash
bats tests/phase-prb/test-codex-wrappers.bats
```

Expected: scripts not found.

- [ ] **Step 4: Implement call-codex.sh (shared base)**

`skills/photo-curation/scripts/call-codex.sh`:
```bash
#!/usr/bin/env bash
# call-codex.sh — shared wrapper for codex exec with retry + logging.
#
# Usage:
#   bash call-codex.sh <project_dir> <stage> <prompt_file> [--image <path>]
#
# Outputs codex stdout to stdout. Logs full prompt + response to:
#   <project_dir>/07c_PHOTOS/.logs/YYYY-MM-DD_HHMMSS_<stage>.log

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
STAGE="${2:?ERROR: stage name required (classify|match|generate)}"
PROMPT_FILE="${3:?ERROR: prompt_file required}"
shift 3

IMAGE_PATH=""
while [ $# -gt 0 ]; do
    case "$1" in
        --image) IMAGE_PATH="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

CODEX_BIN="${CODEX_BIN:-codex}"
LOGS_DIR="$PROJECT_DIR/07c_PHOTOS/.logs"
mkdir -p "$LOGS_DIR"
TS="$(date +%Y-%m-%d_%H%M%S)"
LOG="$LOGS_DIR/${TS}_${STAGE}.log"

PROMPT="$(cat "$PROMPT_FILE")"

{
    echo "=== STAGE: $STAGE ==="
    echo "=== TIMESTAMP: $(date -Iseconds) ==="
    echo "=== IMAGE_PATH: ${IMAGE_PATH:-<none>} ==="
    echo "=== PROMPT ==="
    echo "$PROMPT"
    echo "=== RESPONSE ==="
} > "$LOG"

# Build codex args. Image input mechanism per Task 0 research — DEFAULTS BELOW
# MAY NEED ADJUSTMENT after research completes.
CODEX_ARGS=("exec" "--skip-git-repo-check")
if [ -n "$IMAGE_PATH" ]; then
    # Mechanism A (preferred): native image flag. Update after Task 0.
    # If not supported, switch to mechanism B/C per research findings.
    PROMPT="Look at the image at $IMAGE_PATH and follow these instructions:

$PROMPT"
fi

# Retry up to 2 times for transient failures
RC=0
for attempt in 1 2; do
    if RESPONSE=$("$CODEX_BIN" "${CODEX_ARGS[@]}" "$PROMPT" 2>>"$LOG"); then
        echo "$RESPONSE" | tee -a "$LOG"
        exit 0
    fi
    RC=$?
    echo "WARN: codex exec attempt $attempt failed (rc=$RC). Retrying..." >&2
    sleep 2
done

echo "ERROR: codex exec failed after 2 attempts. See $LOG" >&2
exit $RC
```

```bash
chmod +x skills/photo-curation/scripts/call-codex.sh
```

- [ ] **Step 5: Implement codex-classify.sh**

`skills/photo-curation/scripts/codex-classify.sh`:
```bash
#!/usr/bin/env bash
# codex-classify.sh — classify ONE photo, append entry to catalog.yaml.
#
# Usage:
#   bash codex-classify.sh <project_dir> <photo_path>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
PHOTO="${2:?ERROR: photo path required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/classify-prompt.md"

# Render prompt: extract Prompt body from template, substitute placeholders
RENDERED=$(python3 "$SCRIPT_DIR/render-prompt.py" "$TEMPLATE" "$PROJECT_DIR")
RENDERED_PROMPT_FILE="$(mktemp)"
# Extract just the prompt body (between first triple-backtick after ## Prompt body and next ```)
python3 -c "
import re, sys
text = open('$TEMPLATE').read()
m = re.search(r'## Prompt body\s*\n+\`\`\`\s*\n(.+?)\n\`\`\`', text, re.DOTALL)
if not m: sys.exit('No Prompt body section')
sys.stdout.write(m.group(1))
" > "$RENDERED_PROMPT_FILE.raw"

python3 "$SCRIPT_DIR/render-prompt.py" "$RENDERED_PROMPT_FILE.raw" "$PROJECT_DIR" > "$RENDERED_PROMPT_FILE"

# Call codex
YAML_RESPONSE=$(bash "$SCRIPT_DIR/call-codex.sh" "$PROJECT_DIR" "classify" "$RENDERED_PROMPT_FILE" --image "$PHOTO")
rm -f "$RENDERED_PROMPT_FILE" "$RENDERED_PROMPT_FILE.raw"

# Parse + append to catalog
PHOTO_ID=$(basename "$PHOTO" .jpg)
CATALOG="$PROJECT_DIR/07c_PHOTOS/catalog.yaml"

# Write codex response to temp file (avoid heredoc quoting on multiline YAML)
RESPONSE_FILE="$(mktemp)"
echo "$YAML_RESPONSE" > "$RESPONSE_FILE"

python3 - "$RESPONSE_FILE" "$CATALOG" "$PHOTO_ID" <<'PYEOF'
import sys, yaml
from pathlib import Path

response_path, catalog_path_str, photo_id = sys.argv[1], sys.argv[2], sys.argv[3]
catalog_path = Path(catalog_path_str)
catalog = yaml.safe_load(catalog_path.read_text()) if catalog_path.exists() else {"photos": []}

try:
    parsed = yaml.safe_load(open(response_path).read())
    if not isinstance(parsed, dict):
        raise yaml.YAMLError("root not a dict")
except yaml.YAMLError as e:
    print(f"WARN: invalid YAML from codex: {e}. Tagging as unclassified.", file=sys.stderr)
    parsed = {"tags": ["unclassified"], "caption": "", "face_count": 0,
              "composition": "object-only", "usable_ratios": [], "brand_compatible": "maybe",
              "notes": "codex YAML parse failed"}

existing = [p for p in catalog["photos"] if p["id"] == photo_id]
if existing:
    existing[0].update(parsed)
    existing[0]["tag_source"] = "ai_classify"
else:
    parsed["id"] = photo_id
    parsed["tag_source"] = "ai_classify"
    catalog["photos"].append(parsed)

catalog_path.write_text(yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False))
print(f"OK: classified {photo_id}")
PYEOF
rm -f "$RESPONSE_FILE"
```

```bash
chmod +x skills/photo-curation/scripts/codex-classify.sh
```

- [ ] **Step 6: Implement codex-match.sh**

`skills/photo-curation/scripts/codex-match.sh`:
```bash
#!/usr/bin/env bash
# codex-match.sh — produce selections.draft.yaml from catalog + slots.
#
# Usage:
#   bash codex-match.sh <project_dir> <catalog_yaml> <slots_yaml>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
CATALOG="${2:?ERROR: catalog.yaml path required}"
SLOTS="${3:?ERROR: slots.yaml path required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/match-prompt.md"

# Build prompt: extract body, inline CATALOG and SLOTS yaml content as placeholders
PROMPT_FILE="$(mktemp)"
python3 <<PYEOF > "$PROMPT_FILE.raw"
import re
text = open("$TEMPLATE").read()
m = re.search(r"## Prompt body\s*\n+\`\`\`\s*\n(.+?)\n\`\`\`", text, re.DOTALL)
body = m.group(1)

catalog = open("$CATALOG").read()
slots = open("$SLOTS").read()

body = body.replace("[CATALOG_YAML]", catalog)
body = body.replace("[SLOTS_YAML]", slots)

print(body)
PYEOF

python3 "$SCRIPT_DIR/render-prompt.py" "$PROMPT_FILE.raw" "$PROJECT_DIR" > "$PROMPT_FILE"

# Call codex (no image input for matcher). Write response to temp file to avoid heredoc quoting issues.
RESPONSE_FILE="$(mktemp)"
bash "$SCRIPT_DIR/call-codex.sh" "$PROJECT_DIR" "match" "$PROMPT_FILE" > "$RESPONSE_FILE"
rm -f "$PROMPT_FILE" "$PROMPT_FILE.raw"

# Validate + save as selections.draft.yaml
DRAFT="$PROJECT_DIR/07c_PHOTOS/selections.draft.yaml"
python3 - "$RESPONSE_FILE" "$DRAFT" <<'PYEOF'
import sys, yaml
response_path, draft_path = sys.argv[1], sys.argv[2]
try:
    parsed = yaml.safe_load(open(response_path).read())
    assert isinstance(parsed, dict) and "slots" in parsed
except (yaml.YAMLError, AssertionError) as e:
    print(f"ERROR: matcher returned invalid YAML: {e}", file=sys.stderr)
    sys.exit(3)
with open(draft_path, "w") as f:
    yaml.safe_dump(parsed, f, allow_unicode=True, sort_keys=False)
print(f"OK: matched, draft at {draft_path}")
PYEOF
rm -f "$RESPONSE_FILE"
```

```bash
chmod +x skills/photo-curation/scripts/codex-match.sh
```

- [ ] **Step 7: Implement codex-generate-fallback.sh**

`skills/photo-curation/scripts/codex-generate-fallback.sh`:
```bash
#!/usr/bin/env bash
# codex-generate-fallback.sh — generate ONE photo via codex image_gen for a missing slot.
# Clones generate-atlas.sh pattern: snapshot ~/.codex/generated_images, exec, copy fresh PNG.
#
# Usage:
#   bash codex-generate-fallback.sh <project_dir> <slot_id> <width> <height> <ratio> <slot_hint>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
SLOT_ID="${2:?ERROR: slot_id required}"
WIDTH="${3:?ERROR: width required}"
HEIGHT="${4:?ERROR: height required}"
RATIO="${5:?ERROR: ratio required}"
SLOT_HINT="${6:?ERROR: slot_hint required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/generate-fallback.md"

OUT_DIR="$PROJECT_DIR/07c_PHOTOS/processed/$SLOT_ID"
mkdir -p "$OUT_DIR"
OUT_PNG="$OUT_DIR/ai-generated.jpg"

# Skip-if-exists (open-design imagegen.ts pattern, --force overrides)
if [ -f "$OUT_PNG" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "SKIP: $OUT_PNG exists. Set FORCE=1 to override."
    exit 0
fi

# Render prompt
PROMPT_FILE="$(mktemp)"
python3 -c "
import re
text = open('$TEMPLATE').read()
m = re.search(r'## Prompt body\s*\n+\`\`\`\s*\n(.+?)\n\`\`\`', text, re.DOTALL)
body = m.group(1)
body = body.replace('[WIDTH]', '$WIDTH').replace('[HEIGHT]', '$HEIGHT').replace('[RATIO]', '$RATIO').replace('[SLOT_HINT]', '''$SLOT_HINT''')
print(body)
" > "$PROMPT_FILE.raw"

python3 "$SCRIPT_DIR/render-prompt.py" "$PROMPT_FILE.raw" "$PROJECT_DIR" > "$PROMPT_FILE"
cp "$PROMPT_FILE" "$OUT_DIR/ai-prompt.txt"

# Snapshot existing codex image dirs (paralaximus pattern)
TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

CODEX_BIN="${CODEX_BIN:-codex}"
echo "→ Generating fallback for slot $SLOT_ID..."
"$CODEX_BIN" exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" >&2 || {
    rc=$?
    echo "ERROR: codex exec failed (rc=$rc)" >&2
    rm -f "$PROMPT_FILE" "$PROMPT_FILE.raw" "$TMP_BEFORE"
    exit "$rc"
}

# Find new session dir
TMP_AFTER="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER" "$PROMPT_FILE" "$PROMPT_FILE.raw"

[ -n "$NEW_DIR" ] || NEW_DIR="$(ls -1t ~/.codex/generated_images/ 2>/dev/null | head -1)"
[ -n "$NEW_DIR" ] || { echo "ERROR: no codex generated_images dir found" >&2; exit 3; }

SRC_PNG="$(ls -1t "$HOME/.codex/generated_images/$NEW_DIR"/*.png 2>/dev/null | head -1 || true)"
[ -n "$SRC_PNG" ] || { echo "ERROR: no PNG produced" >&2; exit 4; }

# Convert PNG → JPG (smaller, no transparency needed for fallback)
python3 -c "
from PIL import Image
img = Image.open('$SRC_PNG').convert('RGB')
img.save('$OUT_PNG', 'JPEG', quality=88)
"
echo "✓ Generated: $OUT_PNG"
```

```bash
chmod +x skills/photo-curation/scripts/codex-generate-fallback.sh
```

- [ ] **Step 8: Run tests — verify they pass**

```bash
bats tests/phase-prb/test-codex-wrappers.bats
```

Expected: 3 PASS, 1 SKIP (generate-fallback E2E).

- [ ] **Step 9: Commit**

```bash
git add skills/photo-curation/scripts/call-codex.sh skills/photo-curation/scripts/codex-*.sh tests/phase-prb/test-codex-wrappers.bats tests/phase-prb/fixtures/codex-mock.sh
git commit -m "feat(pr-b): codex CLI wrappers for classify, match, generate-fallback"
```

---

## Task 6: `gallery-render.py` — photo-board.html (split-view drag-drop)

**Files:**
- Create: `skills/photo-curation/scripts/gallery-render.py`
- Create: `skills/photo-curation/scripts/gallery-template.html` (HTML+CSS+JS template)
- Create: `tests/phase-prb/test-gallery-render.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prb/test-gallery-render.py`:
```python
"""Tests for photo-board.html generator."""
from pathlib import Path

from skills.photo_curation.scripts.gallery_render import render_board


def test_render_board_produces_html_with_photos_and_slots(tmp_path):
    catalog = {
        "photos": [
            {"id": "photo_001", "thumb_path": "intake/photo_001.thumb.jpg",
             "caption": "Test photo", "tags": ["portrait"]},
            {"id": "photo_002", "thumb_path": "intake/photo_002.thumb.jpg",
             "caption": "Other", "tags": ["object"]},
        ]
    }
    selections_draft = {
        "slots": [
            {"slot_id": "hero-bg", "block_id": "ru-hero-01", "ratio": "16:9",
             "candidates": [{"photo_id": "photo_002", "score": 0.9, "reason": "wide"}],
             "ai_fallback_needed": False, "required_user_approval": False},
            {"slot_id": "testimonial-1-avatar", "block_id": "ru-test-01", "ratio": "1:1",
             "candidates": [],
             "ai_fallback_needed": True, "required_user_approval": True,
             "ai_prompt": "Portrait of client"},
        ]
    }
    out = tmp_path / "photo-board.html"
    render_board(catalog, selections_draft, out)
    html = out.read_text()
    # Photos rendered
    assert "photo_001" in html
    assert "photo_002" in html
    # Slots rendered
    assert "hero-bg" in html
    assert "testimonial-1-avatar" in html
    # AI approval checkbox for identity-safe slot
    assert "ai_approved_by_user" in html
    assert "Согласен" in html  # the approval modal copy
    # Drag-drop data attributes
    assert "data-photo-id" in html
    assert "data-slot-id" in html


def test_render_board_includes_confirm_button_that_downloads_yaml(tmp_path):
    catalog = {"photos": []}
    selections_draft = {"slots": []}
    out = tmp_path / "photo-board.html"
    render_board(catalog, selections_draft, out)
    html = out.read_text()
    assert "Confirm" in html or "Подтвердить" in html
    assert "selections.yaml" in html  # JS exports as this filename
```

- [ ] **Step 2: Run test — fails**

```bash
python3 -m pytest tests/phase-prb/test-gallery-render.py -v
```

- [ ] **Step 3: Implement gallery-template.html**

`skills/photo-curation/scripts/gallery-template.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Photo Board — раскладывание фоток по слотам</title>
<style>
  body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI; margin: 0; background: #f5f5f4; }
  header { padding: 16px 24px; background: white; border-bottom: 1px solid #e5e5e4; position: sticky; top: 0; }
  h1 { margin: 0; font-size: 18px; }
  .container { display: grid; grid-template-columns: 1fr 1fr; gap: 0; height: calc(100vh - 56px); }
  .pane { padding: 16px 24px; overflow-y: auto; }
  .pane.left { border-right: 1px solid #e5e5e4; background: white; }
  h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; color: #57534e; margin: 0 0 12px; }
  .photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
  .photo { cursor: grab; background: white; border: 2px solid transparent; border-radius: 6px; overflow: hidden; transition: 0.15s; user-select: none; }
  .photo:hover { border-color: #1e3a8a; }
  .photo img { width: 100%; height: 140px; object-fit: cover; display: block; }
  .photo .caption { padding: 6px 8px; font-size: 11px; color: #57534e; }
  .photo .tags { padding: 0 8px 6px; font-size: 10px; color: #888; }
  .slot { background: white; border: 1px solid #e5e5e4; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
  .slot.has-photo { border-color: #1e3a8a; }
  .slot.fallback { border-color: #c47a3a; background: #fff7ed; }
  .slot-header { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; }
  .slot-meta { font-size: 11px; color: #888; margin-top: 4px; }
  .slot-photo { margin-top: 8px; padding: 12px; background: #f5f5f4; border-radius: 4px; min-height: 60px; display: flex; align-items: center; gap: 12px; }
  .slot-photo.empty { color: #888; font-style: italic; }
  .slot-photo img { width: 80px; height: 60px; object-fit: cover; border-radius: 4px; }
  .ai-banner { background: #c47a3a; color: white; padding: 8px; border-radius: 4px; margin-top: 8px; font-size: 12px; }
  .ai-banner label { display: block; margin-top: 4px; }
  .ai-banner input[type=checkbox] { margin-right: 6px; }
  .controls { padding: 16px 24px; background: white; border-top: 1px solid #e5e5e4; }
  button { padding: 10px 20px; background: #1e3a8a; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
  button:hover { background: #1e2a6a; }
</style>
</head>
<body>
<header>
  <h1>🖼️ Раскладывание фоток по слотам</h1>
  <p style="margin: 4px 0 0; font-size: 12px; color: #57534e;">Перетащи фотку из левой панели в нужный слот справа. Для AI-генерации лиц — поставь галочку.</p>
</header>
<div class="container">
  <div class="pane left">
    <h2>Фотки клиента ({{PHOTO_COUNT}})</h2>
    <div class="photo-grid">
      {{PHOTOS_HTML}}
    </div>
  </div>
  <div class="pane right">
    <h2>Слоты прототипа ({{SLOT_COUNT}})</h2>
    {{SLOTS_HTML}}
    <div class="controls">
      <button id="confirm-btn">✓ Подтвердить и скачать selections.yaml</button>
    </div>
  </div>
</div>
<script>
const SELECTIONS_STATE = {{INITIAL_STATE_JSON}};

// Drag-drop
document.querySelectorAll('.photo').forEach(p => {
  p.draggable = true;
  p.addEventListener('dragstart', e => {
    e.dataTransfer.setData('text/plain', p.dataset.photoId);
  });
});
document.querySelectorAll('.slot').forEach(s => {
  s.addEventListener('dragover', e => e.preventDefault());
  s.addEventListener('drop', e => {
    e.preventDefault();
    const photoId = e.dataTransfer.getData('text/plain');
    const slotId = s.dataset.slotId;
    assignPhoto(slotId, photoId);
  });
});

function assignPhoto(slotId, photoId) {
  const slot = SELECTIONS_STATE.slots.find(s => s.slot_id === slotId);
  slot.chosen_photo_id = photoId;
  slot.strategy = 'bring-your-own';
  slot.ai_fallback_needed = false;
  renderSlot(slotId);
}

function toggleAiApproval(slotId, checked) {
  const slot = SELECTIONS_STATE.slots.find(s => s.slot_id === slotId);
  slot.ai_approved_by_user = checked;
  slot.strategy = checked ? 'generate' : 'placeholder';
}

function renderSlot(slotId) {
  // Re-render the slot's photo area. Implementation kept minimal — full re-render of the slot HTML.
  location.reload();  // simplest path for MVP; future: surgical DOM update
}

document.getElementById('confirm-btn').addEventListener('click', () => {
  // Convert state to canonical selections.yaml shape, download as YAML.
  const canonical = {strategy_default: 'bring-your-own', slots: SELECTIONS_STATE.slots.map(s => ({
    slot_id: s.slot_id,
    block_id: s.block_id,
    ratio: s.ratio,
    mobile_ratio: s.mobile_ratio,
    strategy: s.strategy || (s.chosen_photo_id ? 'bring-your-own' : (s.ai_approved_by_user ? 'generate' : 'placeholder')),
    chosen_photo_id: s.chosen_photo_id || null,
    ai_approved_by_user: s.ai_approved_by_user || false,
    ai_prompt: s.ai_prompt || null
  }))};
  const yaml = canonicalToYaml(canonical);
  const blob = new Blob([yaml], {type: 'text/yaml'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'selections.yaml';
  a.click();
});

function canonicalToYaml(obj) {
  // Minimal YAML serializer — sufficient for our flat structure.
  let out = `strategy_default: ${obj.strategy_default}\nslots:\n`;
  for (const s of obj.slots) {
    out += `  - slot_id: ${s.slot_id}\n`;
    out += `    block_id: ${s.block_id}\n`;
    out += `    ratio: "${s.ratio}"\n`;
    if (s.mobile_ratio) out += `    mobile_ratio: "${s.mobile_ratio}"\n`;
    out += `    strategy: ${s.strategy}\n`;
    out += `    chosen_photo_id: ${s.chosen_photo_id ? s.chosen_photo_id : 'null'}\n`;
    out += `    ai_approved_by_user: ${s.ai_approved_by_user}\n`;
    if (s.ai_prompt) out += `    ai_prompt: "${s.ai_prompt.replace(/"/g, '\\"')}"\n`;
  }
  return out;
}
</script>
</body>
</html>
```

- [ ] **Step 4: Implement gallery-render.py**

`skills/photo-curation/scripts/gallery-render.py`:
```python
#!/usr/bin/env python3
"""Render photo-board.html (split-view drag-drop UI)."""
import json
import sys
from html import escape
from pathlib import Path
from typing import Mapping

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR / "gallery-template.html"


def _photo_card(photo: dict) -> str:
    tags = ", ".join(photo.get("tags", []))
    return f"""<div class="photo" data-photo-id="{escape(photo['id'])}" draggable="true">
  <img src="{escape(photo.get('thumb_path', ''))}" alt="{escape(photo.get('caption', ''))}">
  <div class="caption">{escape(photo.get('caption', ''))}</div>
  <div class="tags">{escape(tags)}</div>
</div>"""


def _slot_card(slot: dict, photos_by_id: Mapping[str, dict]) -> str:
    slot_id = slot["slot_id"]
    chosen = slot.get("chosen_photo_id")
    candidates = slot.get("candidates", [])
    if not chosen and candidates:
        chosen = candidates[0]["photo_id"]
    classes = "slot"
    if chosen: classes += " has-photo"
    elif slot.get("ai_fallback_needed"): classes += " fallback"

    photo_html = '<div class="slot-photo empty">Перетащи фотку сюда</div>'
    if chosen and chosen in photos_by_id:
        p = photos_by_id[chosen]
        photo_html = f'<div class="slot-photo"><img src="{escape(p["thumb_path"])}"><span>{escape(p.get("caption",""))}</span></div>'

    ai_banner = ""
    if slot.get("required_user_approval"):
        ai_banner = f"""<div class="ai-banner">
          ⚠️ Этот слот требует AI-сгенерированного лица человека.
          <label><input type="checkbox" onchange="toggleAiApproval('{escape(slot_id)}', this.checked)"> Согласен на использование AI</label>
        </div>"""

    return f"""<div class="{classes}" data-slot-id="{escape(slot_id)}">
  <div class="slot-header">
    <span>{escape(slot_id)}</span>
    <span>{escape(slot.get('ratio', ''))}</span>
  </div>
  <div class="slot-meta">{escape(slot.get('block_id', ''))}</div>
  {photo_html}
  {ai_banner}
</div>"""


def render_board(catalog: dict, selections_draft: dict, out_path: Path) -> None:
    template = TEMPLATE_PATH.read_text()
    photos = catalog.get("photos", [])
    slots = selections_draft.get("slots", [])
    photos_by_id = {p["id"]: p for p in photos}

    photos_html = "\n".join(_photo_card(p) for p in photos)
    slots_html = "\n".join(_slot_card(s, photos_by_id) for s in slots)

    initial_state = json.dumps({"slots": slots}, ensure_ascii=False)

    rendered = (template
        .replace("{{PHOTO_COUNT}}", str(len(photos)))
        .replace("{{SLOT_COUNT}}", str(len(slots)))
        .replace("{{PHOTOS_HTML}}", photos_html)
        .replace("{{SLOTS_HTML}}", slots_html)
        .replace("{{INITIAL_STATE_JSON}}", initial_state)
    )
    Path(out_path).write_text(rendered, encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    catalog = yaml.safe_load(Path(args.catalog).read_text())
    draft = yaml.safe_load(Path(args.draft).read_text())
    render_board(catalog, draft, Path(args.out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests — pass**

```bash
python3 -m pytest tests/phase-prb/test-gallery-render.py -v
```

- [ ] **Step 6: Commit**

```bash
git add skills/photo-curation/scripts/gallery-render.py skills/photo-curation/scripts/gallery-template.html tests/phase-prb/test-gallery-render.py
git commit -m "feat(pr-b): photo-board.html generator with drag-drop split-view UI"
```

---

## Task 7: `preview-render.py` — photo-preview.html ("фото в местах")

**Files:**
- Create: `skills/photo-curation/scripts/preview-render.py`
- Create: `tests/phase-prb/test-preview-render.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prb/test-preview-render.py`:
```python
"""Tests for photo-preview.html generator."""
from pathlib import Path

from skills.photo_curation.scripts.preview_render import render_preview


def test_preview_shows_all_slots_with_processed_paths(tmp_path):
    selections = {
        "strategy_default": "bring-your-own",
        "slots": [
            {"slot_id": "hero-bg", "block_id": "ru-hero-01", "ratio": "16:9",
             "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg",
                           "mobile": "processed/hero-bg/mobile.jpg"},
             "ai_approved_by_user": False},
            {"slot_id": "testimonial-1", "block_id": "ru-test-01", "ratio": "1:1",
             "strategy": "generate", "chosen_photo_id": None,
             "processed": {"desktop": "processed/testimonial-1/ai-generated.jpg",
                           "mobile": None},
             "ai_approved_by_user": True},
            {"slot_id": "process-3", "block_id": "ru-proc-01", "ratio": "4:3",
             "strategy": "placeholder", "chosen_photo_id": None,
             "processed": {"desktop": "processed/process-3/placeholder.png",
                           "mobile": None},
             "ai_approved_by_user": False},
        ]
    }
    out = tmp_path / "photo-preview.html"
    render_preview(selections, out)
    html = out.read_text()
    # All 3 slots rendered
    assert "hero-bg" in html
    assert "testimonial-1" in html
    assert "process-3" in html
    # AI badge for the generate slot
    assert "AI" in html
    # Strategy labels
    assert "bring-your-own" in html or "Клиент" in html
```

- [ ] **Step 2: Run — fails**

- [ ] **Step 3: Implement preview-render.py**

`skills/photo-curation/scripts/preview-render.py`:
```python
#!/usr/bin/env python3
"""Render photo-preview.html — 'photos in their slot positions' for final approval."""
from html import escape
from pathlib import Path

import yaml


PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<title>Photo Preview — фото в местах</title>
<style>
body { font-family: ui-sans-serif, system-ui; margin: 0; padding: 24px; background: #f5f5f4; }
h1 { font-size: 20px; }
.slot { background: white; border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid #e5e5e4; }
.slot.ai { border-color: #c47a3a; }
.slot.placeholder { border-color: #aaa; background: #fafafa; }
.slot-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.badge.client { background: #ddf; color: #1e3a8a; }
.badge.ai { background: #c47a3a; color: white; }
.badge.placeholder { background: #888; color: white; }
.images { display: grid; grid-template-columns: 1fr 200px; gap: 16px; align-items: start; }
.images img { max-width: 100%; border-radius: 4px; border: 1px solid #e5e5e4; }
.controls { text-align: center; padding: 24px; }
button { padding: 12px 24px; background: #1e3a8a; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
</style>
</head><body>
<h1>📸 Фото в макетных местах</h1>
<p>Проверь как выглядят фотки в финальной композиции. Если всё ок — переходи в композицию страницы.</p>
{{SLOTS_HTML}}
<div class="controls">
  <button onclick="alert('Approve flow handled by photo-curator agent — return to chat.')">✓ Утвердить и собрать composed.html</button>
</div>
</body></html>"""


STRATEGY_LABELS = {
    "bring-your-own": ("client", "Фото клиента"),
    "generate": ("ai", "AI-генерация"),
    "placeholder": ("placeholder", "Плейсхолдер"),
}


def _slot_block(slot: dict) -> str:
    strategy = slot.get("strategy", "placeholder")
    badge_class, badge_text = STRATEGY_LABELS.get(strategy, ("placeholder", "—"))
    processed = slot.get("processed") or {}
    desktop = processed.get("desktop") or ""
    mobile = processed.get("mobile")

    images_html = f'<img src="{escape(desktop)}" alt="desktop">'
    if mobile:
        images_html += f'<img src="{escape(mobile)}" alt="mobile" style="max-width:200px">'

    slot_class = f"slot {strategy}".replace("bring-your-own", "")

    return f"""<div class="{slot_class}">
  <div class="slot-header">
    <span>{escape(slot['slot_id'])} <small style="font-weight:400;color:#888">({escape(slot.get('block_id',''))})</small></span>
    <span class="badge {badge_class}">{badge_text}</span>
  </div>
  <div class="images">{images_html}</div>
</div>"""


def render_preview(selections: dict, out_path: Path) -> None:
    slots = selections.get("slots", [])
    slots_html = "\n".join(_slot_block(s) for s in slots)
    out = PREVIEW_TEMPLATE.replace("{{SLOTS_HTML}}", slots_html)
    Path(out_path).write_text(out, encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--selections", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sel = yaml.safe_load(Path(args.selections).read_text())
    render_preview(sel, Path(args.out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add skills/photo-curation/scripts/preview-render.py tests/phase-prb/test-preview-render.py
git commit -m "feat(pr-b): photo-preview.html generator (фото в макетных местах)"
```

---

## Task 8: `selections-validator.py` — schema validation

**Files:**
- Create: `skills/photo-curation/scripts/selections-validator.py`
- Create: `tests/phase-prb/test-selections-validator.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prb/test-selections-validator.py`:
```python
"""Tests for selections.yaml schema validator."""
import pytest

from skills.photo_curation.scripts.selections_validator import validate, ValidationError


def test_valid_selections_passes():
    data = {
        "strategy_default": "bring-your-own",
        "slots": [
            {"slot_id": "hero-bg", "block_id": "ru-hero-01", "ratio": "16:9",
             "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "ai_approved_by_user": False}
        ]
    }
    validate(data)


def test_invalid_strategy_enum_fails():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "x", "block_id": "y", "ratio": "1:1", "strategy": "INVALID",
         "ai_approved_by_user": False}
    ]}
    with pytest.raises(ValidationError, match="strategy"):
        validate(data)


def test_generate_without_user_approval_for_identity_safe_slot_fails():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "testimonial-1-avatar", "block_id": "x", "ratio": "1:1",
         "strategy": "generate", "chosen_photo_id": None,
         "ai_approved_by_user": False}
    ]}
    with pytest.raises(ValidationError, match="ai_approved_by_user"):
        validate(data)


def test_generate_with_approval_passes():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "testimonial-1-avatar", "block_id": "x", "ratio": "1:1",
         "strategy": "generate", "chosen_photo_id": None,
         "ai_approved_by_user": True, "ai_prompt": "..."}
    ]}
    validate(data)


def test_bring_your_own_without_photo_id_fails():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "x", "block_id": "y", "ratio": "1:1",
         "strategy": "bring-your-own", "chosen_photo_id": None,
         "ai_approved_by_user": False}
    ]}
    with pytest.raises(ValidationError, match="chosen_photo_id"):
        validate(data)
```

- [ ] **Step 2: Run — fails**

- [ ] **Step 3: Implement**

`skills/photo-curation/scripts/selections-validator.py`:
```python
#!/usr/bin/env python3
"""Validate selections.yaml schema (canonical, post-approve)."""
import sys
from pathlib import Path

import yaml


VALID_STRATEGIES = {"generate", "placeholder", "bring-your-own"}
IDENTITY_SAFE_PATTERNS = ["testimonial", "expert", "team-member", "team_member", "avatar"]


class ValidationError(ValueError):
    pass


def _is_identity_safe_slot(slot_id: str) -> bool:
    sid = slot_id.lower()
    return any(p in sid for p in IDENTITY_SAFE_PATTERNS)


def validate(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValidationError("Root must be a dict")
    if "slots" not in data or not isinstance(data["slots"], list):
        raise ValidationError("Missing 'slots' list")

    for i, s in enumerate(data["slots"]):
        prefix = f"slot[{i}] ({s.get('slot_id', '?')})"
        for req in ["slot_id", "block_id", "ratio", "strategy"]:
            if req not in s:
                raise ValidationError(f"{prefix}: missing field '{req}'")
        if s["strategy"] not in VALID_STRATEGIES:
            raise ValidationError(f"{prefix}: strategy='{s['strategy']}' not in {VALID_STRATEGIES}")
        # Strategy-specific rules
        if s["strategy"] == "bring-your-own" and not s.get("chosen_photo_id"):
            raise ValidationError(f"{prefix}: strategy=bring-your-own requires chosen_photo_id")
        if s["strategy"] == "generate":
            if _is_identity_safe_slot(s["slot_id"]) and not s.get("ai_approved_by_user"):
                raise ValidationError(f"{prefix}: identity-safe slot requires ai_approved_by_user=True for strategy=generate")


def main():
    if len(sys.argv) < 2:
        print("Usage: selections-validator.py <selections.yaml>", file=sys.stderr)
        sys.exit(2)
    data = yaml.safe_load(Path(sys.argv[1]).read_text())
    try:
        validate(data)
    except ValidationError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
    print("OK: selections.yaml is valid")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Pass tests + commit**

```bash
python3 -m pytest tests/phase-prb/test-selections-validator.py -v
git add skills/photo-curation/scripts/selections-validator.py tests/phase-prb/test-selections-validator.py
git commit -m "feat(pr-b): selections.yaml schema validator with identity-safe enforcement"
```

---

## Task 9: Extend `style.py` with `--target-ratio` and `--target-ratio-mobile`

**Files:**
- Modify: `skills/photo-styling/scripts/style.py`
- Create: `tests/phase-prb/test-style-target-ratio.py`

- [ ] **Step 1: Read existing style.py to understand current API**

```bash
cat skills/photo-styling/scripts/style.py
```

Note current functions: `resize`, `crop_aspect`, `cutout`. We add a new mode `target-ratio` that combines crop + resize.

- [ ] **Step 2: Write failing test**

`tests/phase-prb/test-style-target-ratio.py`:
```python
"""Tests for style.py --target-ratio extension."""
import subprocess
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
STYLE = REPO / "skills" / "photo-styling" / "scripts" / "style.py"


def test_target_ratio_produces_correct_aspect(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(src)
    dst = tmp_path / "out.jpg"
    subprocess.run(["python3", str(STYLE), str(src), str(dst),
                    "--mode", "target-ratio", "--ratio", "16:9", "--max-dim", "1920"],
                   check=True)
    with Image.open(dst) as img:
        w, h = img.size
    # Should be 16:9 ratio (within rounding)
    assert abs((w / h) - (16 / 9)) < 0.01
    # Should fit in max-dim
    assert max(w, h) <= 1920


def test_target_ratio_for_mobile_smaller_dimension(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (3000, 4000), (0, 255, 0)).save(src)
    dst = tmp_path / "mobile.jpg"
    subprocess.run(["python3", str(STYLE), str(src), str(dst),
                    "--mode", "target-ratio", "--ratio", "9:16", "--max-dim", "1080"],
                   check=True)
    with Image.open(dst) as img:
        w, h = img.size
    assert abs((w / h) - (9 / 16)) < 0.01
    assert max(w, h) <= 1080
```

- [ ] **Step 3: Run — fails**

- [ ] **Step 4: Extend style.py**

In `skills/photo-styling/scripts/style.py`, add new function and CLI mode:

```python
def target_ratio(src: str, dst: str, ratio: str, max_dim: int = 1920) -> None:
    """Crop to target ratio (center), then resize to fit max_dim."""
    a, b = map(int, ratio.split(":"))
    target = a / b
    img = Image.open(src)
    w, h = img.size
    current = w / h
    if current > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current < target:
        new_h = int(w / target)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    # else: already correct ratio
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.save(dst, "JPEG", quality=85)
```

Add to argparse / dispatch:
```python
# ... in main() existing argparse:
parser.add_argument("--ratio", help="Target aspect ratio, e.g. 16:9")
parser.add_argument("--max-dim", type=int, default=1920)

# ... in mode dispatch:
elif args.mode == "target-ratio":
    if not args.ratio:
        sys.exit("--ratio required for target-ratio mode")
    target_ratio(args.input, args.output, args.ratio, args.max_dim)
```

(See full existing style.py and apply minimal surgery — don't rewrite.)

- [ ] **Step 5: Run test — pass**

```bash
python3 -m pytest tests/phase-prb/test-style-target-ratio.py -v
```

- [ ] **Step 6: Commit**

```bash
git add skills/photo-styling/scripts/style.py tests/phase-prb/test-style-target-ratio.py
git commit -m "feat(pr-b): style.py --target-ratio for slot-aware crop+resize"
```

---

## Task 10: Extend `inject-content.py` to substitute real photos

**Files:**
- Modify: `skills/block-composition/scripts/inject-content.py`
- Create: `tests/phase-prb/test-inject-photos.py`

- [ ] **Step 1: Read existing inject-content.py**

```bash
cat skills/block-composition/scripts/inject-content.py
```

- [ ] **Step 2: Write failing test**

`tests/phase-prb/test-inject-photos.py`:
```python
"""Tests for inject-content.py photo substitution."""
from pathlib import Path

from bs4 import BeautifulSoup


def test_inject_uses_processed_photo_when_selections_exists(tmp_path):
    from skills.block_composition.scripts.inject_content import inject_block

    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9", "hint": "Фото объекта"}]
    }
    content = {}
    selections = {
        "slots": [
            {"slot_id": "hero-bg", "strategy": "bring-your-own",
             "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg",
                           "mobile": "processed/hero-bg/mobile.jpg"}}
        ]
    }
    result = inject_block(block_html, block_meta, content, photo_selections=selections)
    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    assert img is not None
    assert "processed/hero-bg/desktop.jpg" in img.get("src", "")


def test_inject_falls_back_to_placeholder_when_no_selections(tmp_path):
    from skills.block_composition.scripts.inject_content import inject_block

    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9", "hint": "Фото"}]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=None)
    soup = BeautifulSoup(result, "html.parser")
    placeholder = soup.find(class_="slot-placeholder")
    assert placeholder is not None
    assert "photo slot" in placeholder.text


def test_inject_uses_picture_element_for_mobile_variant(tmp_path):
    from skills.block_composition.scripts.inject_content import inject_block

    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9", "mobile_ratio": "9:16"}]
    }
    selections = {
        "slots": [
            {"slot_id": "hero-bg", "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg",
                           "mobile": "processed/hero-bg/mobile.jpg"}}
        ]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=selections)
    soup = BeautifulSoup(result, "html.parser")
    picture = soup.find("picture")
    assert picture is not None
    sources = picture.find_all("source")
    assert any("mobile" in s.get("srcset", "") for s in sources)
```

- [ ] **Step 3: Run — fails**

- [ ] **Step 4: Modify inject-content.py**

In `skills/block-composition/scripts/inject-content.py`, modify the photo-slot branch:

```python
def inject_block(html: str, block_meta: dict, content: dict, photo_selections: dict | None = None) -> str:
    """Inject content + photos into block template."""
    soup = BeautifulSoup(html, "html.parser")
    photo_slots = {s["name"]: s for s in block_meta.get("slots", []) if s["type"] == "photo"}

    # Build lookup: photo selections by slot_id
    sel_by_slot = {}
    if photo_selections:
        for s in photo_selections.get("slots", []):
            sel_by_slot[s["slot_id"]] = s

    for el in soup.select("[data-slot]"):
        slot_name = el["data-slot"]
        # ... existing text/cta handling unchanged ...
        if slot_name in photo_slots:
            # NEW: if selections has this slot — substitute real photo
            sel = sel_by_slot.get(slot_name)
            if sel and sel.get("processed", {}).get("desktop"):
                el.clear()
                desktop = sel["processed"]["desktop"]
                mobile = sel["processed"].get("mobile")
                slot_meta = photo_slots[slot_name]
                if mobile and slot_meta.get("mobile_ratio"):
                    # <picture> with mobile source
                    picture = soup.new_tag("picture")
                    src_mobile = soup.new_tag("source",
                        attrs={"srcset": mobile, "media": "(max-width: 768px)"})
                    picture.append(src_mobile)
                    img = soup.new_tag("img", attrs={"src": desktop, "alt": slot_meta.get("hint", "")})
                    picture.append(img)
                    el.append(picture)
                else:
                    img = soup.new_tag("img", attrs={"src": desktop, "alt": slot_meta.get("hint", "")})
                    el.append(img)
            else:
                # FALLBACK (existing PR-A behavior): placeholder div
                el.clear()
                label_div = soup.new_tag("div", **{"class": "slot-placeholder"})
                label_div.string = f"[photo slot: {slot_name} — hint: {photo_slots[slot_name].get('hint', '')}]"
                el.append(label_div)
    return str(soup)
```

Update the CLI / caller (`compose-blocks.py`) to read `07c_PHOTOS/selections.yaml` if it exists and pass to `inject_block`:

```python
# In compose-blocks.py main():
photo_selections_path = project_dir / "07c_PHOTOS" / "selections.yaml"
photo_selections = yaml.safe_load(photo_selections_path.read_text()) if photo_selections_path.exists() else None

# Pass photo_selections to inject_block calls
```

Add conftest module map for `skills.block_composition.scripts.inject_content`.

- [ ] **Step 5: Run all tests including existing PR-A tests**

```bash
python3 -m pytest tests/phase-prb/test-inject-photos.py -v
bats tests/phase-pra/ # ensure PR-A tests still pass
```

- [ ] **Step 6: Commit**

```bash
git add skills/block-composition/scripts/inject-content.py skills/block-composition/scripts/compose-blocks.py tests/phase-prb/test-inject-photos.py
git commit -m "feat(pr-b): inject-content.py substitutes real photos from selections.yaml (PR-A backward compatible)"
```

---

## Task 11: 4 agent docs (curator, classifier, matcher, preview-board)

**Files:**
- Create: `agents/photo-curator.md`
- Create: `agents/photo-classifier.md`
- Create: `agents/photo-matcher.md`
- Create: `agents/photo-preview-board.md`
- Create: `tests/phase-prb/test-agents-frontmatter.bats`

- [ ] **Step 1: Write failing test for frontmatter shape**

`tests/phase-prb/test-agents-frontmatter.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "photo-curator agent has frontmatter with name + description" {
    head -10 "$REPO/agents/photo-curator.md" | grep -q "^name: photo-curator$"
    head -10 "$REPO/agents/photo-curator.md" | grep -q "^description:"
}

@test "photo-classifier agent has correct frontmatter" {
    head -10 "$REPO/agents/photo-classifier.md" | grep -q "^name: photo-classifier$"
}

@test "photo-matcher agent has correct frontmatter" {
    head -10 "$REPO/agents/photo-matcher.md" | grep -q "^name: photo-matcher$"
}

@test "photo-preview-board agent has correct frontmatter" {
    head -10 "$REPO/agents/photo-preview-board.md" | grep -q "^name: photo-preview-board$"
}

@test "all 4 agents reference IDENTITY_SAFE.md" {
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-curator.md"
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-classifier.md"
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-matcher.md"
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-preview-board.md"
}
```

- [ ] **Step 2: Run — fails**

- [ ] **Step 3: Create photo-curator.md**

`agents/photo-curator.md`:
```markdown
---
name: photo-curator
description: Stage 07c orchestrator (PR-B). Runs intake, dispatches photo-classifier/photo-matcher/photo-preview-board, manages STATE.yaml, renders photo-board.html, waits for user approve. Triggered by /landing-photos.
---

# photo-curator

## Mission

Orchestrate full photo pipeline (stage 07c) for landing project. Identity-safe rules per [`skills/photo-curation/IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md).

## Gate (hard prerequisites)

Before running anything, verify:
- `<project>/.landing-state.yaml:stages.05_design.status == approved`
- `<project>/.landing-state.yaml:stages.07a_wireframe.status == approved` (or equivalent — wireframe selections.yaml exists)

If either gate fails: exit 1 with russian message.

## Process

1. **Bootstrap.** Ensure `<project>/07c_PHOTOS/inbox/` exists with all 7 subfolders (+ `_свалка/`). Print where to put photos.
2. **Dual-path intake.** Also scan `<project>/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` — copy any photos into `07c_PHOTOS/inbox/_свалка/` for migration.
3. **Intake.** Run `python3 skills/photo-curation/scripts/intake.py --inbox 07c_PHOTOS/inbox --intake 07c_PHOTOS/intake`. Update `STATE.yaml:stages.intake`.
4. **Classify.** For each photo in `intake/` with `tag_source: pending_ai_classify` — dispatch `photo-classifier` (in batches of 5, sleep 2s between). Update catalog.yaml progressively.
5. **Match.** Dispatch `photo-matcher` once over full catalog + slots from `07_ПРОТОТИП/prototype.yaml` filtered by `07a_WIREFRAME/selections.yaml`. Produces `selections.draft.yaml`.
6. **Render gallery.** `python3 skills/photo-curation/scripts/gallery-render.py --catalog 07c_PHOTOS/catalog.yaml --draft 07c_PHOTOS/selections.draft.yaml --out 07c_PHOTOS/photo-board.html`.
7. **HARD GATE.** Print `📂 Открой 07c_PHOTOS/photo-board.html в браузере. Расставь фотки, скачай selections.yaml в эту же папку.` Wait for user.
8. **Validate.** Run `python3 skills/photo-curation/scripts/selections-validator.py 07c_PHOTOS/selections.yaml`. If invalid — print errors, return to step 7.
9. **Process.** Dispatch `photo-preview-board`.
10. **HARD GATE.** Print `📸 Открой 07c_PHOTOS/photo-preview.html — проверь как фото лягут в макет.` Wait for user approve.
11. **Re-render composed.** Run `python3 skills/block-composition/scripts/compose-blocks.py --project <project>` (existing PR-A; it now reads 07c_PHOTOS/selections.yaml).
12. Mark `STATE.yaml:stages.process` done. Print success summary.

## State

`07c_PHOTOS/STATE.yaml`:
- `stages.{intake,classify,match,approval,process}`: status, finished, counts, errors
- `warnings: []`
- `errors: []`

## Idempotency

On restart: read STATE.yaml, resume from first non-done stage. `--force-stage X` resets stage X.

## Tools

Bash, Read, Write, Edit, Glob, Task (for dispatching the 3 sub-agents).
```

- [ ] **Step 4: Create photo-classifier.md**

`agents/photo-classifier.md`:
```markdown
---
name: photo-classifier
description: Tags one photo via codex CLI (image input). Outputs YAML entry that photo-curator appends to catalog.yaml. Identity-safe rules apply.
---

# photo-classifier

## Mission

For each photo in `intake/` with `tag_source: pending_ai_classify`, call codex via `skills/photo-curation/scripts/codex-classify.sh` to produce tags + caption + composition + usable_ratios.

Per [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md): never alter the photo itself. Classifier only reads.

## Input

- `<project_dir>` (absolute path)
- `<photo_path>` (single photo to classify)

## Output

Appends entry to `<project>/07c_PHOTOS/catalog.yaml`.

## Process

```bash
bash skills/photo-curation/scripts/codex-classify.sh <project_dir> <photo_path>
```

This script:
1. Renders `templates/classify-prompt.md` with context from `tokens.json` + niche analysis.
2. Calls `codex` via `call-codex.sh` wrapper (with image input mechanism per Task 0 research).
3. Parses YAML response; appends/updates entry in `catalog.yaml`.
4. Logs prompt+response to `07c_PHOTOS/.logs/`.

## Errors

- Invalid YAML from codex → retry 2× with stricter prompt; after — tag = `unclassified`, warning in STATE.yaml.
- codex silent fail → handled by `call-codex.sh` (retry, fall through to error).

## Tools

Bash, Read.
```

- [ ] **Step 5: Create photo-matcher.md**

`agents/photo-matcher.md`:
```markdown
---
name: photo-matcher
description: Ranks photos as candidates for each photo-slot in the wireframe. Output → selections.draft.yaml. Identity-safe constraints enforced in prompt.
---

# photo-matcher

## Mission

Single-shot ranking: codex reads full `catalog.yaml` + active slot list → returns top-3 candidates per slot + `ai_fallback_needed` flag + `required_user_approval` flag for identity-safe slots.

## Input

- `<project_dir>`

## Output

`<project>/07c_PHOTOS/selections.draft.yaml`.

## Process

1. Build `_slots-input.yaml` from `07_ПРОТОТИП/prototype.yaml` filtered by `07a_WIREFRAME/selections.yaml` (only the variants the user chose, only photo-typed slots).
2. ```bash
   bash skills/photo-curation/scripts/codex-match.sh \
     <project_dir> \
     <project>/07c_PHOTOS/catalog.yaml \
     <project>/07c_PHOTOS/_slots-input.yaml
   ```
3. Validates output is YAML with required keys.

## Errors

- Invalid YAML → retry 2×; after — abort, ask user to inspect codex log.
- Empty candidate list for safe slots → `ai_fallback_needed: true` (this is expected, not an error).

## Identity-safe enforcement

The match-prompt instructs codex: identity-safe slots set `required_user_approval: true`. Validator and photo-board UI enforce this downstream.

## Tools

Bash, Read.
```

- [ ] **Step 6: Create photo-preview-board.md**

`agents/photo-preview-board.md`:
```markdown
---
name: photo-preview-board
description: After user approves selections.yaml, process each slot — crop/resize client photos (style.py) OR codex image_gen fallback OR SVG placeholder. Render photo-preview.html for final approve.
---

# photo-preview-board

## Mission

Turn `selections.yaml` into `processed/<slot_id>/{desktop,mobile}.jpg` files + render `photo-preview.html`.

## Input

- `<project_dir>` (must have valid `07c_PHOTOS/selections.yaml`)

## Output

- `<project>/07c_PHOTOS/processed/<slot_id>/desktop.jpg`
- `<project>/07c_PHOTOS/processed/<slot_id>/mobile.jpg` (where block has mobile_ratio)
- `<project>/07c_PHOTOS/photo-preview.html`

## Process

1. Validate `selections.yaml` via `selections-validator.py`. Abort on invalid.
2. For each slot:
   - If `strategy: bring-your-own`:
     - `style.py --target-ratio <ratio> --max-dim 1920` → `processed/<slot_id>/desktop.jpg`
     - If `mobile_ratio`: `style.py --target-ratio <mobile_ratio> --max-dim 1080` → `mobile.jpg`
   - If `strategy: generate`:
     - Identity-safe check: if slot_id matches testimonial/expert/team patterns AND `ai_approved_by_user == false` — silently switch to `placeholder` strategy.
     - Else: `codex-generate-fallback.sh <project_dir> <slot_id> <width> <height> <ratio> <hint>` → `processed/<slot_id>/ai-generated.jpg`
     - Update `selections.yaml:slots[].log_ref` to point to the codex log.
   - If `strategy: placeholder`:
     - `svg-placeholder.py --slot-id <id> --width <w> --height <h> --hint <hint> --brand-primary <color> --out processed/<slot_id>/placeholder.png`
3. Run `preview-render.py --selections selections.yaml --out photo-preview.html`.

## Identity-safe

Per [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md): the silent strategy downgrade in step 2 (generate → placeholder when `ai_approved_by_user == false` for identity-safe slot) is the enforcement point.

## Tools

Bash, Read, Write.
```

- [ ] **Step 7: Run tests — pass**

```bash
bats tests/phase-prb/test-agents-frontmatter.bats
```

- [ ] **Step 8: Commit**

```bash
git add agents/photo-*.md tests/phase-prb/test-agents-frontmatter.bats
git commit -m "feat(pr-b): 4 photo-pipeline agents (curator, classifier, matcher, preview-board)"
```

---

## Task 12: `/landing-photos` slash command + stage gates

**Files:**
- Create: `commands/landing-photos.md`
- Create: `tests/phase-prb/test-landing-photos-gate.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-prb/test-landing-photos-gate.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "/landing-photos command file exists with frontmatter" {
    [ -f "$REPO/commands/landing-photos.md" ]
    head -10 "$REPO/commands/landing-photos.md" | grep -q "^description:"
}

@test "/landing-photos command mentions photo-curator agent" {
    grep -q "photo-curator" "$REPO/commands/landing-photos.md"
}

@test "/landing-photos command lists --force-stage and --all-ai flags" {
    grep -q -- "--force-stage" "$REPO/commands/landing-photos.md"
    grep -q -- "--all-ai" "$REPO/commands/landing-photos.md"
}

@test "/landing-photos command references stage gates 05_design and 07a_wireframe" {
    grep -q "05_design" "$REPO/commands/landing-photos.md"
    grep -q "07a_wireframe" "$REPO/commands/landing-photos.md"
}
```

- [ ] **Step 2: Run — fails**

- [ ] **Step 3: Create commands/landing-photos.md**

`commands/landing-photos.md`:
```markdown
---
description: Stage 07c (PR-B) — process client photos, AI-classify, match to wireframe slots, generate fallbacks, render preview. Requires approved 05_design + 07a_wireframe.
---

# /landing-photos

Запускает полный photo pipeline для проекта.

## Использование

```
/landing-photos [--project <slug>] [--force-stage <name>] [--all-ai]
```

- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--force-stage <intake|classify|match|preview>` — принудительный сброс этапа (для повторного прогона).
- `--all-ai` — пропустить inbox-сканирование, на все слоты использовать generative fallback. Требует подтверждения пользователем (modal в UI).

## Гейты

1. `<project>/.landing-state.yaml:stages.05_design.status == approved` — иначе:
   > Сначала утверди дизайн-систему (`05_ДИЗАЙН-СИСТЕМА/DESIGN.md`) — без tokens.json codex не может попасть в стиль.
2. `<project>/07a_WIREFRAME/selections.yaml` exists и пользователь выбрал варианты — иначе:
   > Сначала выбери варианты блоков в `wireframe.html` — нужно знать какие photo-слоты в финале.

## Что происходит

Команда вызывает `photo-curator` агента. См. [agents/photo-curator.md](../agents/photo-curator.md) для деталей этапов.

Артефакты появятся в `<project>/07c_PHOTOS/`:
- `inbox/` (7 подпапок) — куда положить фотки клиента
- `catalog.yaml`, `selections.yaml`, `photo-board.html`, `photo-preview.html`, `processed/`

## После выполнения

`composed.html` (PR-A) перерендерится с реальными фото вместо placeholders.
```

- [ ] **Step 4: Run + commit**

```bash
bats tests/phase-prb/test-landing-photos-gate.bats
git add commands/landing-photos.md tests/phase-prb/test-landing-photos-gate.bats
git commit -m "feat(pr-b): /landing-photos slash command with stage gates"
```

---

## Task 13: inbox/ subfolder template + READMEs

**Files:**
- Create: `template/07c_PHOTOS/README.md`
- Create: `template/07c_PHOTOS/inbox/_свалка/.gitkeep`
- Create: `template/07c_PHOTOS/inbox/портреты_и_команда/README.md`
- Create: `template/07c_PHOTOS/inbox/процесс_работы/README.md`
- Create: `template/07c_PHOTOS/inbox/объекты_и_продукты/README.md`
- Create: `template/07c_PHOTOS/inbox/интерьер_экстерьер/README.md`
- Create: `template/07c_PHOTOS/inbox/до_после/README.md`
- Create: `template/07c_PHOTOS/inbox/документы_сертификаты/README.md`
- Create: `tests/phase-prb/test-template-07c.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-prb/test-template-07c.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "template/07c_PHOTOS exists with README" {
    [ -d "$REPO/template/07c_PHOTOS" ]
    [ -f "$REPO/template/07c_PHOTOS/README.md" ]
}

@test "template has all 8 inbox subfolders" {
    for sub in "_свалка" "портреты_и_команда" "процесс_работы" "объекты_и_продукты" "интерьер_экстерьер" "до_после" "документы_сертификаты"; do
        [ -d "$REPO/template/07c_PHOTOS/inbox/$sub" ] || {
            echo "Missing subfolder: $sub"
            return 1
        }
    done
}

@test "every non-_свалка subfolder has a README" {
    for sub in "портреты_и_команда" "процесс_работы" "объекты_и_продукты" "интерьер_экстерьер" "до_после" "документы_сертификаты"; do
        [ -f "$REPO/template/07c_PHOTOS/inbox/$sub/README.md" ] || {
            echo "Missing README in $sub"
            return 1
        }
    done
}

@test "main README explains all 7 subfolders" {
    body="$(cat "$REPO/template/07c_PHOTOS/README.md")"
    for sub in "портреты_и_команда" "процесс_работы" "объекты_и_продукты" "интерьер_экстерьер" "до_после" "документы_сертификаты" "_свалка"; do
        echo "$body" | grep -q "$sub" || {
            echo "README doesn't mention $sub"
            return 1
        }
    done
}
```

- [ ] **Step 2: Run — fails**

- [ ] **Step 3: Create directory structure and main README**

```bash
mkdir -p template/07c_PHOTOS/inbox/{_свалка,портреты_и_команда,процесс_работы,объекты_и_продукты,интерьер_экстерьер,до_после,документы_сертификаты}
touch template/07c_PHOTOS/inbox/_свалка/.gitkeep
```

`template/07c_PHOTOS/README.md`:
```markdown
# 07c_PHOTOS — фото клиента и обработка

Это папка для фото клиента и всего что с ними происходит на конвейере PR-B.

## Куда что класть

Открой `inbox/` — внутри **7 подпапок с понятными русскими названиями**. Подсказка простая:

| Подпапка | Что туда | Пример |
|---|---|---|
| `_свалка/` | Если не знаешь куда — кидай сюда. AI разберётся. | Любая случайная фотка |
| `портреты_и_команда/` | Фото людей: эксперт, команда, клиенты для отзывов | Фото директора, групповое фото команды |
| `процесс_работы/` | Фото процесса: монтаж, ремонт, услуга в действии | Мастер работает, рука держит инструмент |
| `объекты_и_продукты/` | Готовые работы, изделия, объекты | Готовая кухня, упаковка товара |
| `интерьер_экстерьер/` | Офис, цех, помещение, фасад | Фото офиса, входная группа |
| `до_после/` | Пары «было → стало» | Старая кухня → новая кухня (именуй парами: `room1_before.jpg`, `room1_after.jpg`) |
| `документы_сертификаты/` | Дипломы, лицензии, сертификаты | Скан грамоты, лицензия СРО |

В каждой подпапке есть свой `README.md` с подсказкой по технике (какие пропорции, какой свет).

## Что произойдёт дальше

Когда запустишь `/landing-photos`:
1. Все фотки автоматически конвертируются в JPEG (если были HEIC с айфона), очищаются метаданные.
2. Фотки из `_свалка/` AI пометит тегами (портрет / объект / процесс / ...).
3. AI расставит фотки по слотам прототипа (где какая лучше подойдёт).
4. Ты увидишь HTML-галерею с предложением расстановки — можешь докрутить вручную.
5. Фотки обрежутся под нужные пропорции (16:9 для hero, 1:1 для аватаров, и т.д.).
6. На пустые слоты AI сгенерирует фото под брендинг сайта.
7. Финальный preview `photo-preview.html` покажет «фото в макетных местах».

## Что НЕ делать

- Не клади документы с персональными данными (паспорта, договоры) — это для другой папки.
- Не пытайся ретушировать лица — AI не трогает реальных людей (это правило системы, identity-safe).

## Артефакты после прогона

- `intake/` — обработанные JPEG + миниатюры (auto-generated)
- `catalog.yaml` — каталог фоток с тегами (auto-generated)
- `selections.yaml` — какое фото в какой слот (от тебя через photo-board.html)
- `processed/` — финальные обработанные фото для сайта (auto-generated)
- `photo-board.html` — UI для раскладывания (auto-generated)
- `photo-preview.html` — превью «фото в местах» (auto-generated)
- `STATE.yaml` — статусы этапов (auto-generated)
- `.logs/` — логи всех AI-вызовов для аудита
```

- [ ] **Step 4: Create per-subfolder READMEs**

`template/07c_PHOTOS/inbox/портреты_и_команда/README.md`:
```markdown
# портреты_и_команда

Фото людей для лендинга:
- **Эксперт / директор / основатель** — для блока «о нас», для testimonials
- **Команда** — групповое фото или индивидуальные портреты сотрудников
- **Клиенты** — для testimonials (с разрешением!)

## Рекомендации по технике

- **Пропорции:** лучше всего 1:1 (квадрат) или 3:4 (портретная). Это автоматически подойдёт под слоты testimonial-avatar (1:1) и expert-photo.
- **Свет:** мягкий, ровный. Не контровый, не сильные тени на лице.
- **Фон:** светлый, не пёстрый. Лучше офисный интерьер или нейтральный.
- **Кадрирование:** грудной портрет (medium-shot) лучше всего — лицо не слишком крупно, видны плечи.

## Чего избегать

- Селфи с фронталки (низкое качество)
- Групповые фото где половина закрыта другими
- Старые ч/б фотографии (если только не для специально стилизованного сайта)

После прогона `/landing-photos` AI пометит эти фотки тегами `portrait` и/или `team`.
```

`template/07c_PHOTOS/inbox/процесс_работы/README.md`:
```markdown
# процесс_работы

Фото услуги в действии: монтаж, ремонт, обработка, мастер за работой.

## Рекомендации

- **Пропорции:** 16:9 или 4:3 (горизонтальные) — идут в слоты process-step / how-we-work.
- **Композиция:** видно руки/инструменты/действие. Динамика, движение.
- **Свет:** рабочий, не постановочный.

## Чего избегать

- Постановочные фото с актёрами в чистой одежде
- Только продукт без процесса (это в `объекты_и_продукты/`)
```

`template/07c_PHOTOS/inbox/объекты_и_продукты/README.md`:
```markdown
# объекты_и_продукты

Готовые работы, изделия, товары, объекты.

## Рекомендации

- **Пропорции:** 4:3 или 16:9 (для hero-bg), 1:1 для product-card.
- **Резкость:** объект должен быть в фокусе, без размытия.
- **Фон:** чистый, не отвлекает от объекта.
- **Несколько ракурсов:** если возможно — фронт, ¾, деталь.

## Чего избегать

- Стоковые фото (Google → «кухня готовая»)
- Объект в захламлённом окружении
```

`template/07c_PHOTOS/inbox/интерьер_экстерьер/README.md`:
```markdown
# интерьер_экстерьер

Фото офиса, цеха, помещения, фасада здания.

## Рекомендации

- **Пропорции:** 16:9 (широкие) — для hero-bg, для блока «приходите к нам».
- **Перспектива:** прямая, не перекошенная. Используй panorama-режим на телефоне если узкое помещение.
- **Свет:** дневной если возможно. Включи всё освещение если съёмка вечером.

## Чего избегать

- Стоковые «офисы будущего»
- Фото с людьми (это в `портреты_и_команда/`)
```

`template/07c_PHOTOS/inbox/до_после/README.md`:
```markdown
# до_после

Пары «было → стало». Очень мощный социальный proof.

## Правила именования

Парами: `<id>_before.jpg` и `<id>_after.jpg`. Примеры:
- `kitchen_before.jpg` → `kitchen_after.jpg`
- `bathroom_2_before.jpg` → `bathroom_2_after.jpg`

## Рекомендации

- **Одинаковый ракурс** до и после! Это критично.
- **Одинаковый свет.** Если можно — заснять оба в одно и то же время суток.
- **Пропорции:** 4:3 или 16:9.
```

`template/07c_PHOTOS/inbox/документы_сертификаты/README.md`:
```markdown
# документы_сертификаты

Дипломы, лицензии, сертификаты, грамоты — для trust-блока.

## Рекомендации

- **Сканировать**, а не фотографировать — лучше резкость, нет бликов.
- Если фотографируешь — снимай прямо, без угла, при хорошем свете.
- **Размытие** персональных данных (имя, номер) если документ выложен в публичный блок.

## Чего избегать

- Размытые/наклонные фото
- Документы с явными ошибками (опечатки в сертификате)
```

- [ ] **Step 5: Run tests + commit**

```bash
bats tests/phase-prb/test-template-07c.bats
git add template/07c_PHOTOS/ tests/phase-prb/test-template-07c.bats
git commit -m "feat(pr-b): 07c_PHOTOS template with 7 inbox subfolders + russian READMEs"
```

---

## Task 14: Extend `scripts/test-pipeline.sh` with photo stage

**Files:**
- Modify: `scripts/test-pipeline.sh`
- Create: `tests/phase-prb/fixtures/sample-photos/team.jpg` (1 small)
- Create: `tests/phase-prb/fixtures/sample-photos/process.jpg`

- [ ] **Step 1: Create fixture photos**

```bash
mkdir -p tests/phase-prb/fixtures/sample-photos
python3 -c "
from PIL import Image
Image.new('RGB', (800, 800), (200, 150, 100)).save('tests/phase-prb/fixtures/sample-photos/team.jpg')
Image.new('RGB', (1200, 800), (100, 150, 200)).save('tests/phase-prb/fixtures/sample-photos/process.jpg')
Image.new('RGB', (1920, 1080), (150, 100, 150)).save('tests/phase-prb/fixtures/sample-photos/hero.jpg')
"
```

- [ ] **Step 2: Read existing test-pipeline.sh to find insertion point**

```bash
cat scripts/test-pipeline.sh | head -80
```

Locate the section after composed.html is generated. The photo stage runs AFTER PR-A pipeline completes.

- [ ] **Step 3: Add photo stage section to test-pipeline.sh**

At end of pipeline (after composed.html), append:

```bash
# --- PR-B Photo stage (optional, only if sample photos provided) ---
PHOTO_SAMPLES="${PHOTO_SAMPLES:-$LS_ROOT/tests/phase-prb/fixtures/sample-photos}"
if [ -d "$PHOTO_SAMPLES" ] && [ "$(ls -A "$PHOTO_SAMPLES" 2>/dev/null)" ]; then
    echo "→ Stage PR-B: running photo pipeline with sample photos..."

    PROJECT_DIR="$LS_ROOT/projects/$SLUG"
    mkdir -p "$PROJECT_DIR/07c_PHOTOS/inbox/_свалка"
    cp "$PHOTO_SAMPLES"/* "$PROJECT_DIR/07c_PHOTOS/inbox/_свалка/"

    # Stage 1: intake
    python3 "$LS_ROOT/skills/photo-curation/scripts/intake.py" \
        --inbox "$PROJECT_DIR/07c_PHOTOS/inbox" \
        --intake "$PROJECT_DIR/07c_PHOTOS/intake"
    echo "  ✓ intake done"

    # Stage 2: classify (using codex mock for predictable tests)
    if [ -n "${USE_CODEX_MOCK:-}" ]; then
        export CODEX_BIN="$LS_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    fi
    for photo in "$PROJECT_DIR/07c_PHOTOS/intake"/*.jpg; do
        [ -f "$photo" ] || continue
        [[ "$photo" == *.thumb.jpg ]] && continue
        bash "$LS_ROOT/skills/photo-curation/scripts/codex-classify.sh" "$PROJECT_DIR" "$photo"
    done
    echo "  ✓ classify done"

    # Stage 3: match (skipped in mock mode — we synthesize a draft)
    cat > "$PROJECT_DIR/07c_PHOTOS/selections.draft.yaml" <<'EOF'
slots: []
EOF
    echo "  ✓ match stub"

    # Stage 4: render gallery
    python3 "$LS_ROOT/skills/photo-curation/scripts/gallery-render.py" \
        --catalog "$PROJECT_DIR/07c_PHOTOS/catalog.yaml" \
        --draft "$PROJECT_DIR/07c_PHOTOS/selections.draft.yaml" \
        --out "$PROJECT_DIR/07c_PHOTOS/photo-board.html"
    echo "  ✓ gallery rendered"

    echo "  PR-B photo stage smoke test PASSED"
fi
```

- [ ] **Step 4: Run with mock**

```bash
USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh test-prb-pipeline tests/phase-pra/fixtures/example-prototype.md
```

Expected: pipeline completes, `projects/test-prb-pipeline/07c_PHOTOS/` populated.

- [ ] **Step 5: Commit**

```bash
git add scripts/test-pipeline.sh tests/phase-prb/fixtures/sample-photos/
git commit -m "test(pr-b): extend test-pipeline.sh with photo stage smoke test"
```

---

## Task 15: Update THIRD_PARTY_NOTICES.md and CLAUDE.md

**Files:**
- Modify: `THIRD_PARTY_NOTICES.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Read existing THIRD_PARTY_NOTICES.md**

```bash
cat THIRD_PARTY_NOTICES.md
```

- [ ] **Step 2: Append PR-B section**

Add at end of `THIRD_PARTY_NOTICES.md`:

```markdown

## nexu-io/open-design — PR-B Photo Pipeline patterns (Apache-2.0)

Added 2026-05-13 as part of PR-B (Photo Pipeline). Patterns ported from
https://github.com/nexu-io/open-design (Apache-2.0):

1. **selections.yaml `strategy` enum** (`generate | placeholder | bring-your-own`) —
   from `design-templates/open-design-landing/schema.ts:413`.
2. **Slot description fields** (id, file, width, height, ratio, required) —
   adapted from `design-templates/open-design-landing/assets/image-manifest.json`.
3. **SVG-placeholder as PNG** technique — re-implemented in
   `skills/photo-curation/scripts/svg-placeholder.py`. Original:
   `design-templates/open-design-landing/scripts/placeholder.ts`.
4. **AI-imagery anti-patterns list** (no lens flare, glitch, AI faces in collage,
   watermarks, surreal artifacts) — incorporated into
   `skills/photo-curation/templates/generate-fallback.md`. Original:
   `design-systems/atelier-zero/DESIGN.md` §11 + anti-patterns section.
5. **Skip-if-exists + --force pattern** — applied to
   `codex-generate-fallback.sh` and STATE.yaml stage tracking. Original:
   `design-templates/open-design-landing/scripts/imagegen.ts`.

License: Apache-2.0. Full text:
https://github.com/nexu-io/open-design/blob/main/LICENSE
```

- [ ] **Step 3: Update CLAUDE.md with PR-B section**

In `CLAUDE.md`, after the "Новые команды PR-A" section, add:

```markdown
## Новые команды PR-B (Photo Pipeline)

- `/landing-photos` — обработка клиентских фоток (intake/classify/match/process). Stage 07c.

**Workflow PR-B:**
1. Утверди этапы 05 (design-system) и 07a (wireframe).
2. Положи фотки клиента в `<project>/07c_PHOTOS/inbox/` (или в подпапки по типу — см. `07c_PHOTOS/README.md`).
3. Запусти `/landing-photos`.
4. Открой `07c_PHOTOS/photo-board.html` — расставь фотки по слотам, нажми Confirm — скачается `selections.yaml`.
5. Положи `selections.yaml` обратно в `07c_PHOTOS/`.
6. Открой `07c_PHOTOS/photo-preview.html` — проверь как фото лягут в макет.
7. После approve — `composed.html` перерендерится с реальными фото.

См. [spec](docs/superpowers/specs/2026-05-13-photo-pipeline-design.md).
```

- [ ] **Step 4: Commit**

```bash
git add THIRD_PARTY_NOTICES.md CLAUDE.md
git commit -m "docs(pr-b): attribution for nexu-io/open-design patterns + CLAUDE.md workflow"
```

---

## Final task: Run full test suite

- [ ] **Step 1: Run all PR-B tests**

```bash
python3 -m pytest tests/phase-prb/ -v
bats tests/phase-prb/
```

Expected: all tests pass.

- [ ] **Step 2: Run all PR-A tests to ensure no regressions**

```bash
bats tests/phase-pra/ tests/gate-check/ tests/phase-preview-panel/
```

Expected: all existing tests still pass.

- [ ] **Step 3: Run full test-pipeline.sh end-to-end**

```bash
USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh pr-b-final tests/phase-pra/fixtures/example-prototype.md
```

Expected: pipeline produces composed.html WITH photo substitution from sample fixtures.

- [ ] **Step 4: Manual smoke test on a real project (if available)**

```bash
# Choose a project where 05_design and 07a_wireframe are approved
cd <real-project>
# Run /landing-photos manually
```

Verify photo-board.html renders correctly, drag-drop works, selections.yaml downloads.

- [ ] **Step 5: Update plan with status**

Mark all tasks completed. If anything regressed — file as follow-up issue (not PR-B blocker).

---

## Acceptance checklist (from spec)

- [ ] `bash scripts/test-pipeline.sh` проходит включая photo-stage (Task 14)
- [ ] `/landing-photos` в живом проекте даёт `composed.html` с реальными фото (Task 10 + Final)
- [ ] `photo-board.html` корректно показывает слоты с pre-filled candidates, drag-drop работает (Task 6 + Final manual)
- [ ] 25+ unit-тестов проходят (Tasks 1-13)
- [ ] `STATE.yaml` фиксирует каждый этап, перезапуск продолжает с прерванного (Task 11 photo-curator)
- [ ] Идемпотентность: 2 запуска подряд = одна работа (Task 2 intake, Task 5 generate skip-if-exists)
- [ ] Identity-safe гейт работает: testimonial слот без `ai_approved_by_user` → placeholder, не AI (Task 8 validator + Task 11 preview-board)
- [ ] `THIRD_PARTY_NOTICES.md` обновлён (Task 15)
- [ ] `07c_PHOTOS/README.md` на русском с инструкцией для маркетолога (Task 13)
- [ ] Backward compatibility: проект без `07c_PHOTOS/selections.yaml` продолжает работать (Task 10)
