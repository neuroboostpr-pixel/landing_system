# Phase 4 — WP Build Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать WP Build Pipeline (этап 08) — скрипты generate-theme.py, generate-acf.py, bundle-assets.py, render-build-preview.py, скиллы wp-gutenberg-block-builder + wp-theme-assembler, агентов wp-builder / integrations-engineer / analytics-engineer / seo-optimizer, и slash-команду /landing-build.

**Architecture:** generate-theme.py читает `05_ДИЗАЙН-СИСТЕМА/tokens.json` + `06_СТЕК/design-stack.yaml` → генерирует детерминированный скаффолдинг WP-темы в `08_КОД/wp-theme/` (style.css с CSS-переменными, functions.php с enqueue, PHP-шаблоны). generate-acf.py парсит `07_КОНТЕНТ/final-copy.md` → генерирует `08_КОД/acf-fields.json`. Агент wp-builder заполняет template-parts PHP+JS кодом, агенты integrations-engineer / analytics-engineer / seo-optimizer дополняют functions.php. bundle-assets.py скачивает иконки + копирует фото. render-build-preview.py рендерит статический `08_КОД/build-preview.html` через Jinja2.

**Tech Stack:** Python 3.10+, PyYAML, Jinja2, pytest, bats-core. Паттерны Phase 3: `importlib.util` загрузка скриптов в тестах, `sys.path.insert(0, parents[3])` для `tools`, `main(argv: list) -> int`.

---

## Файловая структура

**Создать:**
- `tests/phase-4/conftest.py`
- `tests/phase-4/python/test_generate_theme.py`
- `tests/phase-4/python/test_generate_acf.py`
- `tests/phase-4/python/test_bundle_assets.py`
- `tests/phase-4/python/test_render_build_preview.py`
- `tests/phase-4/test-agents-phase4.bats`
- `tests/phase-4/test-commands-phase4.bats`
- `tests/phase-4/integration/test-phase4-pipeline.bats`
- `skills/wp-gutenberg-block-builder/SKILL.md`
- `skills/wp-gutenberg-block-builder/scripts/generate-theme.py`
- `skills/wp-gutenberg-block-builder/scripts/generate-acf.py`
- `skills/wp-theme-assembler/SKILL.md`
- `skills/wp-theme-assembler/scripts/bundle-assets.py`
- `skills/wp-theme-assembler/scripts/render-build-preview.py`
- `tools/html/templates/build-preview.html.j2`
- `agents/wp-builder.md`
- `agents/integrations-engineer.md`
- `agents/analytics-engineer.md`
- `agents/seo-optimizer.md`
- `.claude/commands/landing-build.md`

**Изменить:**
- `agents/landing-orchestrator.md` — добавить Phase 4 scope
- `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` — Phase 4 started/complete

---

## Task 1: conftest.py с fixtures для Phase 4

**Files:**
- Create: `tests/phase-4/conftest.py`

- [ ] **Step 1: Написать conftest.py**

```python
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
```

- [ ] **Step 2: Запустить (должен собраться без ошибок)**

```bash
cd /Users/kirillbezikov/Desktop/Обучение\ вайбкодинг\ Кодекс/02_projects\ -\ проекты/Агентство\ лидогенерации/landing-system
python -c "import tests.phase_4.conftest" 2>&1 || echo "OK (import check not needed for conftest)"
pytest tests/phase-4/conftest.py --collect-only 2>&1 | tail -5
```

- [ ] **Step 3: Commit**

```bash
git add tests/phase-4/conftest.py
git commit -m "test(phase-4): conftest fixtures for WP Build Pipeline tests"
```

---

## Task 2: test_generate_theme.py (RED) → generate-theme.py (GREEN)

**Files:**
- Create: `tests/phase-4/python/test_generate_theme.py`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-theme.py`

- [ ] **Step 1: Написать failing tests**

```python
# tests/phase-4/python/test_generate_theme.py
"""Tests for wp-gutenberg-block-builder/scripts/generate-theme.py"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "generate-theme.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_theme", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"


def test_find_project_root_success(wp_theme_project):
    mod = _load()
    root = mod._find_project_root(wp_theme_project)
    assert root == wp_theme_project


def test_find_project_root_fail(tmp_path):
    mod = _load()
    with pytest.raises(FileNotFoundError):
        mod._find_project_root(tmp_path)


def test_css_variables_has_root_block(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert css.startswith(":root {")
    assert css.strip().endswith("}")


def test_css_variables_includes_colors(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert "--color-primary: #ff5733" in css
    assert "--color-secondary: #33c1ff" in css


def test_css_variables_includes_typography(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert "--font-display-family: 'Cabinet Grotesk'" in css
    assert "--font-body-family: 'Inter'" in css


def test_css_variables_includes_spacing(sample_tokens):
    mod = _load()
    css = mod._css_variables(sample_tokens)
    assert "--space-md: 1rem" in css


def test_main_returns_zero(wp_theme_project):
    mod = _load()
    result = mod.main(["prog", str(wp_theme_project)])
    assert result == 0


def test_main_creates_style_css(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    css_path = wp_theme_project / "08_КОД" / "wp-theme" / "style.css"
    assert css_path.exists()
    content = css_path.read_text(encoding="utf-8")
    assert "Theme Name:" in content
    assert ":root {" in content
    assert "--color-primary:" in content


def test_main_creates_functions_php(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    php_path = wp_theme_project / "08_КОД" / "wp-theme" / "functions.php"
    assert php_path.exists()
    content = php_path.read_text(encoding="utf-8")
    assert "lp_enqueue_assets" in content
    assert "wp_enqueue_style" in content
    assert "bunny.net" in content


def test_main_functions_php_cinematic_has_gsap(tmp_path, sample_tokens, sample_stack_cinematic):
    import json, yaml
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(json.dumps(sample_tokens))
    (tmp_path / "06_СТЕК").mkdir()
    (tmp_path / "06_СТЕК" / "design-stack.yaml").write_text(yaml.dump(sample_stack_cinematic, allow_unicode=True))
    (tmp_path / "07_КОНТЕНТ").mkdir()
    (tmp_path / "07_КОНТЕНТ" / "final-copy.md").write_text("## HERO\ntext")
    (tmp_path / "08_КОД").mkdir()

    mod = _load()
    mod.main(["prog", str(tmp_path)])
    php = (tmp_path / "08_КОД" / "wp-theme" / "functions.php").read_text()
    assert "gsap" in php.lower()


def test_main_creates_template_parts_dir(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "wp-theme" / "template-parts").is_dir()


def test_main_creates_assets_dirs(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    theme = wp_theme_project / "08_КОД" / "wp-theme"
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images"]:
        assert (theme / sub).is_dir(), f"Missing: {sub}"


def test_main_creates_index_php(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "wp-theme" / "index.php").exists()


def test_main_creates_front_page_php(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    php = (wp_theme_project / "08_КОД" / "wp-theme" / "front-page.php").read_text()
    assert "get_header" in php
    assert "get_footer" in php
    assert "template-parts/section" in php


def test_main_creates_gutenberg_blocks_dir(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    assert (wp_theme_project / "08_КОД" / "gutenberg-blocks").is_dir()


def test_main_missing_tokens_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
```

- [ ] **Step 2: Запустить тесты — убедиться что они ПАДАЮТ**

```bash
cd /Users/kirillbezikov/Desktop/Обучение\ вайбкодинг\ Кодекс/02_projects\ -\ проекты/Агентство\ лидогенерации/landing-system
pytest tests/phase-4/python/test_generate_theme.py -v 2>&1 | tail -20
```

Ожидание: `ERROR` или `FAILED` — скрипт не существует.

- [ ] **Step 3: Создать директорию скрипта**

```bash
mkdir -p skills/wp-gutenberg-block-builder/scripts
```

- [ ] **Step 4: Написать generate-theme.py**

```python
#!/usr/bin/env python3
"""Generate WordPress theme scaffold from tokens.json + design-stack.yaml.

CLI: python3 generate-theme.py <project-dir>
Stdout: path to created wp-theme/ directory
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, info, success


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").exists():
            return parent
    raise FileNotFoundError("tokens.json not found — run /landing-design first")


