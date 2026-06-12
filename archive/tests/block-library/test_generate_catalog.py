"""B34 Фаза 2 — generate-catalog.py читает category+variant из meta.yaml.

Правила:
- В catalog каждый блок имеет `category` и `variant` из meta.yaml (а НЕ из
  имени папки) — meta.yaml это source of truth (B34).
- Поле `folder` хранит физическую папку (для path), т.к. она может отличаться
  от семантической B34-категории.
- Невалидная category/variant → stderr warning, но блок попадает в catalog
  (скрипт не падает).
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate-catalog.py"


def _make_block(lib: Path, folder: str, bid: str, meta: dict):
    bd = lib / folder / bid
    (bd / "assets").mkdir(parents=True, exist_ok=True)
    (bd / "assets" / "template.html").write_text("<section></section>", encoding="utf-8")
    (bd / "meta.yaml").write_text(
        yaml.dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def _run(lib: Path, out: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--library", str(lib), "--output", str(out)],
        capture_output=True, text=True,
    )


def test_catalog_includes_variant_from_meta(tmp_path):
    lib = tmp_path / "block-library"
    # семантическая category из meta отличается от папки (quiz → forms)
    _make_block(lib, "quiz", "ru-quiz-01", {
        "id": "ru-quiz-01", "category": "forms", "variant": "quiz",
        "type": "quiz", "layout_pattern": "step-card",
    })
    _make_block(lib, "hero", "hero-001", {
        "id": "hero-001", "category": "hero", "variant": None,
        "type": "hero", "layout_pattern": "split",
    })
    out = tmp_path / "catalog.yaml"
    r = _run(lib, out)
    assert r.returncode == 0, r.stderr
    cat = yaml.safe_load(out.read_text(encoding="utf-8"))
    blocks = {b["id"]: b for b in cat["blocks"]}

    # variant присутствует и берётся из meta
    assert blocks["ru-quiz-01"]["variant"] == "quiz"
    assert blocks["hero-001"]["variant"] is None
    # category из meta (forms), НЕ из папки (quiz)
    assert blocks["ru-quiz-01"]["category"] == "forms"
    # folder сохраняет физическую папку для path
    assert blocks["ru-quiz-01"]["folder"] == "quiz"
    assert blocks["ru-quiz-01"]["path"] == "quiz/ru-quiz-01/"


def test_invalid_category_warns_but_keeps_block(tmp_path):
    lib = tmp_path / "block-library"
    _make_block(lib, "hero", "bad-001", {
        "id": "bad-001", "category": "NotARealCategory", "variant": None,
    })
    out = tmp_path / "catalog.yaml"
    r = _run(lib, out)
    assert r.returncode == 0, r.stderr
    assert "bad-001" in r.stderr or "NotARealCategory" in r.stderr, \
        "ожидался warning про невалидную category в stderr"
    cat = yaml.safe_load(out.read_text(encoding="utf-8"))
    ids = {b["id"] for b in cat["blocks"]}
    assert "bad-001" in ids, "блок с невалидной категорией должен остаться в catalog"
