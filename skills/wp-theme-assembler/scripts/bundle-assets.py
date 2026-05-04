#!/usr/bin/env python3
"""Download icons from Iconify API; note font CDN references; copy processed photos.

CLI: python3 bundle-assets.py <project-dir>
Stdout: JSON {"fonts": [...], "icons": [...], "images_copied": N}
"""
import json
import shutil
import sys
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, info, success, warn


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "06_СТЕК" / "design-stack.yaml").exists():
            return parent
    raise FileNotFoundError("design-stack.yaml not found — run /landing-stack first")


def _load_stack(project: Path) -> dict:
    return yaml.safe_load((project / "06_СТЕК" / "design-stack.yaml").read_text(encoding="utf-8"))


def _note_fonts(project: Path, stack: dict) -> list:
    """Write CDN stub files — actual fonts are loaded by browser from CDN."""
    fonts_dir = project / "08_КОД" / "wp-theme" / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    families = stack.get("fonts", {}).get("families", [])
    cdn = stack.get("fonts", {}).get("cdn", "bunny")
    noted = []
    for font in families:
        name = font["name"]
        weights = font.get("weights", [400])
        slug = name.lower().replace(" ", "-")
        (fonts_dir / f"{slug}.txt").write_text(
            f"Font: {name}\nWeights: {weights}\nCDN: {cdn}\n", encoding="utf-8"
        )
        info(f"Font noted: {name} via {cdn}")
        noted.append(name)
    return noted


def _download_icons(project: Path) -> list:
    """Download SVG icons from Iconify API."""
    icons_dir = project / "08_КОД" / "wp-theme" / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    icons_yaml = project / "04_БРЕНД" / "extracted" / "icons.yaml"
    if not icons_yaml.exists():
        warn("icons.yaml not found — skipping icon download")
        return []

    data = yaml.safe_load(icons_yaml.read_text(encoding="utf-8")) or {}
    icons_list = data.get("icons", []) if isinstance(data, dict) else (data or [])

    downloaded = []
    for icon in icons_list:
        icon_id = icon.get("id") if isinstance(icon, dict) else str(icon)
        if not icon_id or ":" not in icon_id:
            continue
        prefix, name = icon_id.split(":", 1)
        url = f"https://api.iconify.design/{prefix}/{name}.svg"
        out = icons_dir / f"{prefix}-{name}.svg"
        try:
            urllib.request.urlretrieve(url, out)
            downloaded.append(icon_id)
            info(f"Icon: {icon_id}")
        except Exception as exc:
            warn(f"Icon download failed {icon_id}: {exc}")

    return downloaded


def _copy_images(project: Path) -> int:
    src = project / "02_МАТЕРИАЛЫ_КЛИЕНТА" / "photos" / "processed"
    dst = project / "08_КОД" / "wp-theme" / "assets" / "images"
    dst.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        warn(f"Processed photos not found: {src}")
        return 0

    count = 0
    for img in src.iterdir():
        if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".svg"}:
            shutil.copy2(img, dst / img.name)
            count += 1

    info(f"Copied {count} images → assets/images/")
    return count


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        project = _find_project_root(cwd)
    except FileNotFoundError as e:
        error(str(e))
        return 1

    stack = _load_stack(project)
    fonts = _note_fonts(project, stack)
    icons = _download_icons(project)
    images = _copy_images(project)

    result = {"fonts": fonts, "icons": icons, "images_copied": images}
    print(json.dumps(result))
    success(f"Assets bundled: {len(fonts)} fonts, {len(icons)} icons, {images} images")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
