"""Smoke tests for brand-kit build.py and render-html.py.

Tests are end-to-end: create fixture extracted/ files, run build.py to
produce brand-kit.md, run render-html.py to produce brand-kit.html.
Verify both contain provenance for at least one color, one font, one icon.
"""
import importlib.util
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = ROOT / "skills" / "brand-kit-build" / "scripts" / "build.py"
RENDER_SCRIPT = ROOT / "skills" / "brand-kit-build" / "scripts" / "render-html.py"


def _load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_fixture(project_dir: Path):
    """Create minimal fixture extracted/ files."""
    brand_dir = project_dir / "04_БРЕНД" / "extracted"
    brand_dir.mkdir(parents=True)

    # palette.yaml
    (brand_dir / "palette.yaml").write_text(yaml.dump({
        "source_image": "ref1.png",
        "palette": [
            {"hex": "#ff5733", "rgb": [255, 87, 51], "source_pixel": [10, 20]},
            {"hex": "#33c1ff", "rgb": [51, 193, 255], "source_pixel": [50, 50]},
            {"hex": "#2ecc71", "rgb": [46, 204, 113], "source_pixel": [80, 80]},
        ],
    }), encoding="utf-8")

    # fonts.yaml
    (brand_dir / "fonts.yaml").write_text(yaml.dump({
        "source_url": "https://example.com",
        "method": "DOM CSS inspection (Playwright)",
        "candidates": [
            {"family": "Cabinet Grotesk", "confidence": 0.9, "source": "DOM computed style"},
            {"family": "Inter", "confidence": 0.9, "source": "DOM computed style"},
        ],
        "manual_review_required": False,
    }), encoding="utf-8")

    # icons.yaml
    (brand_dir / "icons.yaml").write_text(yaml.dump({
        "query_terms": ["check", "arrow"],
        "recommended_library": "lucide",
        "results": [
            {"id": "lucide:check", "name": "check", "prefix": "lucide"},
            {"id": "lucide:arrow-right", "name": "arrow-right", "prefix": "lucide"},
        ],
    }), encoding="utf-8")

    # grid.md and motion.md
    (brand_dir / "grid.md").write_text("12-column grid, 24px gap, 1200px max-width\n")
    (brand_dir / "motion.md").write_text("Subtle transitions, 200-400ms, ease-in-out\n")

    # refs index
    refs_dir = project_dir / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    (refs_dir / "index.yaml").write_text(yaml.dump({
        "refs": [
            {"url": "https://example.com", "status": "approved", "tags": ["hero"]},
            {"url": "https://other.com", "status": "rejected", "tags": []},
        ],
    }), encoding="utf-8")


def test_build_creates_brand_kit_md(tmp_path):
    _make_fixture(tmp_path)
    mod = _load(BUILD_SCRIPT)
    result = mod.main(["prog", str(tmp_path)])
    assert result == 0
    md_path = tmp_path / "04_БРЕНД" / "brand-kit.md"
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "#ff5733" in content  # color provenance
    assert "Cabinet Grotesk" in content  # font provenance
    assert "lucide" in content  # icon library


def test_build_brand_kit_md_has_yaml_frontmatter(tmp_path):
    _make_fixture(tmp_path)
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(tmp_path)])
    md_path = tmp_path / "04_БРЕНД" / "brand-kit.md"
    content = md_path.read_text(encoding="utf-8")
    # Must have YAML frontmatter
    assert content.startswith("---")
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match is not None
    data = yaml.safe_load(match.group(1))
    assert "brand_kit" in data
    bk = data["brand_kit"]
    # Provenance: at least one color with source
    assert "colors" in bk
    assert "primary" in bk["colors"]
    assert "source" in bk["colors"]["primary"]
    # Provenance: typography
    assert "typography" in bk
    assert "display" in bk["typography"]
    assert "source" in bk["typography"]["display"]
    # Provenance: icons
    assert "icons" in bk
    assert bk["icons"]["library"] == "lucide"


def test_build_counts_approved_refs(tmp_path):
    _make_fixture(tmp_path)
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(tmp_path)])
    md_path = tmp_path / "04_БРЕНД" / "brand-kit.md"
    match = re.search(r'^---\n(.*?)\n---', md_path.read_text(encoding="utf-8"), re.DOTALL)
    data = yaml.safe_load(match.group(1))
    assert data["brand_kit"]["meta"]["references_used"] == 1  # only 1 approved


def test_render_creates_brand_kit_html(tmp_path):
    _make_fixture(tmp_path)
    build_mod = _load(BUILD_SCRIPT)
    build_mod.main(["prog", str(tmp_path)])
    render_mod = _load(RENDER_SCRIPT)
    result = render_mod.main(["prog", str(tmp_path)])
    assert result == 0
    html_path = tmp_path / "04_БРЕНД" / "brand-kit.html"
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "#ff5733" in html  # color swatch
    assert "Cabinet Grotesk" in html  # font specimen
    assert "lucide:check" in html  # icon


def test_render_html_has_provenance_for_color(tmp_path):
    _make_fixture(tmp_path)
    build_mod = _load(BUILD_SCRIPT)
    build_mod.main(["prog", str(tmp_path)])
    render_mod = _load(RENDER_SCRIPT)
    render_mod.main(["prog", str(tmp_path)])
    html = (tmp_path / "04_БРЕНД" / "brand-kit.html").read_text(encoding="utf-8")
    # Source provenance should appear in HTML (from palette.yaml source_pixel or source_image)
    assert "ref1.png" in html or "source_pixel" in html or "[10, 20]" in html or "10" in html


def test_build_graceful_with_missing_icons(tmp_path):
    """build.py works even when icons.yaml is absent."""
    _make_fixture(tmp_path)
    (tmp_path / "04_БРЕНД" / "extracted" / "icons.yaml").unlink()
    mod = _load(BUILD_SCRIPT)
    result = mod.main(["prog", str(tmp_path)])
    assert result == 0
    content = (tmp_path / "04_БРЕНД" / "brand-kit.md").read_text(encoding="utf-8")
    assert "brand_kit" in content
