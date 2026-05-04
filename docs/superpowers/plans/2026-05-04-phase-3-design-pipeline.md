# Phase 3 — Design Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать Design Pipeline (этапы 05–07) — агентов design-system-generator, scene-director, stack-planner, content-writer, скрипты build-tokens.py + render-preview.py, Jinja2 шаблон design-preview.html.j2, и slash-команды /landing-design, /landing-stack, /landing-content.

**Architecture:** build-tokens.py читает `04_БРЕНД/brand-kit.md` (YAML frontmatter) → расширяет токены (цвета, типографика, отступы, сетка, радиус, тени, брейкпоинты, моушн) → пишет `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` + `tokens.json`. render-preview.py читает tokens.json и рендерит design-preview.html через Jinja2. Агенты являются .md-файлами с инструкциями — генерируют контент (scenes.md, design-stack.yaml, final-copy.md) средствами AI.

**Tech Stack:** Python 3.10+, PyYAML, Jinja2, pytest/bats для тестов. Паттерны Phase 2: `main(argv: list) -> int`, `tools.html.render.render()`, `tools.logger`.

---

## Файловая структура

**Создать:**
- `tests/phase-3/conftest.py` — pytest fixtures (brand_kit_project)
- `tests/phase-3/python/test_build_tokens.py` — тесты build-tokens.py
- `tests/phase-3/python/test_render_preview.py` — тесты render-preview.py
- `tests/phase-3/test-agents-phase3.bats` — bats-тесты агентов
- `tests/phase-3/test-commands-phase3.bats` — bats-тесты команд
- `tests/phase-3/integration/test-phase3-pipeline.bats` — интеграционные тесты
- `skills/design-tokens-generation/SKILL.md` — дескриптор скилла
- `skills/design-tokens-generation/scripts/build-tokens.py` — генерация DESIGN.md + tokens.json
- `skills/design-tokens-generation/scripts/render-preview.py` — рендер HTML preview
- `tools/html/templates/design-preview.html.j2` — Jinja2 шаблон
- `agents/design-system-generator.md`
- `agents/scene-director.md`
- `agents/stack-planner.md`
- `agents/content-writer.md`
- `.claude/commands/landing-design.md`
- `.claude/commands/landing-stack.md`
- `.claude/commands/landing-content.md`

**Изменить:**
- `agents/landing-orchestrator.md` — добавить Phase 3 Scope
- `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` — отметить Phase 3 Complete

---

## Task 1: conftest.py + test_build_tokens.py (RED)

**Files:**
- Create: `tests/phase-3/conftest.py`
- Create: `tests/phase-3/python/test_build_tokens.py`

- [ ] **Step 1: Создать conftest.py с fixture brand_kit_project**

```python
# tests/phase-3/conftest.py
"""Pytest fixtures for Phase 3 tests."""
import yaml
from pathlib import Path
import pytest


@pytest.fixture
def brand_kit_project(tmp_path):
    """Project dir with 04_БРЕНД/brand-kit.md in Phase 2 format."""
    brand_dir = tmp_path / "04_БРЕНД"
    brand_dir.mkdir(parents=True)
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir()

    brand_kit = {
        "brand_kit": {
            "meta": {
                "project": "test-project",
                "created": "2026-05-04",
                "references_used": 2,
            },
            "colors": {
                "primary": {
                    "hex": "#ff5733",
                    "role": "primary",
                    "source": "ref1.png@[10, 20]",
                    "extracted_by": "color-thief",
                },
                "secondary": {
                    "hex": "#33c1ff",
                    "role": "secondary",
                    "source": "ref1.png@[50, 50]",
                    "extracted_by": "color-thief",
                },
                "accent": {
                    "hex": "#2ecc71",
                    "role": "accent",
                    "source": "ref1.png@[80, 80]",
                    "extracted_by": "color-thief",
                },
            },
            "typography": {
                "display": {
                    "family": "Cabinet Grotesk",
                    "confidence": 0.9,
                    "source": "DOM computed style",
                },
                "body": {
                    "family": "Inter",
                    "confidence": 0.9,
                    "source": "DOM computed style",
                },
            },
            "icons": {
                "library": "lucide",
                "selected": [{"id": "lucide:check", "name": "check"}],
            },
            "motion": {"notes": "Subtle transitions, 200-400ms"},
            "grid": {"notes": "12-column grid, 24px gap, 1200px max-width"},
        }
    }

    yaml_block = yaml.dump(brand_kit, allow_unicode=True, default_flow_style=False)
    content = f"---\n{yaml_block}---\n\n# Brand Kit — test-project\n"
    (brand_dir / "brand-kit.md").write_text(content, encoding="utf-8")
    return tmp_path
```

- [ ] **Step 2: Создать test_build_tokens.py с failing-тестами**

```python
# tests/phase-3/python/test_build_tokens.py
"""Tests for design-tokens-generation/scripts/build-tokens.py"""
import importlib.util
import json
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = ROOT / "skills" / "design-tokens-generation" / "scripts" / "build-tokens.py"


def _load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_creates_design_md(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    result = mod.main(["prog", str(brand_kit_project)])
    assert result == 0
    assert (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").exists()


def test_design_md_has_yaml_frontmatter(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    content = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").read_text(encoding="utf-8")
    assert content.startswith("---")
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    assert match is not None
    data = yaml.safe_load(match.group(1))
    assert "tokens" in data


def test_design_md_contains_primary_color(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    content = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").read_text(encoding="utf-8")
    assert "#ff5733" in content


def test_design_md_contains_typography(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    content = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").read_text(encoding="utf-8")
    assert "Cabinet Grotesk" in content
    assert "Inter" in content


def test_build_creates_tokens_json(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens_path = brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    assert tokens_path.exists()
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    assert "colors" in tokens
    assert "typography" in tokens
    assert "spacing" in tokens


def test_tokens_json_has_all_sections(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens = json.loads(
        (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").read_text(encoding="utf-8")
    )
    for section in ["colors", "typography", "spacing", "grid", "radius", "shadow", "breakpoints", "motion"]:
        assert section in tokens, f"Missing section: {section}"


def test_tokens_json_colors_have_provenance(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens = json.loads(
        (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json").read_text(encoding="utf-8")
    )
    assert "source" in tokens["colors"]["primary"]
    assert tokens["colors"]["primary"]["hex"] == "#ff5733"


def test_tokens_json_is_valid_json(brand_kit_project):
    mod = _load(BUILD_SCRIPT)
    mod.main(["prog", str(brand_kit_project)])
    tokens_path = brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    assert isinstance(tokens, dict)


def test_build_graceful_with_missing_brand_kit(tmp_path):
    """build-tokens.py must succeed even when brand-kit.md is absent."""
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    mod = _load(BUILD_SCRIPT)
    result = mod.main(["prog", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md").exists()
```

