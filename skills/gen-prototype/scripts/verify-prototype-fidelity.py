#!/usr/bin/env python3
"""gen-prototype — проверка точности парсинга: полнота + анти-галлюцинация
+ структурные ассерты (счётчик блоков, ровно один active).

Сравнивает текст источника (extracted.txt из extract-docx-text.py / текстовый
слой PDF / .txt прототип) с текстом prototype-NN.yaml:

  COMPLETENESS: доля строк источника, присутствующих в yaml (нормализованное
                сравнение). FAIL если покрытие < порога (по умолч. 90%).
                client_notes/block_instructions ТОЖЕ считаются покрытием —
                дизайн-комментарии, хранимые там дословно, не «теряются».
  HALLUCINATION: blocklist типовых заглушек (Home/About/Services/Contact,
                 Lorem, Get Started, abstract price standard/premium/vip).
  STRUCTURE (#7/#8): meta.blocks == len(blocks); при --folder — ровно один
                 yaml с meta.active: true во всей папке прототипов.

Отчёт по умолчанию пишется во ВРЕМЕННУЮ папку (tempfile.gettempdir()), НЕ в
проект (правило скила «не плодить промежуточные файлы»). Переопределить — --report.

Использование:
  python verify-prototype-fidelity.py --source-text <extracted.txt> \
         --prototype <prototype-NN.yaml> [--min-coverage 0.9] [--report <md>] \
         [--folder <07_ПРОТОТИП/>]
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

import yaml

# типовые заглушки-галлюцинации в СВОБОДНОМ тексте.
_BLOCKLIST = [
    (r"home\b.{0,4}about\b.{0,4}services\b.{0,4}contact", "generic menu Home/About/Services/Contact"),
    (r"lorem ipsum", "Lorem ipsum"),
    (r"\bget started\b", "generic CTA 'Get Started'"),
    (r"your text here|sample text|placeholder text", "template placeholder"),
]
_FAKE_PRICE_VALUES = {"standard", "premium", "vip", "basic", "pro", "free"}


def _norm(s: str) -> str:
    """Нормализовать строку для сравнения: lower, схлопнуть пробелы/пунктуацию."""
    s = s.lower()
    s = re.sub(r"[«»\"'`(),.:;!?—–\-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _yaml_strings(node) -> list[str]:
    """Все строковые значения yaml (рекурсивно)."""
    out: list[str] = []
    if isinstance(node, dict):
        for v in node.values():
            out += _yaml_strings(v)
    elif isinstance(node, list):
        for v in node:
            out += _yaml_strings(v)
    elif isinstance(node, str):
        out.append(node)
    return out


def _count_active(folder: Path) -> tuple[int, list[str]]:
    """Сколько yaml в папке имеют meta.active: true. Вернуть (count, имена)."""
    actives: list[str] = []
    for f in sorted(folder.glob("prototype-*.yaml")):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if (d.get("meta") or {}).get("active") is True:
            actives.append(f.name)
    return len(actives), actives


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source-text", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--min-coverage", type=float, default=0.9)
    p.add_argument("--report", default="")
    p.add_argument("--folder", default="",
                   help="папка прототипов для проверки 'ровно один active' (#8)")
    args = p.parse_args()

    src_lines = [
        ln.strip() for ln in Path(args.source_text).read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    proto_path = Path(args.prototype)
    structural_errors: list[str] = []

    if proto_path.suffix.lower() in (".md", ".txt"):
        proto = {}
        yaml_blob = _norm(proto_path.read_text(encoding="utf-8"))
    else:
        proto = yaml.safe_load(proto_path.read_text(encoding="utf-8")) or {}
        yaml_blob = _norm(" \n ".join(_yaml_strings(proto)))

        # #7: meta.blocks == len(blocks)
        meta = proto.get("meta") or {}
        declared = meta.get("blocks")
        actual = len(proto.get("blocks") or [])
        if declared is not None and declared != actual:
            structural_errors.append(
                f"meta.blocks={declared}, но фактических блоков {actual} (#7)")

    # #8: ровно один active в папке
    folder = Path(args.folder) if args.folder else proto_path.parent
    if folder.is_dir():
        n_active, names = _count_active(folder)
        if n_active != 1:
            structural_errors.append(
                f"в папке active=true у {n_active} файлов {names} — должен быть РОВНО один (#8)")

    # COMPLETENESS
    significant = [ln for ln in src_lines if len(ln) >= 12]
    missing: list[str] = []
    for ln in significant:
        n = _norm(ln)
        probe = n[:40]
        if probe and probe in yaml_blob:
            continue
        words = [w for w in n.split() if len(w) > 3]
        if words:
            hit = sum(1 for w in words if w in yaml_blob) / len(words)
            if hit >= 0.7:
                continue
        missing.append(ln)
    covered = len(significant) - len(missing)
    coverage = covered / len(significant) if significant else 1.0

    # HALLUCINATION
    hallucinations: list[str] = []
    for pat, desc in _BLOCKLIST:
        if re.search(pat, yaml_blob, re.IGNORECASE):
            hallucinations.append(desc)

    def _check_price_fields(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k).lower() in ("price", "tier", "plan") and isinstance(v, str):
                    if v.strip().lower() in _FAKE_PRICE_VALUES:
                        hallucinations.append(f"abstract {k}='{v}' (нет реальной цены)")
                _check_price_fields(v)
        elif isinstance(node, list):
            for v in node:
                _check_price_fields(v)
    _check_price_fields(proto)

    # отчёт
    lines = ["# Fidelity-отчёт парсинга прототипа\n"]
    lines.append(f"Покрытие источника: **{coverage*100:.1f}%** "
                 f"({covered}/{len(significant)} значимых строк), порог {args.min_coverage*100:.0f}%")
    lines.append(f"Галлюцинации (blocklist): {len(hallucinations)}")
    lines.append(f"Структурные ошибки: {len(structural_errors)}\n")
    if structural_errors:
        lines.append("## ❌ Структура")
        for e in structural_errors:
            lines.append(f"- {e}")
        lines.append("")
    if hallucinations:
        lines.append("## ❌ Выдуманные паттерны")
        for h in hallucinations:
            lines.append(f"- {h}")
        lines.append("")
    if missing:
        lines.append(f"## ⚠️ Потеряно из источника ({len(missing)})")
        for ln in missing[:40]:
            lines.append(f"- {ln[:120]}")
        if len(missing) > 40:
            lines.append(f"- … ещё {len(missing) - 40}")
        lines.append("")

    # #1: по умолчанию — во временную папку, НЕ в проект.
    report_path = Path(args.report) if args.report else (
        Path(tempfile.gettempdir()) / f"fidelity-report-{proto_path.stem}.md")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    ok = (coverage >= args.min_coverage
          and not hallucinations
          and not structural_errors)
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] покрытие {coverage*100:.1f}% (порог {args.min_coverage*100:.0f}%), "
          f"галлюцинаций {len(hallucinations)}, потеряно {len(missing)}, "
          f"структурных ошибок {len(structural_errors)}")
    print(f"Отчёт (temp): {report_path}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
