#!/usr/bin/env python3
"""Generate WordPress theme scaffold from tokens.json + design-stack.yaml.

CLI: python3 generate-theme.py <project-dir>
Stdout: path to created wp-theme/ directory
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, info, success


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").exists():
            return parent
    raise FileNotFoundError("tokens.json not found — run /landing-design first")


def _load_tokens(project: Path) -> dict:
    return json.loads((project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").read_text(encoding="utf-8"))


def _load_stack(project: Path) -> dict:
    p = project / "06_СТЕК" / "design-stack.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


_REF_RE = __import__("re").compile(r"^\{([^}]+)\}$")


def _resolve(value, root_tokens, depth: int = 0):
    """Resolve design-tokens.org reference strings like '{color.accent.mint}'.

    Follows chains recursively up to depth 10; if cycle/too deep, returns literal.
    Non-string values pass through unchanged.
    """
    if depth > 10 or not isinstance(value, str):
        return value
    m = _REF_RE.match(value.strip())
    if not m:
        return value
    path = m.group(1).split(".")
    node = root_tokens
    for part in path:
        if not isinstance(node, dict) or part not in node:
            return value  # unresolvable — emit literal
        node = node[part]
    # Resolved node should be a leaf {"value": ...}
    if isinstance(node, dict) and "value" in node:
        return _resolve(node["value"], root_tokens, depth + 1)
    return _resolve(node, root_tokens, depth + 1) if isinstance(node, str) else value


def _is_leaf(node) -> bool:
    return isinstance(node, dict) and "value" in node and not isinstance(node["value"], dict)


def _emit_nested(lines: list, prefix: str, node: dict, root: dict) -> None:
    """Walk a nested design-tokens.org group, emitting --{prefix}-{key...}: value;."""
    for key, sub in node.items():
        css_key = str(key)
        if _is_leaf(sub):
            val = _resolve(sub["value"], root)
            lines.append(f"  --{prefix}-{css_key}: {val};")
        elif isinstance(sub, dict):
            _emit_nested(lines, f"{prefix}-{css_key}", sub, root)


def _camel_to_kebab(s: str) -> str:
    out = []
    for ch in s:
        if ch.isupper():
            out.append("-")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out)


def _css_variables(tokens: dict) -> str:
    lines = [":root {"]

    # Detect schema: design-tokens.org nested uses singular keys
    has_nested = any(k in tokens for k in ("color", "font", "space")) and not any(
        k in tokens for k in ("colors", "typography", "spacing")
    )

    if has_nested:
        if isinstance(tokens.get("color"), dict):
            _emit_nested(lines, "color", tokens["color"], tokens)
        if isinstance(tokens.get("font"), dict):
            for sub_key, sub_node in tokens["font"].items():
                if not isinstance(sub_node, dict):
                    continue
                # font.family / font.weight / font.size / font.lineHeight / font.letterSpacing
                prefix = f"font-{_camel_to_kebab(sub_key)}"
                _emit_nested(lines, prefix, sub_node, tokens)
        if isinstance(tokens.get("space"), dict):
            _emit_nested(lines, "space", tokens["space"], tokens)
        if isinstance(tokens.get("radius"), dict):
            _emit_nested(lines, "radius", tokens["radius"], tokens)
        if isinstance(tokens.get("shadow"), dict):
            _emit_nested(lines, "shadow", tokens["shadow"], tokens)
        if isinstance(tokens.get("zIndex"), dict):
            _emit_nested(lines, "z", tokens["zIndex"], tokens)
    else:
        for name, props in tokens.get("colors", {}).items():
            hex_val = props["hex"] if isinstance(props, dict) else str(props)
            lines.append(f"  --color-{name}: {hex_val};")
        for role, props in tokens.get("typography", {}).items():
            if not isinstance(props, dict):
                continue
            lines.append(f"  --font-{role}-family: '{props.get('family', 'sans-serif')}', sans-serif;")
            lines.append(f"  --font-{role}-size: {props.get('size', '1rem')};")
            lines.append(f"  --font-{role}-weight: {props.get('weight', '400')};")
            lines.append(f"  --font-{role}-line-height: {props.get('line_height', '1.5')};")
        for key, val in tokens.get("spacing", {}).items():
            lines.append(f"  --space-{key}: {val};")
        for key, val in tokens.get("radius", {}).items():
            lines.append(f"  --radius-{key}: {val};")
        for key, val in tokens.get("shadow", {}).items():
            lines.append(f"  --shadow-{key}: {val};")
    lines.append("}")
    return "\n".join(lines)


_BASELINE_MAIN_CSS = """/* Block styles — generated by wp-builder agent */
:root { color-scheme: light dark; }
body {
    margin: 0;
    font-family: var(--font-family-body, system-ui, sans-serif);
    background: var(--color-bg-base, #fff);
    color: var(--color-text-primary, #111);
    font-size: var(--font-size-body, 1rem);
    line-height: var(--font-line-height-body, 1.3);
}
.lp-main { display: flex; flex-direction: column; }

/* Section defaults */
.lp-block { padding: var(--space-9, 64px) var(--space-5, 24px); }
.lp-block + .lp-block { background: var(--color-bg-section, transparent); }

/* Typography */
h1, .nu-h1 {
    font-family: var(--font-family-display);
    font-size: var(--font-size-h1);
    font-weight: var(--font-weight-bold);
    line-height: var(--font-line-height-display);
    letter-spacing: var(--font-letter-spacing-display);
    margin: 0 0 var(--space-5) 0;
}
h2 {
    font-size: var(--font-size-h2);
    font-weight: var(--font-weight-bold);
    line-height: var(--font-line-height-display);
    margin: 0 0 var(--space-5) 0;
}
h3 {
    font-size: var(--font-size-h3);
    font-weight: var(--font-weight-semibold);
    line-height: var(--font-line-height-h3);
    margin: 0 0 var(--space-4) 0;
}
h4 {
    font-size: var(--font-size-h4);
    font-weight: var(--font-weight-semibold);
    line-height: var(--font-line-height-h4);
    margin: 0 0 var(--space-3) 0;
}
p { margin: 0 0 var(--space-4) 0; }
a { color: var(--color-accent-coral, currentColor); text-decoration: none; }
a:hover { color: var(--color-accent-coral-hover, var(--color-accent-coral)); }

/* Grids commonly used by section-card blocks (nu-* convention) */
.nu-tier-grid,
.nu-module-grid,
.nu-cases-grid,
.nu-reviews-grid,
.nu-audience-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--space-5, 24px);
    margin-top: var(--space-6, 32px);
}
.nu-faq-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
    margin-top: var(--space-6);
}

