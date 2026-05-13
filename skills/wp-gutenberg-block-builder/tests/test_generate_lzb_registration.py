import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-lzb-registration.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    (project / "08_КОД" / "wp-theme" / "functions.php").write_text(
        "<?php\n// existing theme code\n", encoding="utf-8"
    )
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_writes_lzb_init_action(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "AUTO-GENERATED START: lzb-block-registration" in out
    assert "add_action('lzb/init'" in out or "add_action( 'lzb/init'" in out
    assert "lazyblocks()->add_block" in out


def test_registers_both_section_and_card_for_section_card_block(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "'slug' => 'lazyblock/hero'" in out
    assert "'slug' => 'lazyblock/tarify'" in out
    assert "'slug' => 'lazyblock/tarify-card'" in out


def test_child_of_uses_control_id_not_name(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    # c_ft has child_of: c_f — must appear as literal 'c_f', not 'features'
    assert "'child_of' => 'c_f'" in out


def test_idempotent_regeneration(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    first = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    _run(project)
    second = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert first == second


def test_preserves_existing_functions_php_content(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "// existing theme code" in out


def test_fails_when_block_spec_missing(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme").mkdir(parents=True)
    (project / "08_КОД" / "wp-theme" / "functions.php").write_text("<?php\n", encoding="utf-8")
    r = _run(project)
    assert r.returncode != 0
    assert "block-spec.yaml" in (r.stderr + r.stdout)


def test_boolean_default_renders_as_php_boolean(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme").mkdir(parents=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_t, name: enabled, type: toggle, label: E, default: true }\n"
        "      - { id: c_f, name: visible, type: toggle, label: V, default: false }\n",
        encoding="utf-8",
    )
    (project / "08_КОД" / "wp-theme" / "functions.php").write_text("<?php\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    # Must be unquoted PHP literals, not quoted strings
    assert "'default' => true" in out
    assert "'default' => false" in out
    assert "'default' => 'True'" not in out
    assert "'default' => 'False'" not in out


def test_integer_default_renders_as_php_integer(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme").mkdir(parents=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: Hero\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c_r, name: opacity, type: range, label: O, default: 75 }\n",
        encoding="utf-8",
    )
    (project / "08_КОД" / "wp-theme" / "functions.php").write_text("<?php\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "'default' => 75" in out
    assert "'default' => '75'" not in out


def test_no_bak_file_created(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    bak = project / "08_КОД" / "wp-theme" / "functions.php.bak"
    assert not bak.exists(), "generator must not create .bak file"
