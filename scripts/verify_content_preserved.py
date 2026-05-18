#!/usr/bin/env python3
"""Проверяет что текст из prototype.yaml присутствует в composed.html.

Exit codes:
  0 — все строки прототипа найдены, порядок блоков сохранён
  1 — есть расхождения (детали в stderr)
  2 — файл prototype.yaml или composed.html не найден
"""
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup


SKIP_KEYS = {"id", "type", "block_id", "class", "tag", "data-block"}
MIN_LEN = 3  # минимальная длина строки чтобы проверять (короткие — false positives)
PLACEHOLDER_MARKERS = ("____", "___", "TBD", "tbd")


def normalize(s: str) -> str:
    """Нормализует whitespace, сохраняет регистр."""
    return re.sub(r"\s+", " ", s).strip()


def is_placeholder(s: str) -> bool:
    return any(m in s for m in PLACEHOLDER_MARKERS)


def extract_yaml_strings(node) -> list[str]:
    """Рекурсивно собирает все строковые значения, кроме служебных."""
    if isinstance(node, str):
        s = node.strip()
        if len(s) >= MIN_LEN and not is_placeholder(s):
            return [s]
        return []
    if isinstance(node, list):
        out = []
        for item in node:
            out.extend(extract_yaml_strings(item))
        return out
    if isinstance(node, dict):
        out = []
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            out.extend(extract_yaml_strings(v))
        return out
    return []


def main(project_dir: Path) -> int:
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    composed_path = project_dir / "07b_COMPOSED" / "composed.html"

    if not proto_path.exists():
        print(f"ERROR: {proto_path} не найден", file=sys.stderr)
        return 2
    if not composed_path.exists():
        print(f"ERROR: {composed_path} не найден", file=sys.stderr)
        return 2

    proto_data = yaml.safe_load(proto_path.read_text(encoding="utf-8")) or {}
    html_raw = composed_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_raw, "html.parser")
    html_text = normalize(soup.get_text(separator=" "))

    # 1. Substring match для всех значимых строк
    blocks = proto_data.get("blocks", [])
    all_strings = extract_yaml_strings(blocks)
    missing = []
    for s in all_strings:
        norm = normalize(s)
        if norm and norm not in html_text:
            missing.append(norm[:100])

    # 2. Порядок блоков по data-block="<id>"
    proto_ids = [b.get("id") for b in blocks if isinstance(b, dict) and b.get("id")]
    html_ids_all = [el.get("data-block") for el in soup.find_all(attrs={"data-block": True})]
    html_ids = [b for b in html_ids_all if b in proto_ids]
    order_ok = True
    if proto_ids and html_ids:
        expected_order = [b for b in proto_ids if b in html_ids]
        if html_ids[: len(expected_order)] != expected_order:
            order_ok = False

    fail = bool(missing) or not order_ok

    if fail:
        if missing:
            print(
                f"❌ В composed.html не найдено {len(missing)} строк из prototype.yaml:",
                file=sys.stderr,
            )
            for m in missing[:10]:
                print(f"   - «{m}»", file=sys.stderr)
            if len(missing) > 10:
                print(f"   ... ещё {len(missing) - 10}", file=sys.stderr)
        if not order_ok:
            print("❌ Порядок блоков в composed.html отличается от prototype.yaml", file=sys.stderr)
            print(f"   Прототип: {proto_ids}", file=sys.stderr)
            print(f"   HTML:     {html_ids}", file=sys.stderr)
        return 1

    print(f"✅ Контент прототипа сохранён ({len(all_strings)} строк проверено)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_content_preserved.py <project-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
