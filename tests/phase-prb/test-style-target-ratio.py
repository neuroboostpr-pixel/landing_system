"""Tests for style.py --target-ratio extension (PR-B)."""
import subprocess
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
STYLE = REPO / "skills" / "photo-styling" / "scripts" / "style.py"


def test_target_ratio_produces_correct_aspect(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(src)
    dst = tmp_path / "out.jpg"
    result = subprocess.run(
        ["python3", str(STYLE), str(src), str(dst),
         "--mode", "target-ratio", "--ratio", "16:9", "--max-dim", "1920"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    with Image.open(dst) as img:
        w, h = img.size
    assert abs((w / h) - (16 / 9)) < 0.01, f"got {w}x{h} = {w/h:.3f}, expected 16:9"
    assert max(w, h) <= 1920


def test_target_ratio_for_mobile_smaller_dimension(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (3000, 4000), (0, 255, 0)).save(src)
    dst = tmp_path / "mobile.jpg"
    result = subprocess.run(
        ["python3", str(STYLE), str(src), str(dst),
         "--mode", "target-ratio", "--ratio", "9:16", "--max-dim", "1080"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    with Image.open(dst) as img:
        w, h = img.size
    assert abs((w / h) - (9 / 16)) < 0.01
    assert max(w, h) <= 1080


def test_target_ratio_with_already_correct_ratio_just_resizes(tmp_path):
    src = tmp_path / "src.jpg"
    Image.new("RGB", (1920, 1080), (100, 100, 100)).save(src)
    dst = tmp_path / "out.jpg"
    result = subprocess.run(
        ["python3", str(STYLE), str(src), str(dst),
         "--mode", "target-ratio", "--ratio", "16:9", "--max-dim", "960"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    with Image.open(dst) as img:
        w, h = img.size
    assert abs((w / h) - (16 / 9)) < 0.01
    assert max(w, h) <= 960


def test_existing_resize_mode_still_works(tmp_path):
    """Regression test: don't break existing resize mode."""
    src = tmp_path / "src.jpg"
    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(src)
    dst = tmp_path / "out.jpg"
    result = subprocess.run(
        ["python3", str(STYLE), str(src), str(dst),
         "--mode", "resize", "--max-dim", "1600"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    with Image.open(dst) as img:
        w, h = img.size
    assert max(w, h) == 1600
