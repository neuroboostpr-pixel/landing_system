import importlib.util
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

ORCH_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
               / ".skills" / "style-decomposition" / "scripts" / "orchestrate.py")


def _load():
    spec = importlib.util.spec_from_file_location("orchestrate_mod", ORCH_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_palette():
    return [{"hex": "#ff0000", "rgb": [255, 0, 0], "source_pixel": [0, 0]}]


def _fake_fonts_yaml(path: Path, families=None):
    """Write a minimal fonts.yaml to path."""
    families = families or ["Inter"]
    data = {
        "source_url": "https://example.com",
        "method": "DOM CSS inspection",
        "candidates": [{"family": f, "full_stack": f, "source": "DOM", "confidence": 1.0} for f in families],
        "manual_review_required": False,
    }
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")


def _fake_icons_result():
    return {
        "needed": ["check", "arrow-right"],
        "matches": {"check": ["lucide:check"], "arrow-right": ["lucide:arrow-right"]},
        "recommendation": {"library": "lucide", "reason": "covers 2/2 icons"},
    }


def test_orchestrate_writes_5_output_files(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "refs"
    refs_dir.mkdir()
    extracted_dir = tmp_path / "04_БРЕНД" / "extracted"
    extracted_dir.mkdir(parents=True)

    # Create a small test image (1x1 red PNG)
    from PIL import Image
    img_path = tmp_path / "test.png"
    Image.new("RGB", (50, 50), (200, 50, 50)).save(str(img_path))

    with patch.object(mod, "extract", return_value=_fake_palette()) as mock_extract, \
         patch.object(mod, "identify_url") as mock_fonts, \
         patch.object(mod, "match_icons") as mock_icons:

        # identify_url should write a fonts.yaml
        def fake_identify(url, out_path):
            _fake_fonts_yaml(Path(out_path))

        mock_fonts.side_effect = fake_identify
        mock_icons.return_value = _fake_icons_result()

        result = mod.run_style_extraction(
            refs_dir=str(tmp_path),
            image_paths=[str(img_path)],
            reference_url="https://example.com",
        )

    # All 5 outputs must exist
    assert "palette" in result
    assert "fonts" in result
    assert "icons" in result
    assert "grid" in result
    assert "motion" in result

    for key, path_str in result.items():
        assert Path(path_str).exists(), f"{key} file missing: {path_str}"


def test_orchestrate_calls_extract_for_each_image(tmp_path):
    mod = _load()

    from PIL import Image
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.png"
    Image.new("RGB", (50, 50), (200, 50, 50)).save(str(img1))
    Image.new("RGB", (50, 50), (50, 200, 50)).save(str(img2))

    with patch.object(mod, "extract", return_value=_fake_palette()) as mock_extract, \
         patch.object(mod, "identify_url") as mock_fonts, \
         patch.object(mod, "match_icons", return_value=_fake_icons_result()):

        mock_fonts.side_effect = lambda url, out_path: _fake_fonts_yaml(Path(out_path))

        mod.run_style_extraction(
            refs_dir=str(tmp_path),
            image_paths=[str(img1), str(img2)],
        )

    # extract called for each image
    assert mock_extract.call_count == 2


def test_orchestrate_skips_fonts_if_no_url(tmp_path):
    mod = _load()

    from PIL import Image
    img_path = tmp_path / "test.png"
    Image.new("RGB", (50, 50), (100, 100, 100)).save(str(img_path))

    with patch.object(mod, "extract", return_value=_fake_palette()), \
         patch.object(mod, "identify_url") as mock_fonts, \
         patch.object(mod, "match_icons", return_value=_fake_icons_result()):

        mod.run_style_extraction(
            refs_dir=str(tmp_path),
            image_paths=[str(img_path)],
            reference_url=None,
        )

    # identify_url must NOT be called when no URL is provided
    mock_fonts.assert_not_called()


def test_orchestrate_returns_all_5_paths(tmp_path):
    mod = _load()

    from PIL import Image
    img_path = tmp_path / "test.png"
    Image.new("RGB", (50, 50), (100, 100, 200)).save(str(img_path))

    with patch.object(mod, "extract", return_value=_fake_palette()), \
         patch.object(mod, "identify_url", side_effect=lambda url, p: _fake_fonts_yaml(Path(p))), \
         patch.object(mod, "match_icons", return_value=_fake_icons_result()):

        result = mod.run_style_extraction(
            refs_dir=str(tmp_path),
            image_paths=[str(img_path)],
            reference_url="https://example.com",
        )

    expected_keys = {"palette", "fonts", "icons", "grid", "motion"}
    assert set(result.keys()) == expected_keys
