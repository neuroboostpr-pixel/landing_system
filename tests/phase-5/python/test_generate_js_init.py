# tests/phase-5/python/test_generate_js_init.py
import importlib.util
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-js-init.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_js_init", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-js-init.py", str(wp_built_project)]) == 0


def test_main_js_created(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    js = wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "main.js"
    assert js.exists()


def test_sliders_js_created_when_swiper_enabled(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    assert (wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "sliders.js").exists()


def test_counters_js_created_when_countup_enabled(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    assert (wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "counters.js").exists()


def test_smooth_scroll_created_when_lenis(wp_built_project_cinematic):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project_cinematic)])
    js = wp_built_project_cinematic / "08_КОД" / "wp-theme" / "assets" / "js" / "smooth-scroll.js"
    assert js.exists()
    assert "Lenis" in js.read_text(encoding="utf-8")


def test_animations_js_created_when_gsap(wp_built_project_cinematic):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project_cinematic)])
    js = wp_built_project_cinematic / "08_КОД" / "wp-theme" / "assets" / "js" / "animations.js"
    assert js.exists()
    assert "ScrollTrigger" in js.read_text(encoding="utf-8")


def test_functions_php_has_swiper_enqueue(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "swiper" in fp.lower()


def test_js_enqueue_is_idempotent(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    mod.main(["generate-js-init.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert fp.count("generate-js-init") == 1


def test_no_optional_files_when_no_libs(tmp_path):
    # Project with design-stack.yaml but all libraries disabled
    stack_dir = tmp_path / "06_СТЕК"
    stack_dir.mkdir()
    (stack_dir / "design-stack.yaml").write_text(
        "js_libraries: []\nui_libraries:\n  swiper: false\n  fancybox: false\n  countup: false\n",
        encoding="utf-8"
    )
    theme = tmp_path / "08_КОД" / "wp-theme"
    theme.mkdir(parents=True)
    (theme / "functions.php").write_text("<?php\n", encoding="utf-8")

    mod = _load()
    assert mod.main(["generate-js-init.py", str(tmp_path)]) == 0
    # main.js always created
    assert (theme / "assets" / "js" / "main.js").exists()
    # no optional files
    assert not (theme / "assets" / "js" / "sliders.js").exists()
    assert not (theme / "assets" / "js" / "counters.js").exists()
    assert not (theme / "assets" / "js" / "smooth-scroll.js").exists()
    assert not (theme / "assets" / "js" / "animations.js").exists()
    # functions.php not touched (no libs to enqueue)
    assert "generate-js-init" not in (theme / "functions.php").read_text(encoding="utf-8")


def test_missing_stack_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-js-init.py", str(tmp_path)]) == 1
