#!/usr/bin/env python3
"""Download fonts from CDN and cache them as WOFF2 files.

Reads recommended fonts from fonts.yaml (output of identify-fonts.py) and
downloads each via Bunny Fonts (free Google Fonts mirror).

CLI: python3 download-fonts.py <fonts-yaml> <output-dir>
"""
import argparse
import sys
from pathlib import Path
from typing import List
from urllib.parse import quote
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.adapters.font_downloader import download_woff2, FontDownloadError
from tools.logger import success, error, warn


def _bunny_woff2_url(family: str, weight: int = 400) -> str:
    """Build Bunny Fonts WOFF2 direct URL approximation.

    Note: Bunny Fonts serves via CSS. We request the CSS and get the
    woff2 URL from there. For simplicity we use the CSS URL as the
    download_woff2 target — the adapter handles the actual binary.
    """
    family_q = quote(family.replace(" ", "+"))
    return f"https://fonts.bunny.net/css?family={family_q}:{weight}"


def download_fonts(fonts_yaml: str, output_dir: str) -> List[Path]:
    """Read fonts.yaml candidates and download WOFF2 for each.

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
        url = _bunny_woff2_url(family)
        filename = family.lower().replace(" ", "-") + ".woff2"
        try:
            path = download_woff2(url, str(output_path), filename=filename)
            downloaded.append(path)
            success(f"Downloaded {family} -> {path}")
        except FontDownloadError as exc:
            warn(f"Skipped {family}: {exc}")

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
