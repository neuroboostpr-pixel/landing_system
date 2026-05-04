"""Tests for download-fonts.py including Block D regression tests."""
import importlib.util
import re
import yaml
from pathlib import Path
import responses as resp_lib
import pytest

DOWNLOAD_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                   / "skills" / "style-decomposition" / "scripts" / "download-fonts.py")


def _load():
    spec = importlib.util.spec_from_file_location("download_fonts_mod", DOWNLOAD_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_fonts_yaml(tmp_path, families):
    """Create a fonts.yaml fixture with given font families."""
    data = {
        "source_url": "https://example.com",
        "method": "DOM CSS inspection (Playwright)",
        "candidates": [
            {
                "family": fam,
                "full_stack": f'"{fam}", sans-serif',
                "source": "DOM computed style",
                "confidence": 1.0,
            }
            for fam in families
        ],
        "manual_review_required": False,
    }
    fonts_yaml = tmp_path / "fonts.yaml"
    fonts_yaml.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return fonts_yaml


INTER_CSS = """
@font-face {
  font-family: 'Inter';
  src: url('https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2') format('woff2');
}
"""
CABINET_CSS = """
@font-face {
  font-family: 'Cabinet Grotesk';
  src: url('https://fonts.bunny.net/cabinet-grotesk/files/cabinet-grotesk-latin-400-normal.woff2') format('woff2');
}
"""
WOFF2_BYTES = b"wOF2" + b"\x00" * 20


@resp_lib.activate
def test_download_fonts_calls_downloader_for_each_font(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter", "Cabinet Grotesk"])
    output_dir = tmp_path / "fonts-cache"

    # CSS for Inter
    resp_lib.add(resp_lib.GET, re.compile(r"https://fonts\.bunny\.net/css\?family=Inter.*"),
                 body=INTER_CSS, status=200, content_type="text/css")
    # CSS for Cabinet Grotesk
    resp_lib.add(resp_lib.GET, re.compile(r"https://fonts\.bunny\.net/css\?family=Cabinet.*"),
                 body=CABINET_CSS, status=200, content_type="text/css")
    # Binary for Inter
    resp_lib.add(resp_lib.GET,
                 "https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2",
                 body=WOFF2_BYTES, status=200)
    # Binary for Cabinet Grotesk
    resp_lib.add(resp_lib.GET,
                 "https://fonts.bunny.net/cabinet-grotesk/files/cabinet-grotesk-latin-400-normal.woff2",
                 body=WOFF2_BYTES, status=200)

    result = mod.download_fonts(str(fonts_yaml), str(output_dir))
    # Should return one path per font family
    assert len(result) == 2


@resp_lib.activate
def test_download_fonts_returns_list_of_paths(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter"])
    output_dir = tmp_path / "fonts-cache"

    resp_lib.add(resp_lib.GET, re.compile(r"https://fonts\.bunny\.net/css.*"),
                 body=INTER_CSS, status=200, content_type="text/css")
    resp_lib.add(resp_lib.GET,
                 "https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2",
                 body=WOFF2_BYTES, status=200)

    result = mod.download_fonts(str(fonts_yaml), str(output_dir))
    assert isinstance(result, list)
    assert len(result) == 1


@resp_lib.activate
def test_download_fonts_skips_failed_downloads(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter", "NonExistent"])
    output_dir = tmp_path / "fonts-cache"

    # Inter succeeds
    resp_lib.add(resp_lib.GET, re.compile(r"https://fonts\.bunny\.net/css\?family=Inter.*"),
                 body=INTER_CSS, status=200, content_type="text/css")
    resp_lib.add(resp_lib.GET,
                 "https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2",
                 body=WOFF2_BYTES, status=200)
    # NonExistent returns 404 on CSS
    resp_lib.add(resp_lib.GET, re.compile(r"https://fonts\.bunny\.net/css\?family=NonExistent.*"),
                 body="", status=404)

    result = mod.download_fonts(str(fonts_yaml), str(output_dir))
    # Should succeed for Inter, skip NonExistent
    assert len(result) == 1


def test_download_fonts_empty_candidates(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, [])
    output_dir = tmp_path / "fonts-cache"

    result = mod.download_fonts(str(fonts_yaml), str(output_dir))
    assert result == []


# ---------------------------------------------------------------------------
# Block D regression tests (C1, I1)
# ---------------------------------------------------------------------------

SAMPLE_CSS = """
@font-face {
  font-family: 'Inter';
  src: url('https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2') format('woff2');
}
"""
WOFF2_MAGIC = b"wOF2" + b"\x00" * 20  # minimal mock binary


def test_css_url_no_double_encoding():
    """I1: spaces in family names must become '+', not '%2B'."""
    mod = _load()
    url = mod._bunny_woff2_url("Cabinet Grotesk", 400)
    assert "Cabinet+Grotesk" in url
    assert "%2B" not in url


@resp_lib.activate
def test_two_step_download_fetches_binary(tmp_path):
    """C1: verify that download_fonts does CSS -> parse -> binary fetch."""
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter"])

    # Step 1: CSS endpoint returns CSS text
    resp_lib.add(
        resp_lib.GET,
        re.compile(r"https://fonts\.bunny\.net/css.*"),
        body=SAMPLE_CSS,
        status=200,
        content_type="text/css",
    )
    # Step 2: WOFF2 binary endpoint
    resp_lib.add(
        resp_lib.GET,
        "https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2",
        body=WOFF2_MAGIC,
        status=200,
        content_type="font/woff2",
    )

    result = mod.download_fonts(str(fonts_yaml), str(tmp_path / "out"))
    assert len(result) == 1
    saved = result[0]
    assert saved.exists()
    assert saved.read_bytes()[:4] == b"wOF2"


@resp_lib.activate
def test_invalid_magic_bytes_skipped(tmp_path):
    """C1: files with wrong magic bytes are deleted and not returned."""
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter"])

    resp_lib.add(
        resp_lib.GET,
        re.compile(r"https://fonts\.bunny\.net/css.*"),
        body=SAMPLE_CSS,
        status=200,
        content_type="text/css",
    )
    resp_lib.add(
        resp_lib.GET,
        "https://fonts.bunny.net/inter/files/inter-latin-400-normal.woff2",
        body=b"GARBAGE_DATA_NOT_WOFF2",
        status=200,
    )

    result = mod.download_fonts(str(fonts_yaml), str(tmp_path / "out"))
    assert len(result) == 0
