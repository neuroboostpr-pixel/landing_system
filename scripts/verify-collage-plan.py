#!/usr/bin/env python3
"""Гейт «анализ блоков для коллажа» для 07c (reference-driven §3.4).

§3.4 требует: перед вёрсткой агент проходит по КАЖДОМУ блоку и решает —
где пусто/плоско → какой визуальный приём это закрывает. Это обязательный
артефакт collage-plan.md, а не «в голове».

Контракт 07b_COMPOSED/collage-plan.md:
  - строка-вердикт `COLLAGE_PLAN: READY` в конце;
  - содержательная таблица/строки по блокам (>= N блоков покрыто): для каждого
    блока указаны «потребность места» и «приём» (см. каталог §3.4);
  - не заглушка (минимальная длина).

Кол-во разобранных блоков должно совпадать с числом блоков прототипа (±0):
сверяем с prototype.yaml/prototype.md.

Exit 0 — OK; 1 — нет плана/заглушка/неполно; 2 — файлы не найдены.
Usage: verify-collage-plan.py <project-dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


def _proto_block_count(project_dir: Path) -> int:
    y = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if y.exists():
        data = yaml.safe_load(y.read_text(encoding="utf-8")) or {}
        blocks = data.get("blocks")
        if isinstance(blocks, list):
            return len(blocks)
    md = project_dir / "07_ПРОТОТИП" / "prototype.md"
    if md.exists():
        return len(re.findall(r"^##\s+Block\s+\d+", md.read_text(encoding="utf-8"),
                              re.MULTILINE))
    return 0


def main(project_dir: Path) -> int:
    plan = project_dir / "07b_COMPOSED" / "collage-plan.md"
    if not plan.exists():
        print(f"FAIL: нет {plan}. Перед вёрсткой агент пишет collage-plan.md: "
              "по каждому блоку — потребность места → визуальный приём (§3.4).",
              file=sys.stderr)
        return 1

    text = plan.read_text(encoding="utf-8")
    if len(text.strip()) < 200:
        print("FAIL: collage-plan.md — заглушка (слишком короткий).", file=sys.stderr)
        return 1

    m = re.search(r"COLLAGE_PLAN:\s*(READY|DRAFT)", text, re.IGNORECASE)
    if not m:
        print("FAIL: в collage-plan.md нет вердикта `COLLAGE_PLAN: READY`.",
              file=sys.stderr)
        return 1
    if m.group(1).upper() != "READY":
        print("FAIL: COLLAGE_PLAN: DRAFT — план не готов.", file=sys.stderr)
        return 1

    # Содержательность: упоминаются приёмы коллажа
    devices = ["подложк", "блоб", "цифр", "якор", "вырезан", "разделит",
               "слой", "свечени", "форм", "иконк", "градиент"]
    hits = sum(1 for d in devices if d.lower() in text.lower())
    if hits < 3:
        print(f"FAIL: collage-plan.md не описывает приёмы коллажа "
              f"(найдено {hits} упоминаний из каталога §3.4).", file=sys.stderr)
        return 1

    # Покрытие блоков: считаем строки «блок»/«block»
    n_proto = _proto_block_count(project_dir)
    n_plan = len(re.findall(r"(?im)^\s*(?:\|\s*)?(?:блок|block)\s*\d", text))
    if n_proto and n_plan < n_proto:
        print(f"FAIL: разобрано блоков в плане {n_plan} < блоков прототипа {n_proto}. "
              "Нужен анализ КАЖДОГО блока.", file=sys.stderr)
        return 1

    print(f"✅ collage-plan.md готов (приёмов {hits}, блоков разобрано {n_plan}/"
          f"{n_proto or '?'}, вердикт READY).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify-collage-plan.py <project-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
