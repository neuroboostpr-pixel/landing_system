import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-css-patches.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "assets" / "css").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").write_text(
        "/* existing styles */\n.foo { color: red; }\n", encoding="utf-8"
    )
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_appends_display_contents_block(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert "AUTO-GENERATED START: lzb-inner-blocks-patches" in css
    assert ".nu-tier-grid .lazyblock-inner-blocks" in css
    assert "wp-block-lazyblock-tarify-card" in css
    assert "display: contents" in css


def test_idempotent_regeneration(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    a = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    _run(project)
    b = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert a == b


def test_preserves_existing_styles(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert "/* existing styles */" in css
    assert ".foo { color: red; }" in css


def test_no_patches_when_no_section_card_blocks(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "assets" / "css").mkdir(parents=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: H\n"
        "    icon: i\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: heading, type: text, label: L, default: '' }\n",
        encoding="utf-8",
    )
    (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").write_text("/* x */\n", encoding="utf-8")
    _run(project)
    css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    # marker present, no rules inside
    assert "AUTO-GENERATED START: lzb-inner-blocks-patches" in css
    inside = css.split("AUTO-GENERATED START")[1].split("AUTO-GENERATED END")[0]
    assert ".lazyblock-inner-blocks" not in inside
