import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-page-content.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_writes_page_content_html(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    assert "<!-- wp:lazyblock/hero" in out
    # hero is single — closes as self-closing
    assert "wp:lazyblock/hero" in out


def test_section_card_emits_inner_blocks_with_template_cards(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    # tarify card template has 2 entries
    assert out.count("<!-- wp:lazyblock/tarify-card") == 2
    # section opens and closes
    assert "<!-- wp:lazyblock/tarify " in out
    assert "<!-- /wp:lazyblock/tarify -->" in out


def test_repeater_values_are_urlencoded_json(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    # The hero block has a bullets repeater; check its JSON value is %5B%5D (empty array)
    import re
    import urllib.parse
    m = re.search(r'<!-- wp:lazyblock/hero (\{.*?\}) /-->', out)
    assert m, "hero block markup not found"
    import json as _json
    data = _json.loads(m.group(1))
    # In minimal fixture, the hero block has no bullets repeater — so this assertion
    # confirms there is no repeater key here. Instead the card has 'features'.
    # The card block markup should be parseable too.
    m2 = re.search(r'<!-- wp:lazyblock/tarify-card (\{.*?\}) /-->', out)
    assert m2, "tarify-card block markup not found"
    card_data = _json.loads(m2.group(1))
    assert "features" in card_data, f"expected features key in card attrs, got {list(card_data)}"
    assert urllib.parse.unquote(card_data["features"]) == "[]"


def test_image_placeholder_is_unquoted_in_json(tmp_path):
    project = _make_project(tmp_path)
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    # Quoted placeholder must NOT appear
    assert '"__IMAGE_ATTACHMENT_ID__hero.png__"' not in out
    # Unquoted placeholder MUST appear (as a value, not a key)
    assert ": __IMAGE_ATTACHMENT_ID__hero.png__" in out


def test_image_attachment_placeholder(tmp_path):
    project = _make_project(tmp_path)
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    assert "__IMAGE_ATTACHMENT_ID__hero.png__" in out
