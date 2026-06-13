# tests/test_log_decisions.py
import importlib.util
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "log-decisions.py"

def _load():
    spec = importlib.util.spec_from_file_location("log_decisions", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_creates_decisions_log_if_missing(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    log = project / "decisions.log.md"
    assert log.exists()

def test_appends_no_deviations_entry(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "04_brand" in content
    assert "нет отклонений" in content

def test_appends_deviations_from_file(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    decisions_dir = project / ".stage-decisions"
    decisions_dir.mkdir()
    dec_file = decisions_dir / "04_brand.md"
    dec_file.write_text(
        "- Типографика: Inter 700 (агент)\n- Иконки: Lucide (агент)\n",
        encoding="utf-8"
    )
    mod.append_decisions(str(project), "04_brand", str(dec_file))
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "Inter 700" in content
    assert "Lucide" in content
    assert "04_brand" in content

def test_appends_multiple_stages(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    mod.append_decisions(str(project), "05_design", None)
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "04_brand" in content
    assert "05_design" in content

def test_deletes_temp_file_after_append(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    decisions_dir = project / ".stage-decisions"
    decisions_dir.mkdir()
    dec_file = decisions_dir / "04_brand.md"
    dec_file.write_text("- Типографика: Inter 700\n", encoding="utf-8")
    mod.append_decisions(str(project), "04_brand", str(dec_file))
    assert not dec_file.exists()

def test_creates_header_on_first_run(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "# Decisions Log" in content
