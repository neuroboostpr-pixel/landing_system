#!/usr/bin/env python3
"""Photo intake: copy from inbox/ subfolders into intake/, dedupe, generate thumbnails.

- HEIC→JPEG via `sips` (macOS); on other OS, skip with warning.
- EXIF strip (removes GPS, camera serial, etc.).
- SHA-256 dedupe.
- Folder-tag detection: file in inbox/X/ inherits X's folder-tag.
- Generates 256px thumbnails for HTML gallery.
- Idempotent: re-runs skip already-processed files (by hash).

Subfolder count: 6 named subfolders + _свалка = 7 total.
(Spec D10 says "7 predefined subfolders" but the concrete structure lists 6 named + _свалка.)
"""
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import yaml
from PIL import Image


# 6 named subfolders + _свалка = 7 total
INTAKE_SUBFOLDERS = [
    "_свалка",
    "портреты_и_команда",
    "процесс_работы",
    "объекты_и_продукты",
    "интерьер_экстерьер",
    "до_после",
    "документы_сертификаты",
]

SUBFOLDER_TO_TAG: dict[str, list[str]] = {
    "портреты_и_команда": ["portrait", "team"],
    "процесс_работы": ["process"],
    "объекты_и_продукты": ["object"],
    "интерьер_экстерьер": ["interior", "exterior"],
    "до_после": ["before-after"],
    "документы_сертификаты": ["document"],
    "_свалка": [],
}

THUMB_SIZE = 256
MAX_DIMENSION = 4096
SUPPORTED_INPUTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _heic_to_jpeg(src: Path, dst: Path) -> bool:
    """Use macOS sips to convert HEIC to JPEG. Returns True on success."""
    try:
        subprocess.run(
            ["sips", "-s", "format", "jpeg", str(src), "--out", str(dst)],
            check=True,
            capture_output=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _strip_exif_and_save(src: Path, dst: Path) -> None:
    """Open image, optionally resize, save as JPEG without EXIF."""
    img = Image.open(src)
    # Convert to RGB if needed (e.g. PNG with alpha, palette mode)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    # Resize if too large
    if max(img.size) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    # Strip EXIF by reconstructing image from raw bytes (no metadata copied)
    raw = img.tobytes()
    img_no_exif = Image.frombytes(img.mode, img.size, raw)
    img_no_exif.save(dst, "JPEG", quality=88)


def _make_thumb(src: Path, dst: Path) -> None:
    """Create a 256px max-dimension thumbnail."""
    with Image.open(src) as img:
        img = img.copy()
    img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
    img.save(dst, "JPEG", quality=80)


def _enumerate_input_files(inbox_root: Path) -> Iterable[tuple[Path, str]]:
    """Yield (file_path, folder_name) for every supported file in inbox subfolders."""
    if not inbox_root.exists():
        return
    for sub in INTAKE_SUBFOLDERS:
        sub_dir = inbox_root / sub
        if not sub_dir.exists():
            continue
        for f in sorted(sub_dir.rglob("*")):
            if f.is_file() and f.suffix.lower() in SUPPORTED_INPUTS:
                yield f, sub


def run_intake(inbox_root: Path, intake_dir: Path) -> dict:
    """Process all files in inbox_root subfolders → intake_dir.

    Returns the intake report dict (also written to intake_dir/intake-report.yaml).
    Idempotent: files whose hash already appears in existing report are skipped.
    """
    inbox_root = Path(inbox_root)
    intake_dir = Path(intake_dir)
    intake_dir.mkdir(parents=True, exist_ok=True)

    report_path = intake_dir / "intake-report.yaml"
    if report_path.exists():
        report = yaml.safe_load(report_path.read_text()) or {"photos": []}
        if "photos" not in report:
            report["photos"] = []
    else:
        report = {"photos": []}

    known_hashes: dict[str, dict] = {p["hash"]: p for p in report["photos"]}

    for src, sub in _enumerate_input_files(inbox_root):
        file_hash = _hash_file(src)

        if file_hash in known_hashes:
            # Track duplicate names in the existing entry
            entry = known_hashes[file_hash]
            if src.name != entry["original_name"]:
                entry.setdefault("duplicates", [])
                if src.name not in entry["duplicates"]:
                    entry["duplicates"].append(src.name)
            continue

        intake_id = f"photo_{file_hash}"
        intake_jpg = intake_dir / f"{intake_id}.jpg"
        intake_thumb = intake_dir / f"{intake_id}.thumb.jpg"

        # Convert HEIC if needed
        if src.suffix.lower() in {".heic", ".heif"}:
            tmp_jpg = intake_dir / f"_tmp_{intake_id}.jpg"
            if not _heic_to_jpeg(src, tmp_jpg):
                print(
                    f"WARN: HEIC conversion failed for {src} (sips unavailable). Skipping.",
                    file=sys.stderr,
                )
                continue
            _strip_exif_and_save(tmp_jpg, intake_jpg)
            tmp_jpg.unlink()
        else:
            _strip_exif_and_save(src, intake_jpg)

        _make_thumb(intake_jpg, intake_thumb)

        with Image.open(intake_jpg) as img:
            width, height = img.size

        tags = SUBFOLDER_TO_TAG.get(sub, [])
        entry = {
            "id": intake_id,
            "hash": file_hash,
            "path": str(intake_jpg.relative_to(intake_dir.parent)),
            "thumb_path": str(intake_thumb.relative_to(intake_dir.parent)),
            "original_name": src.name,
            "folder_origin": sub,
            "tag_source": "folder" if tags else "pending_ai_classify",
            "tags": tags,
            "dimensions": [width, height],
            "duplicates": [],
        }
        report["photos"].append(entry)
        known_hashes[file_hash] = entry

    report_path.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False))
    return report


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Photo intake pipeline")
    ap.add_argument("--inbox", required=True, help="Path to inbox/ root (contains subfolders)")
    ap.add_argument("--intake", required=True, help="Path to intake/ output dir")
    args = ap.parse_args()

    report = run_intake(Path(args.inbox), Path(args.intake))
    print(f"Intake done: {len(report['photos'])} unique photos")


if __name__ == "__main__":
    main()