def _load_tokens(project: Path) -> dict:
    return json.loads((project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").read_text(encoding="utf-8"))


def _load_stack(project: Path) -> dict:
    p = project / "06_СТЕК" / "design-stack.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def _css_variables(tokens: dict) -> str:
    lines = [":root {"]
    for name, props in tokens.get("colors", {}).items():
        hex_val = props["hex"] if isinstance(props, dict) else str(props)
        lines.append(f"  --color-{name}: {hex_val};")
    for role, props in tokens.get("typography", {}).items():
        if not isinstance(props, dict):
            continue
        lines.append(f"  --font-{role}-family: '{props.get('family', 'sans-serif')}', sans-serif;")
        lines.append(f"  --font-{role}-size: {props.get('size', '1rem')};")
        lines.append(f"  --font-{role}-weight: {props.get('weight', '400')};")
        lines.append(f"  --font-{role}-line-height: {props.get('line_height', '1.5')};")
    for key, val in tokens.get("spacing", {}).items():
        lines.append(f"  --space-{key}: {val};")
    for key, val in tokens.get("radius", {}).items():
        lines.append(f"  --radius-{key}: {val};")
    for key, val in tokens.get("shadow", {}).items():
        lines.append(f"  --shadow-{key}: {val};")
    lines.append("}")
    return "\n".join(lines)


def _write_style_css(theme_dir: Path, project_name: str, tokens: dict) -> None:
    css_vars = _css_variables(tokens)
    (theme_dir / "style.css").write_text(
        f"""/*
Theme Name: LP {project_name}
Description: Landing page theme generated by landing-system wp-builder
Version: 1.0
Text Domain: lp-{project_name.lower().replace(' ', '-')}
*/

{css_vars}
""",
        encoding="utf-8",
    )


def _write_functions_php(theme_dir: Path, stack: dict) -> None:
    fonts = stack.get("fonts", {})
    cdn = fonts.get("cdn", "bunny")
    families = fonts.get("families", [])

    base_url = "https://fonts.bunny.net/css" if cdn == "bunny" else "https://fonts.googleapis.com/css2"
    font_query = "|".join(
        f"{f['name'].lower().replace(' ', '-')}:{','.join(str(w) for w in f.get('weights', [400]))}"
        for f in families
    )
    font_url = f"{base_url}?family={font_query}" if font_query else f"{base_url}?family=inter:400"

    js_libs = stack.get("js_libraries", [])
    js_lines = []
    if "gsap" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('gsap', "
            "'https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js', [], null, true);"
        )
    if "scrolltrigger" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('gsap-st', "
            "'https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js', ['gsap'], null, true);"
        )
    if "lenis" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('lenis', "
            "'https://cdn.jsdelivr.net/npm/@studio-freight/lenis', [], null, true);"
        )
    if "split-type" in js_libs:
        js_lines.append(
            "    wp_enqueue_script('split-type', "
            "'https://cdn.jsdelivr.net/npm/split-type', [], null, true);"
        )
    js_block = ("\n" + "\n".join(js_lines)) if js_lines else ""

    (theme_dir / "functions.php").write_text(
        f"""<?php
/**
 * Theme functions — generated by landing-system wp-builder
 * DO NOT EDIT manually; re-run /landing-build to regenerate scaffold.
 */

function lp_enqueue_assets() {{
    wp_enqueue_style('lp-fonts', '{font_url}', [], null);
    wp_enqueue_style('lp-style', get_template_directory_uri() . '/style.css', [], '1.0');
    wp_enqueue_style('lp-main', get_template_directory_uri() . '/assets/css/main.css', ['lp-style'], '1.0');
    wp_enqueue_script('lp-main', get_template_directory_uri() . '/assets/js/main.js', [], '1.0', true);{js_block}
}}
add_action('wp_enqueue_scripts', 'lp_enqueue_assets');

function lp_setup() {{
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('editor-styles');
    add_theme_support('wp-block-styles');
    add_theme_support('align-wide');
}}
add_action('after_setup_theme', 'lp_setup');

// Placeholders for generated code (filled by agents):
// [YM_COUNTER] — Yandex Metrika (analytics-engineer)
// [SEO_META]   — meta tags (seo-optimizer)
// [FLUENT_WEBHOOK] — form webhook (integrations-engineer)
""",
        encoding="utf-8",
    )


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        project = _find_project_root(cwd)
    except FileNotFoundError as e:
        error(str(e))
        return 1

    tokens = _load_tokens(project)
    stack = _load_stack(project)
    project_name = project.name.replace("-", " ").title()

    theme_dir = project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "template-parts").mkdir(exist_ok=True)
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/icons", "assets/images"]:
        (theme_dir / sub).mkdir(parents=True, exist_ok=True)
    (project / "08_КОД" / "gutenberg-blocks").mkdir(parents=True, exist_ok=True)

    _write_style_css(theme_dir, project_name, tokens)
    _write_functions_php(theme_dir, stack)

    (theme_dir / "index.php").write_text(
        "<?php\n// Silence is golden — front-page.php handles landing output.\n",
        encoding="utf-8",
    )
    (theme_dir / "front-page.php").write_text(
        """<?php get_header(); ?>
<main class="lp-landing">
    <?php get_template_part('template-parts/section', 'hero'); ?>
    <?php get_template_part('template-parts/section', 'about'); ?>
    <?php get_template_part('template-parts/section', 'services'); ?>
    <?php get_template_part('template-parts/section', 'proof'); ?>
    <?php get_template_part('template-parts/section', 'form'); ?>
    <?php get_template_part('template-parts/section', 'faq'); ?>
</main>
<?php get_footer(); ?>
""",
        encoding="utf-8",
    )

    for section in ["hero", "about", "services", "proof", "form", "faq"]:
        part = theme_dir / "template-parts" / f"section-{section}.php"
        if not part.exists():
            part.write_text(
                f"<?php\n// section-{section} — filled by wp-builder agent\n",
                encoding="utf-8",
            )

    (theme_dir / "assets" / "css" / "main.css").write_text(
        "/* Block styles — generated by wp-builder agent */\n", encoding="utf-8"
    )
    (theme_dir / "assets" / "js" / "main.js").write_text(
        "// Landing scripts — generated by wp-builder agent\n", encoding="utf-8"
    )

    success(f"Theme scaffold: {theme_dir}")
    print(str(theme_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Запустить тесты — убедиться что они ЗЕЛЁНЫЕ**

```bash
pytest tests/phase-4/python/test_generate_theme.py -v 2>&1 | tail -25
```

Ожидание: все тесты `PASSED`.

- [ ] **Step 6: Commit**

```bash
git add tests/phase-4/python/test_generate_theme.py skills/wp-gutenberg-block-builder/scripts/generate-theme.py
git commit -m "feat(phase-4): generate-theme.py — WP theme scaffold from tokens.json + design-stack.yaml"
```

---

## Task 3: test_generate_acf.py (RED) → generate-acf.py (GREEN)

**Files:**
- Create: `tests/phase-4/python/test_generate_acf.py`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-acf.py`

- [ ] **Step 1: Написать failing tests**

```python
# tests/phase-4/python/test_generate_acf.py
"""Tests for wp-gutenberg-block-builder/scripts/generate-acf.py"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "generate-acf.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_acf", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_parse_sections_finds_h2(wp_theme_project, sample_final_copy):
    mod = _load()
    copy_path = wp_theme_project / "07_КОНТЕНТ" / "final-copy.md"
    sections = mod._parse_sections(copy_path)
    assert len(sections) >= 4
    assert any("HERO" in s.upper() for s in sections)


def test_parse_sections_empty_file(tmp_path):
    mod = _load()
    f = tmp_path / "final-copy.md"
    f.write_text("# No sections here\n", encoding="utf-8")
    assert mod._parse_sections(f) == []


def test_normalize_section_english(sample_final_copy):
    mod = _load()
    assert mod._normalize_section("hero") == "hero"
    assert mod._normalize_section("HERO") == "hero"
    assert mod._normalize_section("form") == "form"
    assert mod._normalize_section("faq") == "faq"


def test_normalize_section_russian():
    mod = _load()
    assert mod._normalize_section("ОТЗЫВЫ") == "proof"
    assert mod._normalize_section("ФОРМА") == "form"
    assert mod._normalize_section("УСЛУГИ") == "services"
    assert mod._normalize_section("FAQ") == "faq"


def test_build_acf_group_has_required_keys():
    mod = _load()
    group = mod._build_acf_group("hero")
    assert "key" in group
    assert "title" in group
    assert "fields" in group
    assert "location" in group
    assert len(group["fields"]) > 0


def test_build_acf_group_hero_fields():
    mod = _load()
    group = mod._build_acf_group("hero")
    field_names = [f["name"] for f in group["fields"]]
    assert "heading" in field_names
    assert "cta_text" in field_names


def test_build_acf_group_unknown_section_uses_defaults():
    mod = _load()
    group = mod._build_acf_group("unknown_block")
    assert len(group["fields"]) >= 1


def test_main_creates_acf_fields_json(wp_theme_project):
    mod = _load()
    result = mod.main(["prog", str(wp_theme_project)])
    assert result == 0
    out = wp_theme_project / "08_КОД" / "acf-fields.json"
    assert out.exists()


def test_acf_json_has_groups(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    data = json.loads((wp_theme_project / "08_КОД" / "acf-fields.json").read_text(encoding="utf-8"))
    assert "groups" in data
    assert len(data["groups"]) >= 4


def test_acf_json_groups_have_fields(wp_theme_project):
    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    data = json.loads((wp_theme_project / "08_КОД" / "acf-fields.json").read_text(encoding="utf-8"))
    for group in data["groups"]:
        assert len(group["fields"]) > 0, f"Group {group['key']} has no fields"


def test_main_missing_final_copy_returns_one(tmp_path):
    (tmp_path / "08_КОД").mkdir()
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
```

- [ ] **Step 2: Запустить — убедиться что ПАДАЮТ**

```bash
pytest tests/phase-4/python/test_generate_acf.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Написать generate-acf.py**

```python
#!/usr/bin/env python3
"""Generate ACF fields JSON from 07_КОНТЕНТ/final-copy.md.

CLI: python3 generate-acf.py <project-dir>
Stdout: path to created acf-fields.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn

SECTION_ALIASES = {
    "hero": "hero", "герой": "hero", "главный": "hero",
    "about": "about", "о нас": "about", "о компании": "about",
    "services": "services", "услуги": "services", "сервисы": "services",
    "what you get": "services",
    "proof": "proof", "отзывы": "proof", "результаты": "proof",
    "testimonials": "proof", "кейсы": "proof",
    "form": "form", "форма": "form", "заявка": "form", "форма заявки": "form",
    "faq": "faq", "вопросы": "faq", "частые вопросы": "faq",
    "вопрос-ответ": "faq",
}

SECTION_FIELDS = {
    "hero": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {"label": "Подзаголовок", "name": "subheading", "type": "textarea"},
        {"label": "Текст кнопки", "name": "cta_text", "type": "text"},
        {"label": "Фоновое изображение", "name": "bg_image", "type": "image"},
    ],
    "about": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {"label": "Текст", "name": "body", "type": "wysiwyg"},
        {"label": "Фото", "name": "photo", "type": "image"},
    ],
    "services": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {
            "label": "Услуги", "name": "items", "type": "repeater",
            "sub_fields": [
                {"label": "Название", "name": "title", "type": "text"},
                {"label": "Описание", "name": "description", "type": "textarea"},
                {"label": "Иконка", "name": "icon", "type": "text"},
            ],
        },
    ],
    "proof": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {
            "label": "Отзывы", "name": "testimonials", "type": "repeater",
            "sub_fields": [
                {"label": "Имя", "name": "name", "type": "text"},
                {"label": "Текст отзыва", "name": "text", "type": "textarea"},
                {"label": "Фото", "name": "photo", "type": "image"},
            ],
        },
    ],
    "form": [
        {"label": "Заголовок формы", "name": "heading", "type": "text"},
        {"label": "Подзаголовок", "name": "subheading", "type": "text"},
        {"label": "ID формы Fluent Forms", "name": "form_id", "type": "number"},
    ],
    "faq": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {
            "label": "Вопросы и ответы", "name": "items", "type": "repeater",
            "sub_fields": [
                {"label": "Вопрос", "name": "question", "type": "text"},
                {"label": "Ответ", "name": "answer", "type": "textarea"},
            ],
        },
    ],
}

