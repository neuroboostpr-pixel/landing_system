# tests/phase-5/conftest.py
import json
import pytest
from pathlib import Path


@pytest.fixture
def wp_built_project(tmp_path):
    """Project with full Phase 4 output: tokens, stack, brief, wp-theme."""
    # 05_ДИЗАЙН-СИСТЕМА
    design = tmp_path / "05_ДИЗАЙН-СИСТЕМА"
    design.mkdir()
    tokens = {
        "colors": {"primary": {"hex": "#ff5733", "role": "primary", "source": "ref.png"},
                   "secondary": {"hex": "#2c2c54", "role": "secondary", "source": "ref.png"},
                   "accent": {"hex": "#ffd700", "role": "accent", "source": "ref.png"},
                   "text": {"hex": "#1a1a2e", "source": "generated"},
                   "bg": {"hex": "#ffffff", "source": "generated"}},
        "typography": {"display": {"family": "Cabinet Grotesk", "weight": 700, "source": "DOM"},
                       "body": {"family": "Inter", "weight": 400, "source": "DOM"},
                       "sizes": {"h1": "clamp(2.5rem,6vw,5rem)", "base": "1rem"}},
        "spacing": {"md": "1.5rem", "lg": "2rem", "xl": "3rem"},
        "radius": {"md": "8px"},
        "shadow": {"md": "0 4px 12px rgba(0,0,0,0.1)"},
        "breakpoints": {"mobile": "375px", "desktop": "1440px"},
        "motion": {"duration_base": "300ms", "easing": "cubic-bezier(0.4,0,0.2,1)"},
    }
    (design / "tokens.json").write_text(json.dumps(tokens, ensure_ascii=False), encoding="utf-8")

    # 06_СТЕК
    stack_dir = tmp_path / "06_СТЕК"
    stack_dir.mkdir()
    (stack_dir / "design-stack.yaml").write_text(
        "mode: standard\nfonts:\n  cdn: bunny\n  families:\n    - name: Cabinet Grotesk\n      weights: [400, 700]\n"
        "icons:\n  library: lucide\njs_libraries: []\nui_libraries:\n  swiper: true\n  fancybox: true\n  countup: true\n",
        encoding="utf-8"
    )

    # 00_БРИФ
    brief_dir = tmp_path / "00_БРИФ"
    brief_dir.mkdir()
    (brief_dir / "brief.md").write_text(
        "# Бриф\n\n## Аналитика\n- YM счётчик: 98765432\n- GTM контейнер: GTM-ABCDEFG\n\n"
        "## Интеграции\n- CRM: AmoCRM\n- Telegram уведомления: да\n- Попапы: да\n",
        encoding="utf-8"
    )

    # 07_КОНТЕНТ
    content_dir = tmp_path / "07_КОНТЕНТ"
    content_dir.mkdir()
    (content_dir / "final-copy.md").write_text("# Copy\n\n## HERO\nЗаголовок\n\n## ФОРМА\nФорма\n", encoding="utf-8")

    # 08_КОД/wp-theme — имитируем вывод generate-theme.py
    theme = tmp_path / "08_КОД" / "wp-theme"
    (theme / "assets" / "css").mkdir(parents=True)
    (theme / "assets" / "js").mkdir(parents=True)
    (theme / "assets" / "fonts").mkdir(parents=True)
    (theme / "assets" / "icons").mkdir(parents=True)
    (theme / "assets" / "images").mkdir(parents=True)
    (theme / "template-parts").mkdir(parents=True)
    (theme / "style.css").write_text(
        "/*\nTheme Name: LP Theme\n*/\n:root {\n  --color-primary: #ff5733;\n}\n", encoding="utf-8"
    )
    (theme / "functions.php").write_text(
        "<?php\nfunction lp_enqueue_assets() {\n"
        "  wp_enqueue_style('lp-style', get_template_directory_uri() . '/style.css');\n"
        "  wp_enqueue_style('bunny-fonts', 'https://fonts.bunny.net/css?family=cabinet-grotesk:400,700');\n"
        "}\nadd_action('wp_enqueue_scripts', 'lp_enqueue_assets');\n\n"
        "// [YM_COUNTER] — Yandex Metrika (analytics-engineer)\n"
        "// [SEO_META]   — meta tags (seo-optimizer)\n"
        "// [FLUENT_WEBHOOK] — form webhook (integrations-engineer)\n",
        encoding="utf-8"
    )
    (theme / "index.php").write_text("<?php get_header(); get_footer(); ?>\n", encoding="utf-8")
    (theme / "front-page.php").write_text(
        "<?php get_header();\nget_template_part('template-parts/section', 'hero');\nget_footer(); ?>\n",
        encoding="utf-8"
    )

    # 08_КОД/acf-fields.json
    (tmp_path / "08_КОД" / "acf-fields.json").write_text(
        json.dumps({"version": "5.12.0", "groups": [{"title": "Hero", "fields": []}]}, ensure_ascii=False),
        encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def wp_built_project_cinematic(wp_built_project):
    """Same but cinematic mode with gsap in js_libraries."""
    stack_path = wp_built_project / "06_СТЕК" / "design-stack.yaml"
    stack_path.write_text(
        "mode: cinematic\nfonts:\n  cdn: bunny\n  families:\n    - name: Cabinet Grotesk\n      weights: [700]\n"
        "icons:\n  library: lucide\njs_libraries: [gsap, scrolltrigger, lenis, split-type]\n"
        "ui_libraries:\n  swiper: true\n  fancybox: false\n  countup: true\n",
        encoding="utf-8"
    )
    return wp_built_project


@pytest.fixture
def sample_system_config():
    return {
        "crm": {
            "amocrm": {"enabled": True, "subdomain": "test.amocrm.ru"},
            "bitrix24": {"enabled": False, "webhook_url": ""},
            "telegram": {"enabled": True, "bot_token": "123:ABC", "chat_id": "-100123"},
        },
        "analytics": {
            "yandex_metrika": {"enabled": True, "counter_id": "98765432"},
            "gtm": {"enabled": True, "container_id": "GTM-ABCDEFG"},
        },
        "ui_libraries": {"swiper": True, "fancybox": True, "countup": True, "typed": False},
        "popups": {"enabled": True, "style": "minimal"},
    }
