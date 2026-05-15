"""Парсит tokens.json (design tokens)."""
import json
from pathlib import Path


def parse(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
