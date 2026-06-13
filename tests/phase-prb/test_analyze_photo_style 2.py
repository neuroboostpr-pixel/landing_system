"""Tests for skills/client-assets-collection/scripts/analyze-photo-style.py"""
import importlib.util
import tempfile
from pathlib import Path
from PIL import Image

SCRIPT = (
    Path(__file__).parents[2]
    / "skills" / "client-assets-collection" / "scripts" / "analyze-photo-style.py"
)

spec = importlib.util.spec_from_file_location("analyze_photo_style", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _make_image(tmpdir: str, name: str, color: tuple, size=(200, 150)) -> str:
    path = Path(tmpdir) / name
    img = Image.new("RGB", size, color)
    img.save(str(path))
    return str(path)


def test_orientation_landscape():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _make_image(tmpdir, "wide.jpg", (200, 100, 50), size=(300, 150))
        result = mod.analyze_photo(p)
        assert result["orientation"] == "landscape"


def test_orientation_portrait():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _make_image(tmpdir, "tall.jpg", (50, 100, 200), size=(150, 300))
        result = mod.analyze_photo(p)
        assert result["orientation"] == "portrait"


def test_dominant_color_returned():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = _make_image(tmpdir, "red.jpg", (220, 30, 30))
        result = mod.analyze_photo(p)
        assert "dominant_color" in result
        assert result["dominant_color"].startswith("#")


def test_generate_report_creates_markdown():
    with tempfile.TemporaryDirectory() as tmpdir:
        photos = [
            _make_image(tmpdir, "a.jpg", (200, 200, 200)),
            _make_image(tmpdir, "b.jpg", (50, 50, 50)),
        ]
        out = Path(tmpdir) / "style-report.md"
        result = mod.generate_report(photos, str(out))
        assert result == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "a.jpg" in content
        assert "b.jpg" in content


def test_verdict_in_report():
    with tempfile.TemporaryDirectory() as tmpdir:
        photos = [_make_image(tmpdir, "photo.jpg", (128, 128, 128))]
        out = Path(tmpdir) / "style-report.md"
        mod.generate_report(photos, str(out))
        content = out.read_text(encoding="utf-8")
        assert any(v in content for v in ("однородный", "нужна обработка", "не хватает"))
