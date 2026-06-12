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


def test_per_card_multi_paragraph_not_inflated_by_sibling_cards(tmp_path):
    """With card_probe_selector, section-level multi-paragraph for
    `feat_statement` must see only the section header (without cards) — NOT
    inflated by every <p> inside each feature-card child.

    The per-card-spec fixture has 2 cards with filled icon_svg, so the
    inline-svg-icon error must NOT fire. Only the statement default mismatch
    (or its absence after card-decompose) should drive output.
    """
    r = _run(FIX / "brutalist-features-section.html", FIX / "per-card-spec.yaml")
    # inline-svg-icon must NOT appear: each card template row has a value
    assert "inline-svg-icon" not in r.stdout
    # If multi-paragraph appears, it must be about a number ≤ 4 (statement card
    # only), never 10 (the inflated count we saw against the whole section).
    if "multi-paragraph" in r.stdout:
        # Extract the number reported. Pattern: "composed has N paragraphs"
        import re as _re
        for m in _re.finditer(r"composed has (\d+) paragraphs", r.stdout):
            n = int(m.group(1))
            assert n <= 4, f"per-card refactor should cap multi-paragraph count at 4, got {n}"


def test_card_skip_selector_excludes_statement_card(tmp_path):
    """`card_skip_selector` removes decorative cards from per-card iteration.

    Refined spec has card_skip_selector='.feature-statement' and template
    length=2 (matching 2 non-statement cards in the fixture). Linter must
    NOT report template[2]/[3] overflow.
    """
    r = _run(FIX / "brutalist-features-section.html", FIX / "refined-spec.yaml")
    assert "template[2]" not in r.stdout
    # The statement-card's <p>×4 must not appear as a card-level multi-p
    # for the `text` control (it has target_selector='.feature-text').
    assert "features.text:" not in r.stdout


def test_target_selector_scopes_multi_paragraph(tmp_path):
    """`target_selector` on a textarea limits <p> counting to that sub-element.

    `feat_statement` has target_selector='.feature-statement' so it sees
    exactly 4 <p> matching the 4 paragraphs in the default → no error.
    """
    r = _run(FIX / "brutalist-features-section.html", FIX / "refined-spec.yaml")
    assert "feat_statement" not in r.stdout, (
        f"feat_statement should not appear in errors when target_selector "
        f"matches scope and default has same paragraph count.\nOutput:\n{r.stdout}"
    )


def test_cli_fix_writes_backup_and_modifies_spec(tmp_path):
    # Copy broken spec to a tmp location so we don't mutate the fixture
    import shutil
    spec_copy = tmp_path / "spec.yaml"
    shutil.copy(FIX / "broken-spec.yaml", spec_copy)
    r = _run(FIX / "brutalist-features-section.html", spec_copy, "--fix")
    # Backup exists
    backups = list(tmp_path.glob("spec.yaml.bak.*"))
    assert len(backups) == 1
    # Spec was modified (contains AUTO-LINT comment)
    new_text = spec_copy.read_text(encoding="utf-8")
    assert "AUTO-LINT" in new_text
    # Re-run without --fix: errors should be reduced
    r2 = _run(FIX / "brutalist-features-section.html", spec_copy)
    assert "multi-paragraph" not in r2.stdout
