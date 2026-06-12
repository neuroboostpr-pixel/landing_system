"""B2 (зона B): verify-composed-premium v2 — чек-лист из спеки §3.2.

ОБЯЗАТЕЛЬНО (fail): :root-токены, clamp(), движение, :hover,
prefers-reduced-motion, production-голова (og:title+og:image, favicon,
theme-color, шрифты), ЗАПРЕТ эмодзи в <h1>–<h3>.
Старые «13 интерактивных фич» (parallax/slider/lightbox...) — рекомендации
(warn), не fail.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SH = ROOT / "scripts" / "verify-composed-premium.sh"

GOOD_HTML = """<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="theme-color" content="#112233">
<meta property="og:title" content="LiXiang Dubai">
<meta property="og:image" content="assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.png">
<link rel="stylesheet" href="https://fonts.bunny.net/css?family=inter:400">
<style>
:root { --lp-bg: #fff; --lp-accent: #c00; }
h1 { font-size: clamp(2rem, 5vw, 4rem); }
.card:hover { transform: translateY(-4px); }
@media (prefers-reduced-motion: reduce) { * { animation: none; } }
</style>
</head><body>
<h1>Автомобили LiXiang</h1>
<h2>Модельный ряд</h2>
<section><p>Текст</p></section>
<script>
new IntersectionObserver(() => {});
</script>
</body></html>
"""


def _run(tmp_path: Path, html: str):
    f = tmp_path / "composed.html"
    f.write_text(html, encoding="utf-8")
    return subprocess.run(["bash", str(SH), str(f)],
                          capture_output=True, text=True, encoding="utf-8")


def test_good_composed_passes(tmp_path):
    r = _run(tmp_path, GOOD_HTML)
    assert r.returncode == 0, r.stdout + r.stderr


def test_emoji_in_heading_fails(tmp_path):
    bad = GOOD_HTML.replace("<h2>Модельный ряд</h2>", "<h2>🎯 Модельный ряд</h2>")
    r = _run(tmp_path, bad)
    assert r.returncode == 1, r.stdout
    assert "эмодзи" in (r.stdout + r.stderr).lower()


def test_missing_og_fails(tmp_path):
    bad = GOOD_HTML.replace('<meta property="og:title" content="LiXiang Dubai">', "")
    r = _run(tmp_path, bad)
    assert r.returncode == 1, r.stdout


def test_missing_clamp_fails(tmp_path):
    bad = GOOD_HTML.replace("clamp(2rem, 5vw, 4rem)", "48px")
    r = _run(tmp_path, bad)
    assert r.returncode == 1, r.stdout


def test_missing_motion_fails(tmp_path):
    bad = GOOD_HTML.replace("new IntersectionObserver(() => {});", "")
    bad = bad.replace(".card:hover { transform: translateY(-4px); }",
                      ".card { color: var(--lp-accent); }")
    r = _run(tmp_path, bad)
    assert r.returncode == 1, r.stdout


def test_old_features_are_warnings_not_failures(tmp_path):
    """Нет parallax/slider/lightbox — это warn, НЕ fail (спека: декор под
    потребность места, не обязательный набор эффектов)."""
    r = _run(tmp_path, GOOD_HTML)  # GOOD_HTML не содержит slider/lightbox
    assert r.returncode == 0, r.stdout


def test_missing_file_exit_2(tmp_path):
    r = subprocess.run(["bash", str(SH), str(tmp_path / "nope.html")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2
