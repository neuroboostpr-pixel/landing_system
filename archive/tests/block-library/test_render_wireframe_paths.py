"""B34: render-wireframe строит путь к блоку по folder/path, а не по category.

Регрессия: после B34 category (footer) может отличаться от папки на диске
(contacts/). Путь обязан использовать physical folder/path из каталога.
"""
import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "wireframe-rendering" / "scripts" / "render-wireframe.py"


def _load():
    spec = importlib.util.spec_from_file_location("render_wireframe", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_catalog(tmp_path, blocks):
    lib = tmp_path / "lib"
    lib.mkdir(parents=True, exist_ok=True)
    (lib / "catalog.yaml").write_text(
        yaml.dump({"version": 3, "blocks": blocks}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return lib


def test_block_dir_uses_physical_folder_not_category(tmp_path):
    m = _load()
    # contacts блок: category=footer, но папка contacts/
    lib = _make_catalog(tmp_path, [{
        "id": "contacts-003", "path": "contacts/contacts-003/",
        "folder": "contacts", "category": "footer", "variant": None,
    }])
    d = m._block_dir_for(str(lib), "contacts-003")
    assert d == lib / "contacts" / "contacts-003", d
    # НЕ footer/
    assert "footer" not in str(d)


def test_block_dir_fallback_to_folder_without_path(tmp_path):
    m = _load()
    lib = _make_catalog(tmp_path, [{
        "id": "x-1", "folder": "quiz", "category": "forms", "variant": "quiz",
    }])
    d = m._block_dir_for(str(lib), "x-1")
    assert d == lib / "quiz" / "x-1", d


def test_category_for_still_returns_semantic_category(tmp_path):
    m = _load()
    lib = _make_catalog(tmp_path, [{
        "id": "contacts-003", "path": "contacts/contacts-003/",
        "folder": "contacts", "category": "footer", "variant": None,
    }])
    # для бейджей категория остаётся семантической
    assert m._category_for(str(lib), "contacts-003") == "footer"
