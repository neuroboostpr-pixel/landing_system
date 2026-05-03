import importlib.util
import yaml
from pathlib import Path
from unittest.mock import patch

IDENT_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / ".skills" / "style-decomposition" / "scripts" / "identify-fonts.py")


def _load():
    spec = importlib.util.spec_from_file_location("idfont_mod", IDENT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_identify_from_url_uses_get_page_fonts(tmp_path):
    mod = _load()
    fake_fonts = [
        '"Cabinet Grotesk", serif',
        "Inter, system-ui, sans-serif",
        "monospace",
    ]
    out = tmp_path / "fonts.yaml"
    with patch.object(mod, "get_page_fonts", return_value=fake_fonts):
        mod.identify_url("https://example.com", str(out))

    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    families = [c["family"] for c in data["candidates"]]
    # Primary family extracted from the stack — quotes stripped
    assert "Cabinet Grotesk" in families
    assert "Inter" in families


def test_parse_font_stack_extracts_primary():
    mod = _load()
    assert mod.parse_font_stack('"Cabinet Grotesk", serif') == "Cabinet Grotesk"
    assert mod.parse_font_stack("Inter, system-ui, sans-serif") == "Inter"
    assert mod.parse_font_stack("monospace") == "monospace"


def test_generic_families_are_filtered(tmp_path):
    mod = _load()
    fake_fonts = [
        "serif",
        "sans-serif",
        "monospace",
        "system-ui",
    ]
    out = tmp_path / "fonts.yaml"
    with patch.object(mod, "get_page_fonts", return_value=fake_fonts):
        mod.identify_url("https://example.com", str(out))

    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    # All are generic — candidates list must be empty
    assert data["candidates"] == []
    assert data["manual_review_required"] is True
