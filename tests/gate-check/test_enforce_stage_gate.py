"""Tests for scripts/hooks/enforce_stage_gate.py — PreToolUse hook
that blocks Write/Edit if file's stage hasn't been approved."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


HOOK = Path(__file__).parent.parent.parent / "scripts" / "hooks" / "enforce_stage_gate.py"


def _make_project(tmp_path: Path, stage_states: dict[str, str]) -> Path:
    """Создаёт минимальный проект с заданными статусами стадий."""
    proj = tmp_path / "proj"
    proj.mkdir()
    yaml_lines = ["project: test", "stages:"]
    for s, st in stage_states.items():
        yaml_lines.append(f'  "{s}": {{status: {st}, timestamp: ""}}')
    (proj / ".landing-state.yaml").write_text("\n".join(yaml_lines))
    return proj


def _invoke_hook(file_path: str | Path) -> tuple[int, str]:
    """Эмулирует PreToolUse hook input."""
    payload = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(file_path)},
    })
    res = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload, text=True, capture_output=True,
    )
    return res.returncode, res.stderr


def test_allows_write_to_current_stage(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {
        "03_references": "approved",
        "04_brand": "in_progress",
    })
    target = proj / "04_БРЕНД" / "brand-kit.md"
    target.parent.mkdir(parents=True)
    code, stderr = _invoke_hook(target)
    assert code == 0, f"expected pass, got stderr={stderr}"


def test_blocks_write_to_future_stage(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {
        "03_references": "in_progress",
        "04_brand": "locked",
        "05_design": "locked",
    })
    target = proj / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    target.parent.mkdir(parents=True)
    code, stderr = _invoke_hook(target)
    assert code != 0
    assert "05_design" in stderr or "predecessor" in stderr.lower()


def test_always_allowed_paths_pass(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {"03_references": "locked"})
    code, _ = _invoke_hook(proj / ".landing-state.yaml")
    assert code == 0


def test_paths_outside_project_pass(tmp_path: Path) -> None:
    # Файлы вне проекта (system-level) — hook не вмешивается
    code, _ = _invoke_hook(tmp_path / "outside.txt")
    assert code == 0


def test_missing_predecessor_treated_as_na(tmp_path):
    """If a predecessor stage isn't in the state file at all, treat it as n/a.

    This is load-bearing for prototype-first projects which legitimately omit
    00/01/01a/02 from state files (see CLAUDE.md).
    """
    proj = _make_project(tmp_path, {"04_brand": "in_progress"})
    target = proj / "04_БРЕНД" / "x.md"
    target.parent.mkdir(parents=True)
    code, stderr = _invoke_hook(target)
    assert code == 0, (
        f"Expected pass (predecessors missing = implicit n/a), got "
        f"exit={code}, stderr={stderr}"
    )


def test_corrupt_state_file_allows_edit(tmp_path):
    """Fail-open: a broken state file should not brick the user's session.

    Hook logs warning to stderr but returns 0 so user can still edit (e.g. fix
    the corrupt state file itself).
    """
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".landing-state.yaml").write_text("this is :: not valid YAML\n%%%")
    target = proj / "04_БРЕНД" / "x.md"
    target.parent.mkdir(parents=True)
    code, stderr = _invoke_hook(target)
    assert code == 0
    assert "error" in stderr.lower() or "allowing" in stderr.lower(), (
        f"Expected warning in stderr, got: {stderr}"
    )
