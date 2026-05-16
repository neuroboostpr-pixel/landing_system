#!/usr/bin/env python3
"""Делает desktop+mobile скриншоты HTML-файла через Playwright.

Использование:
  take-screenshots.py <html-file> --out <dir>

Output:
  <dir>/desktop.png  (1280×800)
  <dir>/mobile.png   (375×812)
"""
import argparse
import sys
from pathlib import Path


VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "mobile": {"width": 375, "height": 812},
}


def take_screenshots(html_path: Path, out_dir: Path) -> dict[str, Path]:
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    url = f"file://{html_path.resolve()}"
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, viewport in VIEWPORTS.items():
            page = browser.new_page(viewport=viewport)
            page.goto(url)
            page.wait_for_load_state("networkidle", timeout=30000)
            screenshot_path = out_dir / f"{name}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            results[name] = screenshot_path
            page.close()
        browser.close()

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_file", help="Path to composed.html")
    parser.add_argument("--out", required=True, help="Output directory for PNGs")
    args = parser.parse_args()

    html_path = Path(args.html_file)
    out_dir = Path(args.out)

    if not html_path.exists():
        print(f"ERROR: {html_path} не найден", file=sys.stderr)
        return 2

    try:
        results = take_screenshots(html_path, out_dir)
    except Exception as e:
        print(f"ERROR: Playwright failed: {e}", file=sys.stderr)
        return 3

    for name, path in results.items():
        size_kb = path.stat().st_size // 1024
        print(f"✅ {name}: {path} ({size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
