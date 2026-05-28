import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "references-collection" / "scripts" / "extract-palette.py"

def _load():
    spec = importlib.util.spec_from_file_location("extract_palette", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_parse_text_description_extracts_colors():
    mod = _load()
    text = "синий фон #2B72B8, золотой акцент #C9A84C, белый текст #FFFFFF"
    result = mod.parse_text_description(text)
    assert len(result["colors"]) >= 2
    assert any(c["hex"] == "#2B72B8" for c in result["colors"])
    assert any(c["hex"] == "#C9A84C" for c in result["colors"])

def test_parse_text_description_extracts_fonts():
    mod = _load()
    text = "шрифт Archivo Black, Inter для тела"
    result = mod.parse_text_description(text)
    assert len(result["fonts"]) >= 1
    assert any("Archivo" in f for f in result["fonts"])

def test_parse_text_description_no_hex_returns_empty_colors():
    mod = _load()
    text = "просто описание без цветов"
    result = mod.parse_text_description(text)
    assert result["colors"] == []

def test_render_palette_html_contains_hex(tmp_path):
    mod = _load()
    palette = {
        "colors": [
            {"hex": "#2B72B8", "role": "background", "label": "насыщенный синий"},
            {"hex": "#C9A84C", "role": "accent", "label": "золотисто-жёлтый"},
        ],
        "fonts": ["Archivo Black"],
        "mood": "editorial, яркий",
        "source": "OFFtrail",
    }
    out = tmp_path / "refs-palette.html"
    mod.render_palette_html([palette], str(out))
    html = out.read_text(encoding="utf-8")
    assert "#2B72B8" in html
    assert "#C9A84C" in html
    assert "Archivo Black" in html
    assert "насыщенный синий" in html

def test_render_palette_html_creates_file(tmp_path):
    mod = _load()
    out = tmp_path / "refs-palette.html"
    mod.render_palette_html([], str(out))
    assert out.exists()
