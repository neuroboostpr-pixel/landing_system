import importlib.util
import yaml
from pathlib import Path
from PIL import Image

PALETTE_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                  / "skills" / "style-decomposition" / "scripts" / "extract-palette.py")


def _load():
    spec = importlib.util.spec_from_file_location("palette_mod", PALETTE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_solid_image(path: Path, color: tuple, size: tuple = (100, 100)):
    """Create a solid-color PNG image."""
    img = Image.new("RGB", size, color)
    img.save(str(path))
    return path


def test_extract_returns_list_of_colors(tmp_path):
    mod = _load()
    img_path = tmp_path / "red.png"
    _make_solid_image(img_path, (255, 0, 0))
    palette = mod.extract(str(img_path), count=1)
    assert isinstance(palette, list)
    assert len(palette) == 1
    color = palette[0]
    assert "hex" in color
    assert "rgb" in color
    assert "source_pixel" in color


def test_extract_hex_format(tmp_path):
    mod = _load()
    img_path = tmp_path / "blue.png"
    _make_solid_image(img_path, (0, 0, 255))
    palette = mod.extract(str(img_path), count=1)
    assert len(palette) == 1
    hex_val = palette[0]["hex"]
    # hex must be #rrggbb format
    assert hex_val.startswith("#")
    assert len(hex_val) == 7


def test_extract_pixel_source_coordinates(tmp_path):
    mod = _load()
    img_path = tmp_path / "green.png"
    _make_solid_image(img_path, (0, 200, 0))
    palette = mod.extract(str(img_path), count=1)
    assert len(palette) == 1
    source = palette[0]["source_pixel"]
    # source_pixel must be a [x, y] list
    assert source is not None
    assert isinstance(source, list)
    assert len(source) == 2
    x, y = source
    assert 0 <= x < 100
    assert 0 <= y < 100


def test_extract_writes_yaml_with_cli(tmp_path):
    mod = _load()
    img_path = tmp_path / "yellow.png"
    out_path = tmp_path / "palette.yaml"
    _make_solid_image(img_path, (255, 255, 0))
    result = mod.main(["prog", str(img_path), str(out_path), "--count", "1"])
    assert result == 0
    assert out_path.exists()
    data = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    assert "source_image" in data
    assert "palette" in data
    assert len(data["palette"]) == 1


def test_rgb_to_hex_conversion(tmp_path):
    mod = _load()
    assert mod.rgb_to_hex((255, 0, 0)) == "#ff0000"
    assert mod.rgb_to_hex((0, 255, 0)) == "#00ff00"
    assert mod.rgb_to_hex((0, 0, 255)) == "#0000ff"
    assert mod.rgb_to_hex((0, 0, 0)) == "#000000"
    assert mod.rgb_to_hex((255, 255, 255)) == "#ffffff"


def test_rgb_to_hex_clamps_overflow():
    mod = _load()
    # Values > 255 must be clamped
    assert mod.rgb_to_hex((300, 0, 0)) == "#ff0000"
    assert mod.rgb_to_hex((0, -10, 255)) == "#0000ff"
    # Result must always be exactly 7 chars
    assert len(mod.rgb_to_hex((300, 400, 500))) == 7


def test_extract_dedupes_identical_colors(tmp_path):
    mod = _load()
    # A solid image returns only one unique color
    img_path = tmp_path / "solid.png"
    _make_solid_image(img_path, (128, 64, 32))
    # Even if we ask for 5, a solid image has 1 unique color
    palette = mod.extract(str(img_path), count=5)
    hexes = [e["hex"] for e in palette]
    # No duplicates
    assert len(hexes) == len(set(hexes))
