"""Tests for lint_heuristics.py — one test per heuristic, pass and fail cases."""
import importlib.util
import sys
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"
sys.path.insert(0, str(LIB))

m = importlib.util.spec_from_file_location("lint_heuristics", LIB / "lint_heuristics.py")
lh = importlib.util.module_from_spec(m); m.loader.exec_module(lh)
si_m = importlib.util.spec_from_file_location("spec_inspector", LIB / "spec_inspector.py")
si = importlib.util.module_from_spec(si_m); si_m.loader.exec_module(si)


def _make_spec_block(slug, controls=None, template=None):
    return si.InspectedSpecBlock(
        slug=slug, probe_selector=".x", probe_kind="single", type="single",
        controls=[si.InspectedControl(name=n, type=t, has_default=True, default_value=v)
                  for n, t, v in (controls or [])],
        template=template or [],
    )


def _soup(html):
    parsed = BeautifulSoup(html, "html.parser")
    # Return first element child (the wrapper div)
    for child in parsed.children:
        if child.name:
            return child
    return parsed


def test_bullets_pass_when_li_count_matches_controls():
    spec_block = _make_spec_block("model-card", controls=[
        ("range", "text", "1,390 km"),
        ("accel", "text", "5.4 s"),
        ("top_speed", "text", "180 km/h"),
        ("fuel", "text", "6.5 L/100km"),
    ])
    soup = _soup('<div class="model-card"><ul class="model-specs"><li>a</li><li>b</li><li>c</li><li>d</li></ul></div>')
    issues = lh.check_bullets(spec_block, soup)
    assert issues == []


def test_bullets_fail_when_li_count_exceeds_controls():
    spec_block = _make_spec_block("model-card", controls=[
        ("range", "text", "x"), ("accel", "text", "x"), ("top_speed", "text", "x"),
    ])
    soup = _soup('<div class="model-card"><ul class="model-specs"><li>a</li><li>b</li><li>c</li><li>d</li></ul></div>')
    issues = lh.check_bullets(spec_block, soup)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "4" in issues[0].message and "3" in issues[0].message


def test_color_swatches_pass_when_colors_control_present():
    spec_block = _make_spec_block("model-card", controls=[("colors", "text", "#FFF,#000,#888")])
    soup = _soup('<div class="model-card"><span class="color-swatch" style="--c:#fff"></span>'
                 '<span class="color-swatch" style="--c:#000"></span></div>')
    issues = lh.check_color_swatches(spec_block, soup)
    assert issues == []


def test_color_swatches_fail_when_swatches_exist_and_no_control():
    spec_block = _make_spec_block("model-card", controls=[("name", "text", "")])
    soup = _soup('<div class="model-card"><span class="color-swatch" style="--c:#fff"></span></div>')
    issues = lh.check_color_swatches(spec_block, soup)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "color" in issues[0].message.lower()


def test_multi_paragraph_pass_when_textarea_has_separators():
    spec_block = _make_spec_block("features", controls=[
        ("feat_statement", "textarea", "Para 1\n\nPara 2\n\nPara 3\n\nPara 4"),
    ])
    soup = _soup('<div class="feature-statement"><p>1</p><p>2</p><p>3</p><p>4</p></div>')
    issues = lh.check_multi_paragraph(spec_block, soup, target_field="feat_statement")
    assert issues == []


def test_multi_paragraph_fail_when_textarea_only_one_para():
    spec_block = _make_spec_block("features", controls=[("feat_statement", "textarea", "Single line")])
    soup = _soup('<div class="feature-statement"><p>1</p><p>2</p><p>3</p><p>4</p></div>')
    issues = lh.check_multi_paragraph(spec_block, soup, target_field="feat_statement")
    assert len(issues) == 1
    assert "4" in issues[0].message and "1" in issues[0].message


def test_slider_images_pass_when_all_photo_fields_filled():
    spec_block = _make_spec_block("model-card", template=[
        {"photo1": "x", "photo2": "x", "photo3": "x", "photo4": "x", "photo5": "x"},
    ])
    soup = _soup('<div class="model-card"><div class="slider-track">'
                 '<img src="a.jpg"><img src="b.jpg"><img src="c.jpg"><img src="d.jpg"><img src="e.jpg">'
                 '</div></div>')
    issues = lh.check_slider_images(spec_block, soup, template_index=0)
    assert issues == []


def test_slider_images_fail_when_photo_fields_empty():
    spec_block = _make_spec_block("model-card", template=[
        {"photo1": "", "photo2": "", "photo3": ""},
    ])
    soup = _soup('<div class="model-card"><div class="slider-track">'
                 '<img src="a.jpg"><img src="b.jpg"><img src="c.jpg"><img src="d.jpg"><img src="e.jpg">'
                 '</div></div>')
    issues = lh.check_slider_images(spec_block, soup, template_index=0)
    assert len(issues) == 1
    assert "5" in issues[0].message


def test_inline_svg_pass_when_control_has_value():
    spec_block = _make_spec_block("feature-card", controls=[("icon_svg", "textarea", "%3Csvg%3E")], template=[{"icon_svg": "%3Csvg%3E"}])
    soup = _soup('<article class="feature-card"><span class="feature-icon"><svg></svg></span></article>')
    issues = lh.check_inline_svg_icon(spec_block, soup, template_index=0)
    assert issues == []


def test_inline_svg_fail_when_dom_has_svg_but_template_empty():
    spec_block = _make_spec_block("feature-card", controls=[("icon_svg", "textarea", "")], template=[{"icon_svg": ""}])
    soup = _soup('<article class="feature-card"><span class="feature-icon"><svg></svg></span></article>')
    issues = lh.check_inline_svg_icon(spec_block, soup, template_index=0)
    assert len(issues) == 1
