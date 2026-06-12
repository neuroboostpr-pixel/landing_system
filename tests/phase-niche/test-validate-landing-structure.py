import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-landing-structure.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("landing-structure-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_missing_hero_fails():
    r = run("landing-structure-missing-hero.md")
    assert r.returncode != 0
    assert "hero" in (r.stdout + r.stderr).lower()
