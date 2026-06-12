#!/usr/bin/env python3
"""PreToolUse hook — блокирует Write/Edit/MultiEdit к файлам стадии,
которая ещё не достигла статуса in_progress/approved.

Запускается из .claude/settings.json:

  {
    "hooks": {
      "PreToolUse": [{
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [{"type": "command",
                   "command": "python3 $CLAUDE_PROJECT_DIR/scripts/hooks/enforce_stage_gate.py"}]
      }]
    }
  }

Контракт PreToolUse hook (Anthropic Claude Code):
- stdin: JSON {"tool_name": str, "tool_input": {...}}
- exit 0: allow
- exit != 0 + stderr: block + show stderr to model
"""
from __future__ import annotations

import functools
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

THIS_DIR = Path(__file__).parent
PATH_MAP_FILE = THIS_DIR / "_stage_paths.yaml"

# Порядок этапов — из config/stages.yaml (E1, single source of truth).
# Note: 10_qa comes BEFORE 09_deploy because config/stage-gates.yaml declares
# 09_deploy require_approved: ["08_build", "10_qa"]. The test in
# tests/gate-check/test_pipeline_order_sync.py enforces this topologically.
# 08b_style intentionally omitted (sub-phase of 08_build, same folder —
# не должен блокировать последующие этапы как «предшественник»).
_STAGES_YAML = THIS_DIR.parent.parent / "config" / "stages.yaml"
PIPELINE_ORDER = [
    s["id"]
    for s in yaml.safe_load(_STAGES_YAML.read_text(encoding="utf-8"))["stages"]
    if s["id"] != "08b_style"
]


@functools.lru_cache(maxsize=1)
def _load_path_map() -> dict[str, Any]:
    """Parse _stage_paths.yaml once per process (cached)."""
    return yaml.safe_load(PATH_MAP_FILE.read_text())


def _find_project_root(file_path: Path) -> Path | None:
    """Поднимается вверх ища .landing-state.yaml."""
    p = file_path.resolve()
    for parent in (p, *p.parents):
        if (parent / ".landing-state.yaml").exists():
            return parent
    return None


def _glob_to_regex(glob: str, project_root: str) -> re.Pattern[str]:
    pattern = glob.replace("{project}", project_root)
    # ** → .*, * → [^/]*
    pattern = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.compile(f"^{pattern}$")


def _stage_for_path(file_path: Path, project_root: Path, path_map: dict) -> str | None:
    file_abs = str(file_path.resolve())
    proj_str = str(project_root)

    for entry in path_map.get("always_allowed", []):
        if _glob_to_regex(entry, proj_str).match(file_abs):
            return None  # explicitly allowed

    for entry in path_map.get("mappings", []):
        if _glob_to_regex(entry["glob"], proj_str).match(file_abs):
            return entry["stage"]
    return "__outside_pipeline__"  # not in mapping at all


def _stage_predecessors_approved(state: dict, stage: str) -> tuple[bool, str]:
    """Returns (ok, reason). ok=False if any predecessor isn't approved/n/a.

    Stages not present in state file are treated as implicit n/a (consistent
    with prototype-first design — many projects don't populate every stage)."""
    try:
        idx = PIPELINE_ORDER.index(stage)
    except ValueError:
        return True, ""

    stages_in_state = (state or {}).get("stages", {}) or {}
    for prev_stage in PIPELINE_ORDER[:idx]:
        st = stages_in_state.get(prev_stage, {})
        if not isinstance(st, dict):
            continue
        status = st.get("status")
        if status is None:
            continue  # missing key → implicit n/a
        if status not in ("approved", "n/a"):
            return False, (
                f"Cannot Write/Edit to '{stage}' — predecessor '{prev_stage}' "
                f"has status '{status}'. Run gate-check.sh and approve previous "
                f"stages before editing this one."
            )
    return True, ""


# ---------------------------------------------------------------------------
# Bash matcher — detects shell write operations to pipeline files.
#
# Conservative parser: catches obvious write patterns, fails open (exit 0 with
# stderr warning) on anything complex. Better to miss a few cases than to
# false-positive-block honest developer Bash commands.
# ---------------------------------------------------------------------------

# `> path` or `>> path` redirect. Stops at shell metachars / quotes.
_WRITE_REDIRECT_RE = re.compile(
    r""">>?\s*(['"]?)(?P<redirect>[^\s'"|;&)<>]+)\1"""
)

# `| tee [-flags] path` (tee without pipe is rare but also matched if standalone)
_TEE_RE = re.compile(
    r"""\btee\b(?:\s+-[aip]+)*\s+(['"]?)(?P<tee>[^\s'"|;&)<>]+)\1"""
)

# `cp/mv/rm/chmod/chown/touch/mkdir/install [flags] [src...] target`
# We greedily take the LAST non-flag token on the line as the target.
_FILE_OP_CMDS = ("cp", "mv", "rm", "chmod", "chown", "touch", "mkdir", "install")


