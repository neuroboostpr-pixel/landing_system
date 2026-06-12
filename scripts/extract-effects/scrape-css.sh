#!/usr/bin/env bash
# scripts/extract-effects/scrape-css.sh — скачивает HTML+CSS живого сайта.
#
# Usage: scrape-css.sh <url> <out-dir>
# Создаёт в <out-dir>:
#   page.html        — исходный HTML
#   inline.css       — все inline <style>...</style>
#   link-N.css       — каждый внешний stylesheet
set -uo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/python-cmd.sh
. "$__SCRIPT_DIR__/../lib/python-cmd.sh"
URL="${1:?ERROR: URL required}"
OUT_DIR="${2:?ERROR: out dir required}"

mkdir -p "$OUT_DIR"

# 1. Скачиваем HTML (с user-agent чтобы не блокировали)
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    "$URL" -o "$OUT_DIR/page.html"

# 2. Извлекаем все <link rel="stylesheet" href="..."> + inline <style>
URL="$URL" OUT_DIR="$OUT_DIR" $PYTHON_CMD << 'PY'
from pathlib import Path
from urllib.parse import urljoin
import re, os, subprocess

out_dir = Path(os.environ["OUT_DIR"])
base_url = os.environ["URL"].strip()
html = (out_dir / "page.html").read_text(encoding="utf-8", errors="ignore")

# Найти все CSS-ссылки
links = re.findall(
    r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
    html, re.IGNORECASE,
)
inline_styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)

(out_dir / "inline.css").write_text("\n\n".join(inline_styles), encoding="utf-8")
print(f"  inline.css: {len(inline_styles)} <style> tags")

for i, link in enumerate(links):
    full = urljoin(base_url, link)
    try:
        result = subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0", full],
            capture_output=True, text=True, timeout=30,
        )
        (out_dir / f"link-{i}.css").write_text(result.stdout, encoding="utf-8")
    except Exception as e:
        print(f"  ⚠ link-{i} ({link}): {e}")
print(f"  external CSS files: {len(links)}")
PY

echo "✅ Scraped: $OUT_DIR"
