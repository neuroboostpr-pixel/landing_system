"""Fix page-content.html assets for Lazy Blocks consumption.

After `wp media import` returns attachment IDs, this script normalises every
asset attribute in page-content.html so Lazy Blocks (LZB) controls receive the
exact wire-format they expect. Three asset families are handled:

1. **Raster images** (image control): photo placeholders / string paths get
   replaced with attachment IDs, and the resulting `{"id": N, "url": ""}`
   object is `rawurlencoded` because LZB image controls store the value as a
   URL-encoded JSON string, not a raw JSON object.

2. **Raw SVG / inline HTML** (textarea control): keys like `icon_svg`,
   `svg`, `background_svg` carry raw `<svg…>` markup which contains quotes and
   `{}` that break Gutenberg's block-attribute JSON parser. We `rawurlencode`
   them so they survive the round-trip; the block.php template must
   `urldecode()` before echoing through `wp_kses`.

3. **Favicons & site icons**: same treatment as raster images (object with
   `id` + `url` → URL-encoded). The keys `favicon`, `site_icon`, `logo`,
   `logo_image` are recognised by default.

Usage:
    python fix-page-content-images.py <page-content.html> <photo-map.txt> [<output.html>]

photo-map.txt format (one per line): filename.<ext>|attachment_id
Supported extensions: jpg/jpeg/png/webp/svg/ico (extend ASSET_FILE_EXTS below).

If <output.html> omitted, modifies <page-content.html> in place.

Contract: this script is the single source of truth for the
HTML → LZB attribute transformation. Block templates (block.php) and
generators (generate-page-content.py) must agree on the keys listed below.
See docs/asset-pipeline.md for the full contract.
"""
import re
import json
import sys
import urllib.parse
from pathlib import Path

# Image-object attribute keys (raster + raw assets uploaded via wp media import).
# LZB image control wire format: rawurlencode(json.dumps({"id": N, "url": ""})).
IMAGE_ATTR_KEYS = (
    # raster / hero / decorative
    "hero_bg", "section_image", "model_image", "background", "side_image",
    "bg_image", "card_image", "thumbnail", "gallery_image",
    # brand identity
    "logo", "logo_image", "favicon", "site_icon",
)

# Raw-HTML / SVG attribute keys (textarea control). Stored as URL-encoded
# string; block.php must `urldecode($attributes[$key])` before `wp_kses`.
SVG_ATTR_KEYS = (
    "icon_svg", "svg", "background_svg", "decoration_svg", "logo_svg",
)

# File extensions recognised in photo-map and string-path replacement.
ASSET_FILE_EXTS = ("jpg", "jpeg", "png", "webp", "svg", "ico", "gif", "avif")


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
    """Apply asset transformations. Returns (html, stats)."""
    stats = {
        "placeholders": 0,
        "string_paths": 0,
        "image_objects": 0,
        "svg_attrs": 0,
    }

    ext_alt = "|".join(ASSET_FILE_EXTS)

    # 1. __IMAGE_ATTACHMENT_ID__<path>/<fname>__ → <id>
    #    Префикс (assets/photos/, ../images/, или вовсе без него) и подчёркивания
    #    в имени файла допускаются: ключ photo_map — basename (см. §4.2 «битые
    #    картинки / плейсхолдеры не заменились»).
    def repl_placeholder(m):
        raw = m.group(1)
        base = raw.rsplit("/", 1)[-1]
        return photo_map.get(base, photo_map.get(raw, "0"))
    html, stats["placeholders"] = re.subn(
        rf'__IMAGE_ATTACHMENT_ID__(.+?\.(?:{ext_alt}))__',
        repl_placeholder, html
    )

    # 2. "<key>": "assets/<sub>/X.<ext>"  →  "<key>": "<url-encoded {id,url}>"
    #    If <key> is an image-attr (photoN, hero_bg, model_image, …), the value
    #    becomes URL-encoded JSON so Lazy Blocks accepts it. Otherwise it stays
    #    a bare ID string (legacy callers may need that form).
    image_keys_pattern = "|".join(IMAGE_ATTR_KEYS)

    def repl_string(m):
        key = m.group(1)
        fname = m.group(2)
        att_id = photo_map.get(fname, "0")
        # Image-attr keys → URL-encoded {id,url} JSON
        if re.fullmatch(image_keys_pattern, key) or re.fullmatch(r"photo\d+", key):
            try:
                obj = {"id": int(att_id), "url": ""}
            except ValueError:
                obj = {"id": 0, "url": ""}
            encoded = urllib.parse.quote(json.dumps(obj, ensure_ascii=False))
            return f'"{key}": "{encoded}"'
        return f'"{key}": "{att_id}"'

    html, stats["string_paths"] = re.subn(
        rf'"(\w+)":\s*"assets/[^/"]+/([^"]+\.(?:{ext_alt}))"',
        repl_string, html
    )

    # 3. URL-encode image attribute objects {"id": N, "url": "..."}
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

    # 4. URL-encode raw-HTML/SVG textarea attributes.
    #    Only encode if value still contains markup-unsafe chars (`<`); skip
    #    if already encoded (idempotent: re-running the script is safe).
    svg_keys_pattern = "|".join(SVG_ATTR_KEYS)

    svg_changed = [0]

    def encode_svg(m):
        key = m.group(1)
        raw = m.group(2)
        if "<" not in raw:
            # Already URL-encoded or plain text — leave alone.
            return m.group(0)
        encoded = urllib.parse.quote(raw)
        svg_changed[0] += 1
        return f'"{key}":"{encoded}"'

    # Match `"key":"<svg...>...</svg>"` where value contains raw markup.
    # JSON strings escape internal `"` as `\"`, so value can include any char
    # except an unescaped closing quote. We use a greedy-but-anchored pattern.
    html = re.sub(
        rf'"({svg_keys_pattern})":\s*"((?:[^"\\]|\\.)*?)"',
        encode_svg, html
    )
    stats["svg_attrs"] = svg_changed[0]

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
    print(f"SVG textareas URL-encoded: {stats['svg_attrs']}")

    dst.write_text(html, encoding="utf-8")
    print(f"Saved: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
