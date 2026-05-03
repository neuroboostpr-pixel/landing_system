"""Tests for .skills/references-collection/scripts/index.py."""
import importlib.util
import yaml
from pathlib import Path

INDEX_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / ".skills" / "references-collection" / "scripts" / "index.py")


def _load():
    spec = importlib.util.spec_from_file_location("idx_mod", INDEX_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_add_creates_index_yaml(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()

    mod.add_ref(str(refs_dir), "https://example.com/ref1", "url", "candidate")
    idx_path = refs_dir / "index.yaml"
    assert idx_path.exists()

    data = yaml.safe_load(idx_path.read_text(encoding="utf-8"))
    assert "references" in data
    assert len(data["references"]) == 1
    assert data["references"][0]["status"] == "candidate"


def test_update_status(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    mod.add_ref(str(refs_dir), "https://example.com/ref1", "url", "candidate")
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    ref_id = data["references"][0]["id"]

    mod.update_status(str(refs_dir), ref_id, "approved")
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    assert data["references"][0]["status"] == "approved"


def test_list_by_status(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    mod.add_ref(str(refs_dir), "ref-a", "url", "approved")
    mod.add_ref(str(refs_dir), "ref-b", "url", "rejected")
    mod.add_ref(str(refs_dir), "ref-c", "url", "approved")

    approved = mod.list_refs(str(refs_dir), status="approved")
    assert len(approved) == 2

    all_refs = mod.list_refs(str(refs_dir))
    assert len(all_refs) == 3


def test_remove_ref(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    mod.add_ref(str(refs_dir), "https://example.com/to-remove", "url", "candidate")
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    ref_id = data["references"][0]["id"]

    mod.remove_ref(str(refs_dir), ref_id)
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    assert len(data["references"]) == 0


def test_show_ref(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    mod.add_ref(str(refs_dir), "https://example.com/show-me", "url", "approved")
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    ref_id = data["references"][0]["id"]

    ref = mod.show_ref(str(refs_dir), ref_id)
    assert ref["value"] == "https://example.com/show-me"
    assert ref["status"] == "approved"
    assert ref["id"] == ref_id
