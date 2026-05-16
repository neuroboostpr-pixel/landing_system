#!/usr/bin/env python3
"""Full-page screenshot через playwright (desktop + mobile)."""
import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright не установлен. pip install playwright && playwright install chromium",
              file=sys.stderr)
        return 2

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, vp in [
            ("desktop", {"width": 1280, "height": 800}),
            ("mobile", {"width": 375, "height": 812}),
        ]:
            page = browser.new_page(viewport=vp)
            try:
                page.goto(args.url, timeout=60000, wait_until="domcontentloaded")
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass
            except Exception as e:
                print(f"WARN {name}: load incomplete ({e})", file=sys.stderr)
            page.screenshot(path=str(out_dir / f"{name}.png"), full_page=True)
            page.close()
        browser.close()
    print("OK Screenshots done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
