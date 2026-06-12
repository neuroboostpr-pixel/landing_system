import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-visual-requirements.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("visual-requirements-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_missing_section_fails():
    r = run("visual-requirements-missing-section.md")
    assert r.returncode != 0
    assert "section" in (r.stdout + r.stderr).lower() or "6" in (r.stdout + r.stderr)


def test_too_few_flags_fails():
    r = run("visual-requirements-too-few-flags.md")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "3" in out or "minimum" in out or "least" in out
