import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_skills_mod = sys.modules.setdefault("skills", type(sys)("skills"))
_vg_mod = type(sys)("skills.visual_generation")
_vg_scripts_mod = type(sys)("skills.visual_generation.scripts")
sys.modules["skills.visual_generation"] = _vg_mod
sys.modules["skills.visual_generation.scripts"] = _vg_scripts_mod

for script in ["slot-scanner", "prompt-picker", "visual-cache"]:
    p = REPO_ROOT / "skills" / "visual-generation" / "scripts" / f"{script}.py"
    if p.exists():
        mod = _load_module(f"skills.visual_generation.scripts.{script.replace('-', '_')}", p)
        sys.modules[f"skills.visual_generation.scripts.{script.replace('-', '_')}"] = mod
