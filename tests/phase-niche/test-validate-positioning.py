import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-positioning.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_rational_passes():
    r = run("positioning-rational-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_emotional_passes():
    r = run("positioning-emotional-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_trust_passes():
    r = run("positioning-trust-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_no_mode_header_fails():
    r = run("positioning-no-mode-header.md")
    assert r.returncode != 0
    assert "mode" in (r.stdout + r.stderr).lower()


def test_mode_template_mismatch_fails():
    r = run("positioning-mode-template-mismatch.md")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "section" in out or "missing" in out
