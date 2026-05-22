"""Tests for site_discovery — parsing .landing-state.yaml for hosts."""
from pathlib import Path
import pytest
from lib.site_discovery import discover_hosts

FIXTURES = Path(__file__).parent / "fixtures"


def test_multisite_returns_all_segments_plus_primary():
    hosts = discover_hosts(FIXTURES / "state-multisite.yaml")
    assert hosts == [
        "https://ailexi.ru",
        "https://russian.ailexi.ru",
        "https://dubai-avto-liza.ailexi.ru",
    ]


def test_single_site_returns_only_primary():
    hosts = discover_hosts(FIXTURES / "state-single.yaml")
    assert hosts == ["https://simple-project.example.com"]


def test_missing_state_file_raises():
    with pytest.raises(FileNotFoundError):
        discover_hosts(FIXTURES / "nonexistent.yaml")


def test_filter_segment():
    hosts = discover_hosts(FIXTURES / "state-multisite.yaml",
                            filter_host="dubai-avto-liza.ailexi.ru")
    assert hosts == ["https://dubai-avto-liza.ailexi.ru"]


def test_filter_unknown_segment_raises():
    with pytest.raises(ValueError):
        discover_hosts(FIXTURES / "state-multisite.yaml", filter_host="nonexistent.com")
