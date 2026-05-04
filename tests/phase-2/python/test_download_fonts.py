import importlib.util
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

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


def test_download_fonts_calls_downloader_for_each_font(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter", "Cabinet Grotesk"])
    output_dir = tmp_path / "fonts-cache"

    fake_path = output_dir / "inter.woff2"
    with patch.object(mod, "download_woff2", return_value=fake_path) as mock_dl:
        result = mod.download_fonts(str(fonts_yaml), str(output_dir))

    # Should be called once per font family
    assert mock_dl.call_count == 2


def test_download_fonts_returns_list_of_paths(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter"])
    output_dir = tmp_path / "fonts-cache"

    fake_path = output_dir / "inter.woff2"
    with patch.object(mod, "download_woff2", return_value=fake_path):
        result = mod.download_fonts(str(fonts_yaml), str(output_dir))

    assert isinstance(result, list)
    assert len(result) == 1


def test_download_fonts_skips_failed_downloads(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, ["Inter", "NonExistent"])
    output_dir = tmp_path / "fonts-cache"

    from tools.adapters.font_downloader import FontDownloadError

    def side_effect(url, target_dir, filename=None):
        if "NonExistent" in url or "nonexistent" in url.lower():
            raise FontDownloadError("HTTP 404")
        return output_dir / "inter.woff2"

    with patch.object(mod, "download_woff2", side_effect=side_effect):
        result = mod.download_fonts(str(fonts_yaml), str(output_dir))

    # Should succeed for Inter, skip NonExistent
    assert len(result) == 1


def test_download_fonts_empty_candidates(tmp_path):
    mod = _load()
    fonts_yaml = _make_fonts_yaml(tmp_path, [])
    output_dir = tmp_path / "fonts-cache"

    with patch.object(mod, "download_woff2") as mock_dl:
        result = mod.download_fonts(str(fonts_yaml), str(output_dir))

    mock_dl.assert_not_called()
    assert result == []