- [ ] **Step 3: Запустить тесты, убедиться что FAIL**

```bash
cd /path/to/landing-system
python3 -m pytest tests/phase-3/python/test_build_tokens.py -v
```

Ожидаемый результат: `ModuleNotFoundError` или `FileNotFoundError` — скрипт ещё не существует.

- [ ] **Step 4: Commit тестов**

```bash
git add tests/phase-3/conftest.py tests/phase-3/python/test_build_tokens.py
git commit -m "test(phase-3): RED — build-tokens.py test suite"
```

---

## Task 2: build-tokens.py (GREEN)

**Files:**
- Create: `skills/design-tokens-generation/SKILL.md`
- Create: `skills/design-tokens-generation/scripts/build-tokens.py`

- [ ] **Step 1: Создать SKILL.md**

```markdown
---
name: design-tokens-generation
description: Generates DESIGN.md and tokens.json from brand-kit.md. Used by design-system-generator agent at stage 05.
allowed-tools: Bash, Read, Write
---

# design-tokens-generation

Reads `04_БРЕНД/brand-kit.md` YAML frontmatter and builds a complete design token set.

## Scripts

- `scripts/build-tokens.py <project-dir>` — writes `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` + `tokens.json`
- `scripts/render-preview.py <project-dir>` — writes `05_ДИЗАЙН-СИСТЕМА/design-preview.html`
```

- [ ] **Step 2: Создать build-tokens.py**

