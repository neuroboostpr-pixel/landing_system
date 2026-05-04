"""Tests for wp-gutenberg-block-builder/scripts/generate-theme.py"""
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


def test_script_exists():
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"


def test_find_project_root_success(wp_theme_project):
    mod = _load()
    root = mod._find_project_root(wp_theme_project)
    assert root == wp_theme_project


def test_find_project_root_fail(tmp_path):
    mod = _load()
    with pytest.raises(FileNotFoundError):
        mod._find_project_root(tmp_path)


def test_css_variables_has_root_block(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert css.startswith(":root {")
    assert css.strip().endswith("}")


def test_css_variables_includes_colors(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert "--color-primary: #ff5733" in css
    assert "--color-secondary: #33c1ff" in css


def test_css_variables_includes_typography(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert "--font-display-family: 'Cabinet Grotesk'" in css
    assert "--font-body-family: 'Inter'" in css


def test_css_variables_includes_spacing(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert "--space-md: 1rem" in css


def test_main_returns_zero(wp_theme_project):
    mod = _load()
    result = mod.main(["prog", str(wp_theme_project)])
    assert result == 0


def test_main_creates_style_css(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    css_path = wp_theme_project / "08_КОД" / "wp-theme" / "style.css"
    assert css_path.exists()
    content = css_path.read_text(encoding="utf-8")
    assert "Theme Name:" in content
    assert ":root {" in content
    assert "--color-primary:" in content


def test_main_creates_functions_php(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    php_path = wp_theme_project / "08_КОД" / "wp-theme" / "functions.php"
    assert php_path.exists()
    content = php_path.read_text(encoding="utf-8")
    assert "lp_enqueue_assets" in content
    assert "wp_enqueue_style" in content
    assert "bunny.net" in content


def test_main_functions_php_cinematic_has_gsap(tmp_path, sample_tokens, sample_stack_cinematic):
    import json, yaml
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(json.dumps(sample_tokens))
    (tmp_path / "06_СТЕК").mkdir()
    (tmp_path / "06_СТЕК" / "design-stack.yaml").write_text(yaml.dump(sample_stack_cinematic, allow_unicode=True))
    (tmp_path / "07_КОНТЕНТ").mkdir()
    (tmp_path / "07_КОНТЕНТ" / "final-copy.md").write_text("## HERO\ntext")
    (tmp_path / "08_КОД").mkdir()

    mod = _load()
    mod.main(["prog", str(tmp_path)])
    php = (tmp_path / "08_КОД" / "wp-theme" / "functions.php").read_text()
    assert "gsap" in php.lower()


def test_main_creates_template_parts_dir(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "wp-theme" / "template-parts").is_dir()


def test_main_creates_assets_dirs(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    theme = wp_theme_project / "08_КОД" / "wp-theme"
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images"]:
        assert (theme / sub).is_dir(), f"Missing: {sub}"


def test_main_creates_index_php(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "wp-theme" / "index.php").exists()


def test_main_creates_front_page_php(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    php = (wp_theme_project / "08_КОД" / "wp-theme" / "front-page.php").read_text()
    assert "get_header" in php
    assert "get_footer" in php
    assert "template-parts/section" in php


def test_main_creates_gutenberg_blocks_dir(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "gutenberg-blocks").is_dir()


def test_main_missing_tokens_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
