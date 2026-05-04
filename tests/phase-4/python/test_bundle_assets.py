"""Tests for wp-theme-assembler/scripts/bundle-assets.py"""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-theme-assembler" / "scripts" / "bundle-assets.py"


def _load():
    spec = importlib.util.spec_from_file_location("bundle_assets", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_find_project_root_success(wp_theme_project):
    mod = _load()
    root = mod._find_project_root(wp_theme_project)
    assert root == wp_theme_project


def test_find_project_root_fail(tmp_path):
    mod = _load()
    with pytest.raises(FileNotFoundError):
        mod._find_project_root(tmp_path)


def test_note_fonts_creates_stub_files(wp_theme_project, sample_stack):
    mod = _load()
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    noted = mod._note_fonts(wp_theme_project, sample_stack)
    assert "Cabinet Grotesk" in noted
    assert "Inter" in noted
    stub = theme_dir / "assets" / "fonts" / "cabinet-grotesk.txt"
    assert stub.exists()


def test_note_fonts_empty_stack(wp_theme_project):
    mod = _load()
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    noted = mod._note_fonts(wp_theme_project, {})
    assert noted == []


def test_copy_images_copies_files(wp_theme_project):
    src = wp_theme_project / "02_МАТЕРИАЛЫ_КЛИЕНТА" / "photos" / "processed"
    src.mkdir(parents=True, exist_ok=True)
    (src / "hero.jpg").write_bytes(b"\xff\xd8\xff")
    (src / "about.png").write_bytes(b"\x89PNG")

    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    (theme_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)

    mod = _load()
    count = mod._copy_images(wp_theme_project)
    assert count == 2
    assert (theme_dir / "assets" / "images" / "hero.jpg").exists()
    assert (theme_dir / "assets" / "images" / "about.png").exists()


def test_copy_images_missing_dir_returns_zero(wp_theme_project):
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    (theme_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    mod = _load()
    count = mod._copy_images(wp_theme_project)
    assert count == 0


def test_main_returns_zero(wp_theme_project):
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    for p in ["assets/fonts", "assets/icons", "assets/images"]:
        (theme_dir / p).mkdir(parents=True, exist_ok=True)

    mod = _load()
    result = mod.main(["prog", str(wp_theme_project)])
    assert result == 0


def test_main_outputs_json(wp_theme_project, capsys):
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    for p in ["assets/fonts", "assets/icons", "assets/images"]:
        (theme_dir / p).mkdir(parents=True, exist_ok=True)

    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert "fonts" in data
    assert "icons" in data
    assert "images_copied" in data


def test_main_missing_stack_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
