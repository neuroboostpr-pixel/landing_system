"""C3 (зона C): все цвета через токены — прямые цвета только в :root.

Спека §4.3: любой прямой цвет вне токенов «протекает» при смене палитры.
Исключения: бренд-цвета мессенджеров, theme-color meta, маркер /* token-exempt */.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_tokens.py"

CLEAN = """<!doctype html><html><head>
<meta name="theme-color" content="#112233">
<style>
:root { --lp-bg: #ffffff; --lp-fg: rgb(17, 17, 17); --lp-accent: #c00; }
body { background: var(--lp-bg); color: var(--lp-fg); }
.wa-icon { color: #25D366; } /* бренд WhatsApp — whitelist */
.special { background: #ff00ff; /* token-exempt */ }
</style></head><body></body></html>
"""

LEAKY = """<!doctype html><html><head><style>
:root { --lp-bg: #ffffff; }
.hero { background: #1a2b3c; }
.btn { color: rgb(200, 0, 0); }
</style></head><body></body></html>
"""


def _run(*paths):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *[str(p) for p in paths]],
        capture_output=True, text=True, encoding="utf-8")


def test_clean_html_passes(tmp_path):
    f = tmp_path / "composed.html"
    f.write_text(CLEAN, encoding="utf-8")
    r = _run(f)
    assert r.returncode == 0, r.stdout + r.stderr


def test_leaky_html_fails_with_locations(tmp_path):
    f = tmp_path / "composed.html"
    f.write_text(LEAKY, encoding="utf-8")
    r = _run(f)
    assert r.returncode == 1
    assert "#1a2b3c" in r.stdout
    assert "rgb(200, 0, 0)" in r.stdout


def test_css_file_checked_too(tmp_path):
    f = tmp_path / "main.css"
    f.write_text(":root { --a: #fff; }\n.card { border-color: #abcdef; }\n",
                 encoding="utf-8")
    r = _run(f)
    assert r.returncode == 1
    assert "#abcdef" in r.stdout


def test_multiple_files_aggregate(tmp_path):
    good = tmp_path / "ok.css"
    good.write_text(":root { --a: #fff; }\n.x { color: var(--a); }\n", encoding="utf-8")
    bad = tmp_path / "bad.css"
    bad.write_text(".y { color: #123456; }\n", encoding="utf-8")
    r = _run(good, bad)
    assert r.returncode == 1
    assert "bad.css" in r.stdout and "ok.css" not in r.stdout.split("FAIL")[-1]
