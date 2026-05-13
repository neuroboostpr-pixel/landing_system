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
    # repeater becomes a foreach
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
    # extend the fixture YAML in-place with an image control
    project = _make_project(tmp_path)
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "wp_get_attachment_image" in body
    assert "['url']" in body


def test_toggle_emits_visible_conditional(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_t, name: featured, type: toggle, label: F, default: false }\n",
        encoding="utf-8",
    )
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    # No dead PHP comment; an actual conditional users can hook CSS to
    assert "if (!empty($attributes['featured']))" in body
    assert "lp-field--featured" in body
    # No nested <?php inside /* */ artefact
    assert "/* toggle" not in body


def test_repeater_url_child_uses_esc_url(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(
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
        "      - { id: c_rich, name: html, type: rich-text, label: H, default: '', child_of: c_lst }\n",
        encoding="utf-8",
    )
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    # url child uses esc_url, not esc_html
    assert "esc_url($row['href']" in body
    # rich-text child uses wp_kses_post
    assert "wp_kses_post($row['html']" in body


def test_section_grid_class_is_escaped(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify" / "block.php").read_text(encoding="utf-8")
    assert "esc_attr('nu-tier-grid')" in body


# ---------- semantic-HTML heuristics ----------

def _write_spec(project: Path, yaml_body: str) -> None:
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True, exist_ok=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(yaml_body, encoding="utf-8")


def test_title_renders_as_h1(tmp_path):
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
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<h1 class="lp-h1">' in body
    assert "$attributes['title']" in body


def test_heading_in_section_card_renders_as_h2(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify" / "block.php").read_text(encoding="utf-8")
    assert '<h2 class="lp-h2">' in body
    assert "$attributes['heading']" in body


def test_heading_in_single_block_renders_as_h1(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<h1 class="lp-h1">' in body


def test_cta_text_url_pair_renders_as_anchor_btn(tmp_path):
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
        "      - { id: c_ct, name: cta_text, type: text, label: CT, default: Buy }\n"
        "      - { id: c_cu, name: cta_url,  type: url,  label: CU, default: '#' }\n"
    )
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    # exactly one anchor with lp-btn class
    assert body.count('<a class="lp-btn') == 1
    # the anchor must contain BOTH the href from cta_url and the echo of cta_text
    anchor_line = [ln for ln in body.splitlines() if 'lp-btn' in ln][0]
    assert "$attributes['cta_url']" in anchor_line
    assert "$attributes['cta_text']" in anchor_line
    # cta_url must NOT emit its own standalone anchor
    assert 'class="lp-field--cta_url"' not in body


def test_eyebrow_renders_as_span(tmp_path):
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
        "      - { id: c_e, name: eyebrow, type: text, label: E, default: New }\n"
    )
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<span class="lp-eyebrow">' in body
    assert "$attributes['eyebrow']" in body


def test_lede_renders_as_p(tmp_path):
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
        "      - { id: c_l, name: lede, type: text, label: L, default: '' }\n"
    )
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert '<p class="lp-lede">' in body


def test_card_name_renders_as_h3(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify-card" / "block.php").read_text(encoding="utf-8")
    assert '<h3 class="lp-h3">' in body
    assert "$attributes['name']" in body


def test_card_popular_toggle_adds_class(tmp_path):
    project = tmp_path / "proj"
    _write_spec(project,
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: pricing\n"
        "    type: section-card\n"
        "    title: Pricing\n"
        "    icon: money-alt\n"
        "    category: lp-blocks\n"
        "    section_grid_class: nu-tier-grid\n"
        "    controls:\n"
        "      - { id: c_h, name: heading, type: text, label: H, default: P }\n"
        "    card:\n"
        "      slug: pricing-tier\n"
        "      title: Tier\n"
        "      controls:\n"
        "        - { id: c_n, name: name, type: text, label: N, default: Basic }\n"
        "        - { id: c_p, name: popular, type: toggle, label: Pop, default: false }\n"
        "      template:\n"
        "        - { name: Basic }\n"
    )
    r = subprocess.run([sys.executable, str(SCRIPT), "--project", str(project)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-pricing-tier" / "block.php").read_text(encoding="utf-8")
    # wrapper conditionally adds lp-card--popular
    assert "lp-card--popular" in body
    assert "$attributes['popular']" in body
    # popular toggle should NOT emit its own div
    assert 'class="lp-field--popular' not in body


def test_section_wrapper_has_nu_section_class(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "nu-section" in body
    assert 'class="lp-block lp-block--hero nu-section nu-section--hero"' in body


def test_card_wrapper_has_nu_card_class(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify-card" / "block.php").read_text(encoding="utf-8")
    assert "nu-card" in body
