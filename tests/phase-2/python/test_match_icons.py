import importlib.util
import yaml
from pathlib import Path
from unittest.mock import patch

ICONS_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / "skills" / "style-decomposition" / "scripts" / "match-icons.py")


def _load():
    spec = importlib.util.spec_from_file_location("match_icons_mod", ICONS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_search(query, limit=32, prefix=""):
    """Fake iconify search returning predictable results."""
    results = []
    for pfx in ["lucide", "phosphor", "heroicons", "tabler"]:
        if prefix and prefix != pfx:
            continue
        results.append({"prefix": pfx, "name": query, "id": f"{pfx}:{query}"})
    return results


def test_match_icons_returns_matches_per_name(tmp_path):
    mod = _load()
    out = tmp_path / "icons.yaml"
    with patch.object(mod, "search", side_effect=_fake_search):
        result = mod.match_icons(["check", "arrow-right"], str(out))

    assert "check" in result["matches"]
    assert "arrow-right" in result["matches"]
    # Each should have matches from multiple libraries
    assert len(result["matches"]["check"]) > 0
    assert len(result["matches"]["arrow-right"]) > 0


def test_match_icons_groups_by_prefix(tmp_path):
    mod = _load()
    out = tmp_path / "icons.yaml"
    with patch.object(mod, "search", side_effect=_fake_search):
        result = mod.match_icons(["check", "user"], str(out))

    # All icons in 'check' matches should be in format "prefix:name"
    for icon_id in result["matches"]["check"]:
        assert ":" in icon_id


def test_match_icons_recommends_library(tmp_path):
    mod = _load()
    out = tmp_path / "icons.yaml"
    with patch.object(mod, "search", side_effect=_fake_search):
        result = mod.match_icons(["check", "arrow-right", "user"], str(out))

    assert "recommendation" in result
    assert "library" in result["recommendation"]
    assert "reason" in result["recommendation"]
    # Recommendation must be a known library prefix
    assert result["recommendation"]["library"] in {"lucide", "phosphor", "heroicons", "tabler", "material-symbols"}


def test_match_icons_writes_yaml(tmp_path):
    mod = _load()
    out = tmp_path / "icons.yaml"
    with patch.object(mod, "search", side_effect=_fake_search):
        mod.match_icons(["check"], str(out))

    assert out.exists()
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert "needed" in data
    assert "matches" in data
    assert "recommendation" in data


def test_match_icons_needed_list_preserved(tmp_path):
    mod = _load()
    out = tmp_path / "icons.yaml"
    needed = ["check", "arrow-right", "user", "x", "sparkles"]
    with patch.object(mod, "search", side_effect=_fake_search):
        result = mod.match_icons(needed, str(out))

    assert result["needed"] == needed