```python
#!/usr/bin/env python3
"""Build DESIGN.md and tokens.json from 04_БРЕНД/brand-kit.md.

CLI: python3 build-tokens.py <project-dir>
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import success, warn, error

_HEX_RE = re.compile(r'^#[0-9a-fA-F]{3,8}$')
_FAMILY_RE = re.compile(r'[^a-zA-Z0-9 _\-]')


def _safe_hex(value: str) -> str:
    return value if _HEX_RE.match(str(value)) else "#000000"


def _safe_family(value: str) -> str:
    return _FAMILY_RE.sub('', str(value)).strip() or "sans-serif"


def _load_brand_kit(project_dir: Path) -> dict:
    md_path = project_dir / "04_БРЕНД" / "brand-kit.md"
    if not md_path.exists():
        warn(f"brand-kit.md not found: {md_path} — using defaults")
        return {}
    content = md_path.read_text(encoding="utf-8")
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        warn("brand-kit.md has no YAML frontmatter — using defaults")
        return {}
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        return {}
    return data.get("brand_kit", data)


def _extract_colors(bk: dict) -> dict:
    src = bk.get("colors", {})
    if not isinstance(src, dict):
        src = {}

    def _entry(role: str) -> dict:
        c = src.get(role, {})
        if isinstance(c, dict):
            return {"hex": _safe_hex(c.get("hex", "#000000")), "source": c.get("source", "brand-kit.md")}
        return {"hex": _safe_hex(str(c)), "source": "brand-kit.md"}

    return {
        "primary": _entry("primary"),
        "secondary": _entry("secondary"),
        "accent": _entry("accent"),
        "text": {"hex": "#1a1a2e", "source": "generated"},
        "bg": {"hex": "#ffffff", "source": "generated"},
    }


def _extract_typography(bk: dict) -> dict:
    src = bk.get("typography", {})
    if not isinstance(src, dict):
        src = {}

    def _entry(role: str, default_family: str, weight: int) -> dict:
        t = src.get(role, {})
        if isinstance(t, dict):
            return {
                "family": _safe_family(t.get("family", default_family)),
                "weight": weight,
                "source": t.get("source", "brand-kit.md"),
            }
        return {"family": _safe_family(str(t)), "weight": weight, "source": "brand-kit.md"}

    return {
        "display": _entry("display", "sans-serif", 700),
        "body": _entry("body", "sans-serif", 400),
        "sizes": {
            "h1": "clamp(2.5rem, 6vw, 5rem)",
            "h2": "clamp(1.75rem, 4vw, 3rem)",
            "h3": "clamp(1.25rem, 3vw, 2rem)",
            "base": "1rem",
            "sm": "0.875rem",
        },
    }


def build_tokens(bk: dict) -> dict:
    return {
        "colors": _extract_colors(bk),
        "typography": _extract_typography(bk),
        "spacing": {
            "xs": "0.5rem", "sm": "1rem", "md": "1.5rem",
            "lg": "2rem", "xl": "3rem", "2xl": "4rem", "3xl": "6rem",
        },
        "grid": {"columns": 12, "gap": "24px", "max_width": "1200px"},
        "radius": {"sm": "4px", "md": "8px", "lg": "16px", "full": "9999px"},
        "shadow": {
            "sm": "0 1px 3px rgba(0,0,0,0.1)",
            "md": "0 4px 12px rgba(0,0,0,0.1)",
            "lg": "0 16px 40px rgba(0,0,0,0.15)",
        },
        "breakpoints": {"mobile": "375px", "tablet": "768px", "desktop": "1440px"},
        "motion": {
            "duration_fast": "200ms",
            "duration_base": "300ms",
            "duration_slow": "500ms",
            "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        },
    }


def _write_design_md(project_dir: Path, tokens: dict) -> None:
    design_dir = project_dir / "05_ДИЗАЙН-СИСТЕМА"
    design_dir.mkdir(parents=True, exist_ok=True)

    colors = tokens["colors"]
    typo = tokens["typography"]
    spacing = tokens["spacing"]
    motion = tokens["motion"]
    grid = tokens["grid"]

    frontmatter = yaml.dump({"tokens": tokens}, allow_unicode=True, default_flow_style=False)

    md = f"---\n{frontmatter}---\n\n# Design System\n\n"
    md += "## Цвета\n\n| Токен | Hex | Источник |\n|---|---|---|\n"
    for name, color in colors.items():
        md += f"| `--color-{name}` | `{color['hex']}` | {color['source']} |\n"
    md += "\n## Типографика\n\n| Токен | Значение | Источник |\n|---|---|---|\n"
    md += f"| `--font-display` | {typo['display']['family']} | {typo['display']['source']} |\n"
    md += f"| `--font-body` | {typo['body']['family']} | {typo['body']['source']} |\n"
    for size_name, size_val in typo["sizes"].items():
        md += f"| `--size-{size_name}` | {size_val} | generated |\n"
    md += "\n## Отступы\n\n| Токен | Значение |\n|---|---|\n"
    for name, val in spacing.items():
        md += f"| `--space-{name}` | {val} |\n"
    md += f"\n## Сетка\n\n- Колонки: {grid['columns']}\n- Gap: {grid['gap']}\n- Max-width: {grid['max_width']}\n"
    md += "\n## Motion\n\n| Токен | Значение |\n|---|---|\n"
    for name, val in motion.items():
        md += f"| `--{name.replace('_', '-')}` | {val} |\n"

    (design_dir / "DESIGN.md").write_text(md, encoding="utf-8")


def _write_tokens_json(project_dir: Path, tokens: dict) -> None:
    design_dir = project_dir / "05_ДИЗАЙН-СИСТЕМА"
    design_dir.mkdir(parents=True, exist_ok=True)
    (design_dir / "tokens.json").write_text(
        json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(argv: list) -> int:
    p = argparse.ArgumentParser(description="Build DESIGN.md and tokens.json from brand-kit.md.")
    p.add_argument("project_dir")
    args = p.parse_args(argv[1:])
    try:
        project_dir = Path(args.project_dir)
        bk = _load_brand_kit(project_dir)
        tokens = build_tokens(bk)
        _write_design_md(project_dir, tokens)
        _write_tokens_json(project_dir, tokens)
        success(f"DESIGN.md + tokens.json → {project_dir / '05_ДИЗАЙН-СИСТЕМА'}")
        return 0
    except Exception as exc:
        error(f"build-tokens failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Запустить тесты, убедиться что PASS**

```bash
python3 -m pytest tests/phase-3/python/test_build_tokens.py -v
```

Ожидаемый результат: `9 passed`.

- [ ] **Step 4: Commit**

```bash
git add skills/design-tokens-generation/SKILL.md skills/design-tokens-generation/scripts/build-tokens.py
git commit -m "feat(phase-3): build-tokens.py — DESIGN.md + tokens.json from brand-kit"
```

---

## Task 3: test_render_preview.py (RED)

**Files:**
- Create: `tests/phase-3/python/test_render_preview.py`

- [ ] **Step 1: Создать failing-тесты для render-preview.py**

```python
# tests/phase-3/python/test_render_preview.py
"""Tests for design-tokens-generation/scripts/render-preview.py"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = ROOT / "skills" / "design-tokens-generation" / "scripts" / "build-tokens.py"
RENDER_SCRIPT = ROOT / "skills" / "design-tokens-generation" / "scripts" / "render-preview.py"


def _load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_creates_design_preview_html(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    result = _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    assert result == 0
    assert (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").exists()


def test_preview_has_doctype(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    html = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html


def test_preview_has_color_swatches(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    html = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").read_text(encoding="utf-8")
    assert "#ff5733" in html


def test_preview_has_font_specimens(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    html = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").read_text(encoding="utf-8")
    assert "Cabinet Grotesk" in html
    assert "Inter" in html


def test_render_graceful_with_missing_tokens_json(tmp_path):
    """render-preview.py must succeed even when tokens.json is absent."""
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    result = _load(RENDER_SCRIPT).main(["prog", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").exists()
```

- [ ] **Step 2: Запустить, убедиться что FAIL**

```bash
python3 -m pytest tests/phase-3/python/test_render_preview.py -v
```

Ожидаемый результат: `ModuleNotFoundError` — скрипт ещё не существует.

- [ ] **Step 3: Commit**

```bash
git add tests/phase-3/python/test_render_preview.py
git commit -m "test(phase-3): RED — render-preview.py test suite"
```

---

## Task 4: render-preview.py + design-preview.html.j2 (GREEN)

**Files:**
- Create: `tools/html/templates/design-preview.html.j2`
- Create: `skills/design-tokens-generation/scripts/render-preview.py`

- [ ] **Step 1: Создать Jinja2 шаблон design-preview.html.j2**

```jinja2
{# tools/html/templates/design-preview.html.j2 #}
{% extends "base.html.j2" %}

{% block title %}Design Preview{% endblock %}

{% block extra_styles %}
.swatch-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }
.swatch { width: 120px; }
.swatch-color { width: 120px; height: 80px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.08); }
.swatch-label { font-size: 0.75rem; color: #555; margin-top: 6px; }
.swatch-hex { font-family: monospace; font-weight: 600; font-size: 0.8rem; }
.font-specimen { padding: 16px; background: white; border-radius: 8px; margin-bottom: 12px; }
.font-specimen h3 { margin: 0 0 4px; font-size: 1rem; color: #888; }
.type-scale { display: grid; gap: 8px; }
.type-row { display: flex; align-items: baseline; gap: 12px; }
.type-token { font-family: monospace; font-size: 0.75rem; color: #888; min-width: 120px; }
.space-scale { display: flex; align-items: flex-end; gap: 8px; flex-wrap: wrap; }
.space-block { background: #e8f4fd; border-radius: 4px; display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 4px; }
.space-label { font-size: 0.65rem; color: #555; text-align: center; }
.motion-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.motion-card { background: white; border-radius: 8px; padding: 12px; }
.mono { font-family: monospace; font-size: 0.8rem; }
{% endblock %}

{% block heading %}Design Preview{% endblock %}

{% block meta %}
<p class="meta">Токены из <code>05_ДИЗАЙН-СИСТЕМА/tokens.json</code></p>
{% endblock %}

{% block content %}

{% set colors = tokens.get("colors", {}) %}
{% set typography = tokens.get("typography", {}) %}
{% set spacing = tokens.get("spacing", {}) %}
{% set motion = tokens.get("motion", {}) %}
{% set grid = tokens.get("grid", {}) %}
{% set radius = tokens.get("radius", {}) %}

{% if colors %}
<h2>Цвета</h2>
<div class="swatch-grid">
  {% for name, color in colors.items() %}
  <div class="swatch">
    <div class="swatch-color" style="background: {{ color.hex }};"></div>
    <div class="swatch-label">
      <div class="swatch-hex">{{ color.hex }}</div>
      <div>--color-{{ name }}</div>
      {% if color.source %}<div style="color:#aaa;font-size:0.65rem">{{ color.source }}</div>{% endif %}
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

{% if typography %}
<h2>Типографика</h2>
{% set display = typography.get("display", {}) %}
{% set body = typography.get("body", {}) %}
{% set sizes = typography.get("sizes", {}) %}

{% if display %}
<div class="font-specimen">
  <h3>Display — {{ display.family }} ({{ display.source }})</h3>
  <div style="font-family: '{{ display.family }}', sans-serif; font-weight: {{ display.weight }}; font-size: 2.5rem; line-height: 1.1;">
    Заголовок лендинга
  </div>
</div>
{% endif %}

{% if body %}
<div class="font-specimen">
  <h3>Body — {{ body.family }} ({{ body.source }})</h3>
  <div style="font-family: '{{ body.family }}', sans-serif; font-weight: {{ body.weight }}; font-size: 1rem; line-height: 1.6;">
    Основной текст лендинга. Описание продукта, преимуществ и отзывов клиентов.
  </div>
</div>
{% endif %}

{% if sizes %}
<div class="card">
  <h3 style="margin-top:0">Масштаб размеров</h3>
  <div class="type-scale">
    {% for name, val in sizes.items() %}
    <div class="type-row">
      <span class="type-token">--size-{{ name }}</span>
      <span style="font-size: {{ val }}; line-height: 1.2; font-family: '{{ display.family if display else 'sans-serif' }}', sans-serif; white-space: nowrap;">{{ val }}</span>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}
{% endif %}

{% if spacing %}
<h2>Отступы</h2>
<div class="card">
  <div class="space-scale">
    {% for name, val in spacing.items() %}
    <div class="space-block" style="width: {{ val }}; height: {{ val }}; min-width: 16px; min-height: 16px;">
      <span class="space-label">{{ name }}<br>{{ val }}</span>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}

{% if grid %}
<h2>Сетка</h2>
<div class="card">
  <p class="mono">Колонки: {{ grid.columns }} | Gap: {{ grid.gap }} | Max-width: {{ grid.max_width }}</p>
</div>
{% endif %}

{% if motion %}
<h2>Motion</h2>
<div class="motion-grid">
  {% for name, val in motion.items() %}
  <div class="motion-card">
    <div style="color:#888;font-size:0.75rem">--{{ name.replace("_", "-") }}</div>
    <div class="mono" style="font-weight:600">{{ val }}</div>
  </div>
  {% endfor %}
</div>
{% endif %}

{% endblock %}
```

- [ ] **Step 2: Создать render-preview.py**

```python
#!/usr/bin/env python3
"""Render design-preview.html from 05_ДИЗАЙН-СИСТЕМА/tokens.json.

