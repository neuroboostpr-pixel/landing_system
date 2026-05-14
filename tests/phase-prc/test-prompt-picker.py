"""Tests for prompt-picker.py — waterfall: OpenDesign → icons.csv → generic."""
import pytest
from pathlib import Path

from skills.visual_generation.scripts.prompt_picker import (
    pick_icon_prompt,
    pick_infographic_prompt,
    PromptSource,
)


def test_pick_icon_falls_through_to_generic_when_nothing_matches(tmp_path):
    result = pick_icon_prompt(
        hint="completely-unique-xyz-no-match",
        brand_context={"BRAND_ACCENT": "#1e3a8a", "VISUAL_STYLE": "Minimalism"},
        icons_csv=None,
        opendesign_index=None,
    )
    assert result.source == PromptSource.GENERIC
    assert "completely-unique-xyz-no-match" in result.prompt


def test_pick_icon_matches_icons_csv_by_keyword(tmp_path):
    icons_csv = tmp_path / "icons.csv"
    icons_csv.write_text(
        "No,Category,Icon Name,Keywords,Library,Import Code,Usage,Best For,Style\n"
        '1,Navigation,menu,hamburger menu navigation toggle bars,Heroicons,import { MenuIcon },"<MenuIcon />",Mobile drawer,Outline\n'
        '2,Action,shield,shield protect security warranty guarantee,Heroicons,import { ShieldIcon },"<ShieldIcon />",Trust block,Outline\n'
    )
    result = pick_icon_prompt(
        hint="shield",
        brand_context={"BRAND_ACCENT": "#1e3a8a", "VISUAL_STYLE": "Minimalism"},
        icons_csv=icons_csv,
        opendesign_index=None,
    )
    assert result.source == PromptSource.ICONS_CSV
    assert "shield" in result.prompt.lower()


def test_pick_infographic_matches_opendesign_by_category(tmp_path):
    od_index_dir = tmp_path / "image"
    od_index_dir.mkdir()
    sample = od_index_dir / "growth-chart.json"
    sample.write_text('''{
        "id": "growth-chart",
        "category": "Infographic",
        "tags": ["chart", "growth"],
        "model": "gpt-image-2",
        "prompt": "Render a growth chart with smooth line, brand color [BRAND_ACCENT]",
        "source": {"license": "CC-BY-4.0", "author": "test"}
    }''')
    result = pick_infographic_prompt(
        hint="growth",
        chart_type="line",
        brand_context={"BRAND_ACCENT": "#c47a3a", "VISUAL_STYLE": "Editorial"},
        opendesign_index=od_index_dir,
    )
    assert result.source == PromptSource.OPENDESIGN
    assert "growth" in result.prompt.lower() or "chart" in result.prompt.lower()


def test_pick_returns_source_attribution_for_opendesign(tmp_path):
    od_index_dir = tmp_path / "image"
    od_index_dir.mkdir()
    sample = od_index_dir / "bar-chart.json"
    sample.write_text('''{
        "id": "bar-chart",
        "category": "Infographic",
        "tags": ["bar", "stats"],
        "prompt": "Bar chart with 5 bars in [BRAND_ACCENT]",
        "source": {"license": "CC-BY-4.0", "author": "creator-name", "url": "https://example.com"}
    }''')
    result = pick_infographic_prompt(
        hint="stats",
        chart_type="bar",
        brand_context={"BRAND_ACCENT": "#000", "VISUAL_STYLE": "Brutalism"},
        opendesign_index=od_index_dir,
    )
    assert result.attribution is not None
    assert result.attribution["license"] == "CC-BY-4.0"
    assert result.attribution["author"] == "creator-name"
