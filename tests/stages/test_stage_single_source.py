"""E1: единый источник истины списка этапов — config/stages.yaml.

Спека reference-driven flow, раздел 6 «список этапов рассинхронен»:
порядок этапов задан в одном месте, всё остальное читает оттуда.

Порядок топологически согласован с require_approved в stage-gates.yaml
(это дополнительно проверяет tests/gate-check/test_pipeline_order_sync.py):
07a_prototype ПЕРЕД 07_content; 10_qa ПЕРЕД 09_deploy.
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGES_YAML = ROOT / "config" / "stages.yaml"

EXPECTED_ORDER = [
    "00_brief", "01_context", "01a_niche_analysis", "02_assets",
    "07a_prototype",
    "03_references", "03b_visual_concept", "04_brand", "05_design",
    "06_stack", "07_content", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
    "08_build", "08b_style", "10_qa", "09_deploy", "11_analytics", "12_seo",
]


def canonical():
    return yaml.safe_load(STAGES_YAML.read_text(encoding="utf-8"))["stages"]


def test_canonical_file_well_formed():
    stages = canonical()
    ids = [s["id"] for s in stages]
    assert ids == EXPECTED_ORDER
    assert all(s.get("label") for s in stages), "у каждого этапа есть label"


def test_stages_py_prints_order():
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "stages.py"), "--order"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    assert out.stdout.split() == EXPECTED_ORDER


def test_stages_py_prints_labels():
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "stages.py"), "--labels"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    assert len(lines) == len(EXPECTED_ORDER)
    assert all("\t" in l for l in lines)


def test_state_template_matches_canonical():
    state = yaml.safe_load(
        (ROOT / "template" / ".landing-state.yaml").read_text(encoding="utf-8")
    )
    assert list(state["stages"].keys()) == EXPECTED_ORDER


def test_stage_gates_keys_subset_of_canonical():
    gates = yaml.safe_load(
        (ROOT / "config" / "stage-gates.yaml").read_text(encoding="utf-8")
    )
    unknown = set(gates["stages"].keys()) - set(EXPECTED_ORDER)
    assert not unknown, f"stage-gates.yaml содержит этапы вне канона: {unknown}"


def test_no_hardcoded_order_in_bash_scripts():
    for script in ("gate-check.sh", "render-pipeline-map.sh"):
        text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
        assert "00_brief" not in text, f"{script} хардкодит список этапов"
        assert "stages.py" in text, f"{script} должен читать порядок из stages.py"


def test_no_hardcoded_order_in_python_consumers():
    for script in ("landing-go-next-stage.py", "hooks/enforce_stage_gate.py"):
        text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
        assert "stages.yaml" in text or "stages_py" in text or "load_stage" in text, (
            f"{script} должен читать порядок из config/stages.yaml"
        )
        assert '"00_brief"' not in text, f"{script} хардкодит список этапов"
        assert "07b_wireframe" not in text
