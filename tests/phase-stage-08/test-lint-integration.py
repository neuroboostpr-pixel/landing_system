"""End-to-end test for the lint CLI."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lint-composed-vs-spec.py"
FIX = REPO_ROOT / "tests" / "phase-stage-08" / "fixtures" / "lint"


def _run(composed, spec_yaml, *extra):
    return subprocess.run(
        [sys.executable, str(CLI), "--composed", str(composed), "--spec", str(spec_yaml), *extra],
        capture_output=True, text=True,
    )


def test_cli_exits_one_when_statement_short(tmp_path):
    r = _run(FIX / "brutalist-features-section.html", FIX / "broken-spec.yaml")
    assert r.returncode == 1
    assert "multi-paragraph" in r.stdout
    assert "inline-svg-icon" in r.stdout  # template icon_svg is empty


def test_cli_missing_composed_warning_not_error(tmp_path):
    nonexistent = tmp_path / "missing.html"
    r = _run(nonexistent, FIX / "good-spec.yaml")
    assert r.returncode == 0
    assert "warning" in r.stdout.lower()


def test_cli_good_spec_minimal_errors(tmp_path):
    # good-spec also has issues vs brutalist-features (statement is "One paragraph only")
    r = _run(FIX / "brutalist-features-section.html", FIX / "good-spec.yaml")
    # multi-paragraph should fire because composed has 4 <p> but good-spec default has 1 para
    assert "multi-paragraph" in r.stdout
