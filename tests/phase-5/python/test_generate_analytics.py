# tests/phase-5/python/test_generate_analytics.py
import importlib.util
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-analytics.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_analytics", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-analytics.py", str(wp_built_project)]) == 0


def test_ym_placeholder_replaced(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "98765432" in fp
    assert "// [YM_COUNTER]" not in fp


def test_ym_has_reachgoal(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "reachGoal" in fp


def test_gtm_head_injected(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "GTM-ABCDEFG" in fp
    assert "googletagmanager" in fp


def test_gtm_noscript_in_body(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "wp_body_open" in fp
    assert "noscript" in fp


def test_analytics_is_idempotent(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    count_after_first = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8").count("googletagmanager.com")
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert fp.count("googletagmanager.com") == count_after_first


def test_missing_functions_php_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-analytics.py", str(tmp_path)]) == 1


def test_parse_ym_from_brief():
    mod = _load()
    brief = "## Аналитика\n- YM счётчик: 12345678\n- GTM контейнер: GTM-XYZ123\n"
    ym, gtm = mod._parse_analytics(brief)
    assert ym == "12345678"
    assert gtm == "GTM-XYZ123"
