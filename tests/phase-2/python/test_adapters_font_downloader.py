from pathlib import Path
import responses
from tools.adapters.font_downloader import (
    google_fonts_css_url, fontshare_css_url, download_woff2
)


def test_google_fonts_url():
    url = google_fonts_css_url("Inter", [400, 700])
    assert "fonts.bunny.net" in url
    assert "Inter" in url
    assert "400;700" in url


def test_fontshare_url():
    url = fontshare_css_url("cabinet-grotesk", [500, 700, 800])
    assert "api.fontshare.com" in url
    assert "cabinet-grotesk" in url
    assert "500,700,800" in url


def test_download_woff2(http_mock, tmp_path):
    http_mock.add(
        responses.GET,
        "https://example.com/inter-400.woff2",
        body=b"WOFF2_BYTES",
        status=200,
    )
    out = download_woff2("https://example.com/inter-400.woff2", str(tmp_path))
    assert out.exists()
    assert out.read_bytes() == b"WOFF2_BYTES"
    assert out.name == "inter-400.woff2"
