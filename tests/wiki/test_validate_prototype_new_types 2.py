import sys
import importlib.util
from pathlib import Path

REPO = Path(__file__).parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_prototype",
    REPO / "skills" / "prototype-import" / "scripts" / "validate-prototype.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
VALID_BLOCK_TYPES = _mod.VALID_BLOCK_TYPES


def test_new_types_present():
    new_types = {
        "header", "menu", "characteristics", "about",
        "problem-solution", "demo", "testimonials", "logos",
        "stats", "case-study", "media-mentions", "guarantees", "comparison",
        "integrations", "banner", "urgency", "lead-form",
        "gallery", "team", "footer", "contacts",
    }
    for t in new_types:
        assert t in VALID_BLOCK_TYPES, f"Type '{t}' missing from VALID_BLOCK_TYPES"

def test_old_types_still_present():
    for t in ["hero", "features", "pricing", "faq", "cta", "trust", "social-proof", "process", "quiz"]:
        assert t in VALID_BLOCK_TYPES
