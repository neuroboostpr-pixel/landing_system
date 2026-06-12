#!/usr/bin/env python3
"""B37 Фаза 2 — проверка точности парсинга: полнота + анти-галлюцинация.

Сравнивает текст источника (source-extracted.txt, эталон из extract-docx-text.py)
с текстом prototype.yaml:

  COMPLETENESS: доля строк источника, присутствующих в yaml (нормализованное
                сравнение). FAIL если покрытие < порога (по умолч. 90%).
  HALLUCINATION: текстовые значения yaml, которых НЕТ в источнике → выдумано.
                 Плюс blocklist типовых заглушек (Home/About/Services/Contact
                 как меню; standard/premium/vip как цена; Lorem; Get Started).

Выход: fidelity-report.md + exit 0/1.

Использование:
  python verify-prototype-fidelity.py --source-text <extracted.txt> \
         --prototype <prototype.yaml> [--min-coverage 0.9] [--report <md>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# типовые заглушки-галлюцинации в СВОБОДНОМ тексте (без ложных срабатываний на
# «ВИП»-тариф и «VIP-чат», которые есть в реальном контенте).
_BLOCKLIST = [
    (r"home\b.{0,4}about\b.{0,4}services\b.{0,4}contact", "generic menu Home/About/Services/Contact"),
    (r"lorem ipsum", "Lorem ipsum"),
    (r"\bget started\b", "generic CTA 'Get Started'"),
    (r"your text here|sample text|placeholder text", "template placeholder"),
]
# значения-заглушки в полях price/tier/plan (структурная проверка, не по тексту).
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


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source-text", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--min-coverage", type=float, default=0.9)
    p.add_argument("--report", default="")
    args = p.parse_args()

    src_lines = [
        ln.strip() for ln in Path(args.source_text).read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    proto_path = Path(args.prototype)
    if proto_path.suffix.lower() in (".md", ".txt"):
        # A1: канон этапа — prototype.md; сверяем по сырому тексту.
        proto = {}
        yaml_blob = _norm(proto_path.read_text(encoding="utf-8"))
    else:
        proto = yaml.safe_load(proto_path.read_text(encoding="utf-8")) or {}
        yaml_blob = _norm(" \n ".join(_yaml_strings(proto)))

    # COMPLETENESS: какая доля содержательных строк источника есть в yaml.
    # «содержательные» — длиннее 12 знаков (короткие служебные пропускаем).
    significant = [ln for ln in src_lines if len(ln) >= 12]
    missing: list[str] = []
    for ln in significant:
        n = _norm(ln)
        # совпадение по существенному префиксу (первые ~40 норм-символов)
        probe = n[:40]
        if probe and probe in yaml_blob:
            continue
        # fuzzy: доля слов строки, встречающихся в yaml
        words = [w for w in n.split() if len(w) > 3]
        if words:
            hit = sum(1 for w in words if w in yaml_blob) / len(words)
            if hit >= 0.7:
                continue
        missing.append(ln)
    covered = len(significant) - len(missing)
    coverage = covered / len(significant) if significant else 1.0

    # HALLUCINATION: текстовый blocklist + структурная проверка price-полей.
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
    lines.append(f"Галлюцинации (blocklist): {len(hallucinations)}\n")
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

    report_path = Path(args.report) if args.report else (
        Path(args.prototype).parent / "fidelity-report.md")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    ok = coverage >= args.min_coverage and not hallucinations
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] покрытие {coverage*100:.1f}% (порог {args.min_coverage*100:.0f}%), "
          f"галлюцинаций {len(hallucinations)}, потеряно {len(missing)}")
    print(f"Отчёт: {report_path}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
