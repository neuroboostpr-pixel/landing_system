"""A1 (зона A): fidelity-гейт работает на всех форматах источника,
канон этапа — prototype.md.

Спека §2.1: проверка «дошло ли ≥90% текста» раньше работала только для DOCX —
для PDF/MD/картинок защиты не было. Теперь:
  - .md/.txt источник → текст берётся напрямую;
  - .pdf → текстовый слой через extract-pdf-text.py;
  - картинки → OCR (pytesseract), при недоступности — ЯВНОЕ предупреждение
    в отчёте (не молчаливый pass);
  - сверка идёт против prototype.md (канон), fallback — prototype.yaml.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "skills" / "prototype-import" / "scripts" / "gate-prototype-fidelity.py"
VERIFY = ROOT / "skills" / "prototype-import" / "scripts" / "verify-prototype-fidelity.py"

SRC_TEXT = """Заголовок: Автомобили LiXiang в Дубае
Подзаголовок: Полный модельный ряд с гарантией от дилера
Кнопка: Получить персональное предложение
Цена от 250000 дирхам за модель L7 комфорт
Доставка по всем Эмиратам за 48 часов
"""


def _project(tmp_path: Path, source_name: str, source_bytes: bytes,
             proto_md: str | None) -> Path:
    proj = tmp_path / "proj"
    src = proj / "07_ПРОТОТИП" / "source"
    src.mkdir(parents=True)
    (src / source_name).write_bytes(source_bytes)
    if proto_md is not None:
        (proj / "07_ПРОТОТИП" / "prototype.md").write_text(proto_md, encoding="utf-8")
    return proj


def _run_gate(proj: Path):
    return subprocess.run(
        [sys.executable, str(GATE), str(proj)],
        capture_output=True, text=True, encoding="utf-8",
    )


def test_md_source_full_coverage_passes(tmp_path):
    proj = _project(tmp_path, "prototype.md", SRC_TEXT.encode("utf-8"),
                    proto_md="# Прототип\n\n" + SRC_TEXT)
    r = _run_gate(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_md_source_lost_content_fails(tmp_path):
    # prototype.md содержит только первую строку — потеря >10%
    proj = _project(tmp_path, "prototype.md", SRC_TEXT.encode("utf-8"),
                    proto_md="Заголовок: Автомобили LiXiang в Дубае\n")
    r = _run_gate(proj)
    assert r.returncode == 1, r.stdout + r.stderr


def test_md_canon_preferred_over_yaml(tmp_path):
    """Если есть и prototype.md, и prototype.yaml — сверяем против .md."""
    proj = _project(tmp_path, "prototype.md", SRC_TEXT.encode("utf-8"),
                    proto_md="# Прототип\n\n" + SRC_TEXT)
    # подкинем заведомо пустой yaml — не должен влиять
    (proj / "07_ПРОТОТИП" / "prototype.yaml").write_text(
        "project: x\nblocks: []\n", encoding="utf-8")
    r = _run_gate(proj)
    assert r.returncode == 0, r.stdout + r.stderr


def test_pdf_source_text_layer_verified(tmp_path):
    reportlab = pytest.importorskip("reportlab")  # noqa: F841
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    proj = tmp_path / "proj"
    src = proj / "07_ПРОТОТИП" / "source"
    src.mkdir(parents=True)
    pdf_path = src / "prototype.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    y = 800
    for line in ["LiXiang Dubai cars catalog", "Full model range with warranty",
                 "Personal offer button here", "Price from 250000 dirhams L7"]:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    (proj / "07_ПРОТОТИП" / "prototype.md").write_text(
        "LiXiang Dubai cars catalog\nFull model range with warranty\n"
        "Personal offer button here\nPrice from 250000 dirhams L7\n",
        encoding="utf-8")
    r = _run_gate(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_image_source_explicit_warning_when_no_ocr(tmp_path):
    """Картинка без OCR: не FAIL, но ЯВНОЕ предупреждение (не молчаливый pass)."""
    png_1px = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
        "de0000000c4944415408d763f8cfc0000000030001ff5e44ea0000000049454e"
        "44ae426082")
    proj = _project(tmp_path, "scan.png", png_1px, proto_md="# Прототип\nТекст\n")
    r = _run_gate(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    combined = r.stdout + r.stderr
    assert "OCR" in combined or "не проверена" in combined.lower()
    report = proj / "07_ПРОТОТИП" / "fidelity-report.md"
    assert report.exists()
    assert "не проверена" in report.read_text(encoding="utf-8").lower()


def test_missing_prototype_md_and_yaml_fails(tmp_path):
    proj = _project(tmp_path, "prototype.md", SRC_TEXT.encode("utf-8"), proto_md=None)
    r = _run_gate(proj)
    assert r.returncode == 1


def test_verify_accepts_md_prototype(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text(SRC_TEXT, encoding="utf-8")
    proto = tmp_path / "prototype.md"
    proto.write_text("# П\n" + SRC_TEXT, encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(VERIFY), "--source-text", str(src),
         "--prototype", str(proto), "--min-coverage", "0.9"],
        capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