CLI: python3 render-preview.py <project-dir>
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.html.render import render
from tools.logger import success, warn, error


def load_tokens(project_dir: Path) -> dict:
    tokens_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    if not tokens_path.exists():
        warn(f"tokens.json not found: {tokens_path} — using empty tokens")
        return {}
    return json.loads(tokens_path.read_text(encoding="utf-8"))


def main(argv: list) -> int:
    p = argparse.ArgumentParser(description="Render design-preview.html from tokens.json.")
    p.add_argument("project_dir")
    args = p.parse_args(argv[1:])
    try:
        project_dir = Path(args.project_dir)
        tokens = load_tokens(project_dir)
        out_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        html = render("design-preview.html.j2", {"tokens": tokens})
        out_path.write_text(html, encoding="utf-8")
        success(f"Wrote {out_path}")
        return 0
    except Exception as exc:
        error(f"render-preview failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Запустить тесты, убедиться что PASS**

```bash
python3 -m pytest tests/phase-3/python/test_render_preview.py -v
```

Ожидаемый результат: `5 passed`.

- [ ] **Step 4: Commit**

```bash
git add tools/html/templates/design-preview.html.j2 skills/design-tokens-generation/scripts/render-preview.py
git commit -m "feat(phase-3): render-preview.py + design-preview.html.j2"
```

---

## Task 5: Агент design-system-generator

**Files:**
- Create: `agents/design-system-generator.md`

- [ ] **Step 1: Создать файл агента**

```markdown
---
name: design-system-generator
description: Use during stage 05 after brand-architect has run. Reads 04_БРЕНД/brand-kit.md and produces DESIGN.md + tokens.json + design-preview.html for the landing project. Owned by design-tokens-generation skill.
allowed-tools: Bash, Read, Write
---

# design-system-generator (Генератор дизайн-системы)

## Mission

Из `04_БРЕНД/brand-kit.md` строю полную дизайн-систему с провенансом (traceability).

## What I do

1. Читаю `04_БРЕНД/brand-kit.md` — извлекаю цвета, шрифты, иконки, motion, grid.
2. Запускаю `skills/design-tokens-generation/scripts/build-tokens.py <project-dir>`.
3. Проверяю что `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json` созданы.
4. Запускаю `skills/design-tokens-generation/scripts/render-preview.py <project-dir>`.
5. Показываю пользователю путь к `05_ДИЗАЙН-СИСТЕМА/design-preview.html`.
6. **HARD GATE**: жду явного утверждения (`утверждаю`, `ok`, `дальше`) перед переходом к этапу 06.

## Outputs

- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины токенов с YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живые компоненты по токенам

## Token structure

Tokens include: colors (primary/secondary/accent/text/bg с provenance), typography (display/body/sizes), spacing (xs→3xl), grid (columns/gap/max_width), radius (sm/md/lg/full), shadow (sm/md/lg), breakpoints (mobile/tablet/desktop), motion (duration_fast/base/slow, easing).
```

- [ ] **Step 2: Commit**

```bash
git add agents/design-system-generator.md
git commit -m "feat(phase-3): design-system-generator agent"
```

---

## Task 6: Агент scene-director

**Files:**
- Create: `agents/scene-director.md`

- [ ] **Step 1: Создать файл агента**

```markdown
---
name: scene-director
description: Use during stage 05 (cinematic mode only) after design-system-generator. Produces scenes.md with 8-scene grammar and GSAP motion plan for the landing project.
allowed-tools: Bash, Read, Write
---

# scene-director (Режиссёр сцен — Cinematic Premium)

## Mission

Проектирую кинематографическую архитектуру из 6–8 сцен на основе бренд-кита и брифа.

## When activated

Только при флаге `--cinematic` при создании проекта или явном вызове пользователя.

## What I do

1. Читаю `00_БРИФ/brief.md` (ниша, ЦА, тон) и `04_БРЕНД/brand-kit.md` (цвета, motion).
2. Читаю `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` для motion-токенов.
3. Генерирую `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar для каждой сцены:
   - Название и тип сцены
   - Описание визуала и глубины
   - GSAP / ScrollTrigger / Lenis инструкции
   - Parallax-логика
   - Mobile fallback (упрощённая версия)
4. Соблюдаю Motion Rules: ❌ scroll hijack, ❌ particle systems, ❌ fade-up на каждом блоке.

## Scene Grammar (8 типовых сцен)

1. **Hero Film Frame** — full-height split, layered planes, slow parallax
2. **Chaos to Clarity** — text blocks слоями, фоновые орбиты с разной скоростью
3. **What You Get** — карточки с controlled stagger
4. **The Diagnostic Process** — quasi-timeline с parallax
5. **About the Expert** — portrait scene, premium light-depth
6. **Proof / Trust** — цифры, кейсы, restrained motion
7. **FAQ** — лёгкая сцена, clear interactions
8. **Final Call** — кульминация, contrast shift

## Output

- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar, motion-план
```

- [ ] **Step 2: Commit**

```bash
git add agents/scene-director.md
git commit -m "feat(phase-3): scene-director agent (cinematic)"
```

---

## Task 7: Агент stack-planner

**Files:**
- Create: `agents/stack-planner.md`

- [ ] **Step 1: Создать файл агента**

```markdown
---
name: stack-planner
description: Use during stage 06 after design-system-generator. Selects WordPress plugins, JS libraries, icon set, and font CDN. Writes design-stack.yaml and supporting docs.
allowed-tools: Bash, Read, Write
---

# stack-planner (Планировщик стека)

## Mission

Фиксирую выбор плагинов, библиотек, иконок и шрифтов на основе `DESIGN.md` и режима (обычный / cinematic).

## What I do

1. Читаю `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` и `tokens.json`.
2. Читаю `04_БРЕНД/brand-kit.md` — library из icons, font families.
3. Определяю режим из `00_БРИФ/brief.md` (есть ли флаг cinematic).
4. Пишу `06_СТЕК/design-stack.yaml`:

```yaml
mode: standard  # или cinematic
wordpress:
  theme: generatepress
  plugins:
    - advanced-custom-fields
    - generateblocks
    - fluentform
fonts:
  cdn: bunny  # или google
  families:
    - name: "Cabinet Grotesk"
      weights: [400, 700]
    - name: "Inter"
      weights: [400]
icons:
  library: lucide
  delivery: iconify-api  # https://api.iconify.design/{id}.svg
js_libraries: []  # cinematic: [gsap, scrolltrigger, lenis, split-type]
```

5. Пишу `06_СТЕК/component-library-plan.md` — откуда берётся каждый компонент.
6. Пишу `06_СТЕК/effects-plan.md` — анимации и motion (пусто в standard-режиме).
7. Пишет `06_СТЕК/font-and-color-plan.md` — маппинг шрифтов и цветов к токенам.
8. **HARD GATE**: показываю пользователю design-stack.yaml, жду утверждения.

## Rules

- ❌ Никаких ad-hoc пакетов вне design-stack.yaml
- ❌ Tailwind, Elementor, shadcn, Radix — запрещено
- ✅ GenerateBlocks (free) для контейнеров и сеток
- ✅ Bunny Fonts CDN (GDPR/РФ-friendly)
- ✅ Iconify API (без ключа)

## Output

- `06_СТЕК/design-stack.yaml`
- `06_СТЕК/component-library-plan.md`
- `06_СТЕК/effects-plan.md`
- `06_СТЕК/font-and-color-plan.md`
```

- [ ] **Step 2: Commit**

```bash
git add agents/stack-planner.md
git commit -m "feat(phase-3): stack-planner agent"
```

---

## Task 8: Агент content-writer

**Files:**
- Create: `agents/content-writer.md`

- [ ] **Step 1: Создать файл агента**

```markdown
---
name: content-writer
description: Use during stage 07. Adapts the landing prototype text to specific Gutenberg blocks defined in DESIGN.md. Produces final-copy.md and seo-copy.md.
allowed-tools: Bash, Read, Write
---

# content-writer (Контент-райтер)

## Mission

Адаптирую прототип текста под конкретные блоки лендинга.

## What I do

1. Читаю `07_КОНТЕНТ/prototype.md` — исходный прототип текста.
2. Читаю `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — список секций/блоков.
3. Читаю `06_СТЕК/design-stack.yaml` — компонентная библиотека.
4. Читаю `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` и `assets-manifest.yaml` — реальные отзывы и ассеты.
5. Раскладываю текст по блокам в `07_КОНТЕНТ/final-copy.md`:

```markdown
# Final Copy — [PROJECT_NAME]

## HERO
**Заголовок:** [текст ≤ 80 символов]
**Подзаголовок:** [текст ≤ 160 символов]
**CTA:** [текст кнопки ≤ 30 символов]
**Фото:** [ID из assets-manifest.yaml]

## BENEFITS
**Заголовок секции:** [текст]
### Блок 1
- Иконка: lucide:check
- Заголовок: [текст]
- Описание: [≤ 120 символов]
...

## PROOF / TESTIMONIALS
[Список реальных отзывов из 02_МАТЕРИАЛЫ_КЛИЕНТА/]

## FAQ
[5–7 реальных вопросов ЦА]

## CTA-FOOTER
**Заголовок:** [текст]
**CTA:** [текст кнопки]
```

6. Пишет `07_КОНТЕНТ/seo-copy.md`:

```markdown
# SEO Copy

## Title: [ключевое слово — выгода | бренд] (≤ 60 символов)
## Description: [ключевое слово + CTA + выгода] (≤ 155 символов)
## H1: [точное вхождение ключевого слова]
## Alt-теги для ключевых изображений
```

7. **HARD GATE**: показываю пользователю final-copy.md, жду утверждения.

## Rules

- ❌ Lorem ipsum в final-copy.md
- ✅ Только реальные данные из prototype.md и testimonials/
- ✅ Каждый блок с явным указанием иконки/фото из assets-manifest

## Output

- `07_КОНТЕНТ/final-copy.md`
- `07_КОНТЕНТ/seo-copy.md`
```

- [ ] **Step 2: Commit**

```bash
git add agents/content-writer.md
git commit -m "feat(phase-3): content-writer agent"
```

---

## Task 9: Slash-команда /landing-design

**Files:**
- Create: `.claude/commands/landing-design.md`

- [ ] **Step 1: Создать команду**

```markdown
---
description: Generate or regenerate the design system for a landing project (stage 05). Run within a landing project folder after brand-kit is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-design

Run within a landing project after `brand-architect` has produced `04_БРЕНД/brand-kit.md`.

## What I do

1. Invoke `design-system-generator` agent.
2. Run `skills/design-tokens-generation/scripts/build-tokens.py` → `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` + `tokens.json`.
3. Run `skills/design-tokens-generation/scripts/render-preview.py` → `05_ДИЗАЙН-СИСТЕМА/design-preview.html`.
4. If `--cinematic` flag present: also invoke `scene-director` agent → `scenes.md`.
5. **HARD GATE**: show preview path, wait for user approval before proceeding to stage 06.

## Usage

Run: `/landing-design`

Requires `04_БРЕНД/brand-kit.md` produced by `brand-architect` (run after `/landing-brand` is approved).

## Options

- `--cinematic` — also generate `scenes.md` via `scene-director` agent

## Output

- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — token source of truth with YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — machine-readable tokens
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — live components preview
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — cinematic scene grammar (if --cinematic)
```

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/landing-design.md
git commit -m "feat(phase-3): /landing-design slash command"
```

---

## Task 10: Slash-команда /landing-stack

**Files:**
- Create: `.claude/commands/landing-stack.md`

- [ ] **Step 1: Создать команду**

```markdown
---
description: Plan the WordPress plugin and library stack for a landing project (stage 06). Run within a landing project folder after design system is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-stack

Run within a landing project after `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` is approved.

## What I do

1. Invoke `stack-planner` agent.
2. Produce `06_СТЕК/design-stack.yaml` — list of WordPress plugins, JS libs, icon library, font CDN.
3. Produce supporting docs: `component-library-plan.md`, `effects-plan.md`, `font-and-color-plan.md`.
4. **HARD GATE**: show `design-stack.yaml`, wait for user approval before proceeding to stage 07.

## Usage

Run: `/landing-stack`

Requires `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` produced by `design-system-generator` (run after `/landing-design` is approved).

## Output

- `06_СТЕК/design-stack.yaml` — plugin and library registry
- `06_СТЕК/component-library-plan.md`
- `06_СТЕК/effects-plan.md`
- `06_СТЕК/font-and-color-plan.md`
```

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/landing-stack.md
git commit -m "feat(phase-3): /landing-stack slash command"
```

---

## Task 11: Slash-команда /landing-content

**Files:**
- Create: `.claude/commands/landing-content.md`

- [ ] **Step 1: Создать команду**

```markdown
---
description: Adapt the landing prototype text to Gutenberg blocks (stage 07). Run within a landing project folder after stack is approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-content

Run within a landing project after `06_СТЕК/design-stack.yaml` is approved.

## What I do

1. Invoke `content-writer` agent.
2. Read `07_КОНТЕНТ/prototype.md` and block structure from `DESIGN.md`.
3. Read real testimonials from `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/`.
4. Produce `07_КОНТЕНТ/final-copy.md` — text laid out per Gutenberg block.
5. Produce `07_КОНТЕНТ/seo-copy.md` — SEO titles, descriptions, h1 variants.
6. **HARD GATE**: show `final-copy.md`, wait for user approval before proceeding to stage 08.

## Usage

Run: `/landing-content`

Requires:
- `07_КОНТЕНТ/prototype.md` — source prototype text
- `06_СТЕК/design-stack.yaml` — block definitions (run after `/landing-stack`)

## Output

- `07_КОНТЕНТ/final-copy.md` — final copy per block
- `07_КОНТЕНТ/seo-copy.md` — SEO copy variants
```

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/landing-content.md
git commit -m "feat(phase-3): /landing-content slash command"
```

---

## Task 12: Bats-тесты — агенты и команды Phase 3

**Files:**
- Create: `tests/phase-3/test-agents-phase3.bats`
- Create: `tests/phase-3/test-commands-phase3.bats`

- [ ] **Step 1: Создать test-agents-phase3.bats**

```bash
#!/usr/bin/env bats
# tests/phase-3/test-agents-phase3.bats

load '../helpers/test_helpers'

AGENTS_DIR="$ROOT/agents"

@test "design-system-generator agent file exists" {
  [ -f "$AGENTS_DIR/design-system-generator.md" ]
}

@test "design-system-generator has valid frontmatter" {
  grep -q "^name: design-system-generator" "$AGENTS_DIR/design-system-generator.md"
}

@test "design-system-generator mentions design-preview.html" {
  grep -q "design-preview.html" "$AGENTS_DIR/design-system-generator.md"
}

@test "design-system-generator mentions DESIGN.md" {
  grep -q "DESIGN.md" "$AGENTS_DIR/design-system-generator.md"
}

@test "scene-director agent file exists" {
  [ -f "$AGENTS_DIR/scene-director.md" ]
}

@test "scene-director has valid frontmatter" {
  grep -q "^name: scene-director" "$AGENTS_DIR/scene-director.md"
}

@test "scene-director mentions cinematic" {
  grep -qi "cinematic" "$AGENTS_DIR/scene-director.md"
}

@test "stack-planner agent file exists" {
  [ -f "$AGENTS_DIR/stack-planner.md" ]
}

@test "stack-planner has valid frontmatter" {
  grep -q "^name: stack-planner" "$AGENTS_DIR/stack-planner.md"
}

@test "stack-planner mentions design-stack.yaml" {
  grep -q "design-stack.yaml" "$AGENTS_DIR/stack-planner.md"
}

@test "content-writer agent file exists" {
  [ -f "$AGENTS_DIR/content-writer.md" ]
}

@test "content-writer has valid frontmatter" {
  grep -q "^name: content-writer" "$AGENTS_DIR/content-writer.md"
}

@test "content-writer mentions final-copy.md" {
  grep -q "final-copy.md" "$AGENTS_DIR/content-writer.md"
}
```

- [ ] **Step 2: Создать test-commands-phase3.bats**

```bash
#!/usr/bin/env bats
# tests/phase-3/test-commands-phase3.bats

load '../helpers/test_helpers'

COMMANDS_DIR="$ROOT/.claude/commands"

@test "landing-design command file exists" {
  [ -f "$COMMANDS_DIR/landing-design.md" ]
}

@test "landing-design has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-design mentions design-system-generator" {
  grep -q "design-system-generator" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-design mentions design-preview.html" {
  grep -q "design-preview.html" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-design has Usage section" {
  grep -q "## Usage" "$COMMANDS_DIR/landing-design.md"
}

@test "landing-stack command file exists" {
  [ -f "$COMMANDS_DIR/landing-stack.md" ]
}

@test "landing-stack has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-stack.md"
}

