"""Download fonts from CDN (Google Fonts via Bunny, Fontshare).

Bunny Fonts is GDPR/RU-friendly mirror of Google Fonts.
"""
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote
import requests


class FontDownloadError(RuntimeError):
    pass


def google_fonts_css_url(family: str, weights: List[int]) -> str:
    """Build a Bunny Fonts CSS URL for a Google font."""
    family_q = quote(family.replace(" ", "+"))
    weights_str = ";".join(str(w) for w in sorted(weights))
    return f"https://fonts.bunny.net/css?family={family_q}:wght@{weights_str}"


def fontshare_css_url(slug: str, weights: List[int]) -> str:
    """Build a Fontshare CSS URL. slug is the URL-safe family name."""
    weights_str = ",".join(str(w) for w in sorted(weights))
    return f"https://api.fontshare.com/v2/css?f[]={slug}@{weights_str}"


def download_woff2(url: str, target_dir: str, filename: Optional[str] = None) -> Path:
    """Fetch a WOFF2 file from URL into target_dir.

    Returns Path to downloaded file. Raises FontDownloadError on failure.
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        raise FontDownloadError(f"network: {exc}") from exc
    if resp.status_code != 200:
        raise FontDownloadError(f"HTTP {resp.status_code}")
    out_name = filename or url.split("/")[-1].split("?")[0]
    if not out_name.endswith(".woff2"):
        out_name += ".woff2"
    out_path = target / out_name
    out_path.write_bytes(resp.content)
    return out_path
