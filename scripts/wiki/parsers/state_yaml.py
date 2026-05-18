"""Парсит .landing-state.yaml в dict с current_stage и approved."""
from pathlib import Path
import yaml


def parse(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    stages = data.get("stages", {})

    approved = [k for k, v in stages.items() if v.get("status") == "approved"]
    in_progress = [k for k, v in stages.items() if v.get("status") == "in_progress"]
    locked = [k for k, v in stages.items() if v.get("status") == "locked"]
    failed = [k for k, v in stages.items() if v.get("status") == "failed"]

    if in_progress:
        current = in_progress[0]
    elif locked:
        current = locked[0]
    elif failed:
        current = failed[0]
    else:
        current = "complete"

    return {
        "project": data.get("project", ""),
        "current_stage": current,
        "approved": approved,
        "in_progress": in_progress,
        "locked": locked,
        "failed": failed,
        "schema_version": data.get("schema_version"),
    }
