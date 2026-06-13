"""A1: content_sections_match — prototype.md канон, yaml опционален, схема blocks."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "landing-system" / "scripts" / "validate-content-extraction.py"

CONTENT = "# Content\n\n## 1. Hero\nТекст\n\n## 2. Advantages\nТекст\n"


def _run(content, proto_path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(content), str(proto_path), "--check-sections-match"],
        capture_output=True, text=True, encoding="utf-8")


def test_matches_against_prototype_md(tmp_path):
    """yaml нет вовсе — считаем блоки из prototype.md (## Block)."""
    content = tmp_path / "content.md"; content.write_text(CONTENT, encoding="utf-8")
    proto = tmp_path / "prototype.md"
    proto.write_text("# Project\n\n## Block 1: hero\nA\n\n## Block 2: advantages\nB\n",
                     encoding="utf-8")
    r = _run(content, proto)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "match" in r.stdout


def test_yaml_blocks_schema_counted(tmp_path):
    """yaml со схемой 'blocks' (md-to-yaml) считается корректно."""
    content = tmp_path / "content.md"; content.write_text(CONTENT, encoding="utf-8")
    proto = tmp_path / "prototype.yaml"
    proto.write_text("project: p\nblocks:\n  - {id: hero, type: hero}\n  - {id: adv, type: features}\n",
                     encoding="utf-8")
    r = _run(content, proto)
    assert r.returncode == 0, r.stdout + r.stderr


def test_yaml_missing_falls_back_to_md_sibling(tmp_path):
    """Гейт передаёт prototype.yaml, которого нет — fallback на sibling prototype.md."""
    content = tmp_path / "content.md"; content.write_text(CONTENT, encoding="utf-8")
    (tmp_path / "prototype.md").write_text("## Block 1: hero\nA\n\n## Block 2: adv\nB\n",
                                           encoding="utf-8")
    r = _run(content, tmp_path / "prototype.yaml")  # не существует
    assert r.returncode == 0, r.stdout + r.stderr
    assert "fallback" in r.stdout


def test_mismatch_fails(tmp_path):
    content = tmp_path / "content.md"; content.write_text(CONTENT, encoding="utf-8")
    proto = tmp_path / "prototype.md"
    proto.write_text("## Block 1: hero\nA\n", encoding="utf-8")  # 1 vs 2
    r = _run(content, proto)
    assert r.returncode != 0
