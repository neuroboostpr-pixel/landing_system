"""Tests for wp-gutenberg-block-builder/scripts/generate-theme.py.

The theme generator now reads DESIGN.md (via design_extractor) as the canonical
CSS source. Token-derivation logic (``_css_variables`` etc.) was removed in
stage-08 / 2026-05-13 refactor; tokens.json is no longer consumed.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "generate-theme.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_theme", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SAMPLE_DESIGN_MD = """\
# Design

## 2. Design tokens

```css
:root {
  --bg-base: #0E2B30;
  --accent-coral: #E85E48;
  --fs-h1: clamp(2.5rem, 1.5rem + 4vw, 6rem);
}
```

## 3. Grid

```css
.container { max-width: 1200px; margin-inline: auto; }
```

## 5. Per-block

```css
.hero__title { font-size: var(--fs-h1); color: var(--accent-coral); }
```

## 10. Skipped

```css
.must-not-appear { color: red; }
```
"""


def _seed_design_md(project: Path, body: str = SAMPLE_DESIGN_MD) -> None:
    d = project / "05_ДИЗАЙН-СИСТЕМА"
    d.mkdir(parents=True, exist_ok=True)
    (d / "DESIGN.md").write_text(body, encoding="utf-8")


def test_script_exists():
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"


def test_find_project_root_success(wp_theme_project):
    """``wp_theme_project`` fixture seeds tokens.json (legacy); generator still
    finds the project root via that fallback even without DESIGN.md."""
    mod = _load()
    root = mod._find_project_root(wp_theme_project)
    assert root == wp_theme_project


def test_find_project_root_prefers_design_md(tmp_path):
    mod = _load()
    _seed_design_md(tmp_path)
    assert mod._find_project_root(tmp_path) == tmp_path


def test_find_project_root_fail(tmp_path):
    mod = _load()
    with pytest.raises(FileNotFoundError):
        mod._find_project_root(tmp_path)


def test_main_returns_zero(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    assert mod.main(["prog", str(wp_theme_project)]) == 0


def test_main_writes_style_css_from_design_md(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    css = (wp_theme_project / "08_КОД" / "wp-theme" / "style.css").read_text(encoding="utf-8")
    assert "Theme Name:" in css
    assert ":root {" in css
    assert "--bg-base: #0E2B30" in css
    assert "--accent-coral: #E85E48" in css
    assert "--fs-h1: clamp(" in css
    # §10 must NOT bleed through
    assert ".must-not-appear" not in css


def test_main_writes_main_css_from_design_md_sections_3_to_9(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    main_css = (wp_theme_project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert ".container" in main_css
    assert ".hero__title" in main_css
    assert ".must-not-appear" not in main_css


def test_main_placeholder_when_design_md_has_no_css(wp_theme_project):
    """Missing/empty DESIGN.md → tiny placeholders, no crash, return 0."""
    mod = _load()
    d = wp_theme_project / "05_ДИЗАЙН-СИСТЕМА"
    d.mkdir(parents=True, exist_ok=True)
    (d / "DESIGN.md").write_text("# empty\n", encoding="utf-8")
    assert mod.main(["prog", str(wp_theme_project)]) == 0
    css = (wp_theme_project / "08_КОД" / "wp-theme" / "style.css").read_text(encoding="utf-8")
    assert ":root {}" in css
    main_css = (wp_theme_project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert "main.css" in main_css  # the placeholder comment


def test_main_creates_functions_php(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    php_path = wp_theme_project / "08_КОД" / "wp-theme" / "functions.php"
    assert php_path.exists()
    content = php_path.read_text(encoding="utf-8")
    assert "lp_enqueue_assets" in content
    assert "wp_enqueue_style" in content
    assert "bunny.net" in content


def test_main_functions_php_cinematic_has_gsap(tmp_path, sample_stack_cinematic):
    import yaml
    _seed_design_md(tmp_path)
    (tmp_path / "06_СТЕК").mkdir()
    (tmp_path / "06_СТЕК" / "design-stack.yaml").write_text(
        yaml.dump(sample_stack_cinematic, allow_unicode=True)
    )
    (tmp_path / "07_КОНТЕНТ").mkdir()
    (tmp_path / "07_КОНТЕНТ" / "final-copy.md").write_text("## HERO\ntext")
    (tmp_path / "08_КОД").mkdir()

    mod = _load()
    mod.main(["prog", str(tmp_path)])
    php = (tmp_path / "08_КОД" / "wp-theme" / "functions.php").read_text()
    assert "gsap" in php.lower()


def test_main_creates_assets_dirs(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    theme = wp_theme_project / "08_КОД" / "wp-theme"
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images"]:
        assert (theme / sub).is_dir(), f"Missing: {sub}"


def test_main_creates_index_php(wp_theme_project):
    """index.php must be a functional WP template that calls the_content()."""
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    idx = wp_theme_project / "08_КОД" / "wp-theme" / "index.php"
    assert idx.exists()
    body = idx.read_text(encoding="utf-8")
    assert "the_content()" in body
    assert "wp_head()" in body
    assert "wp_footer()" in body
    assert "Silence is golden" not in body


def test_main_creates_blocks_dir(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "wp-theme" / "blocks").is_dir()


def test_main_does_not_create_legacy_dirs(wp_theme_project):
    mod = _load()
    _seed_design_md(wp_theme_project)
    mod.main(["prog", str(wp_theme_project)])
    assert not (wp_theme_project / "08_КОД" / "wp-theme" / "template-parts").exists()
    assert not (wp_theme_project / "08_КОД" / "gutenberg-blocks").exists()


def test_main_missing_tokens_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
