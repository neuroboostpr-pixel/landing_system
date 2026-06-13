"""Re-render composed.html: подстановка визуалов/фото в placeholders
(замена машинного compose-blocks из блочного трека)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "block-composition" / "scripts" / "rerender-composed.py"

HTML = """<html><body>
<section id="hero"><div data-slot="hero-photo"></div></section>
<section id="features">
  <div class="card">[SLOT: feature-1-icon]<h3>А</h3></div>
  <div class="card"><span data-slot="feature-2-icon"></span><h3>Б</h3></div>
</section>
</body></html>
"""


def _proj(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "07b_COMPOSED").mkdir(parents=True)
    (proj / "07b_COMPOSED" / "composed.html").write_text(HTML, encoding="utf-8")
    icons = proj / "07d_VISUALS" / "icons"
    icons.mkdir(parents=True)
    (icons / "feature-1-icon.png").write_bytes(b"\x89PNG\r\n\x00")
    (icons / "feature-2-icon.png").write_bytes(b"\x89PNG\r\n\x00")
    # Реальный контракт photo-pipeline: processed/manifest.json + processed/*.jpg
    processed = proj / "07c_PHOTOS" / "processed"
    processed.mkdir(parents=True)
    (processed / "hero-photo.jpg").write_bytes(b"\xff\xd8\xff\x00")
    (processed / "hero-photo-mobile.jpg").write_bytes(b"\xff\xd8\xff\x00")
    import json as _json
    (processed / "manifest.json").write_text(_json.dumps({
        "hero-photo.jpg": {"slot": "hero-photo", "status": "processed",
                            "path": str(processed / "hero-photo.jpg")}
    }), encoding="utf-8")
    return proj


def _run(proj: Path):
    return subprocess.run([sys.executable, str(SCRIPT), "--project", str(proj)],
                          capture_output=True, text=True, encoding="utf-8")


def test_replaces_marker_dataslot_and_photo(tmp_path):
    proj = _proj(tmp_path)
    r = _run(proj)
    assert r.returncode == 0, r.stdout + r.stderr
    out = (proj / "07b_COMPOSED" / "composed.html").read_text(encoding="utf-8")
    assert "[SLOT:" not in out
    assert 'src="07d_VISUALS/icons/feature-1-icon.png"' in out
    assert "feature-2-icon.png" in out
    assert "<picture>" in out and "hero-photo-mobile.jpg" in out
    assert "hero-photo.jpg" in out
    assert (proj / "07b_COMPOSED" / "composed.html.bak").exists()


def test_noop_when_nothing_to_replace(tmp_path):
    proj = tmp_path / "p2"
    (proj / "07b_COMPOSED").mkdir(parents=True)
    (proj / "07b_COMPOSED" / "composed.html").write_text(
        "<html><body><p>нет слотов</p></body></html>", encoding="utf-8")
    r = _run(proj)
    assert r.returncode == 0
    assert not (proj / "07b_COMPOSED" / "composed.html.bak").exists()
