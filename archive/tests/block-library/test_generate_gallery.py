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


def test_real_gallery_covers_all_catalog_blocks(tmp_path):
    # canonical-генератор на РЕАЛЬНОЙ библиотеке: каждый id каталога — в gallery,
    # у каждого блока iframe-превью. (Заменяет tests/phase-pra/test-gallery.bats,
    # который зависел от удалённого render-gallery.py и сломанного на Windows python3.)
    lib = REPO_ROOT / "block-library"
    catalog = yaml.safe_load((lib / "catalog.yaml").read_text(encoding="utf-8"))
    ids = [b["id"] for b in catalog["blocks"]]
    out = tmp_path / "gallery.html"
    r = _run(lib, out)
    assert r.returncode == 0, r.stderr
    html = out.read_text(encoding="utf-8")
    for bid in ids:
        assert f'data-id="{bid}"' in html, f"блок {bid} отсутствует в gallery"
    # iframe-превью на каждый блок
    assert html.count("<iframe") >= len(ids), "не у каждого блока есть iframe-превью"


def _load_gallery_module():
    spec = importlib.util.spec_from_file_location("generate_gallery", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_extract_srcdoc_falls_back_to_template(tmp_path):
    g = _load_gallery_module()
    bd = tmp_path / "blk"
    (bd / "assets").mkdir(parents=True)
    # нет index.html, но есть assets/template.html
    (bd / "assets" / "template.html").write_text(
        '<section class="lp-x"><h2>{{slot:title}}</h2></section>', encoding="utf-8"
    )
    src = g.extract_srcdoc("blk", bd)
    # template подхвачен как fallback; {{slot}} заполнены демо (Фаза 4)
    assert "lp-x" in src, "template.html не подхвачен как fallback"
    assert "{{slot:" not in src, "сырой {{slot}} должен быть заменён демо-контентом"


def test_extract_srcdoc_prefers_index_over_template(tmp_path):
    g = _load_gallery_module()
    bd = tmp_path / "blk"
    (bd / "assets").mkdir(parents=True)
    (bd / "index.html").write_text("<main>INDEX</main>", encoding="utf-8")
    (bd / "assets" / "template.html").write_text("<main>TEMPLATE</main>", encoding="utf-8")
    src = g.extract_srcdoc("blk", bd)
    assert "INDEX" in src and "TEMPLATE" not in src


def test_template_content_reaches_card_srcdoc(tmp_path):
    # на уровне всей генерации: блок без index.html всё равно получает реальный
    # srcdoc из template.html, а не заглушку с именем
    lib = tmp_path / "block-library"
    blocks = [{"id": "c-1", "path": "contacts/c-1/", "folder": "contacts",
               "category": "footer", "variant": None, "layout_pattern": "grid",
               "display_name_ru": "c-1 (grid)"}]
    _make_catalog(lib, blocks)
    (lib / "contacts" / "c-1" / "assets").mkdir(parents=True, exist_ok=True)
    (lib / "contacts" / "c-1" / "assets" / "template.html").write_text(
        '<section class="real-block">CONTACT FORM</section>', encoding="utf-8"
    )
    out = tmp_path / "gallery.html"
    r = _run(lib, out)
    assert r.returncode == 0, r.stderr
    html = out.read_text(encoding="utf-8")
    assert "real-block" in html, "template-контент не попал в srcdoc карточки"


def test_demo_value_by_slot_semantics(tmp_path):
    g = _load_gallery_module()
    # хвост имени определяет тип демо-значения
    assert "₽" in g.demo_value("plan-1-price")
    assert g.demo_value("primary-cta-label")  # непустая метка кнопки
    assert g.demo_value("feature-2-title")
    assert g.demo_value("faq-1-q").endswith("?")
    # url/href → #
    assert g.demo_value("nav-link-1-url") == "#"
    # value/number → число
    assert any(ch.isdigit() for ch in g.demo_value("stat-1-value"))
    # неизвестный слот → не пусто и не {{slot}}
    v = g.demo_value("some-weird-slot")
    assert v and "{{" not in v


def test_gallery_srcdoc_has_no_raw_slots(tmp_path):
    # после демо-подстановки в превью не остаётся сырых {{slot:}}
    lib = tmp_path / "block-library"
    blocks = [{"id": "b-1", "path": "hero/b-1/", "folder": "hero",
               "category": "hero", "variant": None, "layout_pattern": "split",
               "display_name_ru": "b-1 (split)"}]
    _make_catalog(lib, blocks)
    (lib / "hero" / "b-1" / "assets").mkdir(parents=True, exist_ok=True)
    (lib / "hero" / "b-1" / "assets" / "template.html").write_text(
        '<section><h1>{{slot:headline}}</h1><a>{{slot:primary-cta-label}}</a></section>',
        encoding="utf-8",
    )
    out = tmp_path / "gallery.html"
    r = _run(lib, out)
    assert r.returncode == 0, r.stderr
    html = out.read_text(encoding="utf-8")
    # в srcdoc карточки нет сырого {{slot:
    m = re.search(r'data-id="b-1".*?</article>', html, re.S)
    card = m.group(0) if m else ""
    assert "{{slot:" not in card, "в превью остались сырые {{slot}}"


def test_preview_button_is_clickable_and_opens_modal(tmp_path):
    html = _build(tmp_path)
    # кнопка больше не заглушка
    assert 'onclick="return false;"' not in html, "кнопка осталась нерабочей заглушкой"
    # есть элемент модального окна и его iframe
    assert 'id="preview-modal"' in html
    assert 'id="preview-frame"' in html
    # кнопка «Просмотр» вызывает открытие модалки
    assert "openPreview" in html
    # закрытие по Esc реализовано
    assert "Escape" in html
