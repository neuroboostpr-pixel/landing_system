# scripts/wiki/utils.py
"""Утилиты для wiki: slug, frontmatter, atomic write."""
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

# Карта транслитерации кириллицы (упрощённая, для slug).
CYRILLIC_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str) -> str:
    """Превращает строку в kebab-case slug. Поддерживает кириллицу."""
    text = text.lower()
    text = "".join(CYRILLIC_MAP.get(ch, ch) for ch in text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Извлекает YAML frontmatter из markdown.

    Returns:
        (metadata, body). Если frontmatter нет — metadata={}, body=весь текст.
    """
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text
    return meta, parts[2]


def parse_frontmatter_full(text: str) -> dict[str, Any]:
    """Извлекает полный YAML frontmatter как dict без отделения body.

    Returns:
        dict с полным набором полей. Если frontmatter нет или повреждён — {}.
    """
    meta, _ = parse_frontmatter(text)
    return meta


def write_with_frontmatter(
    path: Path, metadata: dict[str, Any], body: str
) -> None:
    """Атомарно пишет markdown с frontmatter."""
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
    content = f"---\n{fm}---\n{body}"
    atomic_write(path, content)


def atomic_write(path: Path, content: str) -> None:
    """Атомарная запись через временный файл + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
