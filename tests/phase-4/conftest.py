# tests/phase-4/conftest.py
"""Pytest fixtures for Phase 4 tests."""
import json
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sample_tokens():
    return {
        "colors": {
            "primary": {"hex": "#ff5733", "role": "primary", "source": "ref.png@[10,20]"},
            "secondary": {"hex": "#33c1ff", "role": "secondary", "source": "ref.png@[50,50]"},
            "accent": {"hex": "#2ecc71", "role": "accent", "source": "ref.png@[80,80]"},
            "bg": {"hex": "#ffffff", "role": "bg", "source": "default"},
            "text": {"hex": "#1a1a1a", "role": "text", "source": "default"},
        },
        "typography": {
            "display": {
                "family": "Cabinet Grotesk",
                "size": "clamp(2.5rem, 5vw, 4rem)",
                "weight": "700",
                "line_height": "1.1",
                "source": "DOM",
            },
            "body": {
                "family": "Inter",
                "size": "1rem",
                "weight": "400",
                "line_height": "1.6",
                "source": "DOM",
            },
        },
        "spacing": {
            "xs": "0.25rem", "sm": "0.5rem", "md": "1rem",
            "lg": "2rem", "xl": "4rem", "2xl": "8rem",
        },
        "grid": {"columns": 12, "gap": "1.5rem", "max_width": "1200px"},
        "radius": {"none": "0", "sm": "0.25rem", "md": "0.5rem", "lg": "1rem"},
        "shadow": {
            "sm": "0 1px 3px rgba(0,0,0,.12)",
            "md": "0 4px 12px rgba(0,0,0,.12)",
            "lg": "0 8px 24px rgba(0,0,0,.12)",
        },
        "breakpoints": {"mobile": "375px", "tablet": "768px", "desktop": "1440px"},
        "motion": {"duration_fast": "150ms", "duration_base": "300ms", "easing": "ease-out"},
    }


@pytest.fixture
def sample_stack():
    return {
        "mode": "standard",
        "fonts": {
            "cdn": "bunny",
            "families": [
                {"name": "Cabinet Grotesk", "weights": [400, 700]},
                {"name": "Inter", "weights": [400]},
            ],
        },
        "icons": {"library": "lucide", "delivery": "iconify-api"},
        "js_libraries": [],
        "wordpress": {
            "theme": "generatepress",
            "plugins": ["advanced-custom-fields", "generateblocks", "fluentform"],
        },
    }


@pytest.fixture
def sample_stack_cinematic():
    return {
        "mode": "cinematic",
        "fonts": {
            "cdn": "bunny",
            "families": [
                {"name": "Cabinet Grotesk", "weights": [400, 700]},
                {"name": "Inter", "weights": [400]},
            ],
        },
        "icons": {"library": "lucide", "delivery": "iconify-api"},
        "js_libraries": ["gsap", "scrolltrigger", "lenis", "split-type"],
        "wordpress": {
            "theme": "generatepress",
            "plugins": ["advanced-custom-fields", "generateblocks", "fluentform"],
        },
    }


@pytest.fixture
def sample_final_copy():
    return """# Landing Copy

## HERO
**heading**: Лучшие курсы по копирайтингу
**subheading**: Научись писать тексты, которые продают
**cta**: Записаться на курс

## ABOUT
**heading**: О нас
**body**: Мы обучаем копирайтингу с 2018 года

## УСЛУГИ
**heading**: Что вы получите
- Практические задания
- Обратная связь от ментора

## ОТЗЫВЫ
**heading**: Что говорят наши студенты
- Алина: "Отличный курс!"
- Борис: "Рекомендую всем"

## ФОРМА
**heading**: Запишитесь сейчас
**subheading**: Бесплатная консультация

## FAQ
**heading**: Частые вопросы
- Сколько времени займёт? — 3 месяца
- Нужен ли опыт? — Нет
"""


@pytest.fixture
def wp_theme_project(tmp_path, sample_tokens, sample_stack, sample_final_copy):
    """Full Phase 3+4 project fixture with all required dirs and files."""
    # Phase 3 outputs
    ds_dir = tmp_path / "05_ДИЗАЙН-СИСТЕМА"
    ds_dir.mkdir(parents=True)
    (ds_dir / "tokens.json").write_text(json.dumps(sample_tokens), encoding="utf-8")

    stack_dir = tmp_path / "06_СТЕК"
    stack_dir.mkdir()
    (stack_dir / "design-stack.yaml").write_text(
        yaml.dump(sample_stack, allow_unicode=True), encoding="utf-8"
    )

    content_dir = tmp_path / "07_КОНТЕНТ"
    content_dir.mkdir()
    (content_dir / "final-copy.md").write_text(sample_final_copy, encoding="utf-8")

    # Phase 2 outputs
    icons_dir = tmp_path / "04_БРЕНД" / "extracted"
    icons_dir.mkdir(parents=True)
    (icons_dir / "icons.yaml").write_text(
        yaml.dump({"icons": []}, allow_unicode=True), encoding="utf-8"
    )

    photos_dir = tmp_path / "02_МАТЕРИАЛЫ_КЛИЕНТА" / "photos" / "processed"
    photos_dir.mkdir(parents=True)

    # Required dirs
    (tmp_path / "00_БРИФ").mkdir()
    (tmp_path / "08_КОД").mkdir()

    return tmp_path
