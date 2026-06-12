"""B36 — normalize-block-colors.py: хардкод/brand цвета → var(--lp-*) с
нейтральными :root-дефолтами. Унификация префикса --color-* → --lp-*.
"""
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "normalize-block-colors.py"


def _load():
    spec = importlib.util.spec_from_file_location("normalize_block_colors", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rename_color_prefix_to_lp():
    m = _load()
    css = ".x{color:var(--color-fg);background:var(--color-bg)}"
    out = m.normalize_colors(css)
    assert "--lp-text" in out
    assert "--lp-bg" in out
    assert "--color-fg" not in out
    assert "--color-bg" not in out


def test_root_brand_defaults_neutralized():
    m = _load()
    css = ":root{--color-accent:#0066ff;--color-bg:#fafafa;--color-fg:#1a1a1a;--color-border:#e0e0e0}"
    out = m.normalize_colors(css)
    # accent больше не брендовый синий — нейтральный
    assert "#0066ff" not in out
    # переменная переименована и имеет нейтральный дефолт
    assert "--lp-accent:" in out.replace(" ", "")


def test_hardcoded_bg_color_to_var_by_luminance():
    m = _load()
    # яркий насыщенный цвет в background → accent
    css = ".btn{background:#0066ff;color:#ffffff}"
    out = m.normalize_colors(css)
    assert "#0066ff" not in out
    assert "var(--lp-accent)" in out


def test_dark_text_color_to_text_var():
    m = _load()
    css = ".t{color:#15140f}"
    out = m.normalize_colors(css)
    assert "#15140f" not in out
    assert "var(--lp-text)" in out


def test_neutral_colors_left_alone():
    m = _load()
    # чисто структурные нейтральные значения в shadow допустимы — не обязаны меняться
    css = ".c{box-shadow:0 1px 3px rgba(0,0,0,0.1)}"
    out = m.normalize_colors(css)
    assert "rgba(0,0,0,0.1)" in out


def test_luminance_helper():
    m = _load()
    assert m.luminance("#ffffff") > 0.9
    assert m.luminance("#000000") < 0.1
    assert 0.3 < m.luminance("#808080") < 0.7


def test_role_for_color():
    m = _load()
    # очень светлый → bg, очень тёмный → text, насыщенный → accent
    assert m.role_for_color("#fafafa", "background") == "bg"
    assert m.role_for_color("#15140f", "color") == "text"
    assert m.role_for_color("#0066ff", "background") == "accent"
