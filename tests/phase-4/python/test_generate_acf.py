"""Tests for wp-gutenberg-block-builder/scripts/generate-acf.py"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "generate-acf.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_acf", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_parse_sections_finds_h2(wp_theme_project):
    mod = _load()
    copy_path = wp_theme_project / "07_КОНТЕНТ" / "final-copy.md"
    sections = mod._parse_sections(copy_path)
    assert len(sections) >= 4
    assert any("HERO" in s.upper() for s in sections)


def test_parse_sections_empty_file(tmp_path):
    mod = _load()
    f = tmp_path / "final-copy.md"
    f.write_text("# No sections here\n", encoding="utf-8")
    assert mod._parse_sections(f) == []


def test_normalize_section_english():
    mod = _load()
    assert mod._normalize_section("hero") == "hero"
    assert mod._normalize_section("HERO") == "hero"
    assert mod._normalize_section("form") == "form"
    assert mod._normalize_section("faq") == "faq"


def test_normalize_section_russian():
    mod = _load()
    assert mod._normalize_section("ОТЗЫВЫ") == "proof"
    assert mod._normalize_section("ФОРМА") == "form"
    assert mod._normalize_section("УСЛУГИ") == "services"
    assert mod._normalize_section("FAQ") == "faq"


def test_build_acf_group_has_required_keys():
    mod = _load()
    group = mod._build_acf_group("hero")
    assert "key" in group
    assert "title" in group
    assert "fields" in group
    assert "location" in group
    assert len(group["fields"]) > 0


def test_build_acf_group_hero_fields():
    mod = _load()
    group = mod._build_acf_group("hero")
    field_names = [f["name"] for f in group["fields"]]
    assert "heading" in field_names
    assert "cta_text" in field_names


def test_build_acf_group_unknown_section_uses_defaults():
    mod = _load()
    group = mod._build_acf_group("unknown_block")
    assert len(group["fields"]) >= 1


def test_main_creates_acf_fields_json(wp_theme_project):
    mod = _load()
    result = mod.main(["prog", str(wp_theme_project)])
    assert result == 0
    out = wp_theme_project / "08_КОД" / "acf-fields.json"
    assert out.exists()


def test_acf_json_has_groups(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    data = json.loads((wp_theme_project / "08_КОД" / "acf-fields.json").read_text(encoding="utf-8"))
    assert "groups" in data
    assert len(data["groups"]) >= 4


def test_acf_json_groups_have_fields(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    data = json.loads((wp_theme_project / "08_КОД" / "acf-fields.json").read_text(encoding="utf-8"))
    for group in data["groups"]:
        assert len(group["fields"]) > 0, f"Group {group['key']} has no fields"


def test_main_missing_final_copy_returns_one(tmp_path):
    (tmp_path / "08_КОД").mkdir()
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