def _extract_file_op_targets(command: str) -> list[str]:
    """Extract target paths from cp/mv/rm/chmod/chown/touch/mkdir/install."""
    targets: list[str] = []
    # Split on shell separators that end a command
    for segment in re.split(r"[;&|\n]+", command):
        seg = segment.strip()
        if not seg:
            continue
        tokens = seg.split()
        if not tokens:
            continue
        # Find the command word (skip leading env assignments like FOO=bar cmd)
        cmd_idx = 0
        while cmd_idx < len(tokens) and "=" in tokens[cmd_idx] and not tokens[cmd_idx].startswith("-"):
            cmd_idx += 1
        if cmd_idx >= len(tokens):
            continue
        cmd_word = tokens[cmd_idx]
        if cmd_word not in _FILE_OP_CMDS:
            continue
        # For chmod/chown: first arg after flags is mode/owner, not a target;
        # rest are targets. For cp/mv: last is target. For rm/touch/mkdir/install:
        # all non-flag args are targets. Simplest: every non-flag arg after the
        # cmd is a candidate target (over-collects but stage check filters).
        args = tokens[cmd_idx + 1 :]
        # For chmod/chown skip the first non-flag arg (mode/owner)
        if cmd_word in ("chmod", "chown"):
            skipped_mode = False
            for a in args:
                if a.startswith("-"):
                    continue
                if not skipped_mode:
                    skipped_mode = True
                    continue
                targets.append(a.strip("'\""))
        else:
            for a in args:
                if a.startswith("-"):
                    continue
                targets.append(a.strip("'\""))
    return targets


def _extract_write_targets(command: str) -> list[str]:
    """From a bash command string, extract paths likely being written to.

    Conservative: only catches obvious patterns. Complex shell (subshells,
    command substitution, variables, heredocs, eval/exec) returns empty list
    → caller fails open with stderr warning.
    """
    if not command or not isinstance(command, str):
        return []

    complex_markers = ("$(", "`", "<<", "${", " eval ", " exec ", "eval ", "exec ")
    if any(m in command for m in complex_markers):
        # Log uncertainty so it's visible in stderr but don't block
        sys.stderr.write(
            "⚠️  enforce_stage_gate (Bash): complex shell detected, "
            "skipping write-target analysis (fail-open)\n"
        )
        return []

    targets: list[str] = []
    for m in _WRITE_REDIRECT_RE.finditer(command):
        t = m.group("redirect")
        if t and not t.startswith("/dev/") and not t.startswith("&"):
            targets.append(t)

    for m in _TEE_RE.finditer(command):
        t = m.group("tee")
        if t and not t.startswith("/dev/"):
            targets.append(t)

    targets.extend(_extract_file_op_targets(command))
    return targets


def _check_bash_targets(
    targets: list[str], proj_root_hint: Path | None
) -> tuple[int, str]:
    """For each potential write target, check predecessors.

    Returns (exit_code, stderr). 0 = allow, 2 = block.
    """
    path_map = _load_path_map()

    for target_str in targets:
        target = Path(target_str)
        if not target.is_absolute():
            if proj_root_hint is not None:
                target = (proj_root_hint / target).resolve()
            else:
                # Without absolute path and no hint we can't resolve. Skip.
                continue

        proj_root = _find_project_root(target)
        if proj_root is None:
            continue

        stage = _stage_for_path(target, proj_root, path_map)
        if stage is None or stage == "__outside_pipeline__":
            continue

        try:
            state = yaml.safe_load((proj_root / ".landing-state.yaml").read_text()) or {}
        except Exception:
            continue  # fail-open on unreadable state

        ok, reason = _stage_predecessors_approved(state, stage)
        if not ok:
            return 2, (
                f"❌ Stage gate enforcement (Bash): {reason}\n"
                f"   Target: {target}\n"
            )

    return 0, ""


def main() -> int:
    try:
        return _main_inner()
    except Exception as ex:
        # Fail-open policy: a broken hook should not brick the user's editing
        # session. Real gate enforcement happens via gate-check.sh anyway —
        # this hook is a fast pre-flight. If it can't decide, get out of the way.
        sys.stderr.write(
            f"⚠️  enforce_stage_gate hook error (allowing edit): "
            f"{type(ex).__name__}: {ex}\n"
        )
        return 0


def _main_inner() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as ex:
        sys.stderr.write(f"⚠️  enforce_stage_gate: bad payload, allowing: {ex}\n")
        return 0

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    # Bash tool: parse shell command for write operations.
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        targets = _extract_write_targets(command)
        if not targets:
            return 0  # read-only, no writes detected, or complex shell (fail-open)

        # Try to find a project root from any absolute target
        proj_root_hint: Path | None = None
        for t_str in targets:
            t = Path(t_str)
            if t.is_absolute():
                pr = _find_project_root(t)
                if pr is not None:
                    proj_root_hint = pr
                    break

        code, stderr = _check_bash_targets(targets, proj_root_hint)
        if stderr:
            sys.stderr.write(stderr)
        return code

    file_path_str = tool_input.get("file_path")
    if not file_path_str:
        return 0

    file_path = Path(file_path_str).resolve()
    proj_root = _find_project_root(file_path)
    if proj_root is None:
        return 0

    path_map = _load_path_map()
    stage = _stage_for_path(file_path, proj_root, path_map)
    if stage is None or stage == "__outside_pipeline__":
        return 0

    state = yaml.safe_load((proj_root / ".landing-state.yaml").read_text()) or {}
    ok, reason = _stage_predecessors_approved(state, stage)
    if not ok:
        sys.stderr.write(f"❌ Stage gate enforcement: {reason}\n")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
