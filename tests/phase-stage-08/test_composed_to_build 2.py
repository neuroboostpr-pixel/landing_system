"""C1 (зона C): конвертер composed.html → файлы сборки.

Спека §4.1: всё для сборки выводится ИЗ composed.html, а не пишется руками:
  - :root-токены → tokens.from-composed.json
  - секции → block-spec.yaml (single / section-card с repeater-картами)
  - <head> → fonts-deps.yaml
  - <img> → assets-manifest.yaml
Acceptance: lint-composed-vs-spec.py проходит на сгенерированном spec.
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONVERTER = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "composed-to-build.py"
LINT = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lint-composed-vs-spec.py"

COMPOSED = """<!doctype html>
<html><head>
<meta charset="utf-8">
<title>LiXiang Dubai</title>
<meta name="theme-color" content="#112233">
<link rel="stylesheet" href="https://fonts.bunny.net/css?family=manrope:400,700|inter:400">
<style>
:root {
  --lp-bg: #ffffff;
  --lp-fg: #111111;
  --lp-accent: #cc0000;
  --lp-font-display: 'Manrope', sans-serif;
}
.lp-card { border-radius: 16px; }
</style>
</head><body>
<section id="hero" class="lp-hero">
  <h1>Автомобили LiXiang в Дубае</h1>
  <p>Полный модельный ряд с гарантией от дилера</p>
  <a class="lp-btn" href="#lead">Получить предложение</a>
  <img src="assets/photos/hero-car.png" alt="LiXiang L7">
</section>
<section id="advantages" class="lp-advantages">
  <h2>Почему мы</h2>
  <div class="lp-grid">
    <div class="lp-card"><h3>Гарантия</h3><p>Официальная гарантия 5 лет</p></div>
    <div class="lp-card"><h3>Доставка</h3><p>По всем Эмиратам за 48 часов</p></div>
    <div class="lp-card"><h3>Trade-in</h3><p>Примем ваш автомобиль в зачёт</p></div>
  </div>
</section>
</body></html>
"""


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    (proj / "07b_COMPOSED").mkdir(parents=True)
    (proj / "08_КОД").mkdir()
    (proj / "05_ДИЗАЙН-СИСТЕМА").mkdir()
    (proj / "07b_COMPOSED" / "composed.html").write_text(COMPOSED, encoding="utf-8")
    return proj


def _run(proj: Path):
    return subprocess.run(
        [sys.executable, str(CONVERTER), "--project", str(proj)],
        capture_output=True, text=True, encoding="utf-8")


def test_converter_produces_all_artifacts(tmp_path):
    proj = _make_project(tmp_path)
    r = _run(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (proj / "08_КОД" / "block-spec.yaml").exists()
    assert (proj / "08_КОД" / "fonts-deps.yaml").exists()
    assert (proj / "08_КОД" / "assets-manifest.yaml").exists()
    assert (proj / "05_ДИЗАЙН-СИСТЕМА" / "tokens.from-composed.json").exists()


def test_tokens_extracted_from_root(tmp_path):
    proj = _make_project(tmp_path)
    _run(proj)
    import json
    tokens = json.loads((proj / "05_ДИЗАЙН-СИСТЕМА" / "tokens.from-composed.json")
                        .read_text(encoding="utf-8"))
    assert tokens["--lp-accent"] == "#cc0000"
    assert "--lp-font-display" in tokens


def test_spec_has_hero_single_and_cards_section(tmp_path):
    proj = _make_project(tmp_path)
    _run(proj)
    spec = yaml.safe_load((proj / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8"))
    blocks = {b["slug"]: b for b in spec["blocks"]}
    assert "hero" in blocks and blocks["hero"]["type"] == "single"
    assert blocks["hero"]["probe_selector"] == "#hero"
    hero_controls = {c["name"] for c in blocks["hero"]["controls"]}
    assert "heading" in hero_controls
    # карточная секция
    adv = blocks["advantages"]
    assert adv["type"] == "section-card"
    assert "card" in adv
    assert len(adv["card"]["template"]) == 3
    # тексты из composed дословно в дефолтах/шаблоне
    flat = yaml.dump(spec, allow_unicode=True)
    assert "Официальная гарантия 5 лет" in flat
    assert "Получить предложение" in flat


def test_fonts_and_assets_manifest(tmp_path):
    proj = _make_project(tmp_path)
    _run(proj)
    fonts = yaml.safe_load((proj / "08_КОД" / "fonts-deps.yaml").read_text(encoding="utf-8"))
    assert any("bunny" in str(f) for f in fonts.get("stylesheets", []))
    assets = yaml.safe_load((proj / "08_КОД" / "assets-manifest.yaml").read_text(encoding="utf-8"))
    assert "assets/photos/hero-car.png" in assets["images"]


def test_lint_passes_on_generated_spec(tmp_path):
    proj = _make_project(tmp_path)
    _run(proj)
    r = subprocess.run(
        [sys.executable, str(LINT), "--project", str(proj)],
        capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


def test_existing_spec_backed_up(tmp_path):
    proj = _make_project(tmp_path)
    (proj / "08_КОД" / "block-spec.yaml").write_text("version: 1\nblocks: []\n",
                                                     encoding="utf-8")
    r = _run(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (proj / "08_КОД" / "block-spec.yaml.bak").exists()
