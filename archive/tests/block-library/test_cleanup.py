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


import importlib.util as _ilu2
_spec2 = _ilu2.spec_from_file_location(
    "cleanup_blocks",
    Path(__file__).parents[2] / "skills" / "block-library-management" / "scripts" / "cleanup_blocks.py"
)
cleanup_blocks = _ilu2.module_from_spec(_spec2)
_spec2.loader.exec_module(cleanup_blocks)


def test_parse_codex_json_valid():
    raw = '{"type":"hero","category":"Hero","layout_pattern":"split","has_bg_image":false,"slots":[{"name":"headline","type":"text"}],"display_name_ru":"Hero: заголовок","clean_html":"<section>x</section>"}'
    result = cleanup_blocks.parse_codex_json(raw)
    assert result["type"] == "hero"
    assert result["display_name_ru"] == "Hero: заголовок"

def test_parse_codex_json_with_fence():
    raw = 'noise\n```json\n{"type":"faq","category":"FAQ","layout_pattern":"stacked","has_bg_image":false,"slots":[],"display_name_ru":"FAQ","clean_html":"<section></section>"}\n```\nmore'
    result = cleanup_blocks.parse_codex_json(raw)
    assert result["type"] == "faq"

def test_parse_codex_json_invalid_returns_none():
    assert cleanup_blocks.parse_codex_json("not json at all") is None

def test_staging_record_shape(tmp_path):
    codex_out = {
        "type": "hero", "category": "Hero", "layout_pattern": "split",
        "has_bg_image": False, "slots": [{"name": "h", "type": "text"}],
        "display_name_ru": "Hero: h", "clean_html": "<section></section>",
    }
    rec = cleanup_blocks.build_staging_record("hero/old-x", "old-x", codex_out)
    assert rec["old_id"] == "old-x"
    assert rec["type"] == "hero"
    assert rec["status"] == "ok"
    assert "signature" in rec
    assert rec["signature"].startswith("hero|split|")


import importlib.util as _ilu3
_spec3 = _ilu3.spec_from_file_location(
    "dedup_report",
    Path(__file__).parents[2] / "skills" / "block-library-management" / "scripts" / "dedup_report.py"
)
dedup_report = _ilu3.module_from_spec(_spec3)
_spec3.loader.exec_module(dedup_report)


def test_render_report_creates_file(tmp_path):
    groups = {
        "hero|split|[cta,headline]|bg:false": [
            {"old_id": "ru-hero-01", "display_name_ru": "Hero: A", "clean_html": "<section>A</section>"},
            {"old_id": "hero-corp-2", "display_name_ru": "Hero: B", "clean_html": "<section>B</section>"},
        ]
    }
    out = tmp_path / "dedup-report.html"
    dedup_report.render_report(groups, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "ru-hero-01" in content
    assert "hero-corp-2" in content
    assert "keep-list" in content.lower()
    assert "checkbox" in content.lower()

def test_render_report_empty_groups(tmp_path):
    out = tmp_path / "dedup-report.html"
    dedup_report.render_report({}, out)
    assert out.exists()
    assert "дубл" in out.read_text(encoding="utf-8").lower()


def test_rebuild_catalog_from_dirs(tmp_path):
    lib = tmp_path / "block-library"
    block = lib / "Hero" / "hero-001"
    (block / "assets").mkdir(parents=True)
    (block / "assets" / "template.html").write_text("<section></section>", encoding="utf-8")
    import yaml as _y
    (block / "meta.yaml").write_text(_y.safe_dump({
        "id": "hero-001", "type": "hero", "category": "Hero",
        "layout_pattern": "split", "display_name_ru": "Hero: x",
        "slots": [], "signature": "hero|split|[]|bg:false",
    }, allow_unicode=True), encoding="utf-8")

    cleanup_blocks.rebuild_catalog(lib)
    catalog = _y.safe_load((lib / "catalog.yaml").read_text(encoding="utf-8"))
    assert catalog["version"] == 3
    assert len(catalog["blocks"]) == 1
    assert catalog["blocks"][0]["id"] == "hero-001"
    assert catalog["blocks"][0]["path"] == "Hero/hero-001/"
