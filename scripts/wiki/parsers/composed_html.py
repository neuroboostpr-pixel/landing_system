"""Парсит composed.html — извлекает блоки и ссылки на фото."""
import re
from pathlib import Path

from bs4 import BeautifulSoup


def parse(path: Path) -> dict:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    blocks = []
    for el in soup.find_all(attrs={"data-block": True}):
        blocks.append({
            "block_id": el["data-block"],
            "tag": el.name,
            "classes": el.get("class", []),
        })

    photo_references = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and not src.startswith(("http://", "https://", "data:")):
            photo_references.append(src)

    return {
        "blocks": blocks,
        "photo_references": photo_references,
    }