DEFAULT_FIELDS = [
    {"label": "Заголовок", "name": "heading", "type": "text"},
    {"label": "Текст", "name": "body", "type": "wysiwyg"},
]


def _normalize_section(name: str) -> str:
    return SECTION_ALIASES.get(name.lower().strip(), name.lower().strip())


def _parse_sections(copy_path: Path) -> list:
    text = copy_path.read_text(encoding="utf-8")
    return re.findall(r"^##\s+(.+)$", text, re.MULTILINE)


def _build_acf_group(raw_section: str) -> dict:
    normalized = _normalize_section(raw_section)
    group_key = f"group_lp_{normalized[:20].replace(' ', '_')}"
    fields_template = SECTION_FIELDS.get(normalized, DEFAULT_FIELDS)

    def _make_field(f: dict, prefix: str) -> dict:
        field = {
            "key": f"field_{prefix}_{f['name']}",
            "label": f["label"],
            "name": f["name"],
            "type": f["type"],
        }
        if f["type"] == "repeater" and "sub_fields" in f:
            field["sub_fields"] = [_make_field(sf, prefix + "_sub") for sf in f["sub_fields"]]
        return field

    prefix = normalized[:8].replace(" ", "_")
    return {
        "key": group_key,
        "title": f"LP — {raw_section.title()}",
        "fields": [_make_field(f, prefix) for f in fields_template],
        "location": [[{
            "param": "page_template",
            "operator": "==",
            "value": "front-page.php",
        }]],
    }


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    copy_path = cwd / "07_КОНТЕНТ" / "final-copy.md"
    if not copy_path.exists():
        error(f"final-copy.md not found: {copy_path} — run /landing-content first")
        return 1

    sections = _parse_sections(copy_path)
    if not sections:
        warn("No ## sections in final-copy.md — using default section set")
        sections = ["hero", "about", "services", "proof", "form", "faq"]

    groups = [_build_acf_group(s) for s in sections]
    output = {"version": "5.12.0", "groups": groups}

    out_path = cwd / "08_КОД" / "acf-fields.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    success(f"ACF fields: {out_path} ({len(groups)} groups)")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Запустить — убедиться что ЗЕЛЁНЫЕ**

```bash
pytest tests/phase-4/python/test_generate_acf.py -v 2>&1 | tail -20
```

- [ ] **Step 5: Commit**

```bash
git add tests/phase-4/python/test_generate_acf.py skills/wp-gutenberg-block-builder/scripts/generate-acf.py
git commit -m "feat(phase-4): generate-acf.py — ACF fields JSON from final-copy.md sections"
```

---

## Task 4: test_bundle_assets.py (RED) → bundle-assets.py (GREEN)

**Files:**
- Create: `tests/phase-4/python/test_bundle_assets.py`
- Create: `skills/wp-theme-assembler/scripts/bundle-assets.py`

- [ ] **Step 1: Написать failing tests**

```python
# tests/phase-4/python/test_bundle_assets.py
"""Tests for wp-theme-assembler/scripts/bundle-assets.py"""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-theme-assembler" / "scripts" / "bundle-assets.py"


def _load():
    spec = importlib.util.spec_from_file_location("bundle_assets", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_find_project_root_success(wp_theme_project):
    mod = _load()
    root = mod._find_project_root(wp_theme_project)
    assert root == wp_theme_project


def test_find_project_root_fail(tmp_path):
    mod = _load()
    with pytest.raises(FileNotFoundError):
        mod._find_project_root(tmp_path)


def test_note_fonts_creates_stub_files(wp_theme_project, sample_stack):
    mod = _load()
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    noted = mod._note_fonts(wp_theme_project, sample_stack)
    assert "Cabinet Grotesk" in noted
    assert "Inter" in noted
    stub = theme_dir / "assets" / "fonts" / "cabinet-grotesk.txt"
    assert stub.exists()


def test_note_fonts_empty_stack(wp_theme_project):
    mod = _load()
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    (theme_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    noted = mod._note_fonts(wp_theme_project, {})
    assert noted == []


def test_copy_images_copies_files(wp_theme_project):
    # Put a fake image in processed/
    src = wp_theme_project / "02_МАТЕРИАЛЫ_КЛИЕНТА" / "photos" / "processed"
    src.mkdir(parents=True, exist_ok=True)
    (src / "hero.jpg").write_bytes(b"\xff\xd8\xff")  # minimal JPEG header
    (src / "about.png").write_bytes(b"\x89PNG")

    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    (theme_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)

    mod = _load()
    count = mod._copy_images(wp_theme_project)
    assert count == 2
    assert (theme_dir / "assets" / "images" / "hero.jpg").exists()
    assert (theme_dir / "assets" / "images" / "about.png").exists()


def test_copy_images_missing_dir_returns_zero(wp_theme_project):
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    (theme_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    mod = _load()
    count = mod._copy_images(wp_theme_project)
    assert count == 0


def test_main_returns_zero(wp_theme_project, sample_stack):
    # Pre-create theme structure
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    for p in ["assets/fonts", "assets/icons", "assets/images"]:
        (theme_dir / p).mkdir(parents=True, exist_ok=True)

    mod = _load()
    result = mod.main(["prog", str(wp_theme_project)])
    assert result == 0


def test_main_outputs_json(wp_theme_project, capsys):
    theme_dir = wp_theme_project / "08_КОД" / "wp-theme"
    for p in ["assets/fonts", "assets/icons", "assets/images"]:
        (theme_dir / p).mkdir(parents=True, exist_ok=True)

    mod = _load()
    mod.main(["prog", str(wp_theme_project)])
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert "fonts" in data
    assert "icons" in data
    assert "images_copied" in data


def test_main_missing_stack_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
```

- [ ] **Step 2: Запустить — убедиться что ПАДАЮТ**

```bash
pytest tests/phase-4/python/test_bundle_assets.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Создать директорию**

```bash
mkdir -p skills/wp-theme-assembler/scripts
```

- [ ] **Step 4: Написать bundle-assets.py**

```python
#!/usr/bin/env python3
"""Download icons from Iconify API; note font CDN references; copy processed photos.

CLI: python3 bundle-assets.py <project-dir>
Stdout: JSON {"fonts": [...], "icons": [...], "images_copied": N}
"""
import json
import shutil
import sys
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, info, success, warn


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "06_СТЕК" / "design-stack.yaml").exists():
            return parent
    raise FileNotFoundError("design-stack.yaml not found — run /landing-stack first")


def _load_stack(project: Path) -> dict:
    return yaml.safe_load((project / "06_СТЕК" / "design-stack.yaml").read_text(encoding="utf-8"))


def _note_fonts(project: Path, stack: dict) -> list:
    """Write CDN stub files — actual fonts are loaded by browser from CDN."""
    fonts_dir = project / "08_КОД" / "wp-theme" / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    families = stack.get("fonts", {}).get("families", [])
    cdn = stack.get("fonts", {}).get("cdn", "bunny")
    noted = []
    for font in families:
        name = font["name"]
        weights = font.get("weights", [400])
        slug = name.lower().replace(" ", "-")
        (fonts_dir / f"{slug}.txt").write_text(
            f"Font: {name}\nWeights: {weights}\nCDN: {cdn}\n", encoding="utf-8"
        )
        info(f"Font noted: {name} via {cdn}")
        noted.append(name)
    return noted


def _download_icons(project: Path) -> list:
    """Download SVG icons from Iconify API."""
    icons_dir = project / "08_КОД" / "wp-theme" / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    icons_yaml = project / "04_БРЕНД" / "extracted" / "icons.yaml"
    if not icons_yaml.exists():
        warn("icons.yaml not found — skipping icon download")
        return []

    data = yaml.safe_load(icons_yaml.read_text(encoding="utf-8")) or {}
    icons_list = data.get("icons", []) if isinstance(data, dict) else (data or [])

    downloaded = []
    for icon in icons_list:
        icon_id = icon.get("id") if isinstance(icon, dict) else str(icon)
        if not icon_id or ":" not in icon_id:
            continue
        prefix, name = icon_id.split(":", 1)
        url = f"https://api.iconify.design/{prefix}/{name}.svg"
        out = icons_dir / f"{prefix}-{name}.svg"
        try:
            urllib.request.urlretrieve(url, out)
            downloaded.append(icon_id)
            info(f"Icon: {icon_id}")
        except Exception as exc:
            warn(f"Icon download failed {icon_id}: {exc}")

    return downloaded


