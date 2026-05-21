"""Regression: PIPELINE_ORDER in enforce_stage_gate.py must be topologically
consistent with require_approved chains in config/stage-gates.yaml.

If a stage X has require_approved: [Y], then in PIPELINE_ORDER Y must
appear BEFORE X. Otherwise the hook gives chicken-and-egg verdicts.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from scripts.hooks.enforce_stage_gate import PIPELINE_ORDER


def test_pipeline_order_matches_require_approved_chains():
    repo_root = Path(__file__).parent.parent.parent
    gates = yaml.safe_load((repo_root / "config" / "stage-gates.yaml").read_text())

    violations = []
    for stage_id, stage_def in gates.get("stages", {}).items():
        if stage_id not in PIPELINE_ORDER:
            continue  # not all stages are in hook (e.g., 08b_style intentionally absent)
        x_idx = PIPELINE_ORDER.index(stage_id)
        for required in (stage_def or {}).get("require_approved", []) or []:
            if required not in PIPELINE_ORDER:
                continue
            y_idx = PIPELINE_ORDER.index(required)
            if y_idx >= x_idx:
                violations.append(
                    f"{stage_id} (idx {x_idx}) requires {required} (idx {y_idx}) "
                    f"but {required} appears AFTER {stage_id} in PIPELINE_ORDER"
                )

    assert not violations, "\n".join(violations)
