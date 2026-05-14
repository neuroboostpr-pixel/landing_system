#!/usr/bin/env python3
"""Verify materials in a project folder per wizard step.

Output: JSON to stdout with {step, status, found, missing, summary}.
Exit code: 0 if pass or warn, 1 if fail.

Steps:
- prototype: REQUIRED. 07_ПРОТОТИП/source/prototype.{pdf,md,html}
- photos: optional. Count files in 07c_PHOTOS/inbox/**/*.{jpg,jpeg,png,heic}
- logos: optional. 04_БРЕНД/logos/logo.* or any image in logos/
- references: optional. 03_РЕФЕРЕНСЫ/index.yaml non-empty OR screenshots/ non-empty
"""
import argparse
import json
import sys
from pathlib import Path


PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
LOGO_EXTS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
PROTOTYPE_EXTS = {".pdf", ".md", ".html", ".htm"}


def _human_size(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def check_prototype(project: Path) -> dict:
    src = project / "07_ПРОТОТИП" / "source"
    found: list[str] = []
    if src.exists():
        for p in src.iterdir():
            # Accept any file with a supported extension. Skip README/.gitkeep/system files.
            if not p.is_file():
                continue
            if p.suffix.lower() not in PROTOTYPE_EXTS:
                continue
            if p.name.lower() == "readme.md":
                continue  # template README, not user content
            found.append(f"{p.name} ({_human_size(p.stat().st_size)})")
    if not found:
        return {
            "step": "prototype",
            "status": "fail",
            "found": [],
            "missing": ["prototype.pdf or prototype.md in 07_ПРОТОТИП/source/"],
            "summary": "Прототип не найден. Положи prototype.pdf или prototype.md в 07_ПРОТОТИП/source/",
        }
    return {
        "step": "prototype",
        "status": "pass",
        "found": found,
        "missing": [],
        "summary": f"Найдено: {', '.join(found)}",
    }


def check_photos(project: Path) -> dict:
    inbox = project / "07c_PHOTOS" / "inbox"
    photos: list[Path] = []
    if inbox.exists():
        for f in inbox.rglob("*"):
            if f.is_file() and f.suffix.lower() in PHOTO_EXTS:
                photos.append(f)
    if not photos:
        return {
            "step": "photos",
            "status": "warn",
            "found": [],
            "missing": ["any image in 07c_PHOTOS/inbox/"],
            "summary": "Фото клиента не найдены. На отсутствующие слоты сгенерится AI fallback.",
        }
    by_folder: dict[str, int] = {}
    for p in photos:
        rel = p.relative_to(inbox)
        folder = rel.parts[0] if len(rel.parts) > 1 else "inbox"
        by_folder[folder] = by_folder.get(folder, 0) + 1
    breakdown = ", ".join(f"{n} в {fld}" for fld, n in by_folder.items())
    return {
        "step": "photos",
        "status": "pass",
        "found": [f"{len(photos)} photos"],
        "missing": [],
        "summary": f"Найдено {len(photos)} фото ({breakdown})",
    }


def check_logos(project: Path) -> dict:
    logos_dir = project / "04_БРЕНД" / "logos"
    logos: list[Path] = []
    if logos_dir.exists():
        for f in logos_dir.iterdir():
            if f.is_file() and f.suffix.lower() in LOGO_EXTS:
                logos.append(f)
    if not logos:
        return {
            "step": "logos",
            "status": "warn",
            "found": [],
            "missing": ["logo.svg or logo.png in 04_БРЕНД/logos/"],
            "summary": "Логотип не найден. brand-architect сгенерит текстовый логотип на этапе 04.",
        }
    return {
        "step": "logos",
        "status": "pass",
        "found": [f"{p.name} ({_human_size(p.stat().st_size)})" for p in logos],
        "missing": [],
        "summary": f"Найдено: {', '.join(p.name for p in logos)}",
    }


def check_references(project: Path) -> dict:
    refs_dir = project / "03_РЕФЕРЕНСЫ"
    index_yaml = refs_dir / "index.yaml"
    screenshots_dir = refs_dir / "screenshots"

    has_yaml = False
    if index_yaml.exists():
        text = index_yaml.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                has_yaml = True
                break

    has_screenshots = False
    if screenshots_dir.exists() and any(screenshots_dir.iterdir()):
        has_screenshots = True

    if has_yaml or has_screenshots:
        parts = []
        if has_yaml:
            parts.append("index.yaml заполнен")
        if has_screenshots:
            parts.append("есть скриншоты")
        return {
            "step": "references",
            "status": "pass",
            "found": parts,
            "missing": [],
            "summary": ", ".join(parts),
        }

    return {
        "step": "references",
        "status": "warn",
        "found": [],
        "missing": ["URLs in 03_РЕФЕРЕНСЫ/index.yaml or screenshots/"],
        "summary": "Референсы не заданы. references-curator подберёт автоматически.",
    }


CHECKERS = {
    "prototype": check_prototype,
    "photos": check_photos,
    "logos": check_logos,
    "references": check_references,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--step", required=True, choices=list(CHECKERS.keys()))
    args = ap.parse_args()

    project = Path(args.project)
    checker = CHECKERS[args.step]
    result = checker(project)

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["status"] in ("pass", "warn") else 1)


if __name__ == "__main__":
    main()
