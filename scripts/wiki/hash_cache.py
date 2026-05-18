"""SHA256-кэш source-файлов для пропуска неизменённых в compile."""
import hashlib
import json
from pathlib import Path
from typing import Any


def compute_hash(path: Path) -> str:
    """sha256 содержимого файла."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cache(cache_path: Path) -> dict[str, str]:
    """Читает JSON-кэш {relative_path: sha256}. Возвращает {} если файла нет."""
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache_path: Path, data: dict[str, str]) -> None:
    """Пишет JSON-кэш атомарно."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2, sort_keys=True))


def is_changed(path: Path, key: str, cache: dict[str, str]) -> bool:
    """True если файл новый или sha не совпадает с записью в кэше."""
    if key not in cache:
        return True
    return compute_hash(path) != cache[key]