/* Card defaults — children of section-card grids */
.lp-card {
    background: var(--color-bg-elevated, rgba(255,255,255,0.04));
    border: 1px solid var(--color-border-subtle, rgba(255,255,255,0.08));
    border-radius: var(--radius-lg, 16px);
    padding: var(--space-6, 32px);
    box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,0.32));
}
.lp-card--tarify-card { display: flex; flex-direction: column; }
.lp-card--pricing-tier { display: flex; flex-direction: column; }

/* CTA convention */
.lp-block--final-cta { text-align: center; }
.lp-block--final-cta .lp-field--cta_text,
.lp-block--final-cta .lp-field--cta_label {
    display: inline-block;
    padding: var(--space-4) var(--space-6);
    background: var(--color-accent-coral, #e85e48);
    color: var(--color-accent-coral-text, #fff);
    border-radius: var(--radius-pill, 9999px);
    font-weight: var(--font-weight-semibold, 600);
}

/* Repeater lists */
.lp-rep { list-style: none; padding: 0; margin: var(--space-4) 0; }
.lp-rep li { padding: var(--space-2) 0; }
"""


def _write_style_css(theme_dir: Path, project_name: str, tokens: dict) -> None:
    css_vars = _css_variables(tokens)
    (theme_dir / "style.css").write_text(
        f"""/*
Theme Name: LP {project_name}
Description: Landing page theme generated by landing-system wp-builder
Version: 1.0
Text Domain: lp-{project_name.lower().replace(' ', '-')}
*/

{css_vars}
""",
        encoding="utf-8",
    )


def _write_functions_php(theme_dir: Path, stack: dict) -> None:
    fonts = stack.get("fonts", {})
    cdn = fonts.get("cdn", "bunny")
    families = fonts.get("families", [])

    base_url = "https://fonts.bunny.net/css" if cdn == "bunny" else "https://fonts.googleapis.com/css2"
    font_query = "|".join(
        f"{f.get('name', f.get('family', 'inter')).lower().replace(' ', '-')}:{','.join(str(w) for w in f.get('weights', [400]))}"
        for f in families
    )
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
    wp_enqueue_script('lp-main', get_template_directory_uri() . '/assets/js/main.js', [], '1.0', true);{js_block}
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

    tokens = _load_tokens(project)
    stack = _load_stack(project)
    project_name = project.name.replace("-", " ").title()

    theme_dir = project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images", "blocks"]:
        (theme_dir / sub).mkdir(parents=True, exist_ok=True)

    _write_style_css(theme_dir, project_name, tokens)
    _write_functions_php(theme_dir, stack)

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

    (theme_dir / "assets" / "css" / "main.css").write_text(
        _BASELINE_MAIN_CSS, encoding="utf-8"
    )
    (theme_dir / "assets" / "js" / "main.js").write_text(
        "// Landing scripts — generated by wp-builder agent\n", encoding="utf-8"
    )

    success(f"Theme scaffold: {theme_dir}")
    print(str(theme_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
