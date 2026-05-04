import importlib.util
import json
from pathlib import Path

COLLECT_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                  / "skills" / "client-assets-collection" / "scripts" / "collect.py")


def _load():
    spec = importlib.util.spec_from_file_location("collect_mod", COLLECT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_manifest_from_filesystem(temp_project):
    mod = _load()
    materials = temp_project / "02_МАТЕРИАЛЫ_КЛИЕНТА"
    photos_orig = materials / "photos" / "original"
    photos_orig.mkdir(parents=True)
    (photos_orig / "hero.jpg").write_bytes(b"FAKE_JPG")
    (photos_orig / "about.png").write_bytes(b"FAKE_PNG")
    videos = materials / "videos"
    videos.mkdir()
    (videos / "testimonial.mp4").write_bytes(b"FAKE_MP4")

    manifest = mod.build_manifest(materials)
    assert len(manifest["photos"]) == 2
    assert len(manifest["videos"]) == 1
    photo_names = {p["filename"] for p in manifest["photos"]}
    assert {"hero.jpg", "about.png"} == photo_names


def test_render_gallery_html(temp_project):
    mod = _load()
    materials = temp_project / "02_МАТЕРИАЛЫ_КЛИЕНТА"
    (materials / "photos" / "original").mkdir(parents=True)
    (materials / "photos" / "original" / "hero.jpg").write_bytes(b"X")

    html_path = mod.render_gallery(materials)
    assert html_path.exists()
    content = html_path.read_text()
    assert "<!DOCTYPE html>" in content
    assert "hero.jpg" in content


def test_run_writes_manifest_yaml(temp_project):
    mod = _load()
    materials = temp_project / "02_МАТЕРИАЛЫ_КЛИЕНТА"
    (materials / "photos" / "original").mkdir(parents=True)
    (materials / "photos" / "original" / "test.jpg").write_bytes(b"X")

    mod.run(str(materials))
    yml = materials / "assets-manifest.yaml"
    assert yml.exists()
    assert "test.jpg" in yml.read_text(encoding="utf-8")