def _copy_images(project: Path) -> int:
    src = project / "02_МАТЕРИАЛЫ_КЛИЕНТА" / "photos" / "processed"
    dst = project / "08_КОД" / "wp-theme" / "assets" / "images"
    dst.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        warn(f"Processed photos not found: {src}")
        return 0

    count = 0
    for img in src.iterdir():
        if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".svg"}:
            shutil.copy2(img, dst / img.name)
            count += 1

    info(f"Copied {count} images → assets/images/")
    return count


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        project = _find_project_root(cwd)
    except FileNotFoundError as e:
        error(str(e))
        return 1

    stack = _load_stack(project)
    fonts = _note_fonts(project, stack)
    icons = _download_icons(project)
    images = _copy_images(project)

    result = {"fonts": fonts, "icons": icons, "images_copied": images}
    print(json.dumps(result))
    success(f"Assets bundled: {len(fonts)} fonts, {len(icons)} icons, {images} images")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Запустить — убедиться что ЗЕЛЁНЫЕ**

```bash
pytest tests/phase-4/python/test_bundle_assets.py -v 2>&1 | tail -20
```

- [ ] **Step 6: Commit**

```bash
git add tests/phase-4/python/test_bundle_assets.py skills/wp-theme-assembler/scripts/bundle-assets.py
git commit -m "feat(phase-4): bundle-assets.py — note fonts, download icons, copy images"
```

---

## Task 5: build-preview.html.j2 + test_render_build_preview.py (RED) → render-build-preview.py (GREEN)

**Files:**
- Create: `tools/html/templates/build-preview.html.j2`
- Create: `tests/phase-4/python/test_render_build_preview.py`
- Create: `skills/wp-theme-assembler/scripts/render-build-preview.py`

- [ ] **Step 1: Написать build-preview.html.j2**

```html
{# tools/html/templates/build-preview.html.j2 #}
{% extends "base.html.j2" %}
{% block title %}Build Preview — {{ project_name }}{% endblock %}
{% block content %}
<div style="font-family:sans-serif;max-width:1100px;margin:0 auto;padding:2rem">

  <h1 style="font-size:1.75rem;margin-bottom:0.25rem">🏗 Build Preview</h1>
  <p style="color:#666;margin-bottom:2rem">{{ project_name }} — Stage 08</p>

  <!-- CSS Variables Preview -->
  <section style="margin-bottom:2.5rem">
    <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem">Color Tokens</h2>
    <div style="display:flex;flex-wrap:wrap;gap:0.75rem">
      {% for name, props in tokens.get('colors', {}).items() %}
      {% set hex = props.hex if props is mapping else props %}
      <div style="text-align:center">
        <div style="width:64px;height:64px;border-radius:8px;background:{{ hex }};border:1px solid #ddd;margin-bottom:0.25rem"></div>
        <div style="font-size:0.7rem;color:#333">{{ name }}</div>
        <div style="font-size:0.65rem;color:#888">{{ hex }}</div>
      </div>
      {% endfor %}
    </div>
  </section>

  <!-- Typography Preview -->
  <section style="margin-bottom:2.5rem">
    <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem">Typography Tokens</h2>
    {% for role, props in tokens.get('typography', {}).items() %}
    {% if props is mapping %}
    <div style="margin-bottom:0.75rem">
      <span style="font-family:{{ props.family }},sans-serif;font-size:{{ props.size }};font-weight:{{ props.weight }};line-height:{{ props.line_height }}">
        {{ role|title }}: {{ props.family }}
      </span>
      <span style="font-size:0.75rem;color:#888;margin-left:0.5rem">{{ props.size }} / {{ props.weight }}</span>
    </div>
    {% endif %}
    {% endfor %}
  </section>

  <!-- Stack Summary -->
  <section style="margin-bottom:2.5rem">
    <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem">Stack</h2>
    <p><strong>Mode:</strong> {{ stack.get('mode', 'standard') }}</p>
    {% if stack.get('wordpress', {}).get('plugins') %}
    <p><strong>Plugins:</strong> {{ stack.wordpress.plugins | join(', ') }}</p>
    {% endif %}
    {% if stack.get('js_libraries') %}
    <p><strong>JS Libraries:</strong> {{ stack.js_libraries | join(', ') }}</p>
    {% endif %}
  </section>

  <!-- Template Parts -->
  <section style="margin-bottom:2.5rem">
    <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem">Template Parts ({{ template_parts | length }})</h2>
    <div style="display:flex;flex-wrap:wrap;gap:0.5rem">
      {% for part in template_parts %}
      <span style="background:#f0f4ff;border:1px solid #c7d4f5;border-radius:4px;padding:0.2rem 0.6rem;font-size:0.8rem">{{ part }}</span>
      {% endfor %}
    </div>
  </section>

  <!-- ACF Field Groups -->
  <section style="margin-bottom:2.5rem">
    <h2 style="font-size:1.1rem;font-weight:700;margin-bottom:1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem">ACF Field Groups ({{ acf_groups | length }})</h2>
    {% for group in acf_groups %}
    <details style="margin-bottom:0.75rem;border:1px solid #eee;border-radius:6px;padding:0.75rem">
      <summary style="cursor:pointer;font-weight:600">{{ group.title }} <span style="font-weight:400;color:#888;font-size:0.8rem">({{ group.fields | length }} fields)</span></summary>
      <ul style="margin:0.5rem 0 0 1rem;padding:0">
        {% for field in group.fields %}
        <li style="font-size:0.85rem;margin-bottom:0.25rem">
          <code>{{ field.name }}</code> — {{ field.label }} <span style="color:#888">[{{ field.type }}]</span>
        </li>
        {% endfor %}
      </ul>
    </details>
    {% endfor %}
  </section>

  <footer style="color:#aaa;font-size:0.75rem;border-top:1px solid #eee;padding-top:1rem;margin-top:2rem">
    Generated by landing-system wp-theme-assembler · Stage 08
  </footer>

</div>
{% endblock %}
```

- [ ] **Step 2: Написать failing tests**

```python
# tests/phase-4/python/test_render_build_preview.py
"""Tests for wp-theme-assembler/scripts/render-build-preview.py"""
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "wp-theme-assembler" / "scripts" / "render-build-preview.py"


def _load():
    spec = importlib.util.spec_from_file_location("render_build_preview", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _setup_project(tmp_path, sample_tokens, sample_stack):
    """Create minimal phase-4 project with theme scaffold."""
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").write_text(
        json.dumps(sample_tokens), encoding="utf-8"
    )
    (tmp_path / "06_СТЕК").mkdir()
    (tmp_path / "06_СТЕК" / "design-stack.yaml").write_text(
        yaml.dump(sample_stack, allow_unicode=True), encoding="utf-8"
    )
    theme_dir = tmp_path / "08_КОД" / "wp-theme"
    tp = theme_dir / "template-parts"
    tp.mkdir(parents=True)
    (theme_dir / "style.css").write_text("/* Theme Name: LP Test */\n")
    for section in ["hero", "about", "form"]:
        (tp / f"section-{section}.php").write_text("<?php //placeholder\n")
    acf = tmp_path / "08_КОД" / "acf-fields.json"
    acf.write_text(json.dumps({"groups": [
        {"key": "group_hero", "title": "LP — Hero", "fields": [
            {"key": "f1", "label": "Заголовок", "name": "heading", "type": "text"}
        ]}
    ]}))
    return tmp_path


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    result = mod.main(["prog", str(project)])
    assert result == 0


def test_main_creates_build_preview_html(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    out = project / "08_КОД" / "build-preview.html"
    assert out.exists()


def test_preview_contains_project_name(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert project.name in html


def test_preview_contains_color_tokens(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert "#ff5733" in html


def test_preview_contains_acf_group(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert "LP — Hero" in html


def test_preview_contains_template_parts(tmp_path, sample_tokens, sample_stack):
    project = _setup_project(tmp_path, sample_tokens, sample_stack)
    mod = _load()
    mod.main(["prog", str(project)])
    html = (project / "08_КОД" / "build-preview.html").read_text(encoding="utf-8")
    assert "section-hero" in html


def test_main_missing_style_css_returns_one(tmp_path):
    mod = _load()
    result = mod.main(["prog", str(tmp_path)])
    assert result == 1
```

- [ ] **Step 3: Запустить — убедиться что ПАДАЮТ**

```bash
pytest tests/phase-4/python/test_render_build_preview.py -v 2>&1 | tail -10
```

- [ ] **Step 4: Написать render-build-preview.py**

```python
#!/usr/bin/env python3
"""Render static HTML preview of the built WP theme.

CLI: python3 render-build-preview.py <project-dir>
Stdout: path to build-preview.html
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success
from tools.html import render


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "08_КОД" / "wp-theme" / "style.css").exists():
            return parent
    raise FileNotFoundError("08_КОД/wp-theme/style.css not found — run /landing-build first")


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        project = _find_project_root(cwd)
    except FileNotFoundError as e:
        error(str(e))
        return 1

    tokens_path = project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    tokens = json.loads(tokens_path.read_text(encoding="utf-8")) if tokens_path.exists() else {}

    stack_path = project / "06_СТЕК" / "design-stack.yaml"
    stack = yaml.safe_load(stack_path.read_text(encoding="utf-8")) if stack_path.exists() else {}

    acf_path = project / "08_КОД" / "acf-fields.json"
    acf = json.loads(acf_path.read_text(encoding="utf-8")) if acf_path.exists() else {"groups": []}

    theme_dir = project / "08_КОД" / "wp-theme"
    tp_dir = theme_dir / "template-parts"
    template_parts = sorted(f.stem for f in tp_dir.iterdir() if f.suffix == ".php") if tp_dir.exists() else []

    context = {
        "project_name": project.name,
        "tokens": tokens,
        "stack": stack,
        "acf_groups": acf.get("groups", []),
        "template_parts": template_parts,
    }

    html = render.render("build-preview.html.j2", context)
    out = project / "08_КОД" / "build-preview.html"
    out.write_text(html, encoding="utf-8")

    success(f"Build preview: {out}")
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Запустить — убедиться что ЗЕЛЁНЫЕ**

```bash
pytest tests/phase-4/python/test_render_build_preview.py -v 2>&1 | tail -20
```

- [ ] **Step 6: Commit**

```bash
git add tools/html/templates/build-preview.html.j2 \
        tests/phase-4/python/test_render_build_preview.py \
        skills/wp-theme-assembler/scripts/render-build-preview.py
