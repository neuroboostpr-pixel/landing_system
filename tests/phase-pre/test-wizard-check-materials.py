"""Tests for wizard-check-materials.py."""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "wizard-check-materials.py"


def _run(project, step):
    r = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project), "--step", step],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout, r.stderr


def _mkproject(tmp_path):
    p = tmp_path / "proj"
    for sub in ("07_ПРОТОТИП/source", "07c_PHOTOS/inbox/_свалка",
                "07c_PHOTOS/inbox/портреты_и_команда",
                "04_БРЕНД/logos", "03_РЕФЕРЕНСЫ"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    return p


def test_prototype_pass_when_pdf_present(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "07_ПРОТОТИП/source/prototype.pdf").write_bytes(b"%PDF-1.4\n" + b"\x00" * 500)
    rc, out, _ = _run(proj, "prototype")
    assert rc == 0
    data = json.loads(out)
    assert data["status"] == "pass"
    assert any("prototype.pdf" in f for f in data["found"])


def test_prototype_fail_when_missing(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "prototype")
    data = json.loads(out)
    assert data["status"] == "fail"
    assert rc != 0


def test_prototype_accepts_md(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "07_ПРОТОТИП/source/prototype.md").write_text("# Prototype")
    rc, out, _ = _run(proj, "prototype")
    data = json.loads(out)
    assert data["status"] == "pass"


def test_photos_pass_with_jpgs(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "07c_PHOTOS/inbox/_свалка/a.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 500)
    (proj / "07c_PHOTOS/inbox/портреты_и_команда/b.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 500)
    rc, out, _ = _run(proj, "photos")
    data = json.loads(out)
    assert data["status"] == "pass"
    assert "2" in data["summary"] or "photos" in data["summary"].lower()


def test_photos_warn_when_empty(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "photos")
    data = json.loads(out)
    assert data["status"] == "warn"


def test_logos_pass_with_png(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "04_БРЕНД/logos/logo.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 300)
    rc, out, _ = _run(proj, "logos")
    data = json.loads(out)
    assert data["status"] == "pass"


def test_logos_warn_when_empty(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "logos")
    data = json.loads(out)
    assert data["status"] == "warn"


def test_references_pass_with_yaml_urls(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "03_РЕФЕРЕНСЫ/index.yaml").write_text(
        "references:\n  - {url: https://example.com, status: candidate}\n"
    )
    rc, out, _ = _run(proj, "references")
    data = json.loads(out)
    assert data["status"] == "pass"


def test_references_warn_when_empty(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "references")
    data = json.loads(out)
    assert data["status"] == "warn"


def test_invalid_step_fails(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, err = _run(proj, "nonexistent")
    assert rc != 0
