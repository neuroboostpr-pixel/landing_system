import importlib.util
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "design-system-generator" / "scripts" / "generate-mockup.py"

def _load():
    spec = importlib.util.spec_from_file_location("generate_mockup", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _make_concept(tmp_path):
    concept = tmp_path / "visual-concept.yaml"
    data = {
        "name": "Доверие через статус",
        "emotional_goal": "Снять барьер недоверия",
        "palette": {"bg": "#0A0A0A", "accent": "#C9A84C", "text": "#FFFFFF", "surface": "#161616"},
        "typography_direction": "Inter 700",
        "mood": ["cinematic"],
        "approved_by_manager": True,
    }
    concept.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return concept

def _make_prototype(tmp_path):
    proto = tmp_path / "prototype.yaml"
    data = {"blocks": [
        {"position": 1, "type": "hero", "content": {
            "headline": "Premium SUVs built for real life in the UAE",
            "subheadline": "LiXiang in stock in Dubai",
            "cta_primary": "Explore cars",
        }},
        {"position": 2, "type": "trust", "content": {
            "headline": "A world of uncompromising comfort",
        }},
    ]}
    proto.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return proto

def test_generate_creates_html(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    result = mod.generate_mockup(str(concept), str(proto), str(out))
    assert result == 0
    assert out.exists()

def test_html_contains_both_variants(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    mod.generate_mockup(str(concept), str(proto), str(out))
    html = out.read_text(encoding="utf-8")
    assert "Вариант A" in html
    assert "Вариант B" in html

def test_html_contains_real_content(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    mod.generate_mockup(str(concept), str(proto), str(out))
    html = out.read_text(encoding="utf-8")
    assert "Premium SUVs built for real life in the UAE" in html
    assert "Explore cars" in html

def test_html_contains_palette_colors(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    mod.generate_mockup(str(concept), str(proto), str(out))
    html = out.read_text(encoding="utf-8")
    assert "#0A0A0A" in html
    assert "#C9A84C" in html

def test_variant_b_differs_from_a(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    palette = yaml.safe_load(concept.read_text(encoding="utf-8"))["palette"]
    alt = mod.build_variant_b(palette)
    assert alt["bg"] != palette["bg"]
