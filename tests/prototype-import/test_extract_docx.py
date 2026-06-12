"""B37 Фаза 0 — extract-docx-text.py извлекает весь текст, включая таблицы."""
import importlib.util
import json
from pathlib import Path

import pytest

docx = pytest.importorskip("docx")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "prototype-import" / "scripts" / "extract-docx-text.py"


def _load():
    spec = importlib.util.spec_from_file_location("extract_docx_text", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_docx(path: Path):
    d = docx.Document()
    d.add_heading("НЕЙРОКРЕАТОР", level=1)
    d.add_paragraph("Практический онлайн-курс по ИИ-визуалу")
    # таблица тарифов (текст в таблице раньше терялся)
    t = d.add_table(rows=2, cols=2)
    t.rows[0].cells[0].text = "Тариф ВИП"
    t.rows[0].cells[1].text = "211 990 руб."
    t.rows[1].cells[0].text = "Рассрочка"
    t.rows[1].cells[1].text = "от 4 920 руб./мес."
    d.add_paragraph("Хочу на курс")
    d.save(str(path))


def test_extracts_paragraphs_and_tables(tmp_path):
    m = _load()
    docx_path = tmp_path / "proto.docx"
    _make_docx(docx_path)
    units = m.extract(docx_path)
    all_text = "\n".join(u["text"] for u in units)
    # параграфы
    assert "НЕЙРОКРЕАТОР" in all_text
    assert "Практический онлайн-курс" in all_text
    assert "Хочу на курс" in all_text
    # текст ИЗ ТАБЛИЦЫ не потерян (главный баг прошлого парсера)
    assert "211 990" in all_text
    assert "4 920" in all_text
    # есть и paragraph, и table единицы
    kinds = {u["kind"] for u in units}
    assert "paragraph" in kinds and "table" in kinds


def test_document_order_preserved(tmp_path):
    m = _load()
    docx_path = tmp_path / "proto.docx"
    _make_docx(docx_path)
    units = m.extract(docx_path)
    texts = [u["text"] for u in units]
    # заголовок раньше таблицы раньше финального CTA
    i_title = next(i for i, t in enumerate(texts) if "НЕЙРОКРЕАТОР" in t)
    i_table = next(i for i, t in enumerate(texts) if "211 990" in t)
    i_cta = next(i for i, t in enumerate(texts) if "Хочу на курс" in t)
    assert i_title < i_table < i_cta


def test_writes_txt_and_json(tmp_path):
    import subprocess
    import sys
    m = _load()
    docx_path = tmp_path / "proto.docx"
    _make_docx(docx_path)
    out = tmp_path / "extracted"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--source", str(docx_path), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    txt = out.with_suffix(".txt").read_text(encoding="utf-8")
    assert "211 990" in txt
    data = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert any(u["kind"] == "table" for u in data)
