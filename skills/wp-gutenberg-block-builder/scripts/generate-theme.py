#!/usr/bin/env python3
"""Generate WordPress theme scaffold from DESIGN.md + design-stack.yaml.

CLI: python3 generate-theme.py <project-dir>
Stdout: path to created wp-theme/ directory

DESIGN.md (05_ДИЗАЙН-СИСТЕМА/DESIGN.md) is the canonical source of CSS:
  - §2 "Design tokens" — ``:root { ... }`` declarations → ``style.css``
  - §3–§9 "Grid", "Sections", "Per-block layouts", "Forms", "Motion",
    "Accessibility", "Component states" → ``assets/css/main.css``

Sections >=10 (asset checklist / open questions / sources) are skipped.
If DESIGN.md is missing or has no fenced ``css`` blocks, we write tiny
placeholder files and warn on stderr — the deploy stays functional.

The legacy ``_css_variables`` / token-derivation logic was removed in the
stage-08 refactor; tokens.json is no longer consumed by the theme generator.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from tools.logger import error, info, success  # noqa: E402

from design_extractor import DesignExtractError, extract  # noqa: E402

# ── OpenDesign Patterns ────────────────────────────────────────────────────────
# Root of landing-system repo (3 levels up from this script):
#   scripts/ → wp-gutenberg-block-builder/ → skills/ → landing-system/
_SYSTEM_ROOT = Path(__file__).resolve().parents[3]
PATTERNS_DIR = _SYSTEM_ROOT / "block-library" / "_patterns"
STYLES_DIR = _SYSTEM_ROOT / "block-library" / "_styles"

PATTERNS_BY_MODE: dict[str, list[str]] = {
    "none": [],
    "smooth": ["scroll-reveal", "headroom-nav"],
    "cinematic": ["scroll-reveal", "headroom-nav", "ambient-mesh-bg", "paper-texture"],
    "editorial": ["scroll-reveal", "paper-texture", "dot-grid-bg"],
}

# Style mood → recommended patterns mapping
# style_mood in tokens.json OVERRIDES animation_mode pattern selection
STYLE_MOOD_PATTERNS: dict[str, list[str]] = {
    "brutalist": ["scroll-reveal", "bento-grid-hairline", "headroom-nav"],
    "editorial-warm": ["scroll-reveal", "paper-texture", "dot-grid-bg", "text-reveal-mask"],
    "swiss-modernist": ["scroll-reveal", "bento-grid-hairline", "headroom-nav", "text-reveal-mask"],
    "retro-windows": ["scroll-reveal"],
    "coral-soft": ["scroll-reveal", "ambient-mesh-bg", "marquee-fade", "gradient-mesh-animated"],
    "monochrome-precision": ["scroll-reveal", "dot-grid-bg", "conic-ring", "text-reveal-mask"],
}


def _get_animation_mode(tokens_data: dict) -> str:
    """Read animation_mode from tokens.json or default 'smooth'."""
    return str(tokens_data.get("animation_mode", "smooth"))


def _get_style_mood(tokens_data: dict) -> str | None:
    """Read style_mood from tokens.json. Returns None if not set."""
    mood = tokens_data.get("style_mood", None)
    return str(mood) if mood else None


def _apply_style_mood(style_css_path: Path, styles_dir: Path, mood: str) -> None:
    """Append style mood CSS (palette + typography + motion) to style.css.

    Called after patterns are appended so mood variables override pattern defaults.
    """
    if not mood:
        return
    mood_dir = styles_dir / mood
    if not mood_dir.exists():
        info(f"warn: style mood '{mood}' directory not found at {mood_dir}")
        return

    css_chunks = [
        f"\n\n/* ========================================================== */\n"
        f"/* Style Mood: {mood} (from block-library/_styles/{mood}/) */\n"
        f"/* ========================================================== */\n"
    ]
    for fname in ["palette.css", "typography.css", "motion.css"]:
        fpath = mood_dir / fname
        if fpath.exists():
            css_chunks.append(f"\n/* --- {mood}/{fname} --- */\n")
            css_chunks.append(fpath.read_text(encoding="utf-8"))
        else:
            info(f"warn: mood file not found: {fpath}")

    with open(style_css_path, "a", encoding="utf-8") as f:
        f.write("".join(css_chunks))
    info(f"Style mood '{mood}' applied to style.css (palette + typography + motion)")


def _load_tokens_json(project: Path) -> dict:
    """Load tokens.json if it exists — for animation_mode."""
    p = project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    if p.exists():
        import json
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _append_patterns_css(style_css_path: Path, patterns_list: list[str]) -> None:
    """Append OpenDesign pattern CSS snippets to style.css."""
    if not patterns_list:
        return
    css_chunks = [
        "\n\n/* ========================================================== */\n"
        "/* OpenDesign Patterns (auto-included from block-library/_patterns/) */\n"
        "/* Source: github.com/nexu-io/open-design | License: Apache-2.0       */\n"
        "/* ========================================================== */\n"
    ]
    for p in patterns_list:
        snippet = PATTERNS_DIR / p / "snippet.css"
        if snippet.exists():
            css_chunks.append(f"\n/* --- {p} --- */\n")
            css_chunks.append(snippet.read_text(encoding="utf-8"))
        else:
            info(f"warn: pattern snippet not found: {snippet}")
    with open(style_css_path, "a", encoding="utf-8") as f:
        f.write("".join(css_chunks))


def _write_animations_js(assets_js_dir: Path, patterns_list: list[str]) -> None:
    """Create assets/js/animations.js with patterns JS snippets."""
    js_parts = [
        "/* Auto-generated from block-library/_patterns/ */\n"
        "/* Source: github.com/nexu-io/open-design | License: Apache-2.0 */\n\n"
        "/* Respect prefers-reduced-motion */\n"
        "if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {\n"
    ]
    has_js = False
    for p in patterns_list:
        snippet = PATTERNS_DIR / p / "snippet.js"
        if snippet.exists():
            js_parts.append(f"\n  /* --- {p} --- */\n")
            # Indent the snippet body inside the if-block
            content = snippet.read_text(encoding="utf-8")
            indented = "\n".join("  " + line if line.strip() else line for line in content.splitlines())
            js_parts.append(indented + "\n")
            has_js = True
    js_parts.append("}\n")
    (assets_js_dir / "animations.js").write_text("".join(js_parts), encoding="utf-8")
    if has_js:
        info(f"animations.js written with {len([p for p in patterns_list if (PATTERNS_DIR / p / 'snippet.js').exists()])} JS patterns")


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").exists():
            return parent
        # Legacy fallback: accept a project that has tokens.json even without
        # DESIGN.md — we'll then fall back to placeholder CSS and warn.
        if (parent / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").exists():
            return parent
    raise FileNotFoundError(
        "Neither DESIGN.md nor tokens.json found in 05_ДИЗАЙН-СИСТЕМА — run /landing-design first"
    )


def _load_stack(project: Path) -> dict:
    p = project / "06_СТЕК" / "design-stack.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def _write_style_css(theme_dir: Path, project_name: str, style_css: str) -> None:
    header = (
        f"/*\n"
        f"Theme Name: LP {project_name}\n"
        f"Description: Landing page theme generated by landing-system wp-builder\n"
        f"Version: 1.0\n"
        f"Text Domain: lp-{project_name.lower().replace(' ', '-')}\n"
        f"*/\n\n"
    )
    body = style_css.strip() if style_css.strip() else ":root {}\n"
    (theme_dir / "style.css").write_text(header + body + "\n", encoding="utf-8")


def _write_main_css(theme_dir: Path, main_css: str) -> None:
    body = main_css.strip() if main_css.strip() else "/* main.css — DESIGN.md had no §3–§9 styles */\n"
    (theme_dir / "assets" / "css" / "main.css").write_text(body + "\n", encoding="utf-8")


def _write_functions_php(theme_dir: Path, stack: dict) -> None:
    fonts = stack.get("fonts", {})
    cdn = fonts.get("cdn", "bunny")
    families = fonts.get("families", [])

    base_url = "https://fonts.bunny.net/css" if cdn == "bunny" else "https://fonts.googleapis.com/css2"

    # families может быть в двух форматах:
    #   ["Inter", "Roboto"]                                    — список строк (старый/упрощённый)
    #   [{name: "Inter", weights: [400, 700]}, ...]            — список dict'ов (новый)
    def _font_spec(f):
        if isinstance(f, str):
            name = f
            weights = [400, 700]
        else:
            name = f.get('name', f.get('family', 'inter'))
            weights = f.get('weights', [400])
        return f"{name.lower().replace(' ', '-')}:{','.join(str(w) for w in weights)}"

    font_query = "|".join(_font_spec(f) for f in families)
    font_url = f"{base_url}?family={font_query}" if font_query else f"{base_url}?family=inter:400"

    js_libs = stack.get("js_libraries", [])
    js_lines = []
    if "gsap" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('gsap', "
            "'https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js', [], null, true);"
        )
    if "scrolltrigger" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('gsap-st', "
            "'https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js', ['gsap'], null, true);"
        )
    if "lenis" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('lenis', "
            "'https://cdn.jsdelivr.net/npm/@studio-freight/lenis', [], null, true);"
        )
    if "split-type" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('split-type', "
            "'https://cdn.jsdelivr.net/npm/split-type', [], null, true);"
        )
    js_block = ("\n" + "\n".join(js_lines)) if js_lines else ""

    (theme_dir / "functions.php").write_text(
        f"""<?php
