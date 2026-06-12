#!/usr/bin/env python3
"""Единый источник списка этапов (E1). Читает config/stages.yaml.

Usage:
    python3 scripts/stages.py --order    # id по одному в строке
    python3 scripts/stages.py --labels   # id<TAB>label по одному в строке

Как библиотека:
    from scripts.stages import stage_ids, load_stages
"""
import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STAGES_YAML = ROOT / "config" / "stages.yaml"


def load_stages():
    data = yaml.safe_load(STAGES_YAML.read_text(encoding="utf-8"))
    return data["stages"]


def stage_ids():
    return [s["id"] for s in load_stages()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--order", action="store_true")
    group.add_argument("--labels", action="store_true")
    args = ap.parse_args()
    for s in load_stages():
        if args.labels:
            print(f"{s['id']}\t{s['label']}")
        else:
            print(s["id"])


if __name__ == "__main__":
    main()
