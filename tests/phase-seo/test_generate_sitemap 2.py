"""Tests for skills/seo-optimizer/scripts/generate-sitemap.py"""
import importlib.util
import os
import sys
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

SCRIPT = Path(__file__).parents[2] / "skills" / "seo-optimizer" / "scripts" / "generate-sitemap.py"

spec = importlib.util.spec_from_file_location("generate_sitemap", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_sitemap_contains_home_url():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "sitemap.xml"
        result = mod.generate_sitemap("https://example.com", [], str(out))
        assert result == 0
        tree = ET.parse(out)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall(".//sm:loc", ns)]
        assert "https://example.com/" in locs


def test_sitemap_contains_legal_pages():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "sitemap.xml"
        legal = ["/policy", "/consent"]
        mod.generate_sitemap("https://example.com", legal, str(out))
        tree = ET.parse(out)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall(".//sm:loc", ns)]
        assert "https://example.com/policy" in locs
        assert "https://example.com/consent" in locs


def test_sitemap_valid_xml_structure():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "sitemap.xml"
        mod.generate_sitemap("https://example.com", ["/policy"], str(out))
        tree = ET.parse(out)
        root = tree.getroot()
        assert "urlset" in root.tag
        urls = root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        assert len(urls) == 2  # home + /policy


def test_sitemap_deduplicates_home():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "sitemap.xml"
        # passing "/" in legal should not produce duplicate home entry
        mod.generate_sitemap("https://example.com", ["/"], str(out))
        tree = ET.parse(out)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall(".//sm:loc", ns)]
        assert locs.count("https://example.com/") == 1


def test_sitemap_trailing_slash_normalised():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "sitemap.xml"
        mod.generate_sitemap("https://example.com/", [], str(out))
        tree = ET.parse(out)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall(".//sm:loc", ns)]
        assert "https://example.com/" in locs
