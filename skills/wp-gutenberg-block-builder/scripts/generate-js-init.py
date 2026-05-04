#!/usr/bin/env python3
"""Generate JS initialization files and register CDN libraries in functions.php.

CLI: python3 generate-js-init.py <project-dir>
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn

_CDN = {
    "swiper": {
        "css": "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css",
        "js": "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js",
        "handle": "swiper",
    },
    "fancybox": {
        "css": "https://cdn.jsdelivr.net/npm/@fancyapps/ui@5/dist/fancybox/fancybox.css",
        "js": "https://cdn.jsdelivr.net/npm/@fancyapps/ui@5/dist/fancybox/fancybox.umd.js",
        "handle": "fancybox",
    },
    "countup": {
        "js": "https://cdn.jsdelivr.net/npm/countup.js@2/dist/countUp.umd.js",
        "handle": "countup",
    },
    "typed": {
        "js": "https://cdn.jsdelivr.net/npm/typed.js@2/dist/typed.umd.js",
        "handle": "typed",
    },
    "gsap": {
        "js": "https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js",
        "handle": "gsap",
    },
    "scrolltrigger": {
        "js": "https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js",
        "handle": "gsap-scrolltrigger",
        "deps": ["gsap"],
    },
    "lenis": {
        "js": "https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js",
        "handle": "lenis",
    },
    "split-type": {
        "js": "https://cdn.jsdelivr.net/npm/split-type@0/umd/index.min.js",
        "handle": "split-type",
    },
}

_MAIN_JS = """\
// main.js — точка входа
// Инициализация всех библиотек происходит в отдельных файлах
document.addEventListener('DOMContentLoaded', function () {
  console.log('[LP] scripts ready');
});
"""

_SMOOTH_SCROLL_JS = """\
// smooth-scroll.js — Lenis smooth scroll
var lenis = new Lenis({ autoRaf: true, lerp: 0.08, smoothWheel: true });
"""

_ANIMATIONS_JS = """\
// animations.js — GSAP + ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

// Fade-in для элементов с data-animate
document.querySelectorAll('[data-animate]').forEach(function (el) {
  gsap.from(el, {
    scrollTrigger: { trigger: el, start: 'top 82%', once: true },
    opacity: 0,
    y: 40,
    duration: 0.8,
    ease: 'power2.out',
  });
});
"""

_SLIDERS_JS = """\
// sliders.js — Swiper sliders
document.querySelectorAll('.lp-slider').forEach(function (el) {
  new Swiper(el, {
    loop: true,
    slidesPerView: 1,
    spaceBetween: 24,
    pagination: { el: el.querySelector('.swiper-pagination'), clickable: true },
    navigation: {
      nextEl: el.querySelector('.swiper-button-next'),
      prevEl: el.querySelector('.swiper-button-prev'),
    },
    breakpoints: { 768: { slidesPerView: 2 }, 1200: { slidesPerView: 3 } },
  });
});
"""

_COUNTERS_JS = """\
// counters.js — CountUp animated numbers
document.querySelectorAll('[data-countup]').forEach(function (el) {
  var target = parseFloat(el.getAttribute('data-countup')) || 0;
  var decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals')) : 0;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        new countUp.CountUp(el, target, { decimalPlaces: decimals, duration: 2 }).start();
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.3 });
  observer.observe(el);
});
"""


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "06_СТЕК" / "design-stack.yaml").exists():
            return parent
    raise FileNotFoundError("design-stack.yaml not found — run /landing-stack first")


def _load_stack(project: Path) -> dict:
    return yaml.safe_load(
        (project / "06_СТЕК" / "design-stack.yaml").read_text(encoding="utf-8")
    ) or {}


def _enqueue_block(libs: list) -> str:
    lines = ["\n// JS/CSS библиотеки (generate-js-init.py)\nadd_action('wp_enqueue_scripts', function () {"]
    for lib in libs:
        cfg = _CDN.get(lib, {})
        handle = cfg.get("handle", lib)
        deps = cfg.get("deps", [])
        deps_php = "array(" + ", ".join(f"'{d}'" for d in deps) + ")" if deps else "array()"
        if "css" in cfg:
            lines.append(f"    wp_enqueue_style('{handle}', '{cfg['css']}');")
        if "js" in cfg:
            lines.append(f"    wp_enqueue_script('{handle}', '{cfg['js']}', {deps_php}, null, true);")
    lines.append("});")
    return "\n".join(lines) + "\n"


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-js-init.py <project-dir>")
        return 1
    try:
        project = _find_project_root(Path(argv[1]))
        stack = _load_stack(project)
        js_libs = [l.lower() for l in (stack.get("js_libraries") or [])]
        ui_libs_cfg = stack.get("ui_libraries") or {}
        ui_libs = [k for k, v in ui_libs_cfg.items() if v]
        all_libs = js_libs + [l for l in ui_libs if l not in js_libs]

        theme_js = project / "08_КОД" / "wp-theme" / "assets" / "js"
        theme_js.mkdir(parents=True, exist_ok=True)

        (theme_js / "main.js").write_text(_MAIN_JS, encoding="utf-8")

        if "lenis" in all_libs:
            (theme_js / "smooth-scroll.js").write_text(_SMOOTH_SCROLL_JS, encoding="utf-8")
        if "gsap" in all_libs or "scrolltrigger" in all_libs:
            (theme_js / "animations.js").write_text(_ANIMATIONS_JS, encoding="utf-8")
        if "swiper" in all_libs:
            (theme_js / "sliders.js").write_text(_SLIDERS_JS, encoding="utf-8")
        if "countup" in all_libs:
            (theme_js / "counters.js").write_text(_COUNTERS_JS, encoding="utf-8")

        fp = project / "08_КОД" / "wp-theme" / "functions.php"
        if fp.exists() and all_libs:
            current = fp.read_text(encoding="utf-8")
            block = _enqueue_block(all_libs)
            if "generate-js-init" not in current:
                fp.write_text(current + block, encoding="utf-8")

        success(f"JS init files → {theme_js} ({len(all_libs)} libs)")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
