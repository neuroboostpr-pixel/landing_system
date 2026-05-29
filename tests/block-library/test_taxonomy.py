import yaml
from pathlib import Path

TAXONOMY_PATH = Path(__file__).parents[2] / "block-library" / "taxonomy.yaml"

def test_taxonomy_loads():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    assert "categories" in data
    assert "types" in data

def test_taxonomy_has_27_types():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    all_types = [t["id"] for t in data["types"]]
    assert len(all_types) == 27

def test_every_type_has_category():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    category_ids = {c["id"] for c in data["categories"]}
    for t in data["types"]:
        assert t["category"] in category_ids, f"Type {t['id']} has unknown category {t['category']}"

def test_layout_patterns_valid():
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    valid = {"split","centered","grid-2","grid-3","grid-4","stacked","bento","sidebar","cards","timeline","multi-step"}
    for lp in data["layout_patterns"]:
        assert lp in valid
