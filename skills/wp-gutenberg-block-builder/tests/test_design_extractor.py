import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from design_extractor import extract, DesignExtractError  # noqa: E402

MD_MIN = """\
# Design system

## 2. Design tokens

### 2.1 Colors

```css
:root {
  --bg-base: #0E2B30;
  --accent-coral: #E85E48;
}
```

### 2.2 Typography

```css
:root {
  --font-display: "Geologica", sans-serif;
  --fs-h1: clamp(2.5rem, 1.5rem + 4vw, 6rem);
}
```

## 3. Grid

```css
.container { max-width: 1200px; margin-inline: auto; }
```

## 4. Section primitives

```css
.section { padding-block: var(--space-9); }
```

## 5. Per-block layouts

### Block 1 — Hero

```css
.hero__title { font-size: var(--fs-h1); }
```

## 10. Asset checklist

Nothing here.
"""


def test_extract_merges_section_2_css_into_root(tmp_path):
    md = tmp_path / "DESIGN.md"
    md.write_text(MD_MIN, encoding="utf-8")
    style_css, main_css = extract(md)
    assert ":root {" in style_css
    assert "--bg-base: #0E2B30" in style_css
    assert "--accent-coral: #E85E48" in style_css
    assert '--font-display: "Geologica"' in style_css
    assert "--fs-h1: clamp(" in style_css
    assert style_css.count(":root {") == 1


def test_extract_concatenates_sections_3_to_9_into_main(tmp_path):
    md = tmp_path / "DESIGN.md"
    md.write_text(MD_MIN, encoding="utf-8")
    _, main_css = extract(md)
    assert ".container" in main_css
    assert ".section" in main_css
    assert ".hero__title" in main_css


def test_extract_skips_section_10_and_beyond(tmp_path):
    md = tmp_path / "DESIGN.md"
    md.write_text(
        MD_MIN + "\n\n```css\n.should-not-appear { color: red; }\n```\n",
        encoding="utf-8",
    )
    style_css, main_css = extract(md)
    assert ".should-not-appear" not in style_css
    assert ".should-not-appear" not in main_css


def test_extract_missing_file_raises(tmp_path):
    with pytest.raises(DesignExtractError, match="not found"):
        extract(tmp_path / "missing.md")


def test_extract_no_css_blocks_returns_empty_strings(tmp_path):
    md = tmp_path / "DESIGN.md"
    md.write_text("# Empty design doc\n\nNo CSS here.\n", encoding="utf-8")
    style_css, main_css = extract(md)
    assert style_css == ""
    assert main_css == ""


def test_extract_preserves_media_query_wrapping_root(tmp_path):
    """A §2 fenced block may contain ``@media (...) { :root {...} }``.
    The top-level :root is merged into style.css; the @media wrapper must
    survive verbatim so reduced-motion overrides still ship."""
    md = tmp_path / "DESIGN.md"
    md.write_text(
        "## 2. Design tokens\n\n"
        "```css\n"
        ":root { --dur-fast: 120ms; }\n"
        "@media (prefers-reduced-motion: reduce) {\n"
        "  :root { --dur-fast: 0ms; }\n"
        "}\n"
        "```\n",
        encoding="utf-8",
    )
    style_css, _ = extract(md)
    assert "--dur-fast: 120ms" in style_css
    assert "@media (prefers-reduced-motion: reduce)" in style_css
    # The merged :root block appears exactly once at the top.
    assert style_css.count(":root {") == 2  # merged + the one inside @media


def test_extract_real_neuroupgrade_v2_smoke():
    """Smoke test against the real project file (skip if absent)."""
    real = Path("d:/AI_TEAMS/Lendings/neuroupgrade-v2/05_ДИЗАЙН-СИСТЕМА/DESIGN.md")
    if not real.exists():
        pytest.skip("real neuroupgrade-v2 DESIGN.md unavailable")
    style_css, main_css = extract(real)
    assert "--bg-base:" in style_css and "#0E2B30" in style_css
    assert "--accent-coral:" in style_css and "#E85E48" in style_css
    assert "--fw-light:" in style_css
    assert ".container" in main_css
    assert ".section" in main_css
    # at least one fenced css block was carried through from §3–§9
    assert len(main_css) > 200