@test "landing-stack mentions stack-planner" {
  grep -q "stack-planner" "$COMMANDS_DIR/landing-stack.md"
}

@test "landing-stack mentions design-stack.yaml" {
  grep -q "design-stack.yaml" "$COMMANDS_DIR/landing-stack.md"
}

@test "landing-content command file exists" {
  [ -f "$COMMANDS_DIR/landing-content.md" ]
}

@test "landing-content has description frontmatter" {
  grep -q "^description:" "$COMMANDS_DIR/landing-content.md"
}

@test "landing-content mentions content-writer" {
  grep -q "content-writer" "$COMMANDS_DIR/landing-content.md"
}

@test "landing-content mentions final-copy.md" {
  grep -q "final-copy.md" "$COMMANDS_DIR/landing-content.md"
}
```

- [ ] **Step 3: Запустить bats-тесты**

```bash
bats tests/phase-3/test-agents-phase3.bats tests/phase-3/test-commands-phase3.bats
```

Ожидаемый результат: `26 tests, 0 failed`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-3/test-agents-phase3.bats tests/phase-3/test-commands-phase3.bats
git commit -m "test(phase-3): bats tests for Phase 3 agents and commands"
```

---

## Task 13: Интеграционный bats-тест

**Files:**
- Create: `tests/phase-3/integration/test-phase3-pipeline.bats`

