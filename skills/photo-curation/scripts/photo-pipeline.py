#!/usr/bin/env python3
"""Главный pipeline обработки фото для слотов лендинга.

Pipeline:
  validate_ratio → codex_post → resize → identity_check → cache → save

Использование:
  photo-pipeline.py <project> [--slot <name>] [--force]

Без --slot обрабатывает все слоты из selections.yaml.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
CODEX_PROCESS = SCRIPT_DIR / "codex-process-photo.sh"
IDENTITY_CHECK = SCRIPT_DIR / "identity-check.py"
RATIO_TOLERANCE = 0.05  # 5%


def parse_ratio(s: str) -> tuple[int, int]:
    """'16:9' → (16, 9)."""
    a, b = s.split(":")
    return int(a), int(b)


def ratio_value(r: tuple[int, int]) -> float:
    return r[0] / r[1]


def get_image_ratio(path: Path) -> float:
    img = Image.open(path)
    return img.width / img.height


def crop_center(img: Image.Image, target_ratio: float) -> Image.Image:
    """Crop по центру до target ratio."""
    current = img.width / img.height
    if abs(current - target_ratio) < 0.01:
        return img
    if current > target_ratio:
        # Слишком широкое — обрезаем по бокам
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        return img.crop((left, 0, left + new_width, img.height))
    else:
        # Слишком узкое — обрезаем сверху/снизу
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        return img.crop((0, top, img.width, top + new_height))


def resize_to_slot(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)


def compute_cache_key(orig: Path, brand_color: str, niche: str, region: str, ratio: str) -> str:
    h = hashlib.sha256()
    h.update(orig.read_bytes())
    h.update(brand_color.encode())
    h.update(niche.encode())
    h.update(region.encode())
    h.update(ratio.encode())
    return h.hexdigest()[:16]


def process_one_slot(
    project: Path,
    slot_name: str,
    photo_path: Path,
    slot_meta: dict,
    brand_params: dict,
    force: bool = False,
) -> dict:
    """Pipeline для одного слота."""
    processed_dir = project / "07c_PHOTOS" / "processed"
    cache_dir = project / "07c_PHOTOS" / ".cache"
    processed_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    target_ratio = slot_meta.get("ratio", "16:9")
    target_w, target_h = slot_meta.get("width", 1920), slot_meta.get("height", 1080)
    # Если width/height нет — вычислить из ratio как 1920px по длинной стороне
    if "width" not in slot_meta:
        r = parse_ratio(target_ratio)
        if r[0] >= r[1]:
            target_w, target_h = 1920, int(1920 * r[1] / r[0])
        else:
            target_w, target_h = int(1080 * r[0] / r[1]), 1080

    cache_key = compute_cache_key(
        photo_path,
        brand_params.get("primary", "#000000"),
        brand_params.get("niche", "generic"),
        brand_params.get("region", "global"),
        target_ratio,
    )
    cache_path = cache_dir / f"{cache_key}.jpg"
    processed_path = processed_dir / f"{slot_name}.jpg"

    # Cache hit
    if cache_path.exists() and not force:
        shutil.copy(cache_path, processed_path)
        return {"slot": slot_name, "status": "cached", "path": str(processed_path)}

    # 1. Validate ratio
    orig_ratio = get_image_ratio(photo_path)
    target_ratio_val = ratio_value(parse_ratio(target_ratio))
    needs_crop = abs(orig_ratio - target_ratio_val) > RATIO_TOLERANCE

    # 2. Codex post-process (если codex доступен)
    intermediate = cache_dir / f"{cache_key}.codex.jpg"
    codex_ok = False
    try:
        cmd = [
            "bash", str(CODEX_PROCESS),
            "--input", str(photo_path),
            "--output", str(intermediate),
            "--slot-ratio", target_ratio,
            "--brand-color", brand_params.get("primary", "#000000"),
            "--niche", brand_params.get("niche", "generic"),
            "--region", brand_params.get("region", "global"),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        codex_ok = result.returncode == 0 and intermediate.exists()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        codex_ok = False

    # 3. Identity check
    if codex_ok:
        try:
            check = subprocess.run(
                ["python3", str(IDENTITY_CHECK), str(photo_path), str(intermediate)],
                capture_output=True, text=True, timeout=30,
            )
            if check.returncode != 0:
                # Identity changed too much — revert to original
                codex_ok = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Использовать codex результат или оригинал
    source_img = Image.open(intermediate if codex_ok else photo_path)

    # 4. Crop if needed
    if needs_crop:
        source_img = crop_center(source_img, target_ratio_val)

    # 5. Resize to exact slot dimensions
    final = resize_to_slot(source_img, target_w, target_h)

    # 6. Save
    final.save(processed_path, "JPEG", quality=85)
    final.save(cache_path, "JPEG", quality=85)

    return {
        "slot": slot_name,
        "status": "processed" if codex_ok else "raw-resized",
        "path": str(processed_path),
        "size": f"{target_w}x{target_h}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project directory")
    parser.add_argument("--slot", help="Process only one slot")
    parser.add_argument("--force", action="store_true", help="Ignore cache")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    selections = project / "07c_PHOTOS" / "selections.yaml"
    tokens = project / "04_БРЕНД" / "tokens.json"

    if not selections.exists():
        print(f"ERROR: {selections} не найден", file=sys.stderr)
        return 2

    selections_data = yaml.safe_load(selections.read_text(encoding="utf-8")) or {}
    brand = {}
    if tokens.exists():
        t = json.loads(tokens.read_text(encoding="utf-8"))
        brand["primary"] = t.get("colors", {}).get("primary", "#000000")

    brand["niche"] = "generic"
    brand["region"] = "global"
    profile = project / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
    if profile.exists():
        text = profile.read_text(encoding="utf-8")
        # Простой парсинг
        for line in text.splitlines():
            if line.lower().startswith("**niche") or line.lower().startswith("niche:"):
                brand["niche"] = line.split(":", 1)[-1].strip(" *")
            if line.lower().startswith("**geo") or line.lower().startswith("region:"):
                brand["region"] = line.split(":", 1)[-1].strip(" *")

    photo_assignments = selections_data.get("slots", {}) or selections_data.get("blocks", {})

    manifest = {}
    for slot_name, photo_rel in photo_assignments.items():
        if args.slot and args.slot != slot_name:
            continue
        if not isinstance(photo_rel, str):
            continue
        photo_path = project / "07c_PHOTOS" / "inbox" / photo_rel
        if not photo_path.exists():
            photo_path = project / photo_rel
        if not photo_path.exists():
            print(f"⚠ Слот '{slot_name}': фото '{photo_rel}' не найдено", file=sys.stderr)
            continue

        slot_meta = {"ratio": "16:9"}  # дефолт; реальные slot meta берутся из block-library
        result = process_one_slot(project, slot_name, photo_path, slot_meta, brand, force=args.force)
        manifest[f"{slot_name}.jpg"] = result
        print(f"  [{result['status']}] {slot_name} → {result['path']}")

    # Save manifest
    manifest_path = project / "07c_PHOTOS" / "processed" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n✅ Обработано {len(manifest)} слотов, manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
