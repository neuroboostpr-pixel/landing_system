"""Тест fix-display-names.py — техническое имя карточки '<id> (<layout>)'."""
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "fix-display-names.py"


def _load():
    spec = importlib.util.spec_from_file_location("fix_display_names", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_make_name_with_layout():
    m = _load()
    assert m.make_name("header-cinematic-split-portfolio-kdm1-ru-0", "split") == \
        "header-cinematic-split-portfolio-kdm1-ru-0 (split)"


def test_make_name_without_layout():
    m = _load()
    assert m.make_name("hero-001", "") == "hero-001"
    assert m.make_name("hero-001", "   ") == "hero-001"


def test_make_name_is_ascii_id_no_russian_description():
    m = _load()
    name = m.make_name("features-technical-grid-3-portfolio-kdm1-ru-2", "grid-3")
    # имя карточки — id + layout, без русского описания
    assert name == "features-technical-grid-3-portfolio-kdm1-ru-2 (grid-3)"
    # никаких кириллических букв в имени
    assert not any("а" <= ch.lower() <= "я" for ch in name)
