# tests/phase-4/python/test_render_build_preview.py
"""Tests for wp-theme-assembler/scripts/render-build-preview.py"""
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-theme-assembler" / "scripts" / "render-build-preview.py"


def _load():
    spec = importlib.util.spec_from_file_location("render_build_preview", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _setup_project(tmp_path, sample_tokens, sample_stack):
    """Create minimal phase-4 project with theme scaffold."""
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(
        json.dumps(sample_tokens), encoding="utf-8"
    )
    (tmp_path / "06_СТЕК").mkdir()
    (tmp_path / "06_СТЕК" / "design-stack.yaml").write_text(
        yaml.dump(sample_stack, allow_unicode=True), encoding="utf-8"
    )
    theme_dir = tmp_path / "08_КОД" / "wp-theme"
    tp = theme_dir / "template-parts"
    tp.mkdir(parents=True)
    (theme_dir / "style.css").write_text("/* Theme Name: LP Test */\n")
    for section in ["hero", "about", "form"]:
        (tp / f"section-{section}.php").write_text("<?php //placeholder\n")
    acf = tmp_path / "08_КОД" / "acf-fields.json"
    acf.write_text(json.dumps({"groups": [
        {"key": "group_hero", "title": "LP — Hero", "fields": [
            {"key": "f1", "label": "Заголовок", "name": "heading", "type": "text"}
        ]}
    ]}))
    return tmp_path


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    result = mod.main(["prog", str(project)])
    assert result == 0


def test_main_creates_build_preview_html(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    out = project / "08_КОД" / "build-preview.html"
    assert out.exists()


def test_preview_contains_project_name(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert project.name in html


def test_preview_contains_color_tokens(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert "#ff5733" in html


def test_preview_contains_acf_group(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert "LP — Hero" in html


def test_preview_contains_template_parts(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert "section-hero" in html


def test_main_missing_style_css_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
