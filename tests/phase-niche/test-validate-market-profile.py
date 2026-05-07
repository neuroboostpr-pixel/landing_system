import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-market-profile.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("market-profile-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_missing_tier_fails():
    r = run("market-profile-missing-tier.md")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "tier" in out or "section 1" in out or "accessibility" in out