git commit -m "feat(phase-4): render-build-preview.py + build-preview.html.j2"
```

---

## Task 6: SKILL.md для wp-gutenberg-block-builder и wp-theme-assembler

**Files:**
- Create: `skills/wp-gutenberg-block-builder/SKILL.md`
- Create: `skills/wp-theme-assembler/SKILL.md`

- [ ] **Step 1: Написать wp-gutenberg-block-builder/SKILL.md**

```markdown
---
name: wp-gutenberg-block-builder
description: Generate WordPress theme scaffold, Gutenberg blocks, and ACF fields JSON from DESIGN.md + final-copy.md. Used by wp-builder agent during stage 08.
---

# wp-gutenberg-block-builder

Скилл для генерации кода WordPress-темы из токенов и контента.

## Scripts

### generate-theme.py

Читает `05_ДИЗАЙН-СИСТЕМА/tokens.json` + `06_СТЕК/design-stack.yaml`.
Создаёт `08_КОД/wp-theme/` с:
- `style.css` — Theme header + CSS-переменные из всех токенов
- `functions.php` — enqueue стилей/скриптов (шрифты с Bunny CDN, GSAP если cinematic)
- `index.php`, `front-page.php` — базовые PHP-шаблоны
- `template-parts/section-{hero,about,services,proof,form,faq}.php` — заглушки для агента
- `assets/css/main.css`, `assets/js/main.js` — заглушки
- `08_КОД/gutenberg-blocks/` — директория для блоков

```bash
python3 skills/wp-gutenberg-block-builder/scripts/generate-theme.py <project-dir>
```

### generate-acf.py

Парсит `07_КОНТЕНТ/final-copy.md` (H2-секции → ACF-группы).
Создаёт `08_КОД/acf-fields.json` с правильными field types по типу секции.
Поддерживает русские названия секций (ОТЗЫВЫ→proof, ФОРМА→form, УСЛУГИ→services).

```bash
python3 skills/wp-gutenberg-block-builder/scripts/generate-acf.py <project-dir>
```

## Usage in wp-builder agent

```
1. Run generate-theme.py → получаем scaffold
2. Run generate-acf.py → получаем ACF конфиг
3. Заполнить template-parts/*.php реальным кодом блоков
4. Написать assets/css/main.css и assets/js/main.js
```
```

- [ ] **Step 2: Написать wp-theme-assembler/SKILL.md**

```markdown
---
name: wp-theme-assembler
description: Bundle fonts/icons/images into wp-theme assets; render static build-preview.html. Used after wp-builder agent completes stage 08.
---

# wp-theme-assembler

Финальная сборка темы: загрузка ресурсов + генерация preview.

## Scripts

### bundle-assets.py

- Записывает CDN-заглушки для шрифтов (Font Name + CDN) в `assets/fonts/`
- Скачивает SVG-иконки с Iconify API → `assets/icons/`
- Копирует `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/` → `assets/images/`

```bash
python3 skills/wp-theme-assembler/scripts/bundle-assets.py <project-dir>
# stdout: JSON {"fonts": [...], "icons": [...], "images_copied": N}
```

### render-build-preview.py

Читает `tokens.json` + `design-stack.yaml` + `acf-fields.json` + список template-parts.
Рендерит `08_КОД/build-preview.html` через Jinja2 (`build-preview.html.j2`).
Preview показывает: цветовые токены, типографику, стек, template parts, ACF-группы.

```bash
python3 skills/wp-theme-assembler/scripts/render-build-preview.py <project-dir>
# stdout: path to build-preview.html
```

## Usage sequence

```
1. wp-builder agent завершил template-parts + CSS/JS
2. integrations-engineer добавил forms в functions.php
3. analytics-engineer добавил Metrika код
4. seo-optimizer добавил meta tags
5. Run bundle-assets.py → скачиваем ресурсы
6. Run render-build-preview.py → генерируем preview
7. HARD GATE: показываем build-preview.html пользователю
```
```

- [ ] **Step 3: Commit**

```bash
git add skills/wp-gutenberg-block-builder/SKILL.md skills/wp-theme-assembler/SKILL.md
git commit -m "feat(phase-4): SKILL.md for wp-gutenberg-block-builder and wp-theme-assembler"
```

---

## Task 7: agents/wp-builder.md, integrations-engineer.md, analytics-engineer.md, seo-optimizer.md

**Files:**
- Create: `agents/wp-builder.md`
- Create: `agents/integrations-engineer.md`
- Create: `agents/analytics-engineer.md`
- Create: `agents/seo-optimizer.md`

- [ ] **Step 1: Написать agents/wp-builder.md**

```markdown
---
name: wp-builder
description: Use during stage 08 after design-system-generator and content-writer have run. Generates Gutenberg block PHP+JS code, fills template-parts, writes CSS/JS, creates generateblocks-templates.json.
allowed-tools: Bash, Read, Write, Edit
---

# wp-builder (WP-сборщик)

## Mission

Генерирую PHP-код Gutenberg-блоков и CSS/JS для лендинга на основе токенов дизайна и финального контента.

## Prerequisites

- `08_КОД/wp-theme/` уже создан `generate-theme.py` (scaffold готов)
- `08_КОД/acf-fields.json` уже создан `generate-acf.py`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены
- `07_КОНТЕНТ/final-copy.md` — финальный текст по блокам
- `06_СТЕК/design-stack.yaml` — стек и режим (standard/cinematic)

## What I do

1. Читаю `07_КОНТЕНТ/final-copy.md` — извлекаю текст каждой секции.
2. Читаю `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, типографику, отступы, радиус.
3. Читаю `06_СТЕК/design-stack.yaml` — режим, иконки, JS-библиотеки.
4. Читаю `08_КОД/acf-fields.json` — какие поля доступны через ACF.
5. Для каждой секции пишу `template-parts/section-{name}.php`:
   - Использует `get_field()` из ACF для редактируемых полей
   - CSS-классы только через `--token-name` переменные (без хардкода цветов)
   - Каждый файл начинается с комментария `/* wp-builder: source=DESIGN.md, token=... */`
6. Пишу `assets/css/main.css` — стили всех блоков через CSS-переменные.
7. Пишу `assets/js/main.js` — базовые интеракции (аккордеон FAQ, scroll-to-form).
   - Если режим `cinematic`: добавляю GSAP ScrollTrigger анимации по scenes.md.
8. Пишу `08_КОД/gutenberg-blocks/` — для любых кастомных блоков вне GenerateBlocks.
9. Пишу `08_КОД/generateblocks-templates.json` — шаблон для импорта в GenerateBlocks.
10. **HARD GATE**: показываю список созданных файлов, жду утверждения.

## PHP Block Rules

```php
<?php
// section-hero.php — wp-builder: source=DESIGN.md, tokens=[color-primary, font-display]
$heading    = get_field('heading')    ?: 'Заголовок';
$subheading = get_field('subheading') ?: '';
$cta_text   = get_field('cta_text')   ?: 'Записаться';
$bg_image   = get_field('bg_image');
$bg_url     = $bg_image ? esc_url($bg_image['url']) : '';
?>
<section class="lp-hero" <?php if ($bg_url): ?>style="background-image:url('<?= $bg_url ?>')"<?php endif; ?>>
  <div class="lp-hero__inner lp-container">
    <h1 class="lp-hero__heading"><?= esc_html($heading) ?></h1>
    <?php if ($subheading): ?>
    <p class="lp-hero__sub"><?= esc_html($subheading) ?></p>
    <?php endif; ?>
    <a href="#form" class="lp-btn lp-btn--primary"><?= esc_html($cta_text) ?></a>
  </div>
</section>
```

## CSS Rules

- Только CSS-переменные: `var(--color-primary)`, `var(--font-display-family)`, `var(--space-lg)`
- Никакого хардкода цветов или шрифтов
- Mobile-first: базовые стили → `@media (min-width: 768px)` → `@media (min-width: 1440px)`
- Контейнер: `.lp-container { max-width: var(--grid-max-width, 1200px); margin: 0 auto; padding: 0 var(--space-md); }`

## Cinematic Mode (если js_libraries содержит gsap)

Читаю `05_ДИЗАЙН-СИСТЕМА/scenes.md`. Для каждой сцены:
- Добавляю `data-scene="N"` атрибуты в PHP-шаблоны
- В main.js пишу GSAP ScrollTrigger timeline по scenes.md motion-плану
- Инициализирую Lenis для smooth scroll

## Output

- `08_КОД/wp-theme/template-parts/section-*.php` (заполненные)
- `08_КОД/wp-theme/assets/css/main.css`
- `08_КОД/wp-theme/assets/js/main.js`
- `08_КОД/gutenberg-blocks/` (если есть кастомные блоки)
- `08_КОД/generateblocks-templates.json`

## Rules

- ❌ Никакого Lorem ipsum
- ❌ Никакого хардкода цветов — только CSS-переменные
- ❌ Никаких inline-стилей кроме dynamic (background-image из ACF)
- ✅ Каждый PHP-файл начинается с provenance-комментария
- ✅ Все user-facing строки через `esc_html()` или `wp_kses_post()`
```

