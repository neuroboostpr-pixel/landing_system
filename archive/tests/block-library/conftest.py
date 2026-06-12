import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _load_module(module_name: str, file_path: Path):
    """Load a Python file as a module under a namespaced name (handles dashed dirs)."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Pre-register namespace modules so `from skills.landing_import_blocks...` works
_skills_mod = type(sys)("skills")
_lib_mod = type(sys)("skills.landing_import_blocks")
_lib_scripts_mod = type(sys)("skills.landing_import_blocks.scripts")
sys.modules.setdefault("skills", _skills_mod)
sys.modules["skills.landing_import_blocks"] = _lib_mod
sys.modules["skills.landing_import_blocks.scripts"] = _lib_scripts_mod

_CHECK_DUP_PATH = REPO_ROOT / "skills" / "landing-import-blocks" / "scripts" / "check_duplicates.py"
if _CHECK_DUP_PATH.exists():
    _cd_mod = _load_module("skills.landing_import_blocks.scripts.check_duplicates", _CHECK_DUP_PATH)
    sys.modules["skills.landing_import_blocks.scripts.check_duplicates"] = _cd_mod
