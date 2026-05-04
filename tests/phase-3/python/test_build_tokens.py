# tests/phase-3/python/test_build_tokens.py
"""Tests for design-tokens-generation/scripts/build-tokens.py"""
import importlib.util
import json
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = ROOT / "skills" / "design-tokens-generation" / "scripts" / "build-tokens.py"


def _load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_creates_design_md(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    result = mod.main(["prog", str(brand_kit_project)])
    assert result == 0
    assert (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").exists()


def test_design_md_has_yaml_frontmatter(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    content = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").read_text(encoding="utf-8")
    assert content.startswith("---")
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match is not None
    data = yaml.safe_load(match.group(1))
    assert "tokens" in data


def test_design_md_contains_primary_color(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    content = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").read_text(encoding="utf-8")
    assert "#ff5733" in content


def test_design_md_contains_typography(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    content = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").read_text(encoding="utf-8")
    assert "Cabinet Grotesk" in content
    assert "Inter" in content


def test_build_creates_tokens_json(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens_path = brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    assert tokens_path.exists()
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    assert "colors" in tokens
    assert "typography" in tokens
    assert "spacing" in tokens


def test_tokens_json_has_all_sections(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens = json.loads(
        (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").read_text(encoding="utf-8")
    )
    for section in ["colors", "typography", "spacing", "grid", "radius", "shadow", "breakpoints", "motion"]:
        assert section in tokens, f"Missing section: {section}"


def test_tokens_json_colors_have_provenance(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens = json.loads(
        (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").read_text(encoding="utf-8")
    )
    assert "source" in tokens["colors"]["primary"]
    assert tokens["colors"]["primary"]["hex"] == "#ff5733"


def test_tokens_json_is_valid_json(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens_path = brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    assert isinstance(tokens, dict)


def test_build_graceful_with_missing_brand_kit(tmp_path):
    """build-tokens.py must succeed even when brand-kit.md is absent."""
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    mod = _load(BUILD_SCRIPT)
    result = mod.main(["prog", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").exists()
