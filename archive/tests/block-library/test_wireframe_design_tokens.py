"""Wireframe накладывает дизайн-систему проекта (tokens.json) на блоки.

render-wireframe строит :root с --lp-* из tokens.json проекта (реальные цвета/
шрифты клиента), а не нейтральную заглушку. Без tokens.json — нейтральный
fallback. (BACKLOG B31/B35, уточнено 2026-06-02.)
"""
import importlib.util
from pathlib import Path

import json

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "wireframe-rendering" / "scripts" / "render-wireframe.py"


def _load():
    spec = importlib.util.spec_from_file_location("render_wireframe", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_tokens_root_css_from_nested_tokens(tmp_path):
    # структура neurokreator: colors.primary.orange, colors.neutral.*
    m = _load()
    tokens = {
        "colors": {
            "primary": {"orange": "#FFA500"},
            "secondary": {"black": "#000000"},
            "neutral": {"white": "#FFFFFF", "light_gray": "#F5F5F5",
                        "border_gray": "#CCCCCC", "text_gray": "#333333",
                        "placeholder_gray": "#999999"},
        },
        "typography": {"font_family": {"primary": "Inter, sans-serif"}},
    }
    css = m._design_tokens_root_css(tokens)
    assert ":root" in css
    # бренд-акцент попал в --lp-accent
    assert "#FFA500" in css
    assert "--lp-accent" in css
    # фон/текст/бордер заданы
    assert "--lp-bg" in css and "--lp-text" in css and "--lp-border" in css
    # шрифт
    assert "Inter" in css


def test_tokens_root_css_from_flat_tokens():
    # плоская структура (dubai-стиль): colors.accent, colors.bg, colors.fg
    m = _load()
    tokens = {"colors": {"accent": "#06C16E", "bg": "#0A0A0A",
                         "text_primary": "#FFFFFF", "border": "#262626"}}
    css = m._design_tokens_root_css(tokens)
    assert "#06C16E" in css
    assert "--lp-accent" in css


def test_no_tokens_returns_empty():
    m = _load()
    assert m._design_tokens_root_css({}) == ""
    assert m._design_tokens_root_css(None) == ""


def test_load_project_tokens(tmp_path):
    m = _load()
    proj = tmp_path / "proj"
    (proj / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (proj / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(
        json.dumps({"colors": {"accent": "#FF0000"}}), encoding="utf-8"
    )
    tok = m._load_project_tokens(proj)
    assert tok.get("colors", {}).get("accent") == "#FF0000"
    # отсутствие файла → пустой dict
    assert m._load_project_tokens(tmp_path / "nope") == {}
