"""Pytest fixtures for Phase 2 tests."""
import os
import tempfile
from pathlib import Path
import pytest
import responses as resp_lib


@pytest.fixture
def temp_project(tmp_path):
    """Create a fake project directory with the 13 stage folders."""
    stages = [
        "00_БРИФ", "01_КОНТЕКСТ", "02_МАТЕРИАЛЫ_КЛИЕНТА", "03_РЕФЕРЕНСЫ",
        "04_БРЕНД", "05_ДИЗАЙН-СИСТЕМА", "06_СТЕК", "07_КОНТЕНТ",
        "08_КОД", "09_ДЕПЛОЙ", "10_QA", "11_АНАЛИТИКА", "12_SEO",
    ]
    for s in stages:
        (tmp_path / s).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def http_mock():
    """Wrap responses.RequestsMock for declarative HTTP mocking
    (used for Iconify and font-CDN tests)."""
    with resp_lib.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def fixture_html():
    """Sample HTML page content for trafilatura tests."""
    return """<!DOCTYPE html><html><head><title>Test</title></head>
    <body><article><h1>Отзыв 1</h1><p>5 звёзд. Отлично!</p>
    <h1>Отзыв 2</h1><p>4 звезды. Хорошо.</p></article></body></html>"""
