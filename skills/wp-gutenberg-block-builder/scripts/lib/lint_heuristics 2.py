"""Heuristic checks comparing DOM matches to spec blocks.

Each check_X(spec_block, soup_match) returns a list of LintIssue.
soup_match is a BeautifulSoup Tag — the matched DOM element.
"""
import re
from dataclasses import dataclass
from typing import Literal, Optional


# Attribute names that signal raw SVG (mirrored from
# fix-page-content-images.py to keep contracts aligned).
SVG_ATTR_NAMES = {"icon_svg", "svg", "background_svg", "decoration_svg", "logo_svg"}


@dataclass
class LintIssue:
    severity: str  # "error" | "warning"
    block_slug: str
    heuristic: str
    message: str
    suggested_fragment: Optional[str] = None


def _bullet_field_count(spec_block) -> int:
    """Count text-controls that look like a spec list field.

    A spec block has at most one repeater for bullets, OR a set of
    sibling text-controls (range/accel/top_speed/fuel/...).
    """
    count = 0
    for c in spec_block.controls + spec_block.card_controls:
        if c.type == "text":
            count += 1
        elif c.type == "repeater":
            # Repeater rows can be many; treat as "unbounded" by returning a
            # high sentinel so the count check passes (delegated to template).
            return 9999
    return count


def check_bullets(spec_block, soup_match):
    li_nodes = soup_match.select('ul[class$="-specs"] > li, ul.specs > li')
    if not li_nodes:
        return []
    field_count = _bullet_field_count(spec_block)
    if field_count >= len(li_nodes):
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="bullets",
        message=(f"{spec_block.slug} composed has {len(li_nodes)} <li> in specs list "
                 f"but only {field_count} matching controls in spec"),
        suggested_fragment=None,
    )]


def check_color_swatches(spec_block, soup_match):
    swatches = soup_match.select('[style*="--c"], .color-swatch')
    if not swatches:
        return []
    all_names = {c.name for c in spec_block.controls + spec_block.card_controls}
    if "colors" in all_names:
        return []
    hex_values = []
    for s in swatches:
        m = re.search(r'--c\s*:\s*(#[0-9a-fA-F]+)', s.get("style", ""))
        if m:
            hex_values.append(m.group(1))
    suggestion = (
        f"# Add to {spec_block.slug} controls:\n"
        f"  - {{ id: c_colors, name: colors, type: text, label: 'Colors (CSV hex)',\n"
        f"      default: '{','.join(hex_values)}' }}"
    ) if hex_values else None
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="color-swatches",
        message=f"{spec_block.slug} composed has {len(swatches)} color-swatch elements but no 'colors' control in spec",
        suggested_fragment=suggestion,
    )]


def check_multi_paragraph(spec_block, soup_match, target_field):
    # SVG textarea fields carry inline markup, not human-readable paragraphs.
    # Skip them so multi-paragraph noise doesn't shadow real inline-svg-icon issues.
    if target_field in SVG_ATTR_NAMES:
        return []
    control = next((c for c in spec_block.controls + spec_block.card_controls
                    if c.name == target_field), None)
    if control is None or control.type != "textarea":
        return []
    # Scope <p> count to the control's target_selector if provided. Avoids
    # false positives when a card contains sibling <p> belonging to other
    # controls (e.g. .model-tagline + .model-description + .model-disclaimer).
    scope = soup_match
    if getattr(control, "target_selector", None):
        scope = soup_match.select_one(control.target_selector)
        if scope is None:
            return []
    p_count = len(scope.find_all("p"))
    if p_count <= 1:
        return []
    default_str = str(control.default_value or "")
    # Count paragraphs in default by splitting on \n\n
    spec_para_count = len([p for p in default_str.split("\n\n") if p.strip()])
    if spec_para_count >= p_count:
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="multi-paragraph",
        message=(f"{spec_block.slug}.{target_field}: composed has {p_count} paragraphs "
                 f"but spec default has only {spec_para_count}"),
        suggested_fragment=None,
    )]


def check_slider_images(spec_block, soup_match, template_index=0):
    imgs = soup_match.select('.slider-track > img, [data-slider] img')
    if not imgs:
        return []
    photo_keys = [f"photo{i}" for i in range(1, len(imgs) + 1)]
    if template_index >= len(spec_block.template):
        filled = 0
    else:
        row = spec_block.template[template_index]
        filled = sum(1 for k in photo_keys if str(row.get(k, "")).strip())
    if filled >= len(imgs):
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="slider-images",
        message=(f"{spec_block.slug}[template_index={template_index}]: composed slider has "
                 f"{len(imgs)} images but template only fills {filled} photo* fields"),
        suggested_fragment=None,
    )]


def check_inline_svg_icon(spec_block, soup_match, template_index=0):
    svg = soup_match.select_one('.feature-icon > svg, .icon > svg')
    if svg is None:
        return []
    svg_control = next((c for c in spec_block.controls + spec_block.card_controls
                        if c.name in SVG_ATTR_NAMES), None)
    if svg_control is None:
        return [LintIssue(
            severity="error",
            block_slug=spec_block.slug,
            heuristic="inline-svg-icon",
            message=f"{spec_block.slug} composed has inline <svg> but no SVG control in spec (expected one of {sorted(SVG_ATTR_NAMES)})",
        )]
    if template_index < len(spec_block.template):
        row = spec_block.template[template_index]
        if str(row.get(svg_control.name, "")).strip():
            return []
    if svg_control.has_default and str(svg_control.default_value).strip():
        return []
    return [LintIssue(
        severity="error",
        block_slug=spec_block.slug,
        heuristic="inline-svg-icon",
        message=(f"{spec_block.slug}.{svg_control.name}: composed has <svg> but spec "
                 f"template[{template_index}] / default is empty"),
    )]
