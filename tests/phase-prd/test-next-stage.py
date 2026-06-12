"""Tests for landing-go-next-stage.py — pick the next actionable stage."""
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "landing-go-next-stage.py"


def _make_state(tmp_path, stages: dict) -> Path:
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / ".landing-state.yaml").write_text(yaml.safe_dump({
        "project": "x",
        "schema_version": 2,
        "stages": stages,
    }, allow_unicode=True))
    return proj


def _run(project) -> str:
    r = subprocess.run(["python3", str(SCRIPT), "--project", str(project)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_fresh_project_next_is_07a_prototype(tmp_path):
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "07a_prototype": {"status": "in_progress"},
        "07c_composed": {"status": "locked"},
    })
    assert _run(proj) == "07a_prototype"


def test_returns_first_non_approved_non_na(tmp_path):
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "07a_prototype": {"status": "approved"},
        "03_references": {"status": "locked"},
        "07c_composed": {"status": "locked"},
    })
    assert _run(proj) == "03_references"


def test_returns_done_when_all_complete(tmp_path):
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "07a_prototype": {"status": "approved"},
        "12_seo": {"status": "approved"},
    })
    assert _run(proj) == "DONE"


def test_handles_failed_status_by_returning_that_stage(tmp_path):
    proj = _make_state(tmp_path, {
        "07a_prototype": {"status": "failed"},
        "07c_composed": {"status": "locked"},
    })
    assert _run(proj) == "07a_prototype"


def test_in_progress_takes_priority_over_locked(tmp_path):
    """Template-shape: 03_references=locked, 07a_prototype=in_progress → next=07a_prototype."""
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "03_references": {"status": "locked"},
        "04_brand": {"status": "locked"},
        "07a_prototype": {"status": "in_progress"},
        "07c_composed": {"status": "locked"},
    })
    assert _run(proj) == "07a_prototype"


def test_failed_takes_priority_over_locked(tmp_path):
    proj = _make_state(tmp_path, {
        "03_references": {"status": "locked"},
        "07a_prototype": {"status": "failed"},
    })
    assert _run(proj) == "07a_prototype"


def test_in_progress_takes_priority_over_failed(tmp_path):
    proj = _make_state(tmp_path, {
        "03_references": {"status": "in_progress"},
        "07a_prototype": {"status": "failed"},
    })
    assert _run(proj) == "03_references"


def test_real_template_returns_07a_prototype(tmp_path):
    """Use the actual template/.landing-state.yaml as input."""
    import shutil
    from pathlib import Path

    REPO = Path(__file__).resolve().parents[2]
    template = REPO / "template" / ".landing-state.yaml"
    proj = tmp_path / "real"
    proj.mkdir()
    shutil.copy(template, proj / ".landing-state.yaml")

    assert _run(proj) == "07a_prototype"
