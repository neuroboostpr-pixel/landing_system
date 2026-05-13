"""Tests for prompt-picker.py Lucide branch (PR-D extension)."""
import sys
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PP = REPO / "skills" / "visual-generation" / "scripts" / "prompt-picker.py"


def _load_pp():
    spec = importlib.util.spec_from_file_location("prompt_picker_prd", PP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_lucide_source_enum_exists():
    mod = _load_pp()
    assert hasattr(mod.PromptSource, "LUCIDE")


def test_pick_icon_returns_lucide_source_when_icons_csv_says_lucide(tmp_path):
    mod = _load_pp()
    icons_csv = tmp_path / "icons.csv"
    icons_csv.write_text(
        "No,Category,Icon Name,Keywords,Library,Import Code,Usage,Best For,Style\n"
        '1,Navigation,menu,hamburger menu navigation toggle bars,Lucide,import { Menu },<Menu />,Mobile drawer,Outline\n'
    )
    result = mod.pick_icon_prompt(
        hint="menu",
        brand_context={"BRAND_ACCENT": "#1e3a8a", "VISUAL_STYLE": "Minimalism"},
        icons_csv=icons_csv,
        opendesign_index=None,
    )
    assert result.source == mod.PromptSource.LUCIDE
    # PickedPrompt should carry the lucide icon name (either as attribute or attribution dict)
    name = getattr(result, "lucide_icon_name", None) or (result.attribution or {}).get("lucide_icon_name")
    assert name == "menu"


def test_pick_icon_falls_through_to_csv_match_when_library_not_lucide(tmp_path):
    mod = _load_pp()
    icons_csv = tmp_path / "icons.csv"
    icons_csv.write_text(
        "No,Category,Icon Name,Keywords,Library,Import Code,Usage,Best For,Style\n"
        '1,Custom,shield,shield protect security,Heroicons,import,...,Trust,Outline\n'
    )
    result = mod.pick_icon_prompt(
        hint="shield",
        brand_context={"BRAND_ACCENT": "#000", "VISUAL_STYLE": "Minimalism"},
        icons_csv=icons_csv,
        opendesign_index=None,
    )
    assert result.source == mod.PromptSource.ICONS_CSV


def test_pick_icon_no_csv_falls_to_generic():
    mod = _load_pp()
    result = mod.pick_icon_prompt(
        hint="xyz-no-match",
        brand_context={"BRAND_ACCENT": "#000", "VISUAL_STYLE": "Minimalism"},
        icons_csv=None,
        opendesign_index=None,
    )
    assert result.source == mod.PromptSource.GENERIC
