"""B34 Фаза 1 — каждый meta.yaml соответствует таксономии.

Правила (B34 решение 1):
- `category` обязателен и валиден по taxonomy.yaml.
- Для категорий С уровнем 3: `variant` ОБЯЗАТЕЛЕН и валиден.
- Для категорий БЕЗ уровня 3: `variant` отсутствует или null.

Папки cta/ и gallery/ удаляются в Фазе 3 — здесь исключены из проверки.
"""
import importlib.util
from pathlib import Path

import yaml
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "block-library"
LOADER_PATH = REPO_ROOT / "scripts" / "lib" / "taxonomy.py"

# спец-папки и удаляемые в Фазе 3
SKIP_DIRS = {"_patterns", "_shapes", "_styles", "references", "cta", "gallery"}


def _load_loader():
    spec = importlib.util.spec_from_file_location("taxonomy_lib_meta", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _iter_block_metas():
    for catdir in sorted(LIB.iterdir()):
        if not catdir.is_dir() or catdir.name.startswith((".", "_")) or catdir.name in SKIP_DIRS:
            continue
        for bd in sorted(catdir.iterdir()):
            if not bd.is_dir():
                continue
            mp = bd / "meta.yaml"
            if mp.exists():
                yield catdir.name, bd.name, mp


def _all_metas():
    return list(_iter_block_metas())


def test_blocks_exist():
    assert len(_all_metas()) > 0, "не найдено ни одного блока"


@pytest.mark.parametrize("folder,bid,mp", _all_metas(), ids=lambda x: x if isinstance(x, str) else "")
def test_meta_category_and_variant_valid(folder, bid, mp):
    lib = _load_loader()
    meta = yaml.safe_load(mp.read_text(encoding="utf-8")) or {}

    category = meta.get("category")
    assert category, f"{bid}: нет category"
    assert lib.valid_category(category), \
        f"{bid}: невалидная category '{category}' (не в taxonomy.yaml)"

    variant = meta.get("variant")
    if lib.has_variants(category):
        assert variant is not None, \
            f"{bid}: category '{category}' требует variant (B34 решение 1), но variant отсутствует"
        assert lib.valid_variant(category, variant), \
            f"{bid}: невалидный variant '{variant}' для category '{category}'"
    else:
        assert variant in (None, "", "null"), \
            f"{bid}: category '{category}' без уровня 3, но variant='{variant}'"
