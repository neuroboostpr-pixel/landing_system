import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "references-collection" / "scripts" / "validate-url.py"

def _load():
    spec = importlib.util.spec_from_file_location("validate_url", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_accessible_url_returns_true():
    mod = _load()
    result = mod.check_url_accessible("https://httpbin.org/get")
    assert result is True

def test_inaccessible_url_returns_false():
    mod = _load()
    result = mod.check_url_accessible("https://this-domain-does-not-exist-xyz123.com")
    assert result is False

def test_known_blocked_platform_returns_false():
    mod = _load()
    result = mod.check_url_accessible("https://www.behance.net/gallery/246960855/test")
    assert isinstance(result, bool)

def test_known_blocked_platforms_list():
    mod = _load()
    assert mod.is_known_blocked("https://www.behance.net/gallery/123")
    assert mod.is_known_blocked("https://www.instagram.com/p/abc")
    assert mod.is_known_blocked("https://tilda.cc/page123")
    assert not mod.is_known_blocked("https://example.com")

def test_add_ref_has_palette_extracted_field(tmp_path):
    import importlib.util as ilu
    INDEX = ROOT / "skills" / "references-collection" / "scripts" / "index.py"
    spec2 = ilu.spec_from_file_location("index", INDEX)
    mod2 = ilu.module_from_spec(spec2)
    spec2.loader.exec_module(mod2)

    entry = mod2.add_ref(str(tmp_path), "https://example.com", "url", "candidate")
    assert "palette_extracted" in entry
    assert entry["palette_extracted"] is False
