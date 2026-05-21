"""Fix page-content.html images for Lazy Blocks consumption.

After wp media import returns attachment IDs, this script:
1. Replaces __IMAGE_ATTACHMENT_ID__assets/photos/<fname>__ placeholders with real IDs
2. Replaces bare "assets/photos/X.jpg" strings (used in card sub-blocks) with attachment IDs
3. URL-encodes all image attribute objects {"id": N, "url": ""} → "%7B...%7D"
   (Lazy Blocks image control expects rawurlencoded JSON string, not raw object)

Usage:
    python fix-page-content-images.py <page-content.html> <photo-map.txt> [<output.html>]

photo-map.txt format (one per line): filename.jpg|attachment_id

If <output.html> omitted, modifies <page-content.html> in place.
"""
import re
import json
import sys
import urllib.parse
from pathlib import Path

# Image attribute keys to URL-encode (extend if block-spec adds new image controls)
IMAGE_ATTR_KEYS = ("hero_bg", "section_image", "model_image", "background", "side_image", "logo_image", "bg_image")


def load_photo_map(path: Path) -> dict[str, str]:
    """Load {filename.jpg: attachment_id} from pipe-separated file.

    If duplicate filenames (re-imports), keep highest ID (newest).
    """
    m: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        fname, att_id = line.split("|", 1)
        if fname not in m or int(att_id) > int(m[fname]):
            m[fname] = att_id
    return m


def transform(html: str, photo_map: dict[str, str]) -> tuple[str, dict[str, int]]:
    """Apply 3 transformations. Returns (html, stats)."""
    stats = {"placeholders": 0, "string_paths": 0, "image_objects": 0}

    # 1. __IMAGE_ATTACHMENT_ID__assets/photos/<fname>__ → <id>
    def repl_placeholder(m):
        return photo_map.get(m.group(1), "0")
    html, stats["placeholders"] = re.subn(
        r'__IMAGE_ATTACHMENT_ID__assets/photos/([^_]+\.jpg)__',
        repl_placeholder, html
    )

    # 2. "assets/photos/X.jpg" → "<id>"
    def repl_string(m):
        return f'"{photo_map.get(m.group(1), "0")}"'
    html, stats["string_paths"] = re.subn(
        r'"assets/photos/([^"]+\.jpg)"', repl_string, html
    )

    # 3. URL-encode image attribute objects
    keys_pattern = "|".join(IMAGE_ATTR_KEYS)

    def encode_image(m):
        key = m.group(1)
        obj_str = m.group(2)
        id_m = re.search(r'"id":\s*(\d+)', obj_str)
        url_m = re.search(r'"url":\s*"([^"]*)"', obj_str)
        obj = {}
        if id_m:
            obj["id"] = int(id_m.group(1))
        if url_m:
            obj["url"] = url_m.group(1)
        encoded = urllib.parse.quote(json.dumps(obj, ensure_ascii=False))
        return f'"{key}": "{encoded}"'

    html, stats["image_objects"] = re.subn(
        rf'"({keys_pattern})":\s*(\{{[^}}]+\}})',
        encode_image, html
    )

    return html, stats


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("Usage: fix-page-content-images.py <page-content.html> <photo-map.txt> [<output.html>]",
              file=sys.stderr)
        return 1

    src = Path(argv[1])
    photo_map_path = Path(argv[2])
    dst = Path(argv[3]) if len(argv) > 3 else src

    if not src.exists():
        print(f"ERROR: src not found: {src}", file=sys.stderr)
        return 2
    if not photo_map_path.exists():
        print(f"ERROR: photo map not found: {photo_map_path}", file=sys.stderr)
        return 2

    html = src.read_text(encoding="utf-8")
    photo_map = load_photo_map(photo_map_path)
    print(f"Loaded {len(photo_map)} photo mappings from {photo_map_path}")

    html, stats = transform(html, photo_map)
    print(f"Placeholders → IDs:        {stats['placeholders']}")
    print(f"String paths → IDs:        {stats['string_paths']}")
    print(f"Image objects URL-encoded: {stats['image_objects']}")

    dst.write_text(html, encoding="utf-8")
    print(f"Saved: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
