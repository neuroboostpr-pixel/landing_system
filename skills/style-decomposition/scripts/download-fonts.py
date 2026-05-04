#!/usr/bin/env python3
"""Download fonts from CDN and cache them as WOFF2 files.

Reads recommended fonts from fonts.yaml (output of identify-fonts.py) and
downloads each via Bunny Fonts (free Google Fonts mirror).

CLI: python3 download-fonts.py <fonts-yaml> <output-dir>
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List
import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.adapters.font_downloader import FontDownloadError
from tools.logger import success, error, warn


def _bunny_woff2_url(family: str, weight: int = 400) -> str:
    """Build Bunny Fonts CSS URL for a given family and weight.

    Returns the CSS URL — callers must fetch the CSS and parse woff2 URLs
    from it (two-step download).
    """
    family_q = family.replace(" ", "+")
    return f"https://fonts.bunny.net/css?family={family_q}:{weight}"


def download_fonts(fonts_yaml: str, output_dir: str) -> List[Path]:
    """Read fonts.yaml candidates and download WOFF2 for each.

    Two-step process per font:
    1. Fetch CSS from Bunny Fonts CDN.
    2. Parse all woff2 URLs from the CSS with a regex.
    3. Fetch each binary and validate the wOF2 magic bytes.

    Args:
        fonts_yaml: path to fonts.yaml produced by identify-fonts.py
        output_dir: directory to save downloaded WOFF2 files

    Returns list of Path objects for successfully downloaded files.
    """
    data = yaml.safe_load(Path(fonts_yaml).read_text(encoding="utf-8"))
    candidates = data.get("candidates", [])
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    downloaded: List[Path] = []
    for candidate in candidates:
        family = candidate["family"]
        css_url = _bunny_woff2_url(family)

        # Step 1: fetch CSS
        try:
            css_resp = requests.get(css_url, timeout=30)
        except requests.RequestException as exc:
            warn(f"Skipped {family}: network error fetching CSS: {exc}")
            continue
        if css_resp.status_code != 200:
            warn(f"Skipped {family}: CSS HTTP {css_resp.status_code}")
            continue

        css_text = css_resp.text

        # Step 2: parse woff2 URLs from CSS
        woff2_urls = re.findall(
            r'url\(["\']?(https?://[^"\')\s]+\.woff2)["\']?\)',
            css_text,
        )
        if not woff2_urls:
            warn(f"Skipped {family}: no woff2 URLs found in CSS")
            continue

        # Step 3: download each woff2 binary and validate magic bytes
        for woff2_url in woff2_urls:
            fname = family.lower().replace(" ", "-") + ".woff2"
            out_path = output_path / fname
            try:
                bin_resp = requests.get(woff2_url, timeout=30)
            except requests.RequestException as exc:
                warn(f"Skipped {family} ({woff2_url}): {exc}")
                continue
            if bin_resp.status_code != 200:
                warn(f"Skipped {family}: binary HTTP {bin_resp.status_code}")
                continue

            content = bin_resp.content
            # Validate magic bytes: first 4 bytes must be b"wOF2"
            if content[:4] != b"wOF2":
                warn(f"Skipped {family}: invalid WOFF2 magic bytes in {woff2_url}")
                if out_path.exists():
                    out_path.unlink()
                continue

            out_path.write_bytes(content)
            downloaded.append(out_path)
            success(f"Downloaded {family} -> {out_path}")
            break  # one file per family is enough

    return downloaded


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("fonts_yaml")
    p.add_argument("output_dir")
    args = p.parse_args(argv[1:])
    try:
        paths = download_fonts(args.fonts_yaml, args.output_dir)
        success(f"Downloaded {len(paths)} font(s)")
        return 0
    except Exception as exc:
        error(f"font download failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
