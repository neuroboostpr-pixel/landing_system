"""Tests for generate-lzb-templates.py — spec-driven (stage-08/2026-05-13)."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-lzb-templates.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def _write_spec(project: Path, yaml_body: str) -> None:
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True, exist_ok=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(yaml_body, encoding="utf-8")


def test_creates_block_php_for_single_block(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    f = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php"
    assert f.exists()
    body = f.read_text(encoding="utf-8")
    assert "<?php" in body
    assert "$attributes['heading']" in body


def test_creates_section_with_inner_blocks_tag(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    section = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify" / "block.php").read_text(encoding="utf-8")
    assert "<InnerBlocks" in section
    assert "lazyblock/tarify-card" in section
    assert "nu-tier-grid" in section


def test_creates_card_block_php(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    card = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify-card" / "block.php"
    assert card.exists()
    body = card.read_text(encoding="utf-8")
    assert "$attributes['name']" in body
    assert "foreach" in body
    assert "$attributes['features']" in body


def test_never_overwrites_existing_block_php(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    hero = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php"
    hero.write_text("<?php // hand-edited\n", encoding="utf-8")
    _run(project)
    assert hero.read_text(encoding="utf-8") == "<?php // hand-edited\n"


def test_image_control_uses_attachment_src_helper(tmp_path):
    project = _make_project(tmp_path)
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\", css_class: \"hero__title\", element: h1 }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\", css_class: \"hero__title\", element: h1 }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\", css_class: \"hero__portrait\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "wp_get_attachment_image" in body
    assert "['url']" in body
    assert "hero__portrait" in body


def test_toggle_emits_visible_conditional(tmp_path):
    project = tmp_path / "proj"
    _write_spec(project,
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_t, name: featured, type: toggle, label: F, default: false }\n"
    )
    r = _run(project)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "if (!empty($attributes['featured']))" in body
    assert "lp-field--featured" in body
    assert "/* toggle" not in body


def test_repeater_url_child_uses_esc_url(tmp_path):
    project = tmp_path / "proj"
    _write_spec(project,
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_lst, name: links, type: repeater, label: L }\n"
        "      - { id: c_url, name: href, type: url, label: U, default: '#', child_of: c_lst }\n"
        "      - { id: c_rich, name: html, type: rich-text, label: H, default: '', child_of: c_lst }\n"
    )
    r = _run(project)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "esc_url($row['href']" in body
    assert "wp_kses_post($row['html']" in body


def test_section_grid_class_is_escaped(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify" / "block.php").read_text(encoding="utf-8")
    assert "esc_attr('nu-tier-grid')" in body


# ---------- spec-driven rendering ----------


def test_block_uses_spec_css_class_and_element(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<section class="hero">' in body


def test_control_uses_spec_css_class_and_element(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<h1 class="hero__title">' in body
    # And not the old generic fallback
    assert 'class="lp-field--heading"' not in body


def test_card_uses_spec_css_class(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify-card" / "block.php").read_text(encoding="utf-8")
    assert '<article class="tarify-card">' in body
    assert '<h3 class="tarify-card__name">' in body


def test_default_fallback_when_no_spec_fields(tmp_path):
    project = tmp_path / "proj"
    _write_spec(project,
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_t, name: title, type: text, label: T, default: Hi }\n"
    )
    r = _run(project)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    # Fallback: <span class="lp-field--title"> (default text element + class).
    assert '<section class="lp-block lp-block--hero">' in body
    assert '<span class="lp-field--title">' in body


def test_cta_text_with_href_from_emits_anchor_and_skips_url(tmp_path):
    project = tmp_path / "proj"
    _write_spec(project,
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_ct, name: cta_text, type: text, label: CT, default: Buy, css_class: 'hero__cta', element: 'a-btn', href_from: cta_url }\n"
        "      - { id: c_cu, name: cta_url,  type: url,  label: CU, default: '#' }\n"
    )
    r = _run(project)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    # exactly one anchor that combines both
    anchors = [ln for ln in body.splitlines() if 'hero__cta' in ln and '<a ' in ln]
    assert len(anchors) == 1
    assert "$attributes['cta_url']" in anchors[0]
    assert "$attributes['cta_text']" in anchors[0]
    # cta_url must NOT emit its own standalone anchor
    assert 'class="lp-field--cta_url"' not in body


def test_block_wrapper_html_overrides(tmp_path):
    project = tmp_path / "proj"
    _write_spec(project,
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    wrapper_open_html: '<article id=\"x\" class=\"hero hero--grid\">'\n"
        "    wrapper_close_html: '</article>'\n"
        "    controls:\n"
        "      - { id: c_t, name: title, type: text, label: T, default: Hi, css_class: 'hero__title', element: h1 }\n"
    )
    r = _run(project)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<article id="x" class="hero hero--grid">' in body
    assert '</article>' in body
    # Generic section wrapper must NOT be emitted in this case
    assert '<section class="lp-block' not in body
