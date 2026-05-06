import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-competitors.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(fixture_name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / fixture_name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("competitors-valid.yaml")
    assert r.returncode == 0, r.stderr or r.stdout


def test_too_few_fails():
    r = run("competitors-invalid-too-few.yaml")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "15" in out


def test_bad_role_fails():
    r = run("competitors-invalid-bad-role.yaml")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "role" in out
