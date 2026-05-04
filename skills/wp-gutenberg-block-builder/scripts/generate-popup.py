#!/usr/bin/env python3
"""Generate popup system (JS + CSS + PHP overlay) and register in functions.php.

CLI: python3 generate-popup.py <project-dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success

_POPUP_JS = """\
// lp-popup — встроенная система попапов
document.addEventListener('DOMContentLoaded', function () {
  function openPopup(id) {
    var el = document.getElementById(id);
    if (el) { el.classList.add('lp-popup--open'); document.body.classList.add('lp-popup-lock'); }
  }
  function closeAll() {
    document.querySelectorAll('.lp-popup').forEach(function (p) { p.classList.remove('lp-popup--open'); });
    document.body.classList.remove('lp-popup-lock');
  }
  document.querySelectorAll('[data-popup]').forEach(function (btn) {
    btn.addEventListener('click', function (e) { e.preventDefault(); openPopup(btn.getAttribute('data-popup')); });
  });
  document.querySelectorAll('.lp-popup__close').forEach(function (el) {
    el.addEventListener('click', closeAll);
  });
  document.querySelectorAll('.lp-popup__overlay').forEach(function (el) {
    el.addEventListener('click', closeAll);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(); });
});
"""

_POPUP_CSS = """\
/* lp-popup system */
body.lp-popup-lock { overflow: hidden; }
.lp-popup { display: none; position: fixed; inset: 0; z-index: 9999; align-items: center; justify-content: center; }
.lp-popup--open { display: flex; }
.lp-popup__overlay { position: absolute; inset: 0; background: rgba(0,0,0,.55); }
.lp-popup__box {
  position: relative; z-index: 1; background: #fff; border-radius: 12px;
  padding: 2.5rem; width: min(560px, 94vw); max-height: 90vh; overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0,0,0,.18);
}
.lp-popup__close {
  position: absolute; top: 1rem; right: 1rem; background: none; border: none;
  font-size: 1.5rem; cursor: pointer; line-height: 1; color: #555;
}
.lp-popup__close:hover { color: #000; }
"""

_POPUP_PHP = """\
<?php
// template-parts/popup-overlay.php
// Использование: <button data-popup="lead-form">Записаться</button>
// Добавь этот файл через get_template_part() в front-page.php после форм
?>
<div class="lp-popup" id="lead-form">
  <div class="lp-popup__overlay"></div>
  <div class="lp-popup__box">
    <button class="lp-popup__close" aria-label="Закрыть">&times;</button>
    <?php
    // Вставь shortcode Fluent Forms:
    // echo do_shortcode('[fluentform id="1"]');
    ?>
  </div>
</div>
"""

_ENQUEUE_ADDON = """\

// Popup system
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('lp-popup', get_template_directory_uri() . '/assets/css/popup.css');
    wp_enqueue_script('lp-popup', get_template_directory_uri() . '/assets/js/popup.js', [], null, true);
});
"""


def _find_functions_php(start: Path) -> Path:
    candidate = start / "08_КОД" / "wp-theme" / "functions.php"
    if candidate.exists():
        return candidate
    for parent in start.parents:
        c = parent / "08_КОД" / "wp-theme" / "functions.php"
        if c.exists():
            return c
    raise FileNotFoundError("functions.php not found — run /landing-build first")


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-popup.py <project-dir>")
        return 1
    try:
        start = Path(argv[1])
        fp = _find_functions_php(start)
        theme = fp.parent

        (theme / "assets" / "js" / "popup.js").write_text(_POPUP_JS, encoding="utf-8")
        (theme / "assets" / "css" / "popup.css").write_text(_POPUP_CSS, encoding="utf-8")
        (theme / "template-parts" / "popup-overlay.php").write_text(_POPUP_PHP, encoding="utf-8")

        current = fp.read_text(encoding="utf-8")
        if "lp-popup" not in current:
            fp.write_text(current + _ENQUEUE_ADDON, encoding="utf-8")

        success(f"Popup system → {theme}")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
