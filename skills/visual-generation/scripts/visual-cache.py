#!/usr/bin/env python3
"""Hash-based skip-if-exists cache for visual generation.

Pattern from nexu-io/open-design imagegen.ts: cache by hash(hint+style+brand_color+niche);
skip codex call if cache exists (unless FORCE=1).
"""
import hashlib
import shutil
from pathlib import Path
from typing import Optional


MIN_CACHE_FILE_SIZE = 1024  # 1 KB — anything smaller is considered damaged


def cache_key(hint: str, style: str, brand_color: str, niche: str = "") -> str:
    """Deterministic 16-char hex key from inputs."""
    canonical = f"{hint}|{style}|{brand_color}|{niche}".lower().strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def lookup_cache(cache_dir: Path, key: str) -> Optional[Path]:
    """Return cache file if exists and not damaged, else None."""
    cache_dir = Path(cache_dir)
    candidate = cache_dir / f"{key}.png"
    if not candidate.exists():
        return None
    if candidate.stat().st_size < MIN_CACHE_FILE_SIZE:
        return None
    return candidate


def save_to_cache(cache_dir: Path, key: str, source_png: Path) -> Path:
    """Copy source_png into cache_dir/{key}.png. Returns cached path."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f"{key}.png"
    shutil.copyfile(source_png, dest)
    return dest


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--hint", required=True)
    ap.add_argument("--style", required=True)
    ap.add_argument("--brand-color", required=True)
    ap.add_argument("--niche", default="")
    args = ap.parse_args()
    print(cache_key(args.hint, args.style, args.brand_color, args.niche))


if __name__ == "__main__":
    main()
