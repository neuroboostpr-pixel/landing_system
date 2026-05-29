import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from skills.landing_import_blocks.scripts.check_duplicates import (
    compute_signature,
    load_existing_signatures,
    find_duplicate,
)

def test_compute_signature_sorts_slots():
    block = {
        "type": "hero",
        "layout_pattern": "split",
        "slots": [
            {"name": "image", "type": "image"},
            {"name": "headline", "type": "text"},
            {"name": "cta", "type": "cta"},
        ],
        "has_bg_image": False,
    }
    sig = compute_signature(block)
    assert sig == "hero|split|[cta,headline,image]|bg:false"

def test_compute_signature_with_bg():
    block = {
        "type": "hero",
        "layout_pattern": "centered",
        "slots": [{"name": "headline", "type": "text"}],
        "has_bg_image": True,
    }
    sig = compute_signature(block)
    assert sig == "hero|centered|[headline]|bg:true"

def test_load_existing_signatures(tmp_path):
    import yaml
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({
        "blocks": [
            {"id": "hero-001", "signature": "hero|split|[cta,headline,image]|bg:false"},
            {"id": "features-001", "signature": "features|grid-3|[icon,text,title]|bg:false"},
        ]
    }), encoding="utf-8")
    sigs = load_existing_signatures(catalog)
    assert "hero|split|[cta,headline,image]|bg:false" in sigs
    assert sigs["hero|split|[cta,headline,image]|bg:false"] == "hero-001"

def test_find_duplicate_found(tmp_path):
    import yaml
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({
        "blocks": [{"id": "hero-001", "signature": "hero|split|[cta,headline]|bg:false"}]
    }), encoding="utf-8")
    block = {"type": "hero", "layout_pattern": "split",
             "slots": [{"name": "cta"}, {"name": "headline"}], "has_bg_image": False}
    result = find_duplicate(block, catalog)
    assert result == "hero-001"

def test_find_duplicate_not_found(tmp_path):
    import yaml
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({"blocks": []}), encoding="utf-8")
    block = {"type": "hero", "layout_pattern": "split",
             "slots": [{"name": "headline"}], "has_bg_image": False}
    assert find_duplicate(block, catalog) is None