/**
 * Theme functions — generated by landing-system wp-builder
 * DO NOT EDIT manually; re-run /landing-build to regenerate scaffold.
 */

function lp_enqueue_assets() {{
    wp_enqueue_style('lp-fonts', '{font_url}', [], null);
    wp_enqueue_style('lp-style', get_template_directory_uri() . '/style.css', [], '1.0');
    wp_enqueue_style('lp-main', get_template_directory_uri() . '/assets/css/main.css', ['lp-style'], '1.0');
    wp_enqueue_script('lp-main', get_template_directory_uri() . '/assets/js/main.js', [], '1.0', true);
    wp_enqueue_script('lp-animations', get_template_directory_uri() . '/assets/js/animations.js', [], '1.0.0', true);{js_block}
}}
add_action('wp_enqueue_scripts', 'lp_enqueue_assets');

function lp_setup() {{
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('editor-styles');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');
}}
add_action('after_setup_theme', 'lp_setup');

// Placeholders for generated code (filled by agents):
// [YM_COUNTER] — Yandex Metrika (analytics-engineer)
// [SEO_META]   — meta tags (seo-optimizer)
// [FLUENT_WEBHOOK] — form webhook (integrations-engineer)
""",
        encoding="utf-8",
    )


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        project = _find_project_root(cwd)
    except FileNotFoundError as e:
        error(str(e))
        return 1

    stack = _load_stack(project)
    project_name = project.name.replace("-", " ").title()

    theme_dir = project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images", "blocks"]:
        (theme_dir / sub).mkdir(parents=True, exist_ok=True)

    md_path = project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    try:
        style_css, main_css = extract(md_path)
    except DesignExtractError as e:
        print(f"warn: {e} — writing placeholder CSS", file=sys.stderr)
        style_css, main_css = "", ""
    if not style_css and not main_css:
        info("DESIGN.md had no CSS — writing placeholder style.css + main.css")

    _write_style_css(theme_dir, project_name, style_css)
    _write_main_css(theme_dir, main_css)
    _write_functions_php(theme_dir, stack)

    # ── OpenDesign Patterns ────────────────────────────────────────────────
    tokens_data = _load_tokens_json(project)
    animation_mode = _get_animation_mode(tokens_data)
    style_mood = _get_style_mood(tokens_data)

    # style_mood overrides animation_mode for pattern selection
    if style_mood and style_mood in STYLE_MOOD_PATTERNS:
        patterns_list = STYLE_MOOD_PATTERNS[style_mood]
        info(f"style_mood: {style_mood!r} → overriding animation_mode patterns → {patterns_list}")
    else:
        patterns_list = PATTERNS_BY_MODE.get(animation_mode, PATTERNS_BY_MODE["smooth"])
        if animation_mode not in PATTERNS_BY_MODE:
            info(f"Unknown animation_mode '{animation_mode}' — falling back to 'smooth'")
            patterns_list = PATTERNS_BY_MODE["smooth"]
        info(f"animation_mode: {animation_mode!r} → patterns: {patterns_list}")

    _append_patterns_css(theme_dir / "style.css", patterns_list)
    _write_animations_js(theme_dir / "assets" / "js", patterns_list)

    # ── Style Mood CSS (palette + typography + motion) ────────────────────
    if style_mood:
        _apply_style_mood(theme_dir / "style.css", STYLES_DIR, style_mood)
    else:
        info("No style_mood set in tokens.json — skipping mood CSS")

    # Minimal WP template: emits enqueued head/footer + post content. Front page
    # is a Gutenberg page set via page_on_front; the_content() renders its blocks.
    (theme_dir / "index.php").write_text(
        "<?php if (!defined('ABSPATH')) { exit; } ?>\n"
        "<!DOCTYPE html>\n"
        "<html <?php language_attributes(); ?>>\n"
        "<head>\n"
        "    <meta charset=\"<?php bloginfo('charset'); ?>\">\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "    <?php wp_head(); ?>\n"
        "</head>\n"
        "<body <?php body_class(); ?>>\n"
        "<?php wp_body_open(); ?>\n"
        "<main id=\"main\" class=\"lp-main\">\n"
        "<?php\n"
        "if (have_posts()) {\n"
        "    while (have_posts()) {\n"
        "        the_post();\n"
        "        the_content();\n"
        "    }\n"
        "}\n"
        "?>\n"
        "</main>\n"
        "<?php wp_footer(); ?>\n"
        "</body>\n"
        "</html>\n",
        encoding="utf-8",
    )

    (theme_dir / "assets" / "js" / "main.js").write_text(
        "// Landing scripts — generated by wp-builder agent\n", encoding="utf-8"
    )

    success(f"Theme scaffold: {theme_dir}")
    print(str(theme_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