- [ ] **Step 2: Написать agents/integrations-engineer.md**

```markdown
---
name: integrations-engineer
description: Use during stage 08 after wp-builder. Configures Fluent Forms for the landing, adds Telegram webhook and CRM webhook to functions.php.
allowed-tools: Bash, Read, Write, Edit
---

# integrations-engineer (Инженер интеграций)

## Mission

Настраиваю формы и вебхуки: Fluent Forms → Telegram + CRM.

## Prerequisites

- `08_КОД/wp-theme/functions.php` создан wp-builder
- `08_КОД/acf-fields.json` содержит поле `form_id` для секции form
- `.env` проекта содержит `TELEGRAM_BOT_TOKEN`, `TELEGRAM_LEADS_CHAT_ID` (или `CRM_WEBHOOK_URL`)

## What I do

1. Читаю `.env` (или `.env.example` если нет `.env`) — определяю наличие TELEGRAM_BOT_TOKEN и CRM_WEBHOOK_URL.
2. Генерирую PHP-сниппет отправки лида в Telegram:
   ```php
   function lp_send_lead_to_telegram($form_data, $entry, $form) {
       $token   = getenv('TELEGRAM_BOT_TOKEN');
       $chat_id = getenv('TELEGRAM_LEADS_CHAT_ID');
       if (!$token || !$chat_id) return;
       $msg = "🎯 Новый лид с лендинга:\n";
       foreach ($form_data as $key => $val) {
           $msg .= esc_html($key) . ': ' . esc_html($val) . "\n";
       }
       wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", [
           'body' => ['chat_id' => $chat_id, 'text' => $msg],
       ]);
   }
   add_action('fluentform/submission_inserted', 'lp_send_lead_to_telegram', 10, 3);
   ```
3. Если CRM_WEBHOOK_URL задан — аналогичный хук с `wp_remote_post($crm_url, ['body' => $form_data])`.
4. Добавляю оба PHP-сниппета в `functions.php` (заменяю плейсхолдер `// [FLUENT_WEBHOOK]`).
5. Записываю `07_КОНТЕНТ/` — нет. Записываю в `08_КОД/wp-theme/functions.php`.
6. **HARD GATE**: показываю добавленный код, жду утверждения.

## Security Rules

- ❌ Никогда не хардкодить токены — только через `getenv()`
- ✅ Все пользовательские данные — через `esc_html()` перед отправкой
- ✅ Fluent Forms сам валидирует поля формы на WP-стороне

## Output

- `08_КОД/wp-theme/functions.php` (дополнен Telegram/CRM хуком)
```

- [ ] **Step 3: Написать agents/analytics-engineer.md**

```markdown
---
name: analytics-engineer
description: Use during stage 08 after integrations-engineer. Adds Yandex Metrika counter code to functions.php and creates 11_АНАЛИТИКА/ config files.
allowed-tools: Bash, Read, Write, Edit
---

# analytics-engineer (Инженер аналитики)

## Mission

Подключаю Яндекс.Метрику к лендингу и настраиваю цели.

## Prerequisites

- `08_КОД/wp-theme/functions.php` существует
- `.env` содержит `YM_COUNTER_ID` (8-значное число)

## What I do

1. Читаю `YM_COUNTER_ID` из `.env` (или `.env.example`).
2. Генерирую PHP-функцию вставки Метрики в `<head>`:
   ```php
   function lp_yandex_metrika() {
       $counter_id = getenv('YM_COUNTER_ID');
       if (!$counter_id) return;
       ?>
       <!-- Yandex.Metrika counter -->
       <script type="text/javascript">
         (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
         m[i].l=1*new Date();
         for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}
         k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
         (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
         ym(<?= intval($counter_id) ?>, "init", {
           clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true
         });
       </script>
       <noscript><div><img src="https://mc.yandex.ru/watch/<?= intval($counter_id) ?>"
         style="position:absolute;left:-9999px;" alt="" /></div></noscript>
       <!-- /Yandex.Metrika counter -->
       <?php
   }
   add_action('wp_head', 'lp_yandex_metrika');
   ```
3. Добавляю сниппет в `functions.php` (заменяю `// [YM_COUNTER]`).
4. Определяю цели по секциям лендинга (клик по CTA, отправка формы).
5. Пишу `11_АНАЛИТИКА/metrika-config.md` с ID счётчика и списком целей.
6. Пишу `11_АНАЛИТИКА/goals-and-events.json` с целями для ручной настройки в Метрике.
7. Пишу `11_АНАЛИТИКА/utm-templates.md` с шаблонами UTM для Я.Директ.
8. **HARD GATE**: показываю metrika-config.md, жду утверждения.

## Output

- `08_КОД/wp-theme/functions.php` (дополнен кодом Метрики)
- `11_АНАЛИТИКА/metrika-config.md`
- `11_АНАЛИТИКА/goals-and-events.json`
- `11_АНАЛИТИКА/utm-templates.md`
```

- [ ] **Step 4: Написать agents/seo-optimizer.md**

```markdown
---
name: seo-optimizer
description: Use during stage 08 after analytics-engineer. Adds SEO meta tags to functions.php, generates Schema.org JSON-LD, robots.txt, and meta-tags.yaml for 12_SEO/.
allowed-tools: Bash, Read, Write, Edit
---

# seo-optimizer (SEO-оптимизатор)

## Mission

Оптимизирую лендинг под поисковые системы: мета-теги, Schema.org, robots.txt.

## Prerequisites

- `07_КОНТЕНТ/seo-copy.md` — SEO-варианты заголовков и descriptions
- `08_КОД/wp-theme/functions.php` существует
- `00_БРИФ/approved-design-brief.md` — ниша, ЦА, ключевые слова

## What I do

1. Читаю `07_КОНТЕНТ/seo-copy.md` — title, description, h1 варианты.
2. Читаю `00_БРИФ/approved-design-brief.md` — ниша, гео, CTA.
3. Генерирую PHP-функцию мета-тегов:
   ```php
   function lp_seo_meta() {
       remove_action('wp_head', '_wp_render_title_tag', 1);
       $title = 'Заголовок страницы | Бренд';
       $desc  = 'Описание до 160 символов';
       $url   = home_url('/');
       ?>
       <title><?= esc_html($title) ?></title>
       <meta name="description" content="<?= esc_attr($desc) ?>">
       <meta property="og:title" content="<?= esc_attr($title) ?>">
       <meta property="og:description" content="<?= esc_attr($desc) ?>">
       <meta property="og:url" content="<?= esc_url($url) ?>">
       <meta property="og:type" content="website">
       <link rel="canonical" href="<?= esc_url($url) ?>">
       <?php
   }
   add_action('wp_head', 'lp_seo_meta', 1);
   ```
4. Добавляю функцию в functions.php (заменяю `// [SEO_META]`).
5. Генерирую Schema.org JSON-LD (LocalBusiness или Organization по брифу):
   ```php
   function lp_schema_org() { ?>
   <script type="application/ld+json">
   {"@context":"https://schema.org","@type":"LocalBusiness",
    "name":"...", "description":"...", "url":"<?= home_url() ?>"}
   </script>
   <?php }
   add_action('wp_head', 'lp_schema_org');
   ```
6. Пишу `12_SEO/meta-tags.yaml` — title/description/og по правилам.
7. Пишу `12_SEO/structured-data.json` — Schema.org объект.
8. Пишу `12_SEO/robots.txt` — запрет служебных страниц WP, Allow: /.
9. Пишу `12_SEO/keywords.md` — ключевые слова из брифа (Wordstat данные добавляются на этапе 12).
10. **HARD GATE**: показываю meta-tags.yaml + structured-data.json, жду утверждения.

## SEO Rules

- Title: 50–60 символов, ключевое слово первым
- Description: 140–160 символов, призыв к действию
- h1 = один на странице, совпадает с title-темой
- Все изображения должны иметь alt= (проверяю template-parts PHP-код)
- Schema.org тип: LocalBusiness (услуги) или Course (обучение) или Organization

## Output

- `08_КОД/wp-theme/functions.php` (дополнен SEO-функциями)
- `12_SEO/meta-tags.yaml`
- `12_SEO/structured-data.json`
- `12_SEO/robots.txt`
- `12_SEO/keywords.md`
```

- [ ] **Step 5: Commit**

```bash
git add agents/wp-builder.md agents/integrations-engineer.md \
        agents/analytics-engineer.md agents/seo-optimizer.md
git commit -m "feat(phase-4): agents wp-builder, integrations-engineer, analytics-engineer, seo-optimizer"
```

---

## Task 8: .claude/commands/landing-build.md

**Files:**
- Create: `.claude/commands/landing-build.md`

- [ ] **Step 1: Написать landing-build.md**

```markdown
---
description: Generate or regenerate the WordPress theme, Gutenberg blocks, ACF fields, integrations, analytics, and SEO config for a landing project (stage 08). Run within a landing project folder after /landing-content is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-build

Run within a landing project after `content-writer` has produced `07_КОНТЕНТ/final-copy.md`.

## What I do

### Step 1 — Theme Scaffold (deterministic)
Run `generate-theme.py` to create `08_КОД/wp-theme/` structure with CSS variables, functions.php, template-parts stubs.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-theme.py .
```

### Step 2 — ACF Fields (deterministic)
Run `generate-acf.py` to create `08_КОД/acf-fields.json` from final-copy.md sections.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-acf.py .
```

