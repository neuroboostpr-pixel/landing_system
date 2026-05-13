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


# Pre-register namespace modules so `from skills.photo_curation...` works
_skills_mod = type(sys)("skills")
_pc_mod = type(sys)("skills.photo_curation")
_pc_scripts_mod = type(sys)("skills.photo_curation.scripts")
sys.modules.setdefault("skills", _skills_mod)
sys.modules["skills.photo_curation"] = _pc_mod
sys.modules["skills.photo_curation.scripts"] = _pc_scripts_mod

_RP_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "render-prompt.py"
if _RP_PATH.exists():
    _mod = _load_module("skills.photo_curation.scripts.render_prompt", _RP_PATH)
    sys.modules["skills.photo_curation.scripts.render_prompt"] = _mod

_INTAKE_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "intake.py"
if _INTAKE_PATH.exists():
    _intake_mod = _load_module("skills.photo_curation.scripts.intake", _INTAKE_PATH)
    sys.modules["skills.photo_curation.scripts.intake"] = _intake_mod

_SVG_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "svg-placeholder.py"
if _SVG_PATH.exists():
    _svg_mod = _load_module("skills.photo_curation.scripts.svg_placeholder", _SVG_PATH)
    sys.modules["skills.photo_curation.scripts.svg_placeholder"] = _svg_mod

_GALLERY_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "gallery-render.py"
if _GALLERY_PATH.exists():
    _gallery_mod = _load_module("skills.photo_curation.scripts.gallery_render", _GALLERY_PATH)
    sys.modules["skills.photo_curation.scripts.gallery_render"] = _gallery_mod

_PREVIEW_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "preview-render.py"
if _PREVIEW_PATH.exists():
    _preview_mod = _load_module("skills.photo_curation.scripts.preview_render", _PREVIEW_PATH)
    sys.modules["skills.photo_curation.scripts.preview_render"] = _preview_mod

_SELVAL_PATH = REPO_ROOT / "skills" / "photo-curation" / "scripts" / "selections-validator.py"
if _SELVAL_PATH.exists():
    _selval_mod = _load_module("skills.photo_curation.scripts.selections_validator", _SELVAL_PATH)
    sys.modules["skills.photo_curation.scripts.selections_validator"] = _selval_mod
