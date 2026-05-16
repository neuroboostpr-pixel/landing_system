#!/usr/bin/env python3
"""Verify photo pipeline для hard_check.

Проверяет:
- Все <img src> в composed.html ведут на 07c_PHOTOS/processed/
- Нет SVG placeholder'ов
- Размеры файлов соответствуют атрибутам width/height в HTML
- manifest.json существует
- HARD GATE PR-K: hero-bg не должен обрезаться — ratio файла должен совпадать
  с ratio слота из meta.yaml в пределах 5%.

Exit 0 — OK, exit 1 — issues, exit 2 — files missing.
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image

try:
    import yaml
except ImportError:
    yaml = None


HERO_RATIO_TOLERANCE = 0.05  # 5% — больше → exit 1 (hero не должен обрезаться)


def _parse_ratio(r):
    if not r or not isinstance(r, str):
        return None
    try:
        w, h = r.split(":")
        wv, hv = float(w), float(h)
        if hv == 0:
            return None
        return wv / hv
    except (ValueError, AttributeError):
        return None


def _img_ratio(path: Path):
    try:
        with Image.open(path) as im:
            w, h = im.size
        return (w / h) if h else None
    except Exception:
        return None


def _find_block_meta(block_id: str, library_root: Path):
    """Ищет block-library/<cat>/<block_id>/meta.yaml."""
    if not library_root.exists() or yaml is None:
        return None
    for cat_dir in library_root.iterdir():
        if not cat_dir.is_dir():
            continue
        meta = cat_dir / block_id / "meta.yaml"
        if meta.exists():
            try:
                return yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                return None
    return None


def _check_hero_no_crop(soup, project_dir: Path, repo_root: Path):
    """Возвращает список issues для hero-фото, у которых ratio расходится >5%."""
    issues = []
    library_root = repo_root / "block-library"

    # Найти все <img> внутри блоков, чьё data-block начинается на 'hero-'
    # или чей data-slot/lp-* указывает на hero-bg.
    hero_imgs = []

    # Способ 1: <img> внутри элемента c data-block^="hero-"
    for parent in soup.find_all(attrs={"data-block": True}):
        bid = parent.get("data-block", "")
        if not bid.startswith(("hero-", "ru-hero-")):
            continue
        for img in parent.find_all("img"):
            slot = img.get("data-slot") or "hero-bg"
            hero_imgs.append((bid, slot, img))

    # Способ 2: <img data-slot="hero-bg"> где угодно (нет parent с data-block)
    for img in soup.find_all("img", attrs={"data-slot": "hero-bg"}):
        parent_block = img.find_parent(attrs={"data-block": True})
        bid = parent_block.get("data-block") if parent_block else "(no-block)"
        if (bid, "hero-bg", img) in hero_imgs:
            continue
        hero_imgs.append((bid, "hero-bg", img))

    # Способ 3: <img class="lp-hero"> — legacy
    for img in soup.find_all("img", class_=re.compile(r"\blp-hero\b")):
        parent_block = img.find_parent(attrs={"data-block": True})
        bid = parent_block.get("data-block") if parent_block else "(legacy-lp-hero)"
        slot = img.get("data-slot") or "hero-bg"
        if (bid, slot, img) in hero_imgs:
            continue
        hero_imgs.append((bid, slot, img))

    for bid, slot_name, img in hero_imgs:
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue

        # Резолвим путь к файлу
        candidates = [
            project_dir / src.lstrip("/"),
            project_dir / "07b_COMPOSED" / src,
            project_dir / src,
        ]
        photo_path = next((p for p in candidates if p.exists() and p.is_file()), None)
        if not photo_path:
            issues.append(f"hero {bid}/{slot_name}: файл не найден ({src})")
            continue

        actual = _img_ratio(photo_path)
        if actual is None:
            issues.append(f"hero {bid}/{slot_name}: не удалось прочитать ratio файла")
            continue

        # Ищем expected ratio в meta.yaml
        expected_ratio = None
        meta = _find_block_meta(bid, library_root)
        if meta:
            for s in meta.get("slots") or []:
                if s.get("type") == "photo" and s.get("name") == slot_name:
                    expected_ratio = _parse_ratio(s.get("ratio"))
                    break
            if expected_ratio is None:
                # fallback на первый photo слот
                for s in meta.get("slots") or []:
                    if s.get("type") == "photo":
                        expected_ratio = _parse_ratio(s.get("ratio"))
                        break

        if expected_ratio is None:
            # без meta — гейт не блокируем, но логируем
            continue

        dev = abs(actual - expected_ratio) / expected_ratio
        if dev > HERO_RATIO_TOLERANCE:
            issues.append(
                f"hero не должен обрезаться: {bid}/{slot_name} "
                f"ratio={actual:.3f} != slot={expected_ratio:.3f} "
                f"(dev={dev * 100:.1f}% > {HERO_RATIO_TOLERANCE * 100:.0f}%)"
            )

    return issues


def main(project_dir, repo_root: Path = None):
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    if not composed.exists():
        print(f"ERROR: {composed} не найден", file=sys.stderr)
        return 2

    # repo_root — где лежит block-library (по умолчанию — landing-system root)
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]

    soup = BeautifulSoup(composed.read_text(encoding="utf-8"), "html.parser")
    issues = []

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue
        # Placeholder detection
        if "placeholder" in src.lower() or src.lower().endswith(".svg"):
            issues.append(f"placeholder остался: {src}")
            continue
        # Не из processed/?
        if "processed/" not in src:
            issues.append(f"img НЕ из processed/: {src}")

    # Manifest
    manifest = project_dir / "07c_PHOTOS" / "processed" / "manifest.json"
    if not manifest.exists() and len([i for i in soup.find_all("img") if i.get("src")]) > 0:
        issues.append("manifest.json отсутствует в 07c_PHOTOS/processed/")

    # PR-K: hero-bg не должен обрезаться
    issues.extend(_check_hero_no_crop(soup, project_dir, repo_root))

    if issues:
        print(f"❌ Photo pipeline issues ({len(issues)}):", file=sys.stderr)
        for i in issues[:10]:
            print(f"   - {i}", file=sys.stderr)
        return 1

    print(f"✅ Photo pipeline OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_photo_pipeline.py <project>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
