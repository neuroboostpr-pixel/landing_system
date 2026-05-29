import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "cleanup_lib",
    Path(__file__).parents[2] / "skills" / "block-library-management" / "scripts" / "cleanup_lib.py"
)
cleanup_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cleanup_lib)

group_duplicates = cleanup_lib.group_duplicates
renumber = cleanup_lib.renumber
build_new_structure = cleanup_lib.build_new_structure


def test_group_duplicates_finds_groups():
    blocks = [
        {"old_id": "a", "signature": "hero|split|[cta,headline]|bg:false"},
        {"old_id": "b", "signature": "hero|split|[cta,headline]|bg:false"},
        {"old_id": "c", "signature": "faq|stacked|[q]|bg:false"},
    ]
    groups = group_duplicates(blocks)
    assert "hero|split|[cta,headline]|bg:false" in groups
    assert len(groups["hero|split|[cta,headline]|bg:false"]) == 2
    assert "faq|stacked|[q]|bg:false" not in groups

def test_group_duplicates_no_dupes():
    blocks = [
        {"old_id": "a", "signature": "hero|split|[h]|bg:false"},
        {"old_id": "b", "signature": "faq|stacked|[q]|bg:false"},
    ]
    assert group_duplicates(blocks) == {}

def test_renumber_sequential_by_type():
    blocks = [
        {"old_id": "trust-corp-1", "type": "stats"},
        {"old_id": "ru-stats-01", "type": "stats"},
        {"old_id": "hero-x", "type": "hero"},
    ]
    mapping = renumber(blocks)
    assert mapping["ru-stats-01"] == "stats-001"
    assert mapping["trust-corp-1"] == "stats-002"
    assert mapping["hero-x"] == "hero-001"

def test_renumber_ru_priority():
    blocks = [
        {"old_id": "zzz-block", "type": "cta"},
        {"old_id": "ru-cta-09", "type": "cta"},
    ]
    mapping = renumber(blocks)
    assert mapping["ru-cta-09"] == "cta-001"
    assert mapping["zzz-block"] == "cta-002"

def test_build_new_structure_skips_removed():
    blocks = [
        {"old_id": "a", "type": "hero", "category": "Hero", "old_path": "hero/a"},
        {"old_id": "b", "type": "hero", "category": "Hero", "old_path": "hero/b"},
    ]
    keep_list = {"removed": ["b"], "kept": ["a"]}
    actions = build_new_structure(blocks, keep_list)
    assert len(actions) == 1
    assert actions[0]["old_id"] == "a"
    assert actions[0]["new_id"] == "hero-001"
    assert actions[0]["new_path"] == "Hero/hero-001"

def test_build_new_structure_needs_manual_untouched():
    blocks = [
        {"old_id": "a", "type": "hero", "category": "Hero", "old_path": "hero/a", "status": "needs_manual"},
    ]
    keep_list = {"removed": [], "kept": ["a"]}
    actions = build_new_structure(blocks, keep_list)
    assert actions == []
