"""Чистые функции для block-library cleanup: дедуп, нумерация, план перемещений."""
from __future__ import annotations


def group_duplicates(blocks: list[dict]) -> dict[str, list[dict]]:
    """Сгруппировать блоки по signature. Вернуть только группы с >1 блоком."""
    by_sig: dict[str, list[dict]] = {}
    for b in blocks:
        sig = b.get("signature", "")
        by_sig.setdefault(sig, []).append(b)
    return {sig: lst for sig, lst in by_sig.items() if len(lst) > 1}


def _sort_key(block: dict) -> tuple:
    """ru-* блоки идут первыми (приоритет ручным), потом по old_id."""
    old_id = block.get("old_id", "")
    is_ru = 0 if old_id.startswith("ru-") else 1
    return (is_ru, old_id)


def renumber(blocks: list[dict]) -> dict[str, str]:
    """Сквозная нумерация по типу: type-001, type-002. ru-* первыми.
    Returns: {old_id: new_id}
    """
    by_type: dict[str, list[dict]] = {}
    for b in blocks:
        by_type.setdefault(b["type"], []).append(b)
    mapping: dict[str, str] = {}
    for block_type, lst in by_type.items():
        for i, b in enumerate(sorted(lst, key=_sort_key), start=1):
            mapping[b["old_id"]] = f"{block_type}-{i:03d}"
    return mapping


def build_new_structure(blocks: list[dict], keep_list: dict) -> list[dict]:
    """План перемещений для оставшихся (не removed, не needs_manual) блоков.
    Returns: list of {old_id, new_id, old_path, new_path}
    """
    removed = set(keep_list.get("removed", []))
    survivors = [
        b for b in blocks
        if b["old_id"] not in removed and b.get("status") != "needs_manual"
    ]
    mapping = renumber(survivors)
    actions = []
    for b in survivors:
        new_id = mapping[b["old_id"]]
        actions.append({
            "old_id": b["old_id"],
            "new_id": new_id,
            "old_path": b["old_path"],
            "new_path": f"{b['category']}/{new_id}",
        })
    return actions
