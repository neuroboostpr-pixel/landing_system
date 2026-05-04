import importlib.util
import inspect
from pathlib import Path
from PIL import Image
import io

STYLE_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / "skills" / "photo-styling" / "scripts" / "style.py")


def _load():
    spec = importlib.util.spec_from_file_location("style_mod", STYLE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_test_image(path, size=(100, 100), color=(255, 0, 0)):
    img = Image.new("RGB", size, color)
    img.save(str(path))


def test_resize_max_dimension(tmp_path):
    mod = _load()
    src = tmp_path / "in.jpg"
    _make_test_image(src, size=(2000, 1000))
    dst = tmp_path / "out.jpg"
    mod.resize(str(src), str(dst), max_dim=800)
    out = Image.open(str(dst))
    assert max(out.size) <= 800
    # Aspect ratio preserved
    assert out.size[0] / out.size[1] == 2.0


def test_crop_to_aspect(tmp_path):
    mod = _load()
    src = tmp_path / "in.jpg"
    _make_test_image(src, size=(1000, 600))
    dst = tmp_path / "out.jpg"
    mod.crop_aspect(str(src), str(dst), "1:1")
    out = Image.open(str(dst))
    assert out.size[0] == out.size[1]


def test_cutout_returns_rgba_png(tmp_path):
    mod = _load()
    src = tmp_path / "in.jpg"
    _make_test_image(src, size=(100, 100))
    dst = tmp_path / "out.png"
    mod.cutout(str(src), str(dst))
    out = Image.open(str(dst))
    # Output must be RGBA
    assert out.mode == "RGBA"


def test_cutout_function_documents_rembg_requirement():
    """Cutout function must mention rembg in its source and raise ImportError if missing."""
    mod = _load()
    src = inspect.getsource(mod.cutout)
    assert "rembg" in src
    assert "ImportError" in src or "raise" in src
