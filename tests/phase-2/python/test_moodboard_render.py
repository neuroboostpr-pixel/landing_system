"""Tests for .skills/moodboard-creation/scripts/render.py."""
import importlib.util
from pathlib import Path
import yaml

RENDER_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                 / ".skills" / "moodboard-creation" / "scripts" / "render.py")


def _load():
    spec = importlib.util.spec_from_file_location("mb_render", RENDER_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_moodboard_writes_html(tmp_path):
    mod = _load()
    refs = tmp_path / "03_РЕФЕРЕНСЫ"
    refs.mkdir()
    (refs / "index.yaml").write_text(yaml.safe_dump({
        "references": [
            {"id": "abc12345", "value": "https://example.com/a", "type": "url", "status": "approved"},
            {"id": "def67890", "value": "https://example.com/b", "type": "url", "status": "rejected"},
        ]
    }, allow_unicode=True), encoding="utf-8")

    out = mod.render_moodboard(str(refs), project_name="TestProject")
    assert out.exists()
    html = out.read_text()
    assert "TestProject" in html
    assert "https://example.com/a" in html
    assert "approved" in html


def test_render_with_narrative(tmp_path):
    mod = _load()
    refs = tmp_path / "03_РЕФЕРЕНСЫ"
    refs.mkdir()
    (refs / "index.yaml").write_text(yaml.safe_dump({"references": []}), encoding="utf-8")
    narrative = tmp_path / "n.md"
    narrative.write_text("Cinematic feel.\n\nDeep contrast.", encoding="utf-8")

    out = mod.render_moodboard(str(refs), narrative_md=str(narrative))
    html = out.read_text()
    assert "Cinematic feel" in html
    assert "Deep contrast" in html