- [ ] **Step 1: Создать интеграционный тест**

```bash
#!/usr/bin/env bats
# tests/phase-3/integration/test-phase3-pipeline.bats

load '../../helpers/test_helpers'

BUILD_SCRIPT="$ROOT/skills/design-tokens-generation/scripts/build-tokens.py"
RENDER_SCRIPT="$ROOT/skills/design-tokens-generation/scripts/render-preview.py"

setup() {
  PROJECT_DIR="$(mktemp -d)"
  mkdir -p "$PROJECT_DIR/04_БРЕНД" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА"

  python3 -c "
import yaml, pathlib
brand_kit = {
    'brand_kit': {
        'meta': {'project': 'test', 'created': '2026-05-04', 'references_used': 1},
        'colors': {
            'primary': {'hex': '#ff5733', 'role': 'primary', 'source': 'ref1.png'},
            'secondary': {'hex': '#33c1ff', 'role': 'secondary', 'source': 'ref1.png'},
            'accent': {'hex': '#2ecc71', 'role': 'accent', 'source': 'ref1.png'},
        },
        'typography': {
            'display': {'family': 'Cabinet Grotesk', 'confidence': 0.9, 'source': 'DOM'},
            'body': {'family': 'Inter', 'confidence': 0.9, 'source': 'DOM'},
        },
        'icons': {'library': 'lucide', 'selected': [{'id': 'lucide:check', 'name': 'check'}]},
        'motion': {'notes': 'Subtle transitions, 200-400ms'},
        'grid': {'notes': '12-column grid, 24px gap'},
    }
}
yaml_block = yaml.dump(brand_kit, allow_unicode=True, default_flow_style=False)
content = f'---\n{yaml_block}---\n\n# Brand Kit\n'
pathlib.Path('$PROJECT_DIR/04_БРЕНД/brand-kit.md').write_text(content, encoding='utf-8')
"
}

teardown() {
  rm -rf "$PROJECT_DIR"
}

@test "phase3 integration: build-tokens.py produces DESIGN.md" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  [ -f "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md" ]
}

@test "phase3 integration: DESIGN.md has YAML frontmatter" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  grep -q "^---" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
  grep -q "tokens:" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
}

@test "phase3 integration: tokens.json is valid JSON" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 -c "import json; json.load(open('$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/tokens.json', encoding='utf-8'))"
}

@test "phase3 integration: render-preview.py produces design-preview.html" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 "$RENDER_SCRIPT" "$PROJECT_DIR"
  [ -f "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/design-preview.html" ]
}

@test "phase3 integration: design-preview.html contains color swatch" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 "$RENDER_SCRIPT" "$PROJECT_DIR"
  grep -q "#ff5733" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/design-preview.html"
}

@test "phase3 integration: design-preview.html contains font specimen" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 "$RENDER_SCRIPT" "$PROJECT_DIR"
  grep -q "Cabinet Grotesk" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/design-preview.html"
}
```

