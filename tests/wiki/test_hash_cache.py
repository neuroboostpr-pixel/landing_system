"""Тесты hash_cache."""
import json
from pathlib import Path

import pytest

from scripts.wiki import hash_cache


def test_compute_hash_stable(tmp_path):
    """sha256 не меняется для одного контента."""
    p = tmp_path / "foo.md"
    p.write_text("hello")
    h1 = hash_cache.compute_hash(p)
    h2 = hash_cache.compute_hash(p)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_hash_differs_on_content(tmp_path):
    p = tmp_path / "foo.md"
    p.write_text("a")
    h1 = hash_cache.compute_hash(p)
    p.write_text("b")
    h2 = hash_cache.compute_hash(p)
    assert h1 != h2


def test_load_cache_missing(tmp_path):
    """Если файла кэша нет — возвращает пустой dict."""
    cache_path = tmp_path / ".cache.json"
    assert hash_cache.load_cache(cache_path) == {}


def test_save_and_load_cache(tmp_path):
    cache_path = tmp_path / ".cache.json"
    data = {"agents/foo.md": "abc123", "skills/bar.md": "def456"}
    hash_cache.save_cache(cache_path, data)
    assert cache_path.exists()
    loaded = hash_cache.load_cache(cache_path)
    assert loaded == data


def test_is_changed_new_file(tmp_path):
    """Новый файл → is_changed=True."""
    p = tmp_path / "new.md"
    p.write_text("x")
    cache = {}
    assert hash_cache.is_changed(p, "new.md", cache) is True


def test_is_changed_same_content(tmp_path):
    p = tmp_path / "same.md"
    p.write_text("content")
    h = hash_cache.compute_hash(p)
    cache = {"same.md": h}
    assert hash_cache.is_changed(p, "same.md", cache) is False


def test_is_changed_modified(tmp_path):
    p = tmp_path / "mod.md"
    p.write_text("v1")
    old_hash = hash_cache.compute_hash(p)
    p.write_text("v2")
    cache = {"mod.md": old_hash}
    assert hash_cache.is_changed(p, "mod.md", cache) is True
