"""Tests for Bash matcher in enforce_stage_gate.py — detects shell write
operations targeting pipeline files."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).parent.parent.parent / "scripts" / "hooks" / "enforce_stage_gate.py"


def _make_project(tmp_path: Path, stage_states: dict[str, str]) -> Path:
    proj = tmp_path / "proj"
    proj.mkdir()
    yaml_lines = ["project: test", "stages:"]
    for s, st in stage_states.items():
        yaml_lines.append(f'  "{s}": {{status: {st}, timestamp: ""}}')
    (proj / ".landing-state.yaml").write_text("\n".join(yaml_lines))
    return proj


def _invoke_bash(command: str) -> tuple[int, str]:
    payload = json.dumps({
        "tool_name": "Bash",
        "tool_input": {"command": command},
    })
    res = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload, text=True, capture_output=True,
    )
    return res.returncode, res.stderr


def test_bash_read_only_passes(tmp_path: Path) -> None:
    """cat, ls, grep, find — no write operation. Should pass."""
    proj = _make_project(tmp_path, {"04_brand": "in_progress"})
    code, _ = _invoke_bash(f"cat {proj}/04_БРЕНД/foo.md")
    assert code == 0
    code, _ = _invoke_bash(f"ls {proj}/05_ДИЗАЙН-СИСТЕМА/")
    assert code == 0
    code, _ = _invoke_bash(f"grep -r 'foo' {proj}/04_БРЕНД/")
    assert code == 0


def test_bash_redirect_to_future_stage_blocks(tmp_path: Path) -> None:
    """echo ... > 05_ДИЗАЙН-СИСТЕМА/x.md while 04_brand in_progress should BLOCK."""
    proj = _make_project(tmp_path, {
        "04_brand": "in_progress",
        "05_design": "locked",
    })
    code, stderr = _invoke_bash(f"echo hello > {proj}/05_ДИЗАЙН-СИСТЕМА/x.md")
    assert code != 0
    assert "05_design" in stderr or "predecessor" in stderr.lower() or "stage gate" in stderr.lower()


def test_bash_append_to_future_stage_blocks(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {"04_brand": "in_progress", "05_design": "locked"})
    code, _ = _invoke_bash(f"echo hello >> {proj}/05_ДИЗАЙН-СИСТЕМА/x.md")
    assert code != 0


def test_bash_tee_to_future_stage_blocks(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {"04_brand": "in_progress", "05_design": "locked"})
    code, _ = _invoke_bash(f"echo hi | tee {proj}/05_ДИЗАЙН-СИСТЕМА/x.md")
    assert code != 0


def test_bash_cp_to_future_stage_blocks(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {"04_brand": "in_progress", "05_design": "locked"})
    code, _ = _invoke_bash(f"cp /tmp/x.md {proj}/05_ДИЗАЙН-СИСТЕМА/x.md")
    assert code != 0


def test_bash_write_to_current_stage_passes(tmp_path: Path) -> None:
    """echo > 04_БРЕНД/x.md when 04_brand in_progress should PASS."""
    proj = _make_project(tmp_path, {"04_brand": "in_progress"})
    code, _ = _invoke_bash(f"echo hello > {proj}/04_БРЕНД/x.md")
    assert code == 0


def test_bash_complex_command_fails_open(tmp_path: Path) -> None:
    """Complex pipeline/heredoc/subshell we can't parse confidently — fail open with stderr warning."""
    proj = _make_project(tmp_path, {"04_brand": "in_progress", "05_design": "locked"})
    # Heredoc with command substitution + pipe — we can't reliably parse target
    cmd = f'cat <<EOF | tee "$(echo {proj}/05_ДИЗАЙН-СИСТЕМА/x.md)"\nfoo\nEOF'
    code, stderr = _invoke_bash(cmd)
    # Acceptable: either pass with warning, or block if our parser is aggressive
    # For now: prefer fail-open with stderr warning so honest devs aren't blocked
    if code == 0:
        # Acceptable — log should mention uncertainty
        pass
    else:
        # Aggressive parser blocked it — that's also acceptable for security
        assert "stage gate" in stderr.lower() or "warning" in stderr.lower()


def test_bash_outside_pipeline_passes(tmp_path: Path) -> None:
    """Write to /tmp/foo or other non-pipeline path — pass."""
    proj = _make_project(tmp_path, {"04_brand": "in_progress"})
    code, _ = _invoke_bash("echo hello > /tmp/foo.txt")
    assert code == 0


def test_bash_no_command_passes(tmp_path: Path) -> None:
    """Empty/missing command — pass (don't crash)."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {}})
    res = subprocess.run([sys.executable, str(HOOK)], input=payload, text=True, capture_output=True)
    assert res.returncode == 0
