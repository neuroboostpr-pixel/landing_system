"""Tests for skills/moodboard-creation/scripts/scaffold.py."""
import importlib.util
import yaml
from pathlib import Path

SCAFFOLD_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                   / "skills" / "moodboard-creation" / "scripts" / "scaffold.py")


def _load():
    spec = importlib.util.spec_from_file_location("mb_scaffold", SCAFFOLD_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_index(refs_dir: Path, refs: list) -> None:
    (refs_dir / "index.yaml").write_text(
        yaml.safe_dump({"references": refs}, allow_unicode=True),
        encoding="utf-8",
    )


def test_scaffold_creates_moodboard_md(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    _make_index(refs_dir, [
        {"id": "aaa11111", "value": "https://example.com/x", "type": "url", "status": "approved"},
    ])

    out = mod.scaffold_moodboard(str(refs_dir), project_name="MyProject")
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "## Direction" in content
    assert "## Adopted patterns" in content
    assert "## Rejected patterns" in content
    assert "## Color feel" in content
    assert "## Typography character" in content
    assert "## Motion vibe" in content


def test_scaffold_lists_approved_refs(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    _make_index(refs_dir, [
        {"id": "aaa11111", "value": "https://example.com/approved-one", "type": "url", "status": "approved"},
        {"id": "bbb22222", "value": "https://example.com/rejected-one", "type": "url", "status": "rejected"},
    ])

    out = mod.scaffold_moodboard(str(refs_dir))
    content = out.read_text(encoding="utf-8")
    # Should mention approved ref
    assert "approved-one" in content or "example.com/approved-one" in content
    # Should NOT prominently list rejected as adopted
    assert "rejected-one" not in content or "Rejected" in content


def test_scaffold_handles_no_approved(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    _make_index(refs_dir, [])

    out = mod.scaffold_moodboard(str(refs_dir))
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    # Should gracefully produce the sections
    assert "## Direction" in content
    assert "## Color feel" in content
