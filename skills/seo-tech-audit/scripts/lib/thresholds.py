"""Load default + project-override thresholds for hard/soft gates."""
from pathlib import Path
import yaml

_DEFAULTS_PATH = Path(__file__).parent.parent.parent / "config" / "quality-thresholds.yaml"


def load_thresholds(project_overrides_path: Path | None = None) -> dict:
    """Load defaults; merge project-specific overrides if file exists.

    Returns: {check_id: {hard: bool, value: any, justification: str|None}}
    """
    if not _DEFAULTS_PATH.exists():
        raise FileNotFoundError(f"defaults not found: {_DEFAULTS_PATH}")
    defaults = yaml.safe_load(_DEFAULTS_PATH.read_text(encoding="utf-8")) or {}

    if project_overrides_path and project_overrides_path.exists():
        overrides = yaml.safe_load(project_overrides_path.read_text(encoding="utf-8")) or {}
        for check_id, cfg in overrides.items():
            if check_id in defaults:
                defaults[check_id].update(cfg)
            else:
                defaults[check_id] = cfg
    return defaults