- [ ] **Step 2: Запустить интеграционный тест**

```bash
bats tests/phase-3/integration/test-phase3-pipeline.bats
```

Ожидаемый результат: `6 tests, 0 failed`.

- [ ] **Step 3: Commit**

```bash
git add tests/phase-3/integration/test-phase3-pipeline.bats
git commit -m "test(phase-3): integration pipeline bats test"
```

---

## Task 14: Расширение оркестратора + финальный commit + тег

**Files:**
- Modify: `agents/landing-orchestrator.md`
- Modify: `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`

- [ ] **Step 1: Добавить Phase 3 Scope в landing-orchestrator.md**

В файле `agents/landing-orchestrator.md` добавить секцию Phase 3 Scope после Phase 2 Scope:

```markdown
## Phase 3 Scope (расширение)

В Phase 3 я умею дирижировать этапами 05 → 06 → 07. Для каждого этапа:

1. Диспатчу нужного специализированного агента:
   - Этап 05: `design-system-generator` (токены), `scene-director` (cinematic)
   - Этап 06: `stack-planner` (стек плагинов)
   - Этап 07: `content-writer` (контент по блокам)
2. Жду HTML-preview (`design-preview.html`) или текстового артефакта.
3. Показываю пользователю путь; **HARD GATE — жду явного утверждения**.
4. Этапы 08–12 ожидают Phase 4+.

### Stage 05 flow
```bash
design-system-generator   # → 05_ДИЗАЙН-СИСТЕМА/DESIGN.md + tokens.json + design-preview.html
scene-director            # → 05_ДИЗАЙН-СИСТЕМА/scenes.md (только --cinematic)
```

### Stage 06 flow
```bash
stack-planner             # → 06_СТЕК/design-stack.yaml + supporting docs
```

### Stage 07 flow
```bash
content-writer            # → 07_КОНТЕНТ/final-copy.md + seo-copy.md
```
```

