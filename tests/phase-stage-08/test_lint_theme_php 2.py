"""C2 (зона C): линтер собранной темы — болячки сборки из спеки §4.2.

Правила (каждое — реальная болячка с реального прогона):
  1. В block.php НЕТ <script> (скрипт в блоке ломает редактор Gutenberg).
  2. Каждая function в block.php обёрнута в function_exists
     (повторное объявление роняет редактор).
  3. functions.php НЕ включает add_theme_support('wp-block-styles')
     (дефолты WP перебивают наши кнопки).
  4. CSS темы содержит правило ширины для верхних обёрток блоков
     (иначе «масштаб поехал») и baseline img-geometry
     (наша CSS-геометрия приоритетнее размеров от WP).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINT = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lint-theme-php.py"

GOOD_BLOCK = """<section class="lp-block lp-block--hero">
<?php if (!function_exists('lp_hero_helper')) { function lp_hero_helper() { return 1; } } ?>
<h1><?php echo esc_html($attributes['heading'] ?? ''); ?></h1>
</section>
"""

GOOD_FUNCTIONS = """<?php
add_theme_support('title-tag');
add_theme_support('align-wide');
"""

GOOD_CSS = """
/* wrapper width: верхние обёртки Lazy Blocks не должны зажимать сетку */
.entry-content > .wp-block, .wp-block-lazyblock { max-width: none; }
/* img geometry: наша геометрия приоритетнее атрибутов WP */
.lp-block img { max-width: 100%; height: auto; }
"""


def _make_theme(tmp_path: Path, block_php=GOOD_BLOCK, functions_php=GOOD_FUNCTIONS,
                css=GOOD_CSS) -> Path:
    theme = tmp_path / "wp-theme"
    blockdir = theme / "blocks" / "lazyblock-hero"
    blockdir.mkdir(parents=True)
    (blockdir / "block.php").write_text(block_php, encoding="utf-8")
    (theme / "functions.php").write_text(functions_php, encoding="utf-8")
    cssdir = theme / "assets" / "css"
    cssdir.mkdir(parents=True)
    (cssdir / "main.css").write_text(css, encoding="utf-8")
    return theme


def _run(theme: Path):
    return subprocess.run([sys.executable, str(LINT), str(theme)],
                          capture_output=True, text=True, encoding="utf-8")


def test_good_theme_passes(tmp_path):
    r = _run(_make_theme(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr


def test_script_in_block_fails(tmp_path):
    bad = GOOD_BLOCK + "<script>alert(1)</script>\n"
    r = _run(_make_theme(tmp_path, block_php=bad))
    assert r.returncode == 1
    assert "script" in r.stdout.lower()


def test_unwrapped_function_fails(tmp_path):
    bad = "<?php function lp_naked() { return 2; } ?>\n" + GOOD_BLOCK
    r = _run(_make_theme(tmp_path, block_php=bad))
    assert r.returncode == 1
    assert "function_exists" in r.stdout


def test_wp_block_styles_support_fails(tmp_path):
    bad = GOOD_FUNCTIONS + "add_theme_support('wp-block-styles');\n"
    r = _run(_make_theme(tmp_path, functions_php=bad))
    assert r.returncode == 1
    assert "wp-block-styles" in r.stdout


def test_missing_wrapper_width_rule_fails(tmp_path):
    r = _run(_make_theme(tmp_path, css="/* пусто */"))
    assert r.returncode == 1