### Step 3 — Gutenberg Blocks (AI agent)
Invoke `wp-builder` agent → fills template-parts PHP code, writes main.css + main.js, creates generateblocks-templates.json.

### Step 4 — Forms & Integrations (AI agent)
Invoke `integrations-engineer` agent → adds Fluent Forms webhook (Telegram/CRM) to functions.php.

### Step 5 — Analytics (AI agent)
Invoke `analytics-engineer` agent → adds Yandex Metrika code to functions.php, creates 11_АНАЛИТИКА/ files.

### Step 6 — SEO (AI agent)
Invoke `seo-optimizer` agent → adds meta tags + Schema.org to functions.php, creates 12_SEO/ files.

### Step 7 — Bundle Assets
Run `bundle-assets.py` to note fonts, download icons, copy processed photos.

```bash
python3 <landing-system>/skills/wp-theme-assembler/scripts/bundle-assets.py .
```

### Step 8 — Build Preview
Run `render-build-preview.py` to create static `08_КОД/build-preview.html`.

```bash
python3 <landing-system>/skills/wp-theme-assembler/scripts/render-build-preview.py .
```

### Step 9 — HARD GATE
Show path to `08_КОД/build-preview.html`. Wait for user approval before proceeding to stage 09 (deploy).

## Usage

```
/landing-build
/landing-build --cinematic   # also wire GSAP/ScrollTrigger in wp-builder step
```

## Requirements

- `07_КОНТЕНТ/final-copy.md` — from `/landing-content`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — from `/landing-design`
- `06_СТЕК/design-stack.yaml` — from `/landing-stack`

## Output

- `08_КОД/wp-theme/` — complete WP theme (PHP + CSS + JS + assets)
- `08_КОД/acf-fields.json` — ACF field configuration
- `08_КОД/gutenberg-blocks/` — custom Gutenberg blocks
- `08_КОД/generateblocks-templates.json` — GenerateBlocks template export
- `08_КОД/build-preview.html` — static preview for approval
- `11_АНАЛИТИКА/metrika-config.md`, `goals-and-events.json`, `utm-templates.md`
- `12_SEO/meta-tags.yaml`, `structured-data.json`, `robots.txt`, `keywords.md`
```

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/landing-build.md
git commit -m "feat(phase-4): /landing-build slash command"
```

---

## Task 9: Bats-тесты для агентов и команд

**Files:**
- Create: `tests/phase-4/test-agents-phase4.bats`
- Create: `tests/phase-4/test-commands-phase4.bats`

- [ ] **Step 1: Написать test-agents-phase4.bats**

```bash
#!/usr/bin/env bats
# tests/phase-4/test-agents-phase4.bats

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
AGENTS_DIR="$REPO_ROOT/agents"

@test "wp-builder.md exists" {
  [ -f "$AGENTS_DIR/wp-builder.md" ]
}

@test "wp-builder.md has name frontmatter" {
  grep -q "^name: wp-builder" "$AGENTS_DIR/wp-builder.md"
}

@test "wp-builder.md has description frontmatter" {
  grep -q "^description:" "$AGENTS_DIR/wp-builder.md"
}

@test "wp-builder.md mentions stage 08" {
  grep -q "stage 08\|этап 08\|08" "$AGENTS_DIR/wp-builder.md"
}

@test "wp-builder.md has HARD GATE" {
  grep -qi "hard gate" "$AGENTS_DIR/wp-builder.md"
}

@test "integrations-engineer.md exists" {
  [ -f "$AGENTS_DIR/integrations-engineer.md" ]
}

@test "integrations-engineer.md has name frontmatter" {
  grep -q "^name: integrations-engineer" "$AGENTS_DIR/integrations-engineer.md"
}

@test "integrations-engineer.md mentions Telegram" {
  grep -qi "telegram" "$AGENTS_DIR/integrations-engineer.md"
}

@test "integrations-engineer.md mentions Fluent Forms" {
  grep -qi "fluent" "$AGENTS_DIR/integrations-engineer.md"
}

@test "analytics-engineer.md exists" {
  [ -f "$AGENTS_DIR/analytics-engineer.md" ]
}

@test "analytics-engineer.md has name frontmatter" {
  grep -q "^name: analytics-engineer" "$AGENTS_DIR/analytics-engineer.md"
}

@test "analytics-engineer.md mentions Yandex Metrika" {
  grep -qi "метрика\|metrika" "$AGENTS_DIR/analytics-engineer.md"
}

@test "analytics-engineer.md mentions YM_COUNTER_ID" {
  grep -q "YM_COUNTER_ID" "$AGENTS_DIR/analytics-engineer.md"
}

@test "seo-optimizer.md exists" {
  [ -f "$AGENTS_DIR/seo-optimizer.md" ]
}

@test "seo-optimizer.md has name frontmatter" {
  grep -q "^name: seo-optimizer" "$AGENTS_DIR/seo-optimizer.md"
}

@test "seo-optimizer.md mentions Schema.org" {
  grep -qi "schema.org\|schema" "$AGENTS_DIR/seo-optimizer.md"
}

@test "seo-optimizer.md mentions robots.txt" {
  grep -q "robots.txt" "$AGENTS_DIR/seo-optimizer.md"
}

@test "seo-optimizer.md has HARD GATE" {
  grep -qi "hard gate" "$AGENTS_DIR/seo-optimizer.md"
}
```

- [ ] **Step 2: Написать test-commands-phase4.bats**

```bash
#!/usr/bin/env bats
# tests/phase-4/test-commands-phase4.bats

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
COMMANDS_DIR="$REPO_ROOT/.claude/commands"
SKILLS_DIR="$REPO_ROOT/skills"

@test "landing-build.md command exists" {
  [ -f "$COMMANDS_DIR/landing-build.md" ]
}

@test "landing-build.md has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions generate-theme.py" {
  grep -q "generate-theme.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions generate-acf.py" {
  grep -q "generate-acf.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions bundle-assets.py" {
  grep -q "bundle-assets.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions render-build-preview.py" {
  grep -q "render-build-preview.py" "$COMMANDS_DIR/landing-build.md"
}

@test "landing-build.md mentions HARD GATE" {
  grep -qi "hard gate" "$COMMANDS_DIR/landing-build.md"
}

@test "wp-gutenberg-block-builder SKILL.md exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/SKILL.md" ]
}

@test "wp-theme-assembler SKILL.md exists" {
  [ -f "$SKILLS_DIR/wp-theme-assembler/SKILL.md" ]
}

@test "generate-theme.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-theme.py" ]
}

@test "generate-acf.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-acf.py" ]
}

@test "bundle-assets.py exists" {
  [ -f "$SKILLS_DIR/wp-theme-assembler/scripts/bundle-assets.py" ]
}

@test "render-build-preview.py exists" {
  [ -f "$SKILLS_DIR/wp-theme-assembler/scripts/render-build-preview.py" ]
}

@test "build-preview.html.j2 template exists" {
  [ -f "$REPO_ROOT/tools/html/templates/build-preview.html.j2" ]
}
```

- [ ] **Step 3: Запустить — убедиться что ЗЕЛЁНЫЕ**

```bash
bats tests/phase-4/test-agents-phase4.bats tests/phase-4/test-commands-phase4.bats
```

Ожидание: все тесты `ok`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-4/test-agents-phase4.bats tests/phase-4/test-commands-phase4.bats
git commit -m "test(phase-4): bats tests for Phase 4 agents and commands"
```

---

## Task 10: Интеграционный bats-тест пайплайна Phase 4

**Files:**
- Create: `tests/phase-4/integration/test-phase4-pipeline.bats`

- [ ] **Step 1: Написать интеграционный тест**

```bash
#!/usr/bin/env bats
# tests/phase-4/integration/test-phase4-pipeline.bats
# Integration: run generate-theme.py + generate-acf.py + bundle-assets.py + render-build-preview.py on a tmp project

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
GENERATE_THEME="$REPO_ROOT/skills/wp-gutenberg-block-builder/scripts/generate-theme.py"
GENERATE_ACF="$REPO_ROOT/skills/wp-gutenberg-block-builder/scripts/generate-acf.py"
BUNDLE_ASSETS="$REPO_ROOT/skills/wp-theme-assembler/scripts/bundle-assets.py"
RENDER_PREVIEW="$REPO_ROOT/skills/wp-theme-assembler/scripts/render-build-preview.py"

setup() {
  PROJECT="$(mktemp -d)"

  # 05_ДИЗАЙН-СИСТЕМА
  mkdir -p "$PROJECT/05_ДИЗАЙН-СИСТЕМА"
  cat > "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json" <<'TOKENS'
{
  "colors": {"primary": {"hex": "#ff5733", "role": "primary", "source": "ref.png"}},
  "typography": {"display": {"family": "Cabinet Grotesk", "size": "3rem", "weight": "700", "line_height": "1.1", "source": "DOM"}},
  "spacing": {"md": "1rem"},
  "radius": {"md": "0.5rem"},
  "shadow": {},
  "breakpoints": {},
  "motion": {}
}
TOKENS

  # 06_СТЕК
  mkdir -p "$PROJECT/06_СТЕК"
  cat > "$PROJECT/06_СТЕК/design-stack.yaml" <<'STACK'
mode: standard
fonts:
  cdn: bunny
  families:
    - name: Cabinet Grotesk
      weights: [400, 700]
icons:
  library: lucide
js_libraries: []
STACK

  # 07_КОНТЕНТ
  mkdir -p "$PROJECT/07_КОНТЕНТ"
  cat > "$PROJECT/07_КОНТЕНТ/final-copy.md" <<'COPY'
# Landing Copy

## HERO
Заголовок

## ФОРМА
Форма заявки
COPY

  # 04_БРЕНД
  mkdir -p "$PROJECT/04_БРЕНД/extracted"
  echo "icons: []" > "$PROJECT/04_БРЕНД/extracted/icons.yaml"

  # Photos
  mkdir -p "$PROJECT/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed"

  # 08_КОД
  mkdir -p "$PROJECT/08_КОД"
}

