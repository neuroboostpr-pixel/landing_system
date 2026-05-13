import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from block_spec import load, validate, BlockSpecError  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def test_load_minimal_parses_two_blocks():
    spec = load(FIX / "block-spec.minimal.yaml")
    assert spec.version == 1
    assert spec.page.slug == "home"
    assert len(spec.blocks) == 2
    assert spec.blocks[0].slug == "hero"
    assert spec.blocks[0].type == "single"
    assert spec.blocks[1].type == "section-card"
    assert spec.blocks[1].card.slug == "tarify-card"
    assert spec.blocks[1].section_grid_class == "nu-tier-grid"


def test_load_minimal_passes_validation():
    spec = load(FIX / "block-spec.minimal.yaml")
    validate(spec)  # без исключения


def test_nested_repeater_is_rejected():
    spec = load(FIX / "block-spec.invalid.yaml")
    with pytest.raises(BlockSpecError, match="nested repeater"):
        validate(spec)


def test_reserved_attribute_name_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: single\n"
        "    title: X\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: anchor, type: text, label: L, default: '' }\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="reserved"):
        validate(spec)


def test_section_card_missing_card_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: section-card\n"
        "    title: X\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    section_grid_class: grid\n"
        "    controls: []\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="card"):
        validate(spec)


def test_child_of_must_reference_repeater(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: single\n"
        "    title: X\n"
        "    icon: i\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: heading, type: text, label: L, default: '' }\n"
        "      - { id: c2, name: sub, type: text, label: L, default: '', child_of: c1 }\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="child_of.*repeater"):
        validate(spec)


def test_unknown_control_type_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: single\n"
        "    title: X\n"
        "    icon: i\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: heading, type: phantom, label: L }\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="type"):
        validate(spec)


def test_non_list_blocks_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks: not-a-list\n",
        encoding="utf-8",
    )
    with pytest.raises(BlockSpecError, match="blocks.*list"):
        load(bad)


def test_non_dict_block_entry_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - just-a-string\n",
        encoding="utf-8",
    )
    with pytest.raises(BlockSpecError, match="mapping"):
        load(bad)


def test_css_class_and_href_from_roundtrip(tmp_path):
    """stage-08/2026-05-13: spec carries explicit BEM classes + CTA pair refs."""
    f = tmp_path / "spec.yaml"
    f.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    element: section\n"
        "    css_class: 'hero section'\n"
        "    wrapper_open_html: '<section class=\"hero section\">'\n"
        "    wrapper_close_html: '</section>'\n"
        "    controls:\n"
        "      - { id: c_t, name: title, type: text, label: T, default: Hi, css_class: 'hero__title', element: h1 }\n"
        "      - { id: c_cta, name: cta_label, type: text, label: C, default: Go, css_class: 'hero__cta', element: 'a-btn', href_from: cta_url }\n"
        "      - { id: c_url, name: cta_url, type: url, label: U, default: '#' }\n"
        "    card: null\n",
        encoding="utf-8",
    )
    spec = load(f)
    h = spec.blocks[0]
    assert h.css_class == "hero section"
    assert h.element == "section"
    assert h.wrapper_open_html.startswith("<section")
    assert h.wrapper_close_html == "</section>"
    c_title = h.controls[0]
    assert c_title.css_class == "hero__title"
    assert c_title.element == "h1"
    c_cta = h.controls[1]
    assert c_cta.href_from == "cta_url"
    assert c_cta.element == "a-btn"


def test_yaml_parse_error_wrapped(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("version: 1\nblocks: [unclosed\n", encoding="utf-8")
    with pytest.raises(BlockSpecError, match="YAML parse error"):
        load(bad)
