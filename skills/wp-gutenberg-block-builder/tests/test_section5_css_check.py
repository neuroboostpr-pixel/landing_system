"""Tests check-section5-css.py.

Passes when every `### Block N — Name` heading in §5 of DESIGN.md is followed
(within that block's body, before the next ### or ## heading) by at least one
fenced ```css block.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-section5-css.py"


def _write_design(project: Path, body: str) -> Path:
    d = project / "05_ДИЗАЙН-СИСТЕМА"
    d.mkdir(parents=True, exist_ok=True)
    md = d / "DESIGN.md"
    md.write_text(body, encoding="utf-8")
    return md


def test_passes_when_every_block_has_css(tmp_path):
    project = tmp_path / "p"
    _write_design(project, """\
## 5. Per-block layouts

### Block 1 — Hero

prose

```css
.hero { display: grid; }
```

### Block 2 — FAQ

```css
.faq__item { border-block-end: 1px solid var(--border); }
```
""")
    r = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_fails_when_a_block_has_no_css(tmp_path):
    project = tmp_path / "p"
    _write_design(project, """\
## 5. Per-block layouts

### Block 1 — Hero

```css
.hero { display: grid; }
```

### Block 2 — FAQ

just prose, no css fence
""")
    r = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert r.returncode != 0
    assert "FAQ" in r.stderr or "FAQ" in r.stdout or "Block 2" in r.stderr or "Block 2" in r.stdout


def test_fails_when_section5_missing(tmp_path):
    project = tmp_path / "p"
    _write_design(project, "## 2. Tokens\n\n```css\n:root {}\n```\n")
    r = subprocess.run([sys.executable, str(SCRIPT), str(project)], capture_output=True, text=True)
    assert r.returncode != 0
