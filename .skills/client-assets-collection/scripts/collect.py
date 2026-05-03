#!/usr/bin/env python3
"""Build assets manifest and HTML gallery from 02_МАТЕРИАЛЫ_КЛИЕНТА.

CLI: python3 collect.py <MATERIALS_DIR>
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.html.render import render
from tools.logger import info, success, warn


PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv"}


def build_manifest(materials_dir: Path) -> Dict[str, Any]:
    """Walk materials_dir and build a manifest of photos, videos, testimonials."""
    photos = []
    photos_dir = materials_dir / "photos" / "original"
    if photos_dir.exists():
        for p in sorted(photos_dir.iterdir()):
            if p.suffix.lower() in PHOTO_EXTS:
                photos.append({"filename": p.name, "path": str(p.relative_to(materials_dir)), "use": "unspecified"})

    videos = []
    videos_dir = materials_dir / "videos"
    if videos_dir.exists():
        for v in sorted(videos_dir.iterdir()):
            if v.suffix.lower() in VIDEO_EXTS:
                videos.append({"filename": v.name, "path": str(v.relative_to(materials_dir))})

    testimonials = []
    test_dir = materials_dir / "testimonials"
    if test_dir.exists():
        for src_dir in sorted(test_dir.iterdir()):
            if not src_dir.is_dir():
                continue
            for j in sorted(src_dir.glob("*.json")):
                try:
                    payload = json.loads(j.read_text(encoding="utf-8"))
                    testimonials.append({
                        "source": payload.get("source"),
                        "file": str(j.relative_to(materials_dir)),
                        "review_count": payload.get("review_count", 0)
                    })
                except Exception as exc:
                    warn(f"skipping malformed testimonial {j}: {exc}")
                    continue

    return {"photos": photos, "videos": videos, "testimonials": testimonials}


def render_gallery(materials_dir: Path) -> Path:
    """Render assets-gallery.html into materials_dir."""
    manifest = build_manifest(materials_dir)
    html = render("assets-gallery.html.j2", {"manifest": manifest})
    out = materials_dir / "assets-gallery.html"
    out.write_text(html, encoding="utf-8")
    return out


def run(materials_dir: str) -> None:
    """Build manifest and gallery; write both."""
    materials = Path(materials_dir)
    manifest = build_manifest(materials)
    yml_out = materials / "assets-manifest.yaml"
    yml_out.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    info(f"Wrote {yml_out}")
    html_out = render_gallery(materials)
    success(f"Wrote {html_out}")


def main(argv: list) -> int:
    if len(argv) < 2:
        print("Usage: collect.py <MATERIALS_DIR>", file=sys.stderr)
        return 1
    run(argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
