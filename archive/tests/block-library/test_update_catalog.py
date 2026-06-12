import yaml, json, sys, subprocess
from pathlib import Path

REPO = Path(__file__).parents[2]

def test_update_catalog_adds_new_fields(tmp_path):
    # Создаём временный каталог
    catalog = tmp_path / "catalog.yaml"
    catalog.write_text(yaml.dump({"version": 2, "blocks": []}), encoding="utf-8")

    added = tmp_path / "added.json"
    added.write_text(json.dumps([{
        "slug": "hero-001",
        "path": "hero/hero-001/",
        "category": "hero",
        "type": "hero",
        "layout_pattern": "split",
        "signature": "hero|split|[cta,headline,image]|bg:false",
        "display_name_ru": "Hero: фото справа + заголовок + CTA",
    }]), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "import-blocks" / "update-catalog.py"),
         "--library", str(tmp_path),
         "--added-from", str(added)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO)
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    data = yaml.safe_load(catalog.read_text(encoding="utf-8"))
    assert len(data["blocks"]) == 1
    block = data["blocks"][0]
    assert block["id"] == "hero-001"
    assert block.get("type") == "hero"
    assert block.get("signature") == "hero|split|[cta,headline,image]|bg:false"
    assert block.get("display_name_ru") == "Hero: фото справа + заголовок + CTA"
