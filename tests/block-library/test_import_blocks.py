import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

# Прямой импорт через путь (папка с дефисом)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "import_blocks",
    Path(__file__).parents[2] / "skills" / "landing-import-blocks" / "scripts" / "import_blocks.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

next_block_id = mod.next_block_id
format_duplicate_warning = mod.format_duplicate_warning
format_result_summary = mod.format_result_summary


def test_next_block_id_empty():
    assert next_block_id("hero", []) == "hero-001"

def test_next_block_id_existing():
    existing = [{"id": "hero-001"}, {"id": "hero-003"}, {"id": "features-001"}]
    assert next_block_id("hero", existing) == "hero-004"

def test_format_duplicate_warning():
    existing_block = {
        "id": "hero-001",
        "layout_pattern": "split",
        "slots": [{"name": "headline"}, {"name": "image"}, {"name": "cta"}],
        "has_bg_image": False,
    }
    new_block = {
        "type": "hero",
        "layout_pattern": "split",
        "slots": [{"name": "headline"}, {"name": "image"}, {"name": "cta"}, {"name": "badge"}],
        "has_bg_image": False,
        "display_name_ru": "Hero: фото + заголовок + CTA + badge",
    }
    msg = format_duplicate_warning(existing_block, new_block)
    assert "hero-001" in msg
    assert "badge" in msg
    assert "yes/no" in msg.lower() or "да/нет" in msg.lower()

def test_format_result_summary():
    added = [{"id": "hero-004"}, {"id": "features-012"}]
    skipped = [{"id": "hero-001", "reason": "duplicate"}]
    msg = format_result_summary(added, skipped)
    assert "hero-004" in msg
    assert "features-012" in msg
    assert "hero-001" in msg
    assert "gallery.html" in msg
