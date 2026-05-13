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


def test_main_creates_assets_dirs(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    theme = wp_theme_project / "08_КОД" / "wp-theme"
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images"]:
        assert (theme / sub).is_dir(), f"Missing: {sub}"


def test_main_creates_index_php(wp_theme_project):
    """index.php must be a functional WP template that calls the_content() —
    front page is now a Gutenberg page (page_on_front), not a hand-crafted
    front-page.php, so index.php must render it."""
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    idx = wp_theme_project / "08_КОД" / "wp-theme" / "index.php"
    assert idx.exists()
    body = idx.read_text(encoding="utf-8")
    assert "the_content()" in body
    assert "wp_head()" in body
    assert "wp_footer()" in body
    # Must NOT be the old plugin-style stub
    assert "Silence is golden" not in body


def test_main_creates_blocks_dir(wp_theme_project):
    """wp-theme/blocks/ is where generate-lzb-templates.py writes block.php files."""
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "wp-theme" / "blocks").is_dir()


def test_main_does_not_create_legacy_dirs(wp_theme_project):
    """No more template-parts/ or 08_КОД/gutenberg-blocks/ — those were ACF Blocks era."""
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert not (wp_theme_project / "08_КОД" / "wp-theme" / "template-parts").exists()
    assert not (wp_theme_project / "08_КОД" / "gutenberg-blocks").exists()


def test_main_missing_tokens_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1


# --- design-tokens.org nested schema support ---

@pytest.fixture
def nested_tokens():
    return {
        "color": {
            "bg": {
                "base":     {"value": "#0E2B30"},
                "section":  {"value": "#143A3F"},
            },
            "accent": {
                "mint":  {"value": "#77D9D9"},
                "coral": {"value": "#E85E48"},
            },
            "semantic": {
                "focus": {"value": "{color.accent.mint}"},
                "error": {"value": "{color.accent.coral}"},
            },
        },
        "font": {
            "family": {
                "display": {"value": "Geologica, system-ui, sans-serif"},
                "body":    {"value": "Roboto, sans-serif"},
            },
            "weight": {
                "regular": {"value": 400},
                "bold":    {"value": 700},
            },
            "size": {
                "h1":   {"value": "clamp(2.5rem, 1.5rem + 4vw, 6rem)"},
                "body": {"value": "1rem"},
            },
            "lineHeight": {
                "display": {"value": 1.10},
                "body":    {"value": 1.30},
            },
            "letterSpacing": {
                "eyebrow": {"value": "0.18em"},
            },
        },
        "space": {
            "0": {"value": "0"},
            "4": {"value": "16px"},
            "9": {"value": "64px"},
        },
        "radius": {
            "md":   {"value": "8px"},
            "pill": {"value": "9999px"},
        },
        "shadow": {
            "md": {"value": "0 4px 12px rgba(0,0,0,0.32)"},
        },
        "zIndex": {
            "modal": {"value": 100},
        },
    }


def test_css_variables_resolves_design_tokens_org_format(nested_tokens):
    mod = _load()
    css = mod._css_variables(nested_tokens)
    assert "--color-bg-base: #0E2B30" in css
    assert "--color-accent-mint: #77D9D9" in css
    assert "--font-size-h1: clamp(2.5rem, 1.5rem + 4vw, 6rem)" in css
    assert "--font-family-display:" in css
    assert "Geologica" in css
    assert "--font-weight-bold: 700" in css
    assert "--font-line-height-display: 1.1" in css
    assert "--font-letter-spacing-eyebrow: 0.18em" in css
    assert "--space-4: 16px" in css
    assert "--radius-md: 8px" in css
    assert "--shadow-md: 0 4px 12px rgba(0,0,0,0.32)" in css
    assert "--z-modal: 100" in css


def test_css_variables_resolves_token_references(nested_tokens):
    mod = _load()
    css = mod._css_variables(nested_tokens)
    # {color.accent.mint} should resolve to #77D9D9
    assert "--color-semantic-focus: #77D9D9" in css
    assert "--color-semantic-error: #E85E48" in css


def test_css_variables_handles_both_schemas(sample_tokens, nested_tokens):
    mod = _load()
    flat_css = mod._css_variables(sample_tokens)
    assert "--color-primary: #ff5733" in flat_css
    nested_css = mod._css_variables(nested_tokens)
    assert "--color-bg-base: #0E2B30" in nested_css


def test_main_creates_main_css_with_baseline(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    main_css = wp_theme_project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css"
    assert main_css.exists()
    body = main_css.read_text(encoding="utf-8")
    assert "var(--color-bg-base" in body
    assert ".nu-tier-grid" in body
    assert ".lp-card" in body
    assert "display: grid" in body
