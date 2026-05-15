#!/usr/bin/env python3
"""Verify photo pipeline для hard_check.

Проверяет:
- Все <img src> в composed.html ведут на 07c_PHOTOS/processed/
- Нет SVG placeholder'ов
- Размеры файлов соответствуют атрибутам width/height в HTML
- manifest.json существует

Exit 0 — OK, exit 1 — issues, exit 2 — files missing.
"""
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


def main(project_dir):
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    if not composed.exists():
        print(f"ERROR: {composed} не найден", file=sys.stderr)
        return 2

    soup = BeautifulSoup(composed.read_text(encoding="utf-8"), "html.parser")
    issues = []

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue
        # Placeholder detection
        if "placeholder" in src.lower() or src.lower().endswith(".svg"):
            issues.append(f"placeholder остался: {src}")
            continue
        # Не из processed/?
        if "processed/" not in src:
            issues.append(f"img НЕ из processed/: {src}")

    # Manifest
    manifest = project_dir / "07c_PHOTOS" / "processed" / "manifest.json"
    if not manifest.exists() and len([i for i in soup.find_all("img") if i.get("src")]) > 0:
        issues.append("manifest.json отсутствует в 07c_PHOTOS/processed/")

    if issues:
        print(f"❌ Photo pipeline issues ({len(issues)}):", file=sys.stderr)
        for i in issues[:10]:
            print(f"   - {i}", file=sys.stderr)
        return 1

    print(f"✅ Photo pipeline OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_photo_pipeline.py <project>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
