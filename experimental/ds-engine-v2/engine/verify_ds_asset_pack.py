#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a DS-Engine v2 mood asset package.

Plan mode checks that the mood has recipes, an asset manifest, generated prompts,
and a delivery contract. Ready mode also checks that required files exist and are
valid enough for layout.
"""
from __future__ import annotations

import argparse
import imghdr
import sys
from pathlib import Path
from typing import Iterable

import yaml


DESIGN_DIR = "05_ДИЗАЙН-СИСТЕМА"
REQUIRED_ASSET_KEYS = ("id", "нужен", "роль_где", "источник", "формат", "слот", "статус")
SOURCE_MARKERS = ("снят-с-рефа", "под-нишу", "из логотипа", "CSS", "css")
DELIVERY_REQUIRED = {
    "desktop_preview": ("assets/previews/preview-desktop.png",),
    "mobile_preview": ("assets/previews/preview-mobile.png",),
    "layers": (
        "assets/layers/layers.svg",
        "assets/layers/layers.json",
        "assets/layers/layers.pdf",
    ),
    "canvas_file": (
        "assets/canvas/canvas-file.canva",
        "assets/canvas/canvas-file.fig",
        "assets/canvas/canvas-file.svg",
        "assets/canvas/canvas-file.pdf",
        "assets/canvas/canvas-file.html",
        "assets/canvas/canvas-file.md",
        "assets/canvas/canvas-file.url",
    ),
    "prompts": ("assets/prompts.md",),
    "source_rules": ("assets/source-rules.md",),
}


class ValidationError(Exception):
    pass


def _load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - message matters more than type here
        raise ValidationError(f"не могу прочитать YAML {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path} должен быть YAML-объектом")
    return data


def _project_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.exists():
        raise ValidationError(f"проект не найден: {root}")
    return root


def _resolve_mood(project: Path, mood: str | None) -> tuple[str, Path]:
    moods_dir = project / DESIGN_DIR / "moods"
    if not moods_dir.exists():
        raise ValidationError(f"нет папки mood-рецептов: {moods_dir}")

    if mood:
        mood_dir = moods_dir / mood
        if not mood_dir.exists():
            raise ValidationError(f"mood '{mood}' не найден: {mood_dir}")
        return mood, mood_dir

    active_file = moods_dir / "active-mood.txt"
    if active_file.exists():
        active = active_file.read_text(encoding="utf-8").strip()
        if active:
            mood_dir = moods_dir / active
            if mood_dir.exists():
                return active, mood_dir

    candidates = sorted(p for p in moods_dir.iterdir() if (p / "assets-manifest.yaml").exists())
    if (moods_dir / "grooming" / "assets-manifest.yaml").exists():
        return "grooming", moods_dir / "grooming"
    if len(candidates) == 1:
        return candidates[0].name, candidates[0]
    if not candidates:
        raise ValidationError(f"не найден ни один mood с assets-manifest.yaml в {moods_dir}")
    names = ", ".join(p.name for p in candidates)
    raise ValidationError(f"несколько mood-кандидатов ({names}); укажи --mood или active-mood.txt")


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1", "да"}


def _is_css_asset(asset: dict) -> bool:
    return "css" in str(asset.get("формат", "")).lower()


def _is_ready_status(asset: dict) -> bool:
    return str(asset.get("статус", "")).strip().lower().startswith("готов")


def _allowed_exts(asset: dict) -> set[str]:
    fmt = str(asset.get("формат", "")).lower()
    exts: set[str] = set()
    if "svg" in fmt:
        exts.add(".svg")
    if any(x in fmt for x in ("png", "jpg", "jpeg", "photo", "фото")):
        exts.update({".png", ".jpg", ".jpeg", ".webp"})
    if "ico" in fmt:
        exts.add(".ico")
    if not exts:
        exts.update({".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".pdf"})
    return exts


def _asset_files(mood_dir: Path, asset: dict) -> list[Path]:
    assets_dir = mood_dir / "assets"
    if not assets_dir.exists():
        return []
    asset_id = str(asset["id"])
    allowed = _allowed_exts(asset)
    matches = []
    for path in assets_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        stem = path.stem
        if stem == asset_id or stem.startswith(f"{asset_id}-") or stem.startswith(f"{asset_id}_"):
            matches.append(path)
    return sorted(matches)


def _looks_like_real_file(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    ext = path.suffix.lower()
    if ext == ".png":
        return path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    if ext in {".jpg", ".jpeg", ".webp"}:
        return imghdr.what(path) in {"jpeg", "webp"}
    if ext == ".svg":
        head = path.read_text(encoding="utf-8", errors="ignore")[:500].lower()
        return "<svg" in head
    return True


def _validate_manifest(mood_dir: Path) -> tuple[dict, list[dict], list[dict]]:
    recipes = mood_dir / "recipes.yaml"
    manifest = mood_dir / "assets-manifest.yaml"
    if not recipes.exists():
        raise ValidationError(f"нет recipes.yaml: {recipes}")
    if not manifest.exists():
        raise ValidationError(f"нет assets-manifest.yaml: {manifest}")

    data = _load_yaml(manifest)
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValidationError("assets-manifest.yaml должен содержать непустой список assets")

    seen: set[str] = set()
    for idx, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            raise ValidationError(f"assets[{idx}] должен быть объектом")
        missing = [key for key in REQUIRED_ASSET_KEYS if key not in asset]
        if missing:
            raise ValidationError(f"asset {asset.get('id', idx)}: нет полей {', '.join(missing)}")
        asset_id = str(asset["id"])
        if asset_id in seen:
            raise ValidationError(f"дубль id в manifest: {asset_id}")
        seen.add(asset_id)

        source = str(asset.get("источник", ""))
        if not any(marker in source for marker in SOURCE_MARKERS):
            raise ValidationError(f"{asset_id}: источник должен быть снят с рефа или явно помечен как под-нишу")

        needs_prompt = not _is_css_asset(asset) and (not _is_ready_status(asset) or asset_id in _to_generate_ids(data))
        if needs_prompt and not str(asset.get("промпт", "")).strip():
            raise ValidationError(f"{asset_id}: для генерируемого ассета нужен готовый промпт")

    to_generate = data.get("to_generate") or []
    if not isinstance(to_generate, list):
        raise ValidationError("to_generate должен быть списком")
    by_id = {str(asset["id"]): asset for asset in assets}
    for item in to_generate:
        if not isinstance(item, dict) or "id" not in item:
            raise ValidationError("каждый item в to_generate должен иметь id")
        if str(item["id"]) not in by_id:
            raise ValidationError(f"to_generate ссылается на неизвестный id: {item['id']}")
    return data, assets, to_generate


def _to_generate_ids(data: dict) -> set[str]:
    return {str(item.get("id")) for item in data.get("to_generate") or [] if isinstance(item, dict)}


def _validate_plan_files(mood_dir: Path, to_generate: Iterable[dict]) -> None:
    todo = mood_dir / "ASSETS-TODO.md"
    pack = mood_dir / "asset-pack.yaml"
    if not todo.exists():
        raise ValidationError(f"нет ASSETS-TODO.md: запусти gen_assets_report.py для mood {mood_dir.name}")
    if not pack.exists():
        raise ValidationError(f"нет asset-pack.yaml: запусти gen_assets_report.py для mood {mood_dir.name}")

    text = todo.read_text(encoding="utf-8")
    for needle in ("Полный пакет для верстки", "preview-desktop.png", "preview-mobile.png", "Canvas/Canva"):
        if needle not in text:
            raise ValidationError(f"ASSETS-TODO.md не содержит обязательный раздел/маркер: {needle}")
    for item in to_generate:
        asset_id = str(item["id"])
        if asset_id not in text:
            raise ValidationError(f"ASSETS-TODO.md не содержит ассет из to_generate: {asset_id}")


def _validate_delivery_files(mood_dir: Path) -> None:
    missing = []
    invalid = []
    for label, candidates in DELIVERY_REQUIRED.items():
        existing = [mood_dir / rel for rel in candidates if (mood_dir / rel).exists()]
        if not existing:
            missing.append(f"{label}: one of {', '.join(candidates)}")
            continue
        if not any(_looks_like_real_file(path) for path in existing):
            invalid.append(f"{label}: {', '.join(str(path.relative_to(mood_dir)) for path in existing)}")

    if missing or invalid:
        details = []
        if missing:
            details.append("нет файлов полного пакета: " + "; ".join(missing))
        if invalid:
            details.append("файлы выглядят пустыми/битными: " + "; ".join(invalid))
        raise ValidationError(" | ".join(details))


def _validate_required_asset_files(mood_dir: Path, assets: list[dict]) -> None:
    missing = []
    invalid = []
    for asset in assets:
        if not _truthy(asset.get("нужен")) or _is_css_asset(asset):
            continue
        files = _asset_files(mood_dir, asset)
        if not files:
            missing.append(str(asset["id"]))
            continue
        if not any(_looks_like_real_file(path) for path in files):
            invalid.append(str(asset["id"]))

    if missing or invalid:
        parts = []
        if missing:
            parts.append("нет файлов обязательных ассетов: " + ", ".join(missing))
        if invalid:
            parts.append("битые/пустые файлы ассетов: " + ", ".join(invalid))
        raise ValidationError(" | ".join(parts))


def validate(project: Path, mood: str | None, mode: str) -> tuple[str, Path]:
    mood_name, mood_dir = _resolve_mood(project, mood)
    _data, assets, to_generate = _validate_manifest(mood_dir)
    _validate_plan_files(mood_dir, to_generate)
    if mode == "ready":
        _validate_delivery_files(mood_dir)
        _validate_required_asset_files(mood_dir, assets)
    return mood_name, mood_dir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate DS-Engine v2 mood asset package.")
    parser.add_argument("--project", required=True, help="путь к проекту-лендингу")
    parser.add_argument("--mood", help="mood name; иначе active-mood.txt/grooming/единственный manifest")
    parser.add_argument("--mode", choices=("plan", "ready"), default="plan")
    args = parser.parse_args(argv[1:])

    try:
        mood, mood_dir = validate(_project_root(args.project), args.mood, args.mode)
    except ValidationError as exc:
        print(f"❌ DS asset pack не готов: {exc}", file=sys.stderr)
        return 1

    print(f"✅ DS asset pack {args.mode}: {mood} ({mood_dir})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
