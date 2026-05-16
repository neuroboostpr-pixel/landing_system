#!/usr/bin/env python3
"""Извлекает регион/гео-локацию проекта из market-profile.md.

Использование:
  detect-region.py <project>

Output (stdout):
  <region-string> например "Dubai, UAE" или "Moscow"

Если не найдено → "global".
"""
import re
import sys
from pathlib import Path


PATTERNS = [
    r"(?:^|\n)\s*\*\*Geo:?\*\*:?\s*([^\n]+)",
    r"(?:^|\n)\s*\*\*Region:?\*\*:?\s*([^\n]+)",
    r"(?:^|\n)\s*\*\*Location:?\*\*:?\s*([^\n]+)",
    r"(?:^|\n)\s*-\s*Geo:?\s*([^\n]+)",
    r"(?:^|\n)\s*Geo:?\s*([^\n]+)",
    r"(?:^|\n)\s*Region:?\s*([^\n]+)",
    r"(?:^|\n)\s*Location:?\s*([^\n]+)",
]


def detect(project_dir: Path) -> str:
    candidates = [
        project_dir / "01a_АНАЛИЗ_НИШИ" / "market-profile.md",
        project_dir / "00_БРИФ" / "brief.md",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pat in PATTERNS:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1).strip(" *|.,")
    return "global"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: detect-region.py <project>", file=sys.stderr)
        sys.exit(2)
    print(detect(Path(sys.argv[1])))