teardown() {
  rm -rf "$PROJECT"
}

@test "generate-theme.py exits 0 on valid project" {
  run python3 "$GENERATE_THEME" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "generate-theme.py creates style.css with CSS vars" {
  python3 "$GENERATE_THEME" "$PROJECT"
  grep -q ":root {" "$PROJECT/08_КОД/wp-theme/style.css"
  grep -q "--color-primary" "$PROJECT/08_КОД/wp-theme/style.css"
}

@test "generate-theme.py creates functions.php with enqueue" {
  python3 "$GENERATE_THEME" "$PROJECT"
  grep -q "lp_enqueue_assets" "$PROJECT/08_КОД/wp-theme/functions.php"
  grep -q "bunny.net" "$PROJECT/08_КОД/wp-theme/functions.php"
}

@test "generate-theme.py creates template-parts stubs" {
  python3 "$GENERATE_THEME" "$PROJECT"
  [ -f "$PROJECT/08_КОД/wp-theme/template-parts/section-hero.php" ]
  [ -f "$PROJECT/08_КОД/wp-theme/template-parts/section-form.php" ]
}

@test "generate-acf.py exits 0 on valid project" {
  run python3 "$GENERATE_ACF" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "generate-acf.py creates acf-fields.json with groups" {
  python3 "$GENERATE_ACF" "$PROJECT"
  python3 -c "
import json, sys
data = json.load(open('$PROJECT/08_КОД/acf-fields.json'))
assert 'groups' in data
assert len(data['groups']) >= 2
sys.exit(0)
"
}

@test "bundle-assets.py exits 0 after generate-theme creates dirs" {
  python3 "$GENERATE_THEME" "$PROJECT"
  run python3 "$BUNDLE_ASSETS" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "bundle-assets.py stdout is valid JSON" {
  python3 "$GENERATE_THEME" "$PROJECT"
  output="$(python3 "$BUNDLE_ASSETS" "$PROJECT")"
  echo "$output" | python3 -c "import json,sys; json.load(sys.stdin)"
}

@test "render-build-preview.py exits 0 after full pipeline" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$GENERATE_ACF" "$PROJECT"
  run python3 "$RENDER_PREVIEW" "$PROJECT"
  [ "$status" -eq 0 ]
}

@test "render-build-preview.py creates build-preview.html" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$GENERATE_ACF" "$PROJECT"
  python3 "$RENDER_PREVIEW" "$PROJECT"
  [ -f "$PROJECT/08_КОД/build-preview.html" ]
}

@test "build-preview.html contains color token" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$GENERATE_ACF" "$PROJECT"
  python3 "$RENDER_PREVIEW" "$PROJECT"
  grep -q "#ff5733" "$PROJECT/08_КОД/build-preview.html"
}

@test "build-preview.html contains ACF group title" {
  python3 "$GENERATE_THEME" "$PROJECT"
  python3 "$GENERATE_ACF" "$PROJECT"
  python3 "$RENDER_PREVIEW" "$PROJECT"
  grep -qi "hero\|форма" "$PROJECT/08_КОД/build-preview.html"
}
```

- [ ] **Step 2: Запустить — убедиться что ЗЕЛЁНЫЕ**

```bash
bats tests/phase-4/integration/test-phase4-pipeline.bats
```

Ожидание: все тесты `ok`.

- [ ] **Step 3: Commit**

```bash
git add tests/phase-4/integration/test-phase4-pipeline.bats
git commit -m "test(phase-4): integration pipeline bats test"
```

---

## Task 11: Запустить все Python-тесты Phase 4 вместе

- [ ] **Step 1: Запустить полный pytest Phase 4**

```bash
pytest tests/phase-4/ -v 2>&1 | tail -30
```

Ожидание: все тесты `PASSED`.

- [ ] **Step 2: Запустить полный bats Phase 4**

```bash
bats tests/phase-4/test-agents-phase4.bats \
     tests/phase-4/test-commands-phase4.bats \
     tests/phase-4/integration/test-phase4-pipeline.bats
```

Ожидание: все `ok`.

- [ ] **Step 3: Убедиться что Phase 1-3 тесты не поломаны**

```bash
pytest tests/phase-1/ tests/phase-2/ tests/phase-3/ -q 2>&1 | tail -10
bats tests/phase-1/*.bats tests/phase-2/*.bats tests/phase-3/*.bats 2>&1 | tail -10
```

Ожидание: `passed`, `ok`.

---

## Task 12: Обновить landing-orchestrator.md и master plan

**Files:**
- Modify: `agents/landing-orchestrator.md`
- Modify: `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`

- [ ] **Step 1: Добавить Phase 4 scope в landing-orchestrator.md**

Найти секцию Phase 3 Scope и добавить аналогичную Phase 4 Scope. Прочитай файл, найди конец Phase 3 блока, добавь:

```markdown
## Phase 4 Scope (Stage 08 — Код)

When user runs `/landing-build`:
1. Run `generate-theme.py` → `08_КОД/wp-theme/` scaffold
2. Run `generate-acf.py` → `08_КОД/acf-fields.json`
3. Dispatch `wp-builder` agent → fills template-parts, CSS, JS
4. Dispatch `integrations-engineer` agent → Fluent Forms + webhooks
5. Dispatch `analytics-engineer` agent → Yandex Metrika + 11_АНАЛИТИКА/
6. Dispatch `seo-optimizer` agent → meta tags + 12_SEO/
7. Run `bundle-assets.py` → fonts noted, icons downloaded, images copied
8. Run `render-build-preview.py` → `08_КОД/build-preview.html`
9. HARD GATE: show preview path, wait for user approval
10. After approval: mark Stage 08 complete, suggest `/landing-deploy`
```

- [ ] **Step 2: Обновить master plan — Phase 4 статус**

В таблице Phase Index изменить строку Phase 4:

```
| 4 | **WP Build Pipeline** (08) | [phase-4-wp-build-pipeline.md](2026-05-04-phase-4-wp-build-pipeline.md) | ~50 steps | 8–10 ч | 🟢 Complete (2026-05-04) |
```

В секции Status обновить:

```markdown
**Текущий статус:** Phase 4 — WP Build Pipeline **completed (2026-05-04)**, tag `phase-4-complete`.

**Предыдущие фазы:**
- Phase 1 — Skeleton & Infrastructure **completed (2026-05-03)**, tag `phase-1-complete`
- Phase 2 — Brainstorming Pipeline **completed (2026-05-04)**, tag `phase-2-complete`
- Phase 3 — Design Pipeline **completed (2026-05-04)**, tag `phase-3-complete`

**Следующий шаг:** Phase 5 (Deploy & Operations, этапы 09–12) — написать детальный план перед стартом.
```

- [ ] **Step 3: Commit**

```bash
git add agents/landing-orchestrator.md docs/superpowers/plans/2026-05-03-landing-system-master-plan.md
git commit -m "feat(phase-4): extend orchestrator Phase 4 scope + mark complete in master plan"
```

- [ ] **Step 4: Тег phase-4-complete**

```bash
git tag phase-4-complete
```

---

## Self-Review

**1. Spec coverage:**
- ✅ `wp-builder` агент — Gutenberg-блоки (PHP+JS), ACF JSON-конфиг, WP-тема → Task 7
- ✅ `integrations-engineer` — Fluent Forms + Telegram/CRM → Task 7
- ✅ `analytics-engineer` — Я.Метрика, цели, UTM → Task 7
- ✅ `seo-optimizer` — мета-теги, Schema.org, sitemap stub, robots.txt → Task 7
- ✅ Скилл `wp-gutenberg-block-builder` → Task 6
- ✅ Скилл `wp-theme-assembler` → Task 6
- ✅ Slash-команда `/landing-build` → Task 8
- ✅ `08_КОД/wp-theme/` со структурой из spec → generate-theme.py (Task 2)
- ✅ `acf-fields.json` → generate-acf.py (Task 3)
- ✅ `build-preview.html` как visual artifact → Task 5
- ✅ Cinematic режим (GSAP в functions.php, scenes.md в wp-builder) → Task 2, Task 7
- ✅ CSS-переменные из tokens.json → style.css (Task 2)
- ✅ Bunny Fonts CDN → functions.php (Task 2)
- ✅ Iconify icon download → bundle-assets.py (Task 4)
- ✅ Photo copy → bundle-assets.py (Task 4)
- ✅ HARD GATE на каждом агенте → Task 7
- ✅ Provenance-комментарии в PHP-коде → wp-builder.md (Task 7)

**2. Placeholder scan:**
- ✅ Нет TBD/TODO в коде — все шаги содержат реальный код

**3. Type consistency:**
- ✅ `main(argv: list) -> int` во всех скриптах
- ✅ `_find_project_root(start: Path) -> Path` — одинаковая сигнатура
- ✅ `tokens["colors"]["primary"]["hex"]` — везде обращение через `.get("hex", ...)` или `if isinstance(props, dict)`
- ✅ `acf_groups` в context для Jinja2 = `data["groups"]` из acf-fields.json

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-04-phase-4-wp-build-pipeline.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** — свежий субагент на каждый таск, ревью между задачами, fast iteration

**2. Inline Execution** — выполнение задач в этой сессии через executing-plans с чекпоинтами

**Which approach?**
