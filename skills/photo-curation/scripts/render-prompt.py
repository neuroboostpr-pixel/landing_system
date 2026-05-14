#!/usr/bin/env python3
"""Render codex prompt templates: substitute [PLACEHOLDER] tokens from context.

Used by all 3 PR-B codex wrappers (classify, match, generate-fallback) as the
SINGLE substitution point so prompts stay consistent across the pipeline.
"""
import json
import re
import sys
from pathlib import Path
from typing import Mapping


# Match [UPPER_SNAKE_CASE] — at least 2 chars total, uppercase + digits + underscore.
PLACEHOLDER_RE = re.compile(r"\[([A-Z][A-Z0-9_]{1,})\]")


class MissingPlaceholderError(ValueError):
    """Raised when strict=True and a placeholder has no value in context."""


def render(template: str, context: Mapping[str, str], strict: bool = False) -> str:
    """Substitute every [TOKEN] in template with context[TOKEN].

    Unknown tokens are left intact when strict=False (default).
    """
    def _sub(match: re.Match) -> str:
        key = match.group(1)
        if key in context:
            return str(context[key])
        if strict:
            raise MissingPlaceholderError(f"Placeholder [{key}] has no value in context")
        return match.group(0)

    return PLACEHOLDER_RE.sub(_sub, template)


def load_context(project_dir: Path) -> dict:
    """Read tokens.json + DESIGN.md + market-profile.md + positioning.md into context dict."""
    project_dir = Path(project_dir)
    ctx: dict[str, str] = {}

    tokens_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    if tokens_path.exists():
        tokens = json.loads(tokens_path.read_text())
        ctx["BRAND_PRIMARY"] = tokens.get("colors", {}).get("primary", "")
        ctx["BRAND_ACCENT"] = tokens.get("colors", {}).get("accent", "")
        ctx["VISUAL_STYLE"] = tokens.get("design", {}).get("visual_style", "")

    design_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    if design_path.exists():
        design = design_path.read_text()
        m = re.search(r"\*\*Mood:\*\*\s*(.+)$", design, re.MULTILINE)
        if m:
            ctx["BRAND_MOOD"] = m.group(1).strip()

    profile_path = project_dir / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
    if profile_path.exists():
        profile = profile_path.read_text()
        m = re.search(r"\*\*Niche:\*\*\s*(.+)$", profile, re.MULTILINE)
        if m:
            ctx["NICHE"] = m.group(1).strip()

    pos_path = project_dir / "01a_АНАЛИЗ_НИШИ" / "positioning.md"
    if pos_path.exists():
        pos = pos_path.read_text()
        m = re.search(r"\*\*Audience:\*\*\s*(.+)$", pos, re.MULTILINE)
        if m:
            ctx["AUDIENCE"] = m.group(1).strip()

    ctx.setdefault("LIGHTING", _derive_lighting(ctx.get("BRAND_MOOD", "")))
    ctx.setdefault("COLOR_GRADING", _derive_color_grading(
        ctx.get("BRAND_PRIMARY", ""), ctx.get("BRAND_ACCENT", ""), ctx.get("BRAND_MOOD", "")
    ))
    return ctx


def _derive_lighting(mood: str) -> str:
    mood_l = mood.lower()
    if "premium" in mood_l or "editorial" in mood_l:
        return "Soft studio with controlled rim light"
    if "vibrant" in mood_l or "bold" in mood_l:
        return "Bright daylight, high contrast"
    if "calm" in mood_l or "minimal" in mood_l:
        return "Even diffuse natural light"
    return "Natural daylight, soft shadows"


def _derive_color_grading(primary: str, accent: str, mood: str) -> str:
    parts = []
    if primary:
        parts.append(f"primary accent {primary}")
    if accent:
        parts.append(f"secondary accent {accent}")
    if "premium" in mood.lower():
        parts.append("low saturation, deep blacks")
    return ", ".join(parts) if parts else "neutral grading"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("template", help="Path to template .md file")
    ap.add_argument("project", help="Path to project root")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    template_text = Path(args.template).read_text()
    ctx = load_context(Path(args.project))
    sys.stdout.write(render(template_text, ctx, strict=args.strict))


if __name__ == "__main__":
    main()
