import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-lzb-templates.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_creates_block_php_for_single_block(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    f = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php"
    assert f.exists()
    body = f.read_text(encoding="utf-8")
    assert "<?php" in body
    assert "$attributes['heading']" in body


def test_creates_section_with_inner_blocks_tag(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    section = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify" / "block.php").read_text(encoding="utf-8")
    assert "<InnerBlocks" in section
    assert "lazyblock/tarify-card" in section
    assert 'class="nu-tier-grid"' in section


def test_creates_card_block_php(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    card = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify-card" / "block.php"
    assert card.exists()
    body = card.read_text(encoding="utf-8")
    assert "$attributes['name']" in body
    # repeater becomes a foreach
    assert "foreach" in body
    assert "$attributes['features']" in body


def test_never_overwrites_existing_block_php(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    hero = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php"
    hero.write_text("<?php // hand-edited\n", encoding="utf-8")
    _run(project)
    assert hero.read_text(encoding="utf-8") == "<?php // hand-edited\n"


def test_image_control_uses_attachment_src_helper(tmp_path):
    # extend the fixture YAML in-place with an image control
    project = _make_project(tmp_path)
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "wp_get_attachment_image" in body or "['url']" in body
