# tests/phase-5/python/test_generate_popup.py
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-popup.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_popup", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-popup.py", str(wp_built_project)]) == 0


def test_popup_js_created(wp_built_project):
    mod = _load()
    mod.main(["generate-popup.py", str(wp_built_project)])
    js = wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "popup.js"
    assert js.exists()
    content = js.read_text(encoding="utf-8")
    assert "data-popup" in content
    assert "lp-popup--open" in content


def test_popup_css_created(wp_built_project):
    mod = _load()
    mod.main(["generate-popup.py", str(wp_built_project)])
    css = wp_built_project / "08_КОД" / "wp-theme" / "assets" / "css" / "popup.css"
    assert css.exists()
    assert ".lp-popup" in css.read_text(encoding="utf-8")


def test_popup_php_created(wp_built_project):
    mod = _load()
    mod.main(["generate-popup.py", str(wp_built_project)])
    php = wp_built_project / "08_КОД" / "wp-theme" / "popup.php"
    assert php.exists()
    assert "lp-popup" in php.read_text(encoding="utf-8")


def test_functions_php_has_popup_enqueue(wp_built_project):
    mod = _load()
    mod.main(["generate-popup.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "popup.js" in fp
    assert "popup.css" in fp
    # Popup auto-renders via wp_footer hook (no front-page.php dependency)
    assert "lp_render_popup" in fp
    assert "wp_footer" in fp


def test_popup_enqueue_is_idempotent(wp_built_project):
    mod = _load()
    mod.main(["generate-popup.py", str(wp_built_project)])
    mod.main(["generate-popup.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert fp.count("// Popup system") == 1


def test_missing_functions_php_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-popup.py", str(tmp_path)]) == 1
