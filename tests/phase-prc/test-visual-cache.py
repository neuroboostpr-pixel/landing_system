"""Tests for visual-cache.py — hash-based prompt cache."""
from pathlib import Path

from skills.visual_generation.scripts.visual_cache import (
    cache_key,
    lookup_cache,
    save_to_cache,
)


def test_cache_key_deterministic():
    key1 = cache_key(hint="shield", style="outlined", brand_color="#000")
    key2 = cache_key(hint="shield", style="outlined", brand_color="#000")
    assert key1 == key2


def test_cache_key_changes_with_inputs():
    a = cache_key(hint="shield", style="outlined", brand_color="#000")
    b = cache_key(hint="shield", style="filled", brand_color="#000")
    c = cache_key(hint="shield", style="outlined", brand_color="#fff")
    d = cache_key(hint="lock", style="outlined", brand_color="#000")
    assert a != b
    assert a != c
    assert a != d


def test_save_and_lookup_roundtrip(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    src = tmp_path / "src.png"
    src.write_bytes(b"\x89PNG\r\n" + b"\x00" * 2000)

    key = cache_key(hint="x", style="outlined", brand_color="#000")
    save_to_cache(cache_dir, key, src)

    found = lookup_cache(cache_dir, key)
    assert found is not None
    assert found.read_bytes() == b"\x89PNG\r\n" + b"\x00" * 2000


def test_lookup_returns_none_for_missing(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    assert lookup_cache(cache_dir, "nonexistent-hash") is None


def test_lookup_rejects_too_small_files(tmp_path):
    """Damaged/empty cache files should be treated as miss."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "tiny.png").write_bytes(b"x")  # 1 byte = damaged
    assert lookup_cache(cache_dir, "tiny") is None


def test_cache_key_includes_niche():
    a = cache_key(hint="shield", style="outlined", brand_color="#000", niche="")
    b = cache_key(hint="shield", style="outlined", brand_color="#000", niche="services")
    assert a != b
