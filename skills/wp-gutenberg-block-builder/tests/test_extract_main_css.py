"""Tests extract-main-css.py.

Calls design_extractor.extract() under the hood and writes only main.css.
Must NOT touch style.css, functions.php, index.php.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract-main-css.py"


def _make_project(tmp_path: Path, design_md: str, existing_style: str = "/* original */") -> Path:
    project = tmp_path / "proj"
    (project / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").write_text(design_md, encoding="utf-8")
    (project / "08_КОД" / "wp-theme" / "assets" / "css").mkdir(parents=True)
    (project / "08_КОД" / "wp-theme" / "style.css").write_text(existing_style, encoding="utf-8")
    return project


DESIGN = """\
# D
## 2. Design tokens
```css
:root { --x: 1; }
```
## 3. Grid
```css
.container { max-width: 1200px; }
```
## 5. Per-block layouts
### Block 1 — Hero
```css
.hero { display: grid; }
```
"""


def test_writes_main_css_with_section_3_and_5_rules(tmp_path):
    project = _make_project(tmp_path, DESIGN)
    r = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    main_css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert ".container" in main_css
    assert ".hero { display: grid; }" in main_css


def test_does_not_touch_style_css(tmp_path):
    project = _make_project(tmp_path, DESIGN, existing_style="/* DO NOT TOUCH */")
    subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True, check=True)
    assert (project / "08_КОД" / "wp-theme" / "style.css").read_text(encoding="utf-8") == "/* DO NOT TOUCH */"


def test_section_order_preserved_in_document_order(tmp_path):
    """design_extractor walks sections in document order, not numeric order.

    This pins behavior so we know DESIGN.md must be written in numeric order
    for the cascade to be correct.
    """
    md = """\
## 3. Grid
```css
/* THREE */
.three { x: 1; }
```
## 5. Per-block
### Block 1 — Hero
```css
/* FIVE */
.five { x: 1; }
```
## 4. Section primitives
```css
/* FOUR */
.four { x: 1; }
```
"""
    project = _make_project(tmp_path, md)
    subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True, check=True)
    main_css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    pos_three = main_css.index("/* THREE */")
    pos_four = main_css.index("/* FOUR */")
    pos_five = main_css.index("/* FIVE */")
    # Document order: 3 → 5 → 4. design_extractor preserves document order.
    assert pos_three < pos_five < pos_four


def test_missing_theme_dir_fails_gracefully(tmp_path):
    project = tmp_path / "p"
    (project / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").write_text(DESIGN, encoding="utf-8")
    # No 08_КОД/wp-theme/assets/css dir — /landing-build hasn't run
    r = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert r.returncode == 1


def test_missing_design_md_fails(tmp_path):
    project = tmp_path / "p"
    (project / "08_КОД" / "wp-theme" / "assets" / "css").mkdir(parents=True)
    r = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert r.returncode == 1