- [ ] **Step 2: Обновить master-plan — отметить Phase 3 Complete**

В `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` изменить строку Phase 3:

```markdown
| 3 | **Design Pipeline** (05–07) | [phase-3-design-pipeline.md](2026-05-04-phase-3-design-pipeline.md) | ~20 tasks | 5–6 ч | 🟢 Complete (2026-05-04) |
```

- [ ] **Step 3: Запустить весь Phase 3 тест-сьют**

```bash
python3 -m pytest tests/phase-3/python/ -v
bats tests/phase-3/ --recursive
```

Ожидаемый результат: все тесты зелёные.

- [ ] **Step 4: Финальный commit и тег**

```bash
git add agents/landing-orchestrator.md docs/superpowers/plans/2026-05-03-landing-system-master-plan.md
git commit -m "feat(phase-3): extend orchestrator Phase 3 scope + mark complete"
git tag phase-3-complete
```

---

## Self-Review

**1. Spec coverage:**
- ✅ `design-system-generator` — Task 5
- ✅ `scene-director` — Task 6
- ✅ `stack-planner` — Task 7
- ✅ `content-writer` — Task 8
- ✅ `DESIGN.md` + `tokens.json` — Task 2 (build-tokens.py)
- ✅ `design-preview.html` — Task 4 (render-preview.py + Jinja2)
- ✅ `scenes.md` — описано в scene-director agent
- ✅ `/landing-design` — Task 9
- ✅ `/landing-stack` — Task 10
- ✅ `/landing-content` — Task 11
- ✅ Оркестратор Phase 3 — Task 14
- ✅ Все токены из spec: colors/typography/spacing/grid/radius/shadow/breakpoints/motion

**2. Placeholder scan:** Нет TBD, TODO, «add validation» без кода.

**3. Type consistency:**
- `build_tokens(bk: dict) -> dict` — возвращает тот же dict, что читает `render-preview.py`
- `tokens["colors"]["primary"]["hex"]` — используется одинаково в тестах и шаблоне
- `render("design-preview.html.j2", {"tokens": tokens})` — совпадает с `{% set colors = tokens.get("colors", {}) %}` в шаблоне
