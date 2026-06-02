"""B34 Фаза 4 — галерея: 2 комбобокса category→variant, русский UI.

Правила:
- Комбобокс 1 «Категория»: русские метки из taxonomy.yaml, порядок order.
- Комбобокс 2 «Подкатегория»: русские метки вариантов; для категорий БЕЗ
  уровня 3 второй комбобокс скрыт (display:none), не просто disabled.
- В видимых лейблах фильтров нет англоязычных слагов категорий.
- JS-карта CAT_VARIANTS содержит для social-proof все 6 вариантов.
- Карточки несут data-variant.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate-gallery.py"
LOADER_PATH = REPO_ROOT / "scripts" / "lib" / "taxonomy.py"


def _load_loader():
    spec = importlib.util.spec_from_file_location("taxonomy_lib_gallery_test", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_catalog(lib: Path, blocks: list[dict]):
    lib.mkdir(parents=True, exist_ok=True)
    (lib / "catalog.yaml").write_text(
        yaml.dump({"version": 3, "blocks": blocks}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    # каждый блок нуждается в папке (для srcdoc) — пустой index ok
    for b in blocks:
        bd = lib / b["path"]
        bd.mkdir(parents=True, exist_ok=True)


def _run(lib: Path, out: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--library", str(lib), "--output", str(out)],
        capture_output=True, text=True,
    )


def _sample_blocks():
    # hero (no variant), footer (no variant), social-proof x6 variants, forms/quiz
    blocks = [
        {"id": "hero-1", "path": "hero/hero-1/", "folder": "hero",
         "category": "hero", "variant": None, "layout_pattern": "split",
         "display_name_ru": "Герой"},
        {"id": "footer-1", "path": "footer/footer-1/", "folder": "footer",
         "category": "footer", "variant": None, "layout_pattern": "grid-4",
         "display_name_ru": "Подвал"},
        {"id": "quiz-1", "path": "quiz/quiz-1/", "folder": "quiz",
         "category": "forms", "variant": "quiz", "layout_pattern": "step",
         "display_name_ru": "Квиз"},
    ]
    sp_variants = ["testimonials", "clients", "ratings", "numbers", "cases", "media"]
    for i, v in enumerate(sp_variants):
        blocks.append({
            "id": f"sp-{i}", "path": f"social-proof/sp-{i}/", "folder": "social-proof",
            "category": "social-proof", "variant": v, "layout_pattern": "grid-3",
            "display_name_ru": f"SP {v}",
        })
    return blocks


def _build(tmp_path):
    lib = tmp_path / "block-library"
    out = tmp_path / "gallery.html"
    _make_catalog(lib, _sample_blocks())
    r = _run(lib, out)
    assert r.returncode == 0, r.stderr
    return out.read_text(encoding="utf-8")


def _extract_js_map(html: str, name: str) -> dict:
    m = re.search(rf"const {name} = (\{{.*?\}});", html, re.S)
    assert m, f"не найдена JS-карта {name}"
    return json.loads(m.group(1))


def test_category_combobox_has_russian_labels_in_order(tmp_path):
    html = _build(tmp_path)
    tax = _load_loader()
    # русские метки присутствуют
    for cat in ["hero", "social-proof", "forms"]:
        assert tax.category_label(cat) in html, f"нет рус. метки для {cat}"
    # порядок: hero раньше social-proof раньше forms (по order)
    i_hero = html.index(tax.category_label("hero"))
    i_sp = html.index(tax.category_label("social-proof"))
    i_forms = html.index(tax.category_label("forms"))
    assert i_hero < i_sp < i_forms, "категории не в порядке order"


def test_cat_variants_map_has_six_social_proof_variants(tmp_path):
    html = _build(tmp_path)
    cv = _extract_js_map(html, "CAT_VARIANTS")
    assert "social-proof" in cv
    assert len(cv["social-proof"]) == 6, f"ожидалось 6 вариантов, есть {len(cv['social-proof'])}"
    # для категорий без variants — пусто/нет ключа
    assert not cv.get("hero"), "hero не должен иметь вариантов"
    assert not cv.get("footer"), "footer не должен иметь вариантов"


def test_variant_labels_are_russian(tmp_path):
    html = _build(tmp_path)
    cv = _extract_js_map(html, "CAT_VARIANTS")
    tax = _load_loader()
    # каждая метка варианта — русская из taxonomy
    for vslug, info in cv["social-proof"].items():
        assert info["label"] == tax.variant_label("social-proof", vslug)
    # английские слаги не должны быть видимыми метками (label != slug)
    assert cv["social-proof"]["numbers"]["label"] == "цифры"


def test_cards_carry_data_variant(tmp_path):
    html = _build(tmp_path)
    assert 'data-variant="quiz"' in html
    assert 'data-variant="testimonials"' in html
    # блоки без variant — пустой data-variant
    assert re.search(r'data-id="hero-1"[^>]*data-variant=""', html) or \
           re.search(r'data-variant=""[^>]*data-id="hero-1"', html), \
           "hero-1 должен иметь пустой data-variant"
