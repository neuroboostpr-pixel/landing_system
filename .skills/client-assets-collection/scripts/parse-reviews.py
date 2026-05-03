#!/usr/bin/env python3
"""Parse public reviews from Я.Карты / 2GIS / Otzovik / Flamp.

Free, no API keys: uses trafilatura (static) + Playwright (dynamic) under
the hood via tools.adapters.web_scraper.

CLI:  python3 parse-reviews.py <URL> <OUTPUT_DIR>
Lib:  from parse_reviews_mod import parse_reviews
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

# Make tools/ importable when invoked as script
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.adapters.web_scraper import (
    extract_static, extract_dynamic, ScrapeError
)
from tools.logger import info, error, success, warn


# Sources that need JS rendering (SPA, dynamic content)
DYNAMIC_HOSTS = ("yandex.ru/maps", "yandex.com/maps", "2gis.ru", "2gis.com")
# Sources that work with static extraction (server-rendered HTML)
STATIC_HOSTS = ("otzovik.com", "irecommend.ru", "flamp.ru", "yell.ru")


def detect_source(url: str) -> str:
    host = urlparse(url).hostname or ""
    if "yandex" in host:
        return "yandex-maps"
    if "2gis" in host:
        return "2gis"
    if "otzovik" in host:
        return "otzovik"
    if "flamp" in host:
        return "flamp"
    if "irecommend" in host:
        return "irecommend"
    if "yell" in host:
        return "yell"
    return "other"


def needs_dynamic(url: str) -> bool:
    return any(h in url for h in DYNAMIC_HOSTS)


_REVIEW_SPLIT = re.compile(r"\n\n+", re.MULTILINE)


def split_reviews(text: str) -> list:
    """Split a text blob into review-sized chunks.

    Reviews are typically separated by blank lines after trafilatura's
    cleanup. Filter chunks shorter than 20 chars (likely UI noise).
    """
    parts = _REVIEW_SPLIT.split(text or "")
    return [p.strip() for p in parts if len(p.strip()) >= 20]


def parse_reviews(url: str, out_dir: str,
                  wait_for: str = None) -> Dict[str, Any]:
    """Fetch URL, extract reviews, write JSON manifest. Return result dict.

    If url is a dynamic site (Я.Карты/2GIS), uses Playwright.
    Otherwise uses trafilatura.
    """
    info(f"Scraping {url}")
    if needs_dynamic(url):
        try:
            data = extract_dynamic(url, wait_for=wait_for)
        except ScrapeError as exc:
            warn(f"dynamic extract failed: {exc}; falling back to static")
            data = extract_static(url=url)
    else:
        data = extract_static(url=url)

    reviews = split_reviews(data.get("text", ""))
    source = detect_source(url)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    manifest = {
        "source": source,
        "url": url,
        "scraped_at": datetime.utcnow().isoformat(),
        "title": data.get("title", ""),
        "reviews": reviews,
        "review_count": len(reviews),
    }
    file_path = out / f"{source}-{timestamp}.json"
    file_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    success(f"Wrote {len(reviews)} reviews to {file_path}")
    return manifest


def main(argv: list) -> int:
    if len(argv) < 3:
        print("Usage: parse-reviews.py <URL> <OUTPUT_DIR>", file=sys.stderr)
        return 1
    url, out_dir = argv[1], argv[2]
    try:
        parse_reviews(url, out_dir)
        return 0
    except ScrapeError as exc:
        error(str(exc))
        error("Tip: if Я.Карты blocks the request, take a screenshot manually")
        error("and drop it into 02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/yandex-maps/")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
