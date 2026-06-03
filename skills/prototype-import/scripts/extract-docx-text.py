#!/usr/bin/env python3
"""B37 Фаза 0 — детерминированный экстрактор текста из .docx.

Извлекает ВЕСЬ текст прототипа в порядке документа: параграфы (со стилем) И
таблицы (по строкам/ячейкам) — обходя тело документа последовательно, чтобы
ничего не терялось (тарифы клиента лежат в таблицах, которые d.paragraphs не
видит).

Выход:
  <out>.txt   — весь текст построчно (эталон полноты для fidelity-проверки)
  <out>.json  — структурные единицы [{kind, style, text, ...}] в порядке док-та

Использование:
  python extract-docx-text.py --source <prototype.docx> --out <dir>/source-extracted
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import docx
from docx.document import Document as _Doc
from docx.table import Table
from docx.text.paragraph import Paragraph


def _iter_block_items(parent):
    """Итерировать параграфы и таблицы в порядке появления в документе."""
    if isinstance(parent, _Doc):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._tc  # ячейка таблицы
    for child in parent_elm.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def extract(doc_path: Path) -> list[dict]:
    """Вернуть список структурных единиц в порядке документа."""
    doc = docx.Document(str(doc_path))
    units: list[dict] = []
    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            units.append({
                "kind": "paragraph",
                "style": block.style.name if block.style else "",
                "text": text,
            })
        elif isinstance(block, Table):
            rows = []
            for row in block.rows:
                cells = [c.text.strip() for c in row.cells]
                rows.append(cells)
            # текст таблицы — все непустые ячейки (с дедупом подряд идущих,
            # т.к. merged-ячейки повторяют текст)
            flat: list[str] = []
            for r in rows:
                prev = None
                for c in r:
                    if c and c != prev:
                        flat.append(c)
                    prev = c
            units.append({
                "kind": "table",
                "rows": rows,
                "text": "\n".join(flat),
            })
    return units


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="путь к prototype.docx")
    p.add_argument("--out", required=True, help="префикс выходных файлов (без расш.)")
    args = p.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"ERROR: нет файла {src}", file=sys.stderr)
        sys.exit(1)

    units = extract(src)

    # .txt — весь текст построчно
    lines: list[str] = []
    for u in units:
        for ln in u["text"].splitlines():
            ln = ln.strip()
            if ln:
                lines.append(ln)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    out.with_suffix(".json").write_text(
        json.dumps(units, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    n_para = sum(1 for u in units if u["kind"] == "paragraph")
    n_tbl = sum(1 for u in units if u["kind"] == "table")
    total_chars = sum(len(u["text"]) for u in units)
    print(f"Извлечено: {len(lines)} строк, {n_para} параграфов, {n_tbl} таблиц, "
          f"{total_chars} знаков → {out.with_suffix('.txt').name}, {out.with_suffix('.json').name}")


if __name__ == "__main__":
    main()
