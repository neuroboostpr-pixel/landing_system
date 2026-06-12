"""B34 — двухуровневая семантическая таксономия (category → variant).

Модель: 11 категорий, у 5 из них есть уровень 3 (variants).
Источник истины — block-library/taxonomy.yaml, загрузчик — scripts/lib/taxonomy.py.
"""
import importlib.util
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = REPO_ROOT / "block-library" / "taxonomy.yaml"
LOADER_PATH = REPO_ROOT / "scripts" / "lib" / "taxonomy.py"

# 11 категорий, в согласованном порядке
EXPECTED_CATEGORIES = [
    "header", "hero", "marquee", "features", "content",
    "social-proof", "trust", "pricing", "forms", "faq", "footer",
]
# Категории с уровнем 3 (подкатегории)
CATEGORIES_WITH_VARIANTS = {"content", "social-proof", "trust", "pricing", "forms"}


def _load_taxonomy_yaml():
    return yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))


def _load_loader():
    spec = importlib.util.spec_from_file_location("taxonomy_lib", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- YAML структура -------------------------------------------------------

def test_taxonomy_loads():
    data = _load_taxonomy_yaml()
    assert "categories" in data


def test_has_11_categories():
    data = _load_taxonomy_yaml()
    assert len(data["categories"]) == 11


def test_category_slugs_match_expected():
    data = _load_taxonomy_yaml()
    assert set(data["categories"].keys()) == set(EXPECTED_CATEGORIES)


def test_every_category_has_ru_label():
    data = _load_taxonomy_yaml()
    # общепринятые в рунете латинские аббревиатуры — легитимные RU-метки
    allowed_latin = {"FAQ"}
    for slug, cat in data["categories"].items():
        label = cat.get("label_ru")
        assert label, f"{slug} без label_ru"
        if label in allowed_latin:
            continue
        # метка должна содержать кириллицу
        assert any("а" <= ch.lower() <= "я" for ch in label), \
            f"{slug}: метка не на русском: {label}"


def test_only_five_categories_have_variants():
    data = _load_taxonomy_yaml()
    with_variants = {
        slug for slug, cat in data["categories"].items()
        if cat.get("variants")
    }
    assert with_variants == CATEGORIES_WITH_VARIANTS


def test_variants_have_ru_labels():
    data = _load_taxonomy_yaml()
    for slug in CATEGORIES_WITH_VARIANTS:
        variants = data["categories"][slug]["variants"]
        assert variants, f"{slug} должна иметь variants"
        for vslug, v in variants.items():
            assert v.get("label_ru"), f"{slug}/{vslug} без label_ru"


def test_social_proof_has_six_variants():
    data = _load_taxonomy_yaml()
    sp = data["categories"]["social-proof"]["variants"]
    assert set(sp.keys()) == {
        "testimonials", "clients", "ratings", "numbers", "cases", "media",
    }


def test_order_unique_and_sequential():
    data = _load_taxonomy_yaml()
    orders = [cat["order"] for cat in data["categories"].values()]
    assert len(orders) == len(set(orders)), "order должен быть уникальным"
    assert sorted(orders) == list(range(1, 12)), "order — 1..11 без пропусков"


# --- Загрузчик scripts/lib/taxonomy.py ------------------------------------

def test_loader_categories_ordered():
    lib = _load_loader()
    cats = lib.categories_ordered()
    assert cats == EXPECTED_CATEGORIES


def test_loader_category_label():
    lib = _load_loader()
    assert lib.category_label("social-proof") == "Соц. доказательства"
    assert lib.category_label("hero") == "Первый экран"


def test_loader_variant_label():
    lib = _load_loader()
    assert lib.variant_label("social-proof", "testimonials") == "отзывы"
    assert lib.variant_label("pricing", "comparison") == "сравнительные таблицы"


def test_loader_has_variants():
    lib = _load_loader()
    assert lib.has_variants("social-proof") is True
    assert lib.has_variants("hero") is False
    assert lib.has_variants("footer") is False


def test_loader_valid_variant():
    lib = _load_loader()
    assert lib.valid_variant("social-proof", "testimonials") is True
    assert lib.valid_variant("social-proof", "bogus") is False
    # категория без уровня 3: валиден только None
    assert lib.valid_variant("hero", None) is True
    assert lib.valid_variant("hero", "anything") is False


def test_loader_valid_category():
    lib = _load_loader()
    assert lib.valid_category("hero") is True
    assert lib.valid_category("conversion") is False
