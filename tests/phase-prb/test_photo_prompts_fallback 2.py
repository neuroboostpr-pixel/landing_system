"""Tests for skills/photo-styling/scripts/generate-photo-prompts.py"""
import importlib.util
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "skills" / "photo-styling" / "scripts" / "generate-photo-prompts.py"

spec = importlib.util.spec_from_file_location("gen_prompts", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _write_brand_kit(tmpdir: str, palette: str = "#1A1A1A, #C9A84C", tone: str = "premium, dark") -> str:
    path = Path(tmpdir) / "brand-kit.md"
    path.write_text(
        f"## Colors\n{palette}\n\n## Tone\n{tone}\n",
        encoding="utf-8",
    )
    return str(path)


def test_generates_markdown_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        brand = _write_brand_kit(tmpdir)
        photos = ["portrait.jpg", "team.jpg"]
        out = Path(tmpdir) / "photo-prompts.md"
        result = mod.generate_prompts(photos, brand, str(out))
        assert result == 0
        assert out.exists()


def test_one_prompt_per_photo():
    with tempfile.TemporaryDirectory() as tmpdir:
        brand = _write_brand_kit(tmpdir)
        photos = ["hero.jpg", "about.jpg", "process.jpg"]
        out = Path(tmpdir) / "photo-prompts.md"
        mod.generate_prompts(photos, brand, str(out))
        content = out.read_text(encoding="utf-8")
        for name in photos:
            assert name in content, f"{name} not in output"


def test_prompt_contains_brand_color():
    with tempfile.TemporaryDirectory() as tmpdir:
        brand = _write_brand_kit(tmpdir, palette="#FF4400")
        photos = ["product.jpg"]
        out = Path(tmpdir) / "photo-prompts.md"
        mod.generate_prompts(photos, brand, str(out))
        content = out.read_text(encoding="utf-8")
        assert "#FF4400" in content


def test_empty_photo_list_returns_zero():
    with tempfile.TemporaryDirectory() as tmpdir:
        brand = _write_brand_kit(tmpdir)
        out = Path(tmpdir) / "photo-prompts.md"
        result = mod.generate_prompts([], brand, str(out))
        assert result == 0
        assert out.exists()


def test_missing_brand_kit_uses_defaults():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "photo-prompts.md"
        result = mod.generate_prompts(["photo.jpg"], "/nonexistent/brand-kit.md", str(out))
        assert result == 0
        content = out.read_text(encoding="utf-8")
        assert "photo.jpg" in content
