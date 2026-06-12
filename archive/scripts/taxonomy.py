"""B34 taxonomy loader — единый доступ к словарю category → variant.

Источник истины: block-library/taxonomy.yaml.
Все потребители (generate-catalog, generate-gallery, match-candidates,
render-wireframe) читают метки и валидируют значения через этот модуль,
никаких хардкод-словарей в коде или HTML.

Публичный API:
  load_taxonomy()                      -> dict (raw, кэшируется)
  categories_ordered()                 -> list[str]  (слаги в порядке order)
  category_label(slug)                 -> str        (русская метка)
  variant_label(cat, vslug)            -> str        (русская метка подкатегории)
  has_variants(cat)                    -> bool
  variants_ordered(cat)                -> list[str]  (слаги подкатегорий)
  valid_category(slug)                 -> bool
  valid_variant(cat, vslug_or_None)    -> bool
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "block-library" / "taxonomy.yaml"


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else TAXONOMY_PATH
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if "categories" not in data:
        raise ValueError(f"taxonomy.yaml: нет ключа 'categories' ({p})")
    return data


def _categories() -> dict:
    return load_taxonomy()["categories"]


def categories_ordered() -> list[str]:
    """Слаги категорий в согласованном порядке (поле order)."""
    cats = _categories()
    return sorted(cats.keys(), key=lambda s: cats[s].get("order", 999))


def category_label(slug: str) -> str:
    """Русская метка категории. KeyError если слаг неизвестен."""
    return _categories()[slug]["label_ru"]


def has_variants(cat: str) -> bool:
    """Есть ли у категории уровень 3 (непустой словарь variants)."""
    return bool(_categories().get(cat, {}).get("variants"))


def variants_ordered(cat: str) -> list[str]:
    """Слаги подкатегорий в порядке объявления (пустой список если нет)."""
    return list(_categories().get(cat, {}).get("variants", {}).keys())


def variant_label(cat: str, vslug: str) -> str:
    """Русская метка подкатегории. KeyError если cat/vslug неизвестны."""
    return _categories()[cat]["variants"][vslug]["label_ru"]


def valid_category(slug: str) -> bool:
    return slug in _categories()


def valid_variant(cat: str, vslug: str | None) -> bool:
    """Валиден ли variant для категории.

    - Категория без уровня 3: валиден ТОЛЬКО None (B34 решение 1).
    - Категория с уровнем 3: valid если vslug есть в её variants.
    """
    if not valid_category(cat):
        return False
    if has_variants(cat):
        return vslug in _categories()[cat]["variants"]
    return vslug is None
