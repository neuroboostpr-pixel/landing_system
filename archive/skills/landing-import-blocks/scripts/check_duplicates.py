"""Сигнатурная дедупликация блоков block-library."""
from __future__ import annotations
from pathlib import Path
import yaml


def compute_signature(block: dict) -> str:
    """Вычислить строковую сигнатуру блока.
    Формат: "{type}|{layout_pattern}|[slot1,slot2,...]|bg:{bool}"
    Слоты сортируются по имени для детерминизма.
    """
    block_type = block.get("type", "unknown")
    layout = block.get("layout_pattern", "unknown")
    slots = sorted(s["name"] for s in block.get("slots", []))
    has_bg = str(block.get("has_bg_image", False)).lower()
    return f"{block_type}|{layout}|[{','.join(slots)}]|bg:{has_bg}"


def load_existing_signatures(catalog_path: Path) -> dict[str, str]:
    """Загрузить существующие сигнатуры из catalog.yaml.
    Returns: {signature: block_id}
    """
    if not catalog_path.exists():
        return {}
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    result = {}
    for block in data.get("blocks", []):
        sig = block.get("signature")
        if sig:
            result[sig] = block.get("id", "unknown")
    return result


def find_duplicate(block: dict, catalog_path: Path) -> str | None:
    """Найти дубль по сигнатуре. Возвращает id существующего блока или None."""
    sig = compute_signature(block)
    existing = load_existing_signatures(catalog_path)
    return existing.get(sig)
