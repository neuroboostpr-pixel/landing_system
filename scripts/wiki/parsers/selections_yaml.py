"""Парсит selections.yaml (wireframe/photos)."""
from pathlib import Path
import yaml


def parse(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
