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

PIPELINE_ORDER = [
    "00_brief", "01_context", "01a_niche_analysis", "02_assets",
    "03_references", "04_brand", "05_design", "06_stack", "07_content",
    "07a_prototype", "07b_wireframe", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
    "08_build", "10_qa", "09_deploy", "11_analytics", "12_seo",
]
# Note: 10_qa comes BEFORE 09_deploy because config/stage-gates.yaml declares
# 09_deploy require_approved: ["08_build", "10_qa"]. The test in
# tests/gate-check/test_pipeline_order_sync.py enforces this topologically.
# 08b_style intentionally omitted (sub-phase of 08_build, same folder).


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

    tool_input = payload.get("tool_input", {})
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
