"""Tests for skills/photo-curation/scripts/render-prompt.py"""
import pytest

from skills.photo_curation.scripts.render_prompt import render, MissingPlaceholderError


def test_render_substitutes_single_placeholder():
    template = "Brand primary is [BRAND_PRIMARY]."
    context = {"BRAND_PRIMARY": "#c47a3a"}
    assert render(template, context) == "Brand primary is #c47a3a."


def test_render_substitutes_multiple_placeholders():
    template = "[VISUAL_STYLE] | [BRAND_PRIMARY] | [NICHE]"
    context = {"VISUAL_STYLE": "Minimalism", "BRAND_PRIMARY": "#000", "NICHE": "services"}
    assert render(template, context) == "Minimalism | #000 | services"


def test_render_leaves_unknown_placeholders_alone_by_default():
    template = "Known [BRAND_PRIMARY] unknown [MYSTERY]"
    context = {"BRAND_PRIMARY": "#fff"}
    assert render(template, context) == "Known #fff unknown [MYSTERY]"


def test_render_strict_raises_on_unknown_placeholder():
    template = "Known [BRAND_PRIMARY] unknown [MYSTERY]"
    context = {"BRAND_PRIMARY": "#fff"}
    with pytest.raises(MissingPlaceholderError, match="MYSTERY"):
        render(template, context, strict=True)


def test_render_does_not_substitute_inside_brackets_of_unsupported_pattern():
    template = "[link text](http://x) and [BRAND_PRIMARY]"
    context = {"BRAND_PRIMARY": "#abc"}
    assert render(template, context) == "[link text](http://x) and #abc"


def test_render_handles_repeated_placeholder():
    template = "[BRAND_PRIMARY] and again [BRAND_PRIMARY]"
    context = {"BRAND_PRIMARY": "#0f0"}
    assert render(template, context) == "#0f0 and again #0f0"


def test_load_context_merges_tokens_design_niche(tmp_path):
    from skills.photo_curation.scripts.render_prompt import load_context

    project = tmp_path / "proj"
    (project / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (project / "01a_АНАЛИЗ_НИШИ").mkdir(parents=True)
    (project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(
        '{"colors": {"primary": "#c47a3a", "accent": "#1e3a8a"}, "design": {"visual_style": "Minimalism"}}'
    )
    (project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").write_text("# Design\n\n**Mood:** premium and calm\n")
    (project / "01a_АНАЛИЗ_НИШИ" / "market-profile.md").write_text("# Profile\n\n**Niche:** услуги\n")
    (project / "01a_АНАЛИЗ_НИШИ" / "positioning.md").write_text("# Positioning\n\n**Audience:** owners 35-50\n")

    ctx = load_context(project)
    assert ctx["BRAND_PRIMARY"] == "#c47a3a"
    assert ctx["BRAND_ACCENT"] == "#1e3a8a"
    assert ctx["VISUAL_STYLE"] == "Minimalism"
    assert "premium and calm" in ctx["BRAND_MOOD"]
    assert ctx["NICHE"] == "услуги"
    assert "owners 35-50" in ctx["AUDIENCE"]
