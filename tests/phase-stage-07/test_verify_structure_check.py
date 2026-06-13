"""A2: structure_check_md гейт требует явный вердикт, а не просто наличие файла."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify-structure-check.py"

TABLE = ("# Поблочная сверка\n\n| Блок | В макете | Расхождения |\n"
         "|---|---|---|\n| hero | да | нет |\n| advantages | да | нет |\n\n")


def _run(proj):
    return subprocess.run([sys.executable, str(SCRIPT), str(proj)],
                          capture_output=True, text=True, encoding="utf-8")


def _proj(tmp_path, body):
    proj = tmp_path / "p"
    (proj / "07b_COMPOSED").mkdir(parents=True)
    if body is not None:
        (proj / "07b_COMPOSED" / "structure-check.md").write_text(body, encoding="utf-8")
    return proj


def test_pass_verdict(tmp_path):
    r = _run(_proj(tmp_path, TABLE + "STRUCTURE_MATCH: PASS\n"))
    assert r.returncode == 0, r.stdout + r.stderr


def test_fail_verdict_blocks(tmp_path):
    r = _run(_proj(tmp_path, TABLE + "STRUCTURE_MATCH: FAIL\n"))
    assert r.returncode == 1


def test_missing_verdict_blocks(tmp_path):
    r = _run(_proj(tmp_path, TABLE))  # таблица есть, вердикта нет
    assert r.returncode == 1


def test_empty_stub_blocks(tmp_path):
    r = _run(_proj(tmp_path, "ок\n"))
    assert r.returncode == 1


def test_missing_file_blocks(tmp_path):
    r = _run(_proj(tmp_path, None))
    assert r.returncode == 1
