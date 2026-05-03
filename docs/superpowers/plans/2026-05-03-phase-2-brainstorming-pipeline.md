# Phase 2 — Brainstorming Pipeline (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Steps use `- [ ]` checkboxes.

**Goal:** Реализовать первые 5 этапов workflow одного лендинга (00 Бриф → 01 Контекст → 02 Материалы → 03 Референсы → 04 Бренд) через 6 специализированных агентов и набор Python/Bash инструментов. На выходе агент строит `brand-kit.md` с полной трассировкой источников + HTML preview-артефакты на каждом этапе.

**Architecture:** Smart agents + thin Python tools. Каждый агент = markdown spec в `.agents/`. Реальная работа делегируется Python-скриптам в `.skills/<skill>/scripts/`. HTML preview генерируется через единый Jinja2-template движок. Все внешние API вызовы (Firecrawl, WhatTheFont, Iconify) изолированы в адаптерах для удобного mocking в тестах.

**Tech Stack:**
- Python 3.10+ (image-pipeline, color/font/icon extraction)
- Pillow + colorthief (палитра)
- Iconify HTTP API (иконки, без ключа)
- WhatTheFont API + Claude vision fallback (шрифты)
- Firecrawl API (парсинг отзывов)
- rembg или Pillow (фото-cutout)
- Jinja2 (HTML preview templates)
- pytest для Python, bats для shell glue
- requests + responses (HTTP-моки)

**Spec source:** [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](../specs/2026-05-03-landing-system-design.md) (разделы 4 этапы 00–04, 5 этапы 00–04, 6 агенты 1–7, 7.2 MCP, 8.4 Iconify/Fontshare)

**Master plan:** [`2026-05-03-landing-system-master-plan.md`](2026-05-03-landing-system-master-plan.md)

---

## Scope check

Phase 2 содержит **6 связанных подсистем** (по одному агенту на каждую). Они тесно связаны (выход одной — вход следующей), поэтому реализуются в одной фазе с общими Python-helper'ами. Нет смысла разносить на под-фазы — каждый агент сам по себе тонкий, а главная сложность в инфраструктуре (Python deps, HTML templates, API адаптеры).

---

## File Structure

### Новые файлы

```
landing-system/
├─ .agents/
│  ├─ landing-orchestrator.md           # MODIFY — расширяем для этапов 00-04
│  ├─ client-assets-collector.md        # NEW
│  ├─ photo-stylist.md                  # NEW
│  ├─ references-curator.md             # NEW
│  ├─ moodboard-composer.md             # NEW
│  ├─ style-extractor.md                # NEW
│  └─ brand-architect.md                # NEW
│
├─ .claude/commands/
│  ├─ landing-references.md             # NEW
│  ├─ landing-moodboard.md              # NEW
│  └─ landing-brand.md                  # NEW
│
├─ .skills/
│  ├─ client-assets-collection/         # NEW
│  │  ├─ SKILL.md
│  │  └─ scripts/
│  │     ├─ collect.py                  # фото/видео gallery generator
│  │     └─ parse-reviews.py            # Firecrawl-based review parser
│  ├─ photo-styling/                    # NEW
│  │  ├─ SKILL.md
│  │  └─ scripts/
│  │     └─ style.py                    # cutout + edge cleanup (Pillow/rembg)
│  ├─ references-collection/            # NEW
│  │  ├─ SKILL.md
│  │  └─ scripts/
│  │     └─ index.py                    # update index.yaml with statuses
│  ├─ moodboard-creation/               # NEW
│  │  ├─ SKILL.md
│  │  └─ scripts/
│  │     └─ render.py                   # build moodboard.html via Jinja2
│  ├─ style-decomposition/              # NEW
│  │  ├─ SKILL.md
│  │  └─ scripts/
│  │     ├─ extract-palette.py          # color-thief + KMeans
│  │     ├─ identify-fonts.py           # WhatTheFont + fallback
│  │     ├─ match-icons.py              # Iconify search
│  │     └─ download-fonts.py           # Google/Bunny/Fontshare downloader
│  └─ brand-kit-build/                  # NEW
│     ├─ SKILL.md
│     └─ scripts/
│        ├─ build.py                    # synthesize brand-kit.md from extracted/
│        └─ render-html.py              # brand-kit.html via Jinja2
│
├─ tools/                               # NEW — общая Python инфраструктура
│  ├─ __init__.py
│  ├─ adapters/
│  │  ├─ __init__.py
│  │  ├─ firecrawl.py                   # HTTP wrapper for Firecrawl API
│  │  ├─ whatthefont.py                 # HTTP wrapper for WhatTheFont
│  │  ├─ iconify.py                     # HTTP wrapper for Iconify (free)
│  │  └─ font_downloader.py             # Google/Bunny/Fontshare CDN
│  ├─ html/
│  │  ├─ __init__.py
│  │  ├─ render.py                      # Jinja2 setup + base helpers
│  │  └─ templates/
│  │     ├─ base.html.j2
│  │     ├─ assets-gallery.html.j2
│  │     ├─ moodboard.html.j2
│  │     ├─ brand-kit.html.j2
│  │     └─ partials/
│  │        ├─ palette.html.j2
│  │        ├─ font-card.html.j2
│  │        └─ ref-card.html.j2
│  ├─ env.py                            # .env.local + project .env loader
│  └─ logger.py                         # consistent stderr logging
│
├─ requirements.txt                     # NEW — Python deps
│
└─ tests/
   └─ phase-2/                          # NEW
      ├─ __init__.py
      ├─ conftest.py                    # pytest fixtures (mock HTTP, temp dirs)
      ├─ test-deps.bats
      ├─ test-agents-frontmatter.bats   # 6 new agents have valid frontmatter
      ├─ test-commands-phase2.bats      # 3 new slash commands valid
      ├─ test-skills-phase2.bats        # 6 new skills valid
      ├─ python/
      │  ├─ test_adapters_firecrawl.py
      │  ├─ test_adapters_whatthefont.py
      │  ├─ test_adapters_iconify.py
      │  ├─ test_adapters_font_downloader.py
      │  ├─ test_extract_palette.py
      │  ├─ test_identify_fonts.py
      │  ├─ test_match_icons.py
      │  ├─ test_collect_assets.py
      │  ├─ test_parse_reviews.py
      │  ├─ test_photo_styling.py
      │  ├─ test_references_index.py
      │  ├─ test_moodboard_render.py
      │  ├─ test_brand_kit_build.py
      │  └─ test_html_render.py
      └─ integration/
         └─ test-phase2-pipeline.bats    # end-to-end через все 5 этапов на mock data
```

### Файлы, которые меняются

- `package.json` — добавить script `test:phase-2` и `test:python`
- `.env.local.example` — уже содержит все нужные ключи (Phase 1)
- `.claude/settings.json` — расширить permissions.allow для Python
- `template/00_БРИФ/brief.template.md` — NEW шаблон брифа
- `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` — пометить Phase 2 ✅ в финале

---

## Prerequisites

Перед стартом Phase 2 на машине должны быть:

```bash
python3 --version    # >= 3.10
pip3 --version       # any recent
```

Python deps устанавливаются в Task 0:

```
# requirements.txt
requests>=2.31
Pillow>=10
colorthief>=0.2.1
PyYAML>=6
Jinja2>=3.1
rembg>=2.0          # optional, photo cutout
pytest>=7
responses>=0.24     # HTTP mocking
```

API-ключи (из `.env.local`):
- `FIRECRAWL_API_KEY` — обязателен для парсинга отзывов
- `WHATTHEFONT_API_KEY` — опционально, fallback на Claude vision
- Iconify, Google Fonts, Bunny Fonts — без ключей

---

## Task Breakdown

30 tasks по 6 блокам.

| Block | Tasks | What |
|---|---|---|
| **A. Python Infrastructure** | 0–5 | requirements, pytest setup, env loader, HTTP adapters, Jinja2 base |
| **B. Stage 02 — Client Assets** | 6–10 | client-assets-collector + photo-stylist + parse-reviews + assets-gallery.html |
| **C. Stage 03 — References & Moodboard** | 11–15 | references-curator + moodboard-composer + HTML preview |
| **D. Stage 03→04 — Style Extraction** | 16–22 | style-extractor + palette/font/icon tools |
| **E. Stage 04 — Brand Architect** | 23–26 | brand-architect agent + brand-kit.md/html builder with provenance |
| **F. Orchestrator + Slash Commands + Integration** | 27–30 | orchestrator extension, /landing-references, /landing-moodboard, /landing-brand, e2e test |

---

## Block A — Python Infrastructure

### Task 0: Python deps + pytest setup

**Files:**
- Create: `requirements.txt`
- Create: `tests/phase-2/__init__.py` (empty)
- Create: `tests/phase-2/conftest.py`
- Create: `tests/phase-2/test-deps.bats`
- Modify: `package.json` (add `test:python` and `test:phase-2` scripts)

- [ ] **Step 0.1: Создать `requirements.txt`**

```
requests>=2.31
Pillow>=10
colorthief>=0.2.1
PyYAML>=6
Jinja2>=3.1
rembg>=2.0
pytest>=7
responses>=0.24
```

- [ ] **Step 0.2: Установить deps**

```bash
pip3 install -r requirements.txt
```

- [ ] **Step 0.3: Создать `tests/phase-2/conftest.py`**

```python
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
def mock_firecrawl(monkeypatch):
    """Mock FIRECRAWL_API_KEY env var."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")


@pytest.fixture
def mock_whatthefont(monkeypatch):
    monkeypatch.setenv("WHATTHEFONT_API_KEY", "wtf-test-key")


@pytest.fixture
def http_mock():
    """Wrap responses.RequestsMock for declarative HTTP mocking."""
    with resp_lib.RequestsMock() as rsps:
        yield rsps
```

- [ ] **Step 0.4: Создать `tests/phase-2/test-deps.bats`**

```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "python3 installed and >= 3.10" {
  run python3 --version
  [ "$status" -eq 0 ]
  major=$(echo "$output" | sed -E 's/Python ([0-9]+).([0-9]+).*/\1/')
  minor=$(echo "$output" | sed -E 's/Python ([0-9]+).([0-9]+).*/\2/')
  [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]
}

@test "requirements.txt exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/requirements.txt"
}

@test "requirements.txt lists core deps" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "Pillow"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "colorthief"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "Jinja2"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "pytest"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "responses"
}

@test "pytest can discover phase-2 tests folder" {
  cd "$LANDING_SYSTEM_ROOT"
  run python3 -m pytest tests/phase-2/python --collect-only -q 2>&1
  # Either collects something OR returns "no tests collected" (acceptable on first run)
  [ "$status" -eq 0 ] || [ "$status" -eq 5 ]
}
```

- [ ] **Step 0.5: Modify `package.json`** — add scripts:

```json
"test:python": "python3 -m pytest tests/phase-2/python -q",
"test:phase-2": "bats tests/phase-2/*.bats && python3 -m pytest tests/phase-2/python -q"
```

- [ ] **Step 0.6: Run** `npm test` — Phase 1 still 91/91 + new bats deps tests pass.

- [ ] **Step 0.7: Commit**

```bash
git add requirements.txt tests/phase-2/__init__.py tests/phase-2/conftest.py tests/phase-2/test-deps.bats package.json
git commit -m "feat(phase-2): scaffold Python infrastructure (requirements, pytest fixtures, deps test)"
```

---

### Task 1: `tools/env.py` — env loader

**Files:**
- Create: `tools/__init__.py` (empty)
- Create: `tools/env.py`
- Create: `tests/phase-2/python/test_env.py`

- [ ] **Step 1.1: Создать тест `tests/phase-2/python/test_env.py`**

```python
"""Tests for tools.env."""
import os
from pathlib import Path
import pytest
from tools.env import load_env, get_required, get_optional


def test_load_env_reads_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n# comment\n")
    monkeypatch.delenv("FOO", raising=False)
    load_env(str(env_file))
    assert os.environ["FOO"] == "bar"
    assert os.environ["BAZ"] == "qux"


def test_load_env_skips_comments_and_empty(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# header\n\nFOO=bar\n")
    load_env(str(env_file))
    assert os.environ["FOO"] == "bar"


def test_get_required_raises_when_missing(monkeypatch):
    monkeypatch.delenv("MISSING_KEY", raising=False)
    with pytest.raises(KeyError) as exc:
        get_required("MISSING_KEY")
    assert "MISSING_KEY" in str(exc.value)


def test_get_required_returns_value(monkeypatch):
    monkeypatch.setenv("PRESENT_KEY", "value")
    assert get_required("PRESENT_KEY") == "value"


def test_get_optional_returns_default(monkeypatch):
    monkeypatch.delenv("OPT_KEY", raising=False)
    assert get_optional("OPT_KEY", "default") == "default"
```

- [ ] **Step 1.2: Run test, expect FAIL** (`tools.env` not yet)

```bash
cd landing-system && python3 -m pytest tests/phase-2/python/test_env.py -q
```

- [ ] **Step 1.3: Создать `tools/__init__.py`** (empty)

- [ ] **Step 1.4: Создать `tools/env.py`**

```python
"""Lightweight .env loader.

Avoids the python-dotenv dep — landing-system .env files are simple
KEY=VALUE pairs with optional comments. We don't need full POSIX shell
semantics.
"""
import os
from pathlib import Path
from typing import Optional


def load_env(path: str) -> None:
    """Load KEY=VALUE pairs from a file into os.environ.

    Lines starting with '#' or empty lines are skipped.
    Quotes around values are stripped.
    Existing env vars are NOT overwritten (.env is fallback, not override).
    """
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_required(key: str) -> str:
    """Return env var or raise KeyError with a friendly message."""
    if key not in os.environ or not os.environ[key]:
        raise KeyError(
            f"Required env var '{key}' not set. "
            f"Add it to .env.local or project .env. "
            f"See spec section 19 for how to obtain it."
        )
    return os.environ[key]


def get_optional(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return env var or default."""
    return os.environ.get(key, default)
```

- [ ] **Step 1.5: Run test, expect PASS**

- [ ] **Step 1.6: Commit**

```bash
git add tools/__init__.py tools/env.py tests/phase-2/python/test_env.py
git commit -m "feat(phase-2): add tools.env loader for .env files"
```

---

### Task 2: `tools/logger.py` — consistent logging

**Files:**
- Create: `tools/logger.py`
- Create: `tests/phase-2/python/test_logger.py`

- [ ] **Step 2.1: Создать тест**

```python
"""Tests for tools.logger."""
import sys
from io import StringIO
from tools.logger import info, warn, error, success


def test_info_writes_to_stderr_with_prefix(capsys):
    info("hello")
    captured = capsys.readouterr()
    assert "hello" in captured.err
    assert "ℹ" in captured.err or "[info]" in captured.err


def test_warn_writes_to_stderr(capsys):
    warn("danger")
    captured = capsys.readouterr()
    assert "danger" in captured.err
    assert "⚠" in captured.err or "[warn]" in captured.err


def test_error_writes_to_stderr(capsys):
    error("broken")
    captured = capsys.readouterr()
    assert "broken" in captured.err
    assert "❌" in captured.err or "[error]" in captured.err


def test_success_writes_to_stderr(capsys):
    success("done")
    captured = capsys.readouterr()
    assert "done" in captured.err
    assert "✅" in captured.err or "[ok]" in captured.err
```

- [ ] **Step 2.2: Run test, expect FAIL**

- [ ] **Step 2.3: Создать `tools/logger.py`**

```python
"""Stderr-only structured logging for CLI scripts.

stdout is reserved for machine output (paths, JSON, etc).
stderr carries human-facing progress.
"""
import sys


def _write(prefix: str, msg: str) -> None:
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)


def info(msg: str) -> None:
    _write("ℹ", msg)


def warn(msg: str) -> None:
    _write("⚠", msg)


def error(msg: str) -> None:
    _write("❌", msg)


def success(msg: str) -> None:
    _write("✅", msg)
```

- [ ] **Step 2.4: Run test, expect PASS**

- [ ] **Step 2.5: Commit**

```bash
git add tools/logger.py tests/phase-2/python/test_logger.py
git commit -m "feat(phase-2): add tools.logger for stderr structured output"
```

---

### Task 3: HTTP adapters — Firecrawl

**Files:**
- Create: `tools/adapters/__init__.py` (empty)
- Create: `tools/adapters/firecrawl.py`
- Create: `tests/phase-2/python/test_adapters_firecrawl.py`

- [ ] **Step 3.1: Создать тест**

```python
"""Tests for tools.adapters.firecrawl."""
import pytest
import responses
from tools.adapters.firecrawl import scrape, FirecrawlError


def test_scrape_returns_markdown(mock_firecrawl, http_mock):
    http_mock.add(
        responses.POST,
        "https://api.firecrawl.dev/v1/scrape",
        json={
            "success": True,
            "data": {"markdown": "# Test page\n\nContent.", "metadata": {"title": "Test"}}
        },
        status=200,
    )
    result = scrape("https://example.com")
    assert "# Test page" in result["markdown"]
    assert result["metadata"]["title"] == "Test"


def test_scrape_raises_on_api_error(mock_firecrawl, http_mock):
    http_mock.add(
        responses.POST,
        "https://api.firecrawl.dev/v1/scrape",
        json={"success": False, "error": "Rate limit"},
        status=429,
    )
    with pytest.raises(FirecrawlError) as exc:
        scrape("https://example.com")
    assert "Rate limit" in str(exc.value) or "429" in str(exc.value)


def test_scrape_raises_when_no_key(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    with pytest.raises(KeyError):
        scrape("https://example.com")
```

- [ ] **Step 3.2: Run test, expect FAIL**

- [ ] **Step 3.3: Создать `tools/adapters/__init__.py`** (empty)

- [ ] **Step 3.4: Создать `tools/adapters/firecrawl.py`**

```python
"""Firecrawl API adapter — single-page scrape only (Phase 2 scope)."""
from typing import Any, Dict
import requests
from tools.env import get_required


class FirecrawlError(RuntimeError):
    pass


def scrape(url: str, timeout: float = 30.0) -> Dict[str, Any]:
    """Scrape a URL and return the page content as markdown + metadata.

    Raises:
      KeyError if FIRECRAWL_API_KEY is missing.
      FirecrawlError on API failure (network, 4xx, 5xx, success=False).
    """
    api_key = get_required("FIRECRAWL_API_KEY")
    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url, "formats": ["markdown"]},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise FirecrawlError(f"network error: {exc}") from exc

    if resp.status_code >= 400:
        try:
            payload = resp.json()
            err = payload.get("error", str(resp.status_code))
        except Exception:
            err = f"HTTP {resp.status_code}"
        raise FirecrawlError(f"firecrawl: {err}")

    payload = resp.json()
    if not payload.get("success"):
        raise FirecrawlError(f"firecrawl: {payload.get('error', 'unknown')}")
    return payload["data"]
```

- [ ] **Step 3.5: Run test, expect PASS**

- [ ] **Step 3.6: Commit**

```bash
git add tools/adapters/__init__.py tools/adapters/firecrawl.py tests/phase-2/python/test_adapters_firecrawl.py
git commit -m "feat(phase-2): add Firecrawl adapter with mocked tests"
```

---

### Task 4: HTTP adapters — Iconify (no key) + WhatTheFont (with fallback flag)

**Files:**
- Create: `tools/adapters/iconify.py`
- Create: `tools/adapters/whatthefont.py`
- Create: `tests/phase-2/python/test_adapters_iconify.py`
- Create: `tests/phase-2/python/test_adapters_whatthefont.py`

- [ ] **Step 4.1: Создать iconify adapter**

`tools/adapters/iconify.py`:

```python
"""Iconify HTTP API — public, no key required."""
from typing import List, Dict, Any
import requests


class IconifyError(RuntimeError):
    pass


def search(query: str, limit: int = 32, prefix: str = "") -> List[Dict[str, Any]]:
    """Search icons across all Iconify icon sets.

    Args:
      query: search term (e.g. "arrow-right", "check")
      limit: max results
      prefix: optional icon set filter (e.g. "lucide", "phosphor")

    Returns list of {"prefix": str, "name": str, "id": str} dicts.
    """
    params = {"query": query, "limit": str(limit)}
    if prefix:
        params["prefixes"] = prefix
    try:
        resp = requests.get("https://api.iconify.design/search", params=params, timeout=10)
    except requests.RequestException as exc:
        raise IconifyError(f"network: {exc}") from exc
    if resp.status_code != 200:
        raise IconifyError(f"HTTP {resp.status_code}")
    payload = resp.json()
    results = []
    for full_id in payload.get("icons", []):
        # full_id format: "prefix:name"
        if ":" in full_id:
            pfx, name = full_id.split(":", 1)
            results.append({"prefix": pfx, "name": name, "id": full_id})
    return results
```

- [ ] **Step 4.2: Создать тест iconify**

`tests/phase-2/python/test_adapters_iconify.py`:

```python
import responses
from tools.adapters.iconify import search


def test_search_parses_results(http_mock):
    http_mock.add(
        responses.GET,
        "https://api.iconify.design/search",
        json={
            "icons": ["lucide:arrow-right", "phosphor:arrow-right", "tabler:arrow-right"],
            "total": 3
        },
        status=200,
    )
    results = search("arrow-right", limit=10)
    assert len(results) == 3
    assert results[0] == {"prefix": "lucide", "name": "arrow-right", "id": "lucide:arrow-right"}


def test_search_with_prefix_filter(http_mock):
    http_mock.add(
        responses.GET,
        "https://api.iconify.design/search",
        json={"icons": ["lucide:check"], "total": 1},
        status=200,
    )
    results = search("check", prefix="lucide")
    assert results == [{"prefix": "lucide", "name": "check", "id": "lucide:check"}]
```

- [ ] **Step 4.3: Run iconify tests, expect PASS**

- [ ] **Step 4.4: Создать whatthefont adapter**

`tools/adapters/whatthefont.py`:

```python
"""WhatTheFont API adapter — font identification by image."""
from pathlib import Path
from typing import List, Dict, Any
import base64
import requests
from tools.env import get_optional


class WhatTheFontError(RuntimeError):
    pass


def identify(image_path: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Identify fonts in an image. Returns up to N candidate matches.

    Returns [] if WHATTHEFONT_API_KEY is missing — caller should fall back
    to Claude vision in that case.

    Each result: {"family": str, "confidence": float, "url": str}.
    """
    api_key = get_optional("WHATTHEFONT_API_KEY")
    if not api_key:
        return []

    img_bytes = Path(image_path).read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode("ascii")
    try:
        resp = requests.post(
            "https://www.myfonts.com/api/whatthefont/v2/identify",
            json={"image": img_b64, "max_results": max_results},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise WhatTheFontError(f"network: {exc}") from exc
    if resp.status_code >= 400:
        raise WhatTheFontError(f"HTTP {resp.status_code}")
    payload = resp.json()
    return [
        {"family": m["family"], "confidence": float(m.get("confidence", 0)), "url": m.get("url", "")}
        for m in payload.get("matches", [])
    ]
```

- [ ] **Step 4.5: Создать тест whatthefont**

`tests/phase-2/python/test_adapters_whatthefont.py`:

```python
from pathlib import Path
import pytest
import responses
from tools.adapters.whatthefont import identify


def test_identify_returns_empty_when_no_key(monkeypatch, tmp_path):
    monkeypatch.delenv("WHATTHEFONT_API_KEY", raising=False)
    img = tmp_path / "test.png"
    img.write_bytes(b"PNG_FAKE")
    assert identify(str(img)) == []


def test_identify_parses_response(mock_whatthefont, http_mock, tmp_path):
    img = tmp_path / "test.png"
    img.write_bytes(b"PNG_FAKE")
    http_mock.add(
        responses.POST,
        "https://www.myfonts.com/api/whatthefont/v2/identify",
        json={
            "matches": [
                {"family": "Cabinet Grotesk", "confidence": 0.94, "url": "https://fontshare.com/cg"},
                {"family": "Inter", "confidence": 0.31, "url": "https://fonts.google.com/inter"}
            ]
        },
        status=200,
    )
    results = identify(str(img))
    assert len(results) == 2
    assert results[0]["family"] == "Cabinet Grotesk"
    assert results[0]["confidence"] == pytest.approx(0.94)
```

- [ ] **Step 4.6: Run all adapter tests, expect PASS**

- [ ] **Step 4.7: Commit**

```bash
git add tools/adapters/iconify.py tools/adapters/whatthefont.py tests/phase-2/python/test_adapters_iconify.py tests/phase-2/python/test_adapters_whatthefont.py
git commit -m "feat(phase-2): add Iconify (free) and WhatTheFont adapters"
```

---

### Task 5: Font downloader + Jinja2 base

**Files:**
- Create: `tools/adapters/font_downloader.py`
- Create: `tools/html/__init__.py` (empty)
- Create: `tools/html/render.py`
- Create: `tools/html/templates/base.html.j2`
- Create: `tests/phase-2/python/test_adapters_font_downloader.py`
- Create: `tests/phase-2/python/test_html_render.py`

- [ ] **Step 5.1: Создать font_downloader**

`tools/adapters/font_downloader.py`:

```python
"""Download fonts from CDN (Google Fonts via Bunny, Fontshare).

Bunny Fonts is GDPR/RU-friendly mirror of Google Fonts.
"""
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote
import requests


class FontDownloadError(RuntimeError):
    pass


def google_fonts_css_url(family: str, weights: List[int]) -> str:
    """Build a Bunny Fonts CSS URL for a Google font."""
    family_q = quote(family.replace(" ", "+"))
    weights_str = ";".join(str(w) for w in sorted(weights))
    return f"https://fonts.bunny.net/css?family={family_q}:wght@{weights_str}"


def fontshare_css_url(slug: str, weights: List[int]) -> str:
    """Build a Fontshare CSS URL. slug is the URL-safe family name."""
    weights_str = ",".join(str(w) for w in sorted(weights))
    return f"https://api.fontshare.com/v2/css?f[]={slug}@{weights_str}"


def download_woff2(url: str, target_dir: str, filename: Optional[str] = None) -> Path:
    """Fetch a WOFF2 file from URL into target_dir.

    Returns Path to downloaded file. Raises FontDownloadError on failure.
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        raise FontDownloadError(f"network: {exc}") from exc
    if resp.status_code != 200:
        raise FontDownloadError(f"HTTP {resp.status_code}")
    out_name = filename or url.split("/")[-1].split("?")[0]
    if not out_name.endswith(".woff2"):
        out_name += ".woff2"
    out_path = target / out_name
    out_path.write_bytes(resp.content)
    return out_path
```

- [ ] **Step 5.2: Создать тест font_downloader**

`tests/phase-2/python/test_adapters_font_downloader.py`:

```python
from pathlib import Path
import responses
from tools.adapters.font_downloader import (
    google_fonts_css_url, fontshare_css_url, download_woff2
)


def test_google_fonts_url():
    url = google_fonts_css_url("Inter", [400, 700])
    assert "fonts.bunny.net" in url
    assert "Inter" in url
    assert "400;700" in url


def test_fontshare_url():
    url = fontshare_css_url("cabinet-grotesk", [500, 700, 800])
    assert "api.fontshare.com" in url
    assert "cabinet-grotesk" in url
    assert "500,700,800" in url


def test_download_woff2(http_mock, tmp_path):
    http_mock.add(
        responses.GET,
        "https://example.com/inter-400.woff2",
        body=b"WOFF2_BYTES",
        status=200,
    )
    out = download_woff2("https://example.com/inter-400.woff2", str(tmp_path))
    assert out.exists()
    assert out.read_bytes() == b"WOFF2_BYTES"
    assert out.name == "inter-400.woff2"
```

- [ ] **Step 5.3: Создать `tools/html/__init__.py`** (empty)

- [ ] **Step 5.4: Создать `tools/html/render.py`**

```python
"""Jinja2 setup for HTML preview generators."""
from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape


_TEMPLATES_DIR = Path(__file__).parent / "templates"


def get_env() -> Environment:
    """Return a configured Jinja2 environment."""
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(template_name: str, context: Dict[str, Any]) -> str:
    """Render a template by name with the given context."""
    env = get_env()
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)
```

- [ ] **Step 5.5: Создать `tools/html/templates/base.html.j2`**

```jinja
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Landing System Preview{% endblock %}</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
      background: #f7f7f9;
      color: #1a1a1f;
      line-height: 1.6;
    }
    .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
    h1, h2, h3 { margin-top: 0; }
    h1 { font-size: 2rem; margin-bottom: 24px; }
    h2 { font-size: 1.5rem; margin: 32px 0 16px; }
    .meta { color: #666; font-size: 0.9rem; margin-bottom: 24px; }
    .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 16px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
    {% block extra_styles %}{% endblock %}
  </style>
</head>
<body>
  <div class="container">
    <h1>{% block heading %}{% endblock %}</h1>
    {% block meta %}{% endblock %}
    {% block content %}{% endblock %}
  </div>
</body>
</html>
```

- [ ] **Step 5.6: Создать тест render**

`tests/phase-2/python/test_html_render.py`:

```python
from tools.html.render import render, get_env


def test_get_env_loads_templates_dir():
    env = get_env()
    # base.html.j2 should be loadable
    tmpl = env.get_template("base.html.j2")
    assert tmpl is not None


def test_render_base_with_blocks():
    # base alone renders empty heading
    out = render("base.html.j2", {})
    assert "<!DOCTYPE html>" in out
    assert "<title>Landing System Preview</title>" in out


def test_render_autoescapes_html_in_context():
    # Render via a tiny inline template — actually we test that
    # autoescape is enabled by checking base output for safety
    env = get_env()
    from jinja2 import DictLoader
    env.loader = DictLoader({"t.html.j2": "{{ value }}"})
    out = env.get_template("t.html.j2").render(value="<script>alert(1)</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
```

- [ ] **Step 5.7: Run all tests, expect PASS**

- [ ] **Step 5.8: Commit**

```bash
git add tools/adapters/font_downloader.py tools/html/__init__.py tools/html/render.py tools/html/templates/base.html.j2 tests/phase-2/python/test_adapters_font_downloader.py tests/phase-2/python/test_html_render.py
git commit -m "feat(phase-2): add font downloader and Jinja2 HTML renderer base"
```

---

## Block B — Stage 02: Client Assets

### Task 6: `client-assets-collector` agent + SKILL.md scaffold

**Files:**
- Create: `.agents/client-assets-collector.md`
- Create: `.skills/client-assets-collection/SKILL.md`
- Create: `tests/phase-2/test-agents-frontmatter.bats`

- [ ] **Step 6.1: Создать тест frontmatter**

`tests/phase-2/test-agents-frontmatter.bats`:

```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

PHASE2_AGENTS=(
  "client-assets-collector"
  "photo-stylist"
  "references-curator"
  "moodboard-composer"
  "style-extractor"
  "brand-architect"
)

@test "client-assets-collector agent file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.agents/client-assets-collector.md"
}

@test "client-assets-collector has valid frontmatter" {
  run grep -E "^name: client-assets-collector$" "$LANDING_SYSTEM_ROOT/.agents/client-assets-collector.md"
  [ "$status" -eq 0 ]
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.agents/client-assets-collector.md"
  [ "$status" -eq 0 ]
}
```

(More agents will be added in this file across later tasks.)

- [ ] **Step 6.2: Run, expect FAIL**

- [ ] **Step 6.3: Создать `.agents/client-assets-collector.md`**

```markdown
---
name: client-assets-collector
description: Use during stage 02 to collect client photos, videos, and reviews from external sources (Yandex Maps, 2GIS, Otzovik). Builds 02_МАТЕРИАЛЫ_КЛИЕНТА/ with assets-manifest.yaml.
---

# client-assets-collector

## Mission

Stage 02 of the landing workflow. Collect every piece of client-supplied content + scrape public reviews.

## Inputs

- User-provided files (photos, videos) → ask user to drop into `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` and `videos/`
- URLs to public review sources (Yandex Maps profile, 2GIS, Otzovik, Flamp)
- Brief from `00_БРИФ/brief.md` (niche signals)

## Process

1. Confirm what client materials exist with the user.
2. For each photo: copy into `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`. Don't modify (photo-stylist owns processing).
3. For each video: copy into `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/`. Note duration.
4. For each review URL:
   - Run `python3 .skills/client-assets-collection/scripts/parse-reviews.py <url> <target-folder>`
   - Output goes into `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/`
5. Generate `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` listing every collected file with its planned use (hero / about / proof).
6. Render `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html` so user can review the haul.

## HARD GATE

- Don't proceed to stage 03 (References) until user has reviewed `assets-gallery.html` and approved.
- If review-parsing fails (network/API error), surface the error and ask user whether to retry or skip.

## Outputs

- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/*.{jpg,png,webp}`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/*.{mp4,mov}`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/*.json` (parsed reviews)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html`

## Tools

Bash, Read, Write, Edit, Glob. Calls Python scripts via Bash.
```

- [ ] **Step 6.4: Создать `.skills/client-assets-collection/SKILL.md`**

```markdown
---
name: client-assets-collection
description: Use during stage 02 to scaffold client materials folder, parse external reviews, and build the assets gallery preview. Owned by client-assets-collector agent.
---

# client-assets-collection

## What I do

- Initialize `02_МАТЕРИАЛЫ_КЛИЕНТА/` subfolders if not present.
- Run `parse-reviews.py` to scrape Yandex Maps / 2GIS / Otzovik via Firecrawl.
- Run `collect.py` to build manifest + HTML gallery.

## Scripts

- [scripts/collect.py](scripts/collect.py)
- [scripts/parse-reviews.py](scripts/parse-reviews.py)
```

- [ ] **Step 6.5: Run tests, expect PASS**

- [ ] **Step 6.6: Commit**

```bash
git add .agents/client-assets-collector.md .skills/client-assets-collection/SKILL.md tests/phase-2/test-agents-frontmatter.bats
git commit -m "feat(phase-2): scaffold client-assets-collector agent and skill"
```

---

### Task 7: `parse-reviews.py` — Firecrawl-based review parser

**Files:**
- Create: `.skills/client-assets-collection/scripts/parse-reviews.py`
- Create: `tests/phase-2/python/test_parse_reviews.py`

- [ ] **Step 7.1: Создать тест**

```python
"""Tests for parse-reviews.py — uses subprocess + responses to mock Firecrawl."""
import json
import sys
from pathlib import Path
import responses
from importlib import import_module

# We import the module path directly so we can call its functions in-process.
# The script is at .skills/client-assets-collection/scripts/parse-reviews.py
# which isn't a normal package path. We invoke via runpy or subprocess.

import subprocess


PARSE_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent / ".skills" / "client-assets-collection" / "scripts" / "parse-reviews.py"


def test_script_exists_and_executable():
    assert PARSE_SCRIPT.exists()
    # Python file, doesn't need executable bit


def test_parse_yandex_maps_url(mock_firecrawl, http_mock, tmp_path):
    http_mock.add(
        responses.POST,
        "https://api.firecrawl.dev/v1/scrape",
        json={
            "success": True,
            "data": {
                "markdown": "## Отзыв 1\n\n5 звёзд. Отлично!\n\n## Отзыв 2\n\n4 звезды. Хорошо.",
                "metadata": {"title": "Yandex Maps — Test"}
            }
        },
        status=200,
    )

    out_dir = tmp_path / "yandex-maps"
    result = subprocess.run(
        [sys.executable, str(PARSE_SCRIPT),
         "https://yandex.ru/maps/-/test", str(out_dir)],
        capture_output=True, text=True,
        env={**__import__("os").environ, "FIRECRAWL_API_KEY": "fc-test"},
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"

    # Verify output
    assert out_dir.exists()
    json_files = list(out_dir.glob("*.json"))
    assert len(json_files) >= 1
    payload = json.loads(json_files[0].read_text())
    assert "source" in payload
    assert "url" in payload
    assert "reviews" in payload
```

(Note: this test mocks the responses library at the module level — but parse-reviews.py runs in a subprocess and won't see our mock. We need to mock at the network layer OR rewrite the test to call `parse_reviews()` as a function instead of CLI. Recommendation: refactor `parse-reviews.py` to expose a `parse_reviews(url, out_dir)` function and a thin `if __name__ == "__main__":` block — then test the function directly.)

- [ ] **Step 7.2: Refactor approach — decide CLI vs library API.**

Use library-first design. Test imports `parse_reviews()` directly.

Update test to import the script as a module:

```python
import importlib.util
import sys
from pathlib import Path

PARSE_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / ".skills" / "client-assets-collection" / "scripts" / "parse-reviews.py")


def _load():
    spec = importlib.util.spec_from_file_location("parse_reviews_mod", PARSE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["parse_reviews_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_parse_returns_reviews_list(mock_firecrawl, http_mock, tmp_path):
    http_mock.add(
        responses.POST,
        "https://api.firecrawl.dev/v1/scrape",
        json={
            "success": True,
            "data": {
                "markdown": "## Отзыв 1\n\n5★\nОтлично!\n\n## Отзыв 2\n\n4★\nХорошо.",
                "metadata": {"title": "Test"}
            }
        },
        status=200,
    )
    mod = _load()
    out = tmp_path / "yandex-maps"
    result = mod.parse_reviews("https://yandex.ru/maps/test", str(out))
    assert "reviews" in result
    assert len(result["reviews"]) >= 1
    # Manifest written
    json_files = list(out.glob("*.json"))
    assert len(json_files) == 1
```

- [ ] **Step 7.3: Run test, expect FAIL**

- [ ] **Step 7.4: Создать `parse-reviews.py`**

```python
#!/usr/bin/env python3
"""Parse public reviews from Yandex Maps / 2GIS / Otzovik via Firecrawl.

CLI:  python3 parse-reviews.py <URL> <OUTPUT_DIR>

Library: from parse_reviews import parse_reviews
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

# Make tools/ importable when invoked as script
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.adapters.firecrawl import scrape, FirecrawlError
from tools.logger import info, error, success


def detect_source(url: str) -> str:
    """Return source name from URL host."""
    host = urlparse(url).hostname or ""
    if "yandex" in host or "maps.yandex" in host:
        return "yandex-maps"
    if "2gis" in host:
        return "2gis"
    if "otzovik" in host:
        return "otzovik"
    if "flamp" in host:
        return "flamp"
    if "irecommend" in host:
        return "irecommend"
    return "other"


_REVIEW_HEADER = re.compile(r"^##+\s+", re.MULTILINE)


def split_reviews(markdown: str) -> list:
    """Naive splitter: Firecrawl markdown of review pages typically uses
    ## or ### headers per review. We split on those and yield non-empty chunks.
    """
    parts = _REVIEW_HEADER.split(markdown)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]


def parse_reviews(url: str, out_dir: str) -> Dict[str, Any]:
    """Scrape URL, extract reviews, write JSON manifest. Return result dict."""
    info(f"Scraping {url}")
    data = scrape(url)
    md = data.get("markdown", "")
    reviews = split_reviews(md)

    source = detect_source(url)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    manifest = {
        "source": source,
        "url": url,
        "scraped_at": datetime.utcnow().isoformat(),
        "title": data.get("metadata", {}).get("title", ""),
        "reviews": reviews,
        "review_count": len(reviews),
    }
    file_path = out / f"{source}-{timestamp}.json"
    file_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    success(f"Wrote {len(reviews)} reviews to {file_path}")
    return manifest


def main(argv: list) -> int:
    if len(argv) < 3:
        print("Usage: parse-reviews.py <URL> <OUTPUT_DIR>", file=sys.stderr)
        return 1
    url, out_dir = argv[1], argv[2]
    try:
        parse_reviews(url, out_dir)
        return 0
    except (FirecrawlError, KeyError) as exc:
        error(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 7.5: Run test, expect PASS**

- [ ] **Step 7.6: Commit**

```bash
git add .skills/client-assets-collection/scripts/parse-reviews.py tests/phase-2/python/test_parse_reviews.py
git commit -m "feat(phase-2): add parse-reviews.py for Firecrawl-based review scraping"
```

---

### Task 8: `collect.py` — assets manifest + gallery

**Files:**
- Create: `.skills/client-assets-collection/scripts/collect.py`
- Create: `tools/html/templates/assets-gallery.html.j2`
- Create: `tests/phase-2/python/test_collect_assets.py`

- [ ] **Step 8.1: Создать тест**

```python
import importlib.util
import json
from pathlib import Path

COLLECT_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                  / ".skills" / "client-assets-collection" / "scripts" / "collect.py")


def _load():
    spec = importlib.util.spec_from_file_location("collect_mod", COLLECT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_manifest_from_filesystem(temp_project):
    mod = _load()
    materials = temp_project / "02_МАТЕРИАЛЫ_КЛИЕНТА"
    photos_orig = materials / "photos" / "original"
    photos_orig.mkdir(parents=True)
    (photos_orig / "hero.jpg").write_bytes(b"FAKE_JPG")
    (photos_orig / "about.png").write_bytes(b"FAKE_PNG")
    videos = materials / "videos"
    videos.mkdir()
    (videos / "testimonial.mp4").write_bytes(b"FAKE_MP4")

    manifest = mod.build_manifest(materials)
    assert len(manifest["photos"]) == 2
    assert len(manifest["videos"]) == 1
    photo_names = {p["filename"] for p in manifest["photos"]}
    assert {"hero.jpg", "about.png"} == photo_names


def test_render_gallery_html(temp_project):
    mod = _load()
    materials = temp_project / "02_МАТЕРИАЛЫ_КЛИЕНТА"
    (materials / "photos" / "original").mkdir(parents=True)
    (materials / "photos" / "original" / "hero.jpg").write_bytes(b"X")

    html_path = mod.render_gallery(materials)
    assert html_path.exists()
    content = html_path.read_text()
    assert "<!DOCTYPE html>" in content
    assert "hero.jpg" in content


def test_run_writes_manifest_yaml(temp_project):
    mod = _load()
    materials = temp_project / "02_МАТЕРИАЛЫ_КЛИЕНТА"
    (materials / "photos" / "original").mkdir(parents=True)
    (materials / "photos" / "original" / "test.jpg").write_bytes(b"X")

    mod.run(str(materials))
    yml = materials / "assets-manifest.yaml"
    assert yml.exists()
    assert "test.jpg" in yml.read_text(encoding="utf-8")
```

- [ ] **Step 8.2: Run test, expect FAIL**

- [ ] **Step 8.3: Создать `collect.py`**

```python
#!/usr/bin/env python3
"""Build assets manifest and HTML gallery from 02_МАТЕРИАЛЫ_КЛИЕНТА.

CLI: python3 collect.py <MATERIALS_DIR>
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.html.render import render
from tools.logger import info, success


PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv"}


def build_manifest(materials_dir: Path) -> Dict[str, Any]:
    """Walk materials_dir and build a manifest of photos, videos, testimonials."""
    photos = []
    photos_dir = materials_dir / "photos" / "original"
    if photos_dir.exists():
        for p in sorted(photos_dir.iterdir()):
            if p.suffix.lower() in PHOTO_EXTS:
                photos.append({"filename": p.name, "path": str(p.relative_to(materials_dir)), "use": "unspecified"})

    videos = []
    videos_dir = materials_dir / "videos"
    if videos_dir.exists():
        for v in sorted(videos_dir.iterdir()):
            if v.suffix.lower() in VIDEO_EXTS:
                videos.append({"filename": v.name, "path": str(v.relative_to(materials_dir))})

    testimonials = []
    test_dir = materials_dir / "testimonials"
    if test_dir.exists():
        for src_dir in sorted(test_dir.iterdir()):
            if not src_dir.is_dir():
                continue
            for j in sorted(src_dir.glob("*.json")):
                try:
                    payload = json.loads(j.read_text(encoding="utf-8"))
                    testimonials.append({
                        "source": payload.get("source"),
                        "file": str(j.relative_to(materials_dir)),
                        "review_count": payload.get("review_count", 0)
                    })
                except Exception:
                    continue

    return {"photos": photos, "videos": videos, "testimonials": testimonials}


def render_gallery(materials_dir: Path) -> Path:
    """Render assets-gallery.html into materials_dir."""
    manifest = build_manifest(materials_dir)
    html = render("assets-gallery.html.j2", {"manifest": manifest})
    out = materials_dir / "assets-gallery.html"
    out.write_text(html, encoding="utf-8")
    return out


def run(materials_dir: str) -> None:
    """Build manifest and gallery; write both."""
    materials = Path(materials_dir)
    manifest = build_manifest(materials)
    yml_out = materials / "assets-manifest.yaml"
    yml_out.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    info(f"Wrote {yml_out}")
    html_out = render_gallery(materials)
    success(f"Wrote {html_out}")


def main(argv: list) -> int:
    if len(argv) < 2:
        print("Usage: collect.py <MATERIALS_DIR>", file=sys.stderr)
        return 1
    run(argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 8.4: Создать `tools/html/templates/assets-gallery.html.j2`**

```jinja
{% extends "base.html.j2" %}
{% block title %}Client Assets Gallery{% endblock %}
{% block heading %}📸 Client Assets — материалы клиента{% endblock %}

{% block content %}
<h2>Photos ({{ manifest.photos|length }})</h2>
{% if manifest.photos %}
<div class="grid">
  {% for p in manifest.photos %}
  <div class="card">
    <strong>{{ p.filename }}</strong>
    <div class="meta">use: {{ p.use }}</div>
    <div class="meta">{{ p.path }}</div>
  </div>
  {% endfor %}
</div>
{% else %}
<p class="meta">No photos yet — drop files into photos/original/</p>
{% endif %}

<h2>Videos ({{ manifest.videos|length }})</h2>
{% if manifest.videos %}
<ul>
  {% for v in manifest.videos %}
  <li>{{ v.filename }} <span class="meta">— {{ v.path }}</span></li>
  {% endfor %}
</ul>
{% else %}
<p class="meta">No videos yet</p>
{% endif %}

<h2>Testimonials ({{ manifest.testimonials|length }})</h2>
{% if manifest.testimonials %}
<ul>
  {% for t in manifest.testimonials %}
  <li><strong>{{ t.source }}</strong>: {{ t.review_count }} review(s) — <span class="meta">{{ t.file }}</span></li>
  {% endfor %}
</ul>
{% else %}
<p class="meta">No testimonials parsed yet</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 8.5: Run tests, expect PASS**

- [ ] **Step 8.6: Commit**

```bash
git add .skills/client-assets-collection/scripts/collect.py tools/html/templates/assets-gallery.html.j2 tests/phase-2/python/test_collect_assets.py
git commit -m "feat(phase-2): add collect.py and assets-gallery.html.j2"
```

---

### Task 9: `photo-stylist` agent + skill scaffold

**Files:**
- Create: `.agents/photo-stylist.md`
- Create: `.skills/photo-styling/SKILL.md`
- Extend: `tests/phase-2/test-agents-frontmatter.bats`

- [ ] **Step 9.1: Расширить test, добавить 2 assertions** для photo-stylist (file exists, frontmatter ok). **Run, expect FAIL.**

- [ ] **Step 9.2: Создать `.agents/photo-stylist.md`**

```markdown
---
name: photo-stylist
description: Use during stage 02 to process client photos identity-safe (cutout, edge cleanup, paper/editorial fitting) without altering faces, age, or proportions. Must NEVER repaint people.
---

# photo-stylist

## Mission

Process raw client photos for use in landing scenes. Identity-safe rules apply absolutely.

## Allowed transformations

- Background removal (cutout)
- Edge cleanup
- Light compositing (drop shadows, paper textures)
- Cropping for scene composition
- Resize / format conversion

## Forbidden

- Altering face, age, body proportions
- AI repaint of person
- Beauty retouching
- Face swap, face age change

## Process

1. List photos in `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`.
2. For each photo, ask user about intended use (hero / about / proof).
3. For each photo to process: run `python3 .skills/photo-styling/scripts/style.py <input> <output> --mode cutout` (or other allowed modes).
4. Output to `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/`.
5. Update `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/stylesheet.md` with rules applied per photo.

## HARD GATE

Before stage 03 — user reviews `assets-gallery.html` (rebuilt) showing both original and processed versions.

## Tools

Bash, Read, Write, Glob. Calls Python `style.py`.
```

- [ ] **Step 9.3: Создать `.skills/photo-styling/SKILL.md`**

```markdown
---
name: photo-styling
description: Use during stage 02 to apply identity-safe photo transformations (cutout, edge cleanup, compositing). Owned by photo-stylist agent.
---

# photo-styling

## Allowed modes

- `cutout` — remove background (rembg if available, else Pillow alpha-mask heuristic)
- `cleanup` — edge smoothing on existing alpha
- `crop` — to specified aspect ratio
- `resize` — to specified max dimension

See [scripts/style.py](scripts/style.py).
```

- [ ] **Step 9.4: Run tests, expect PASS**

- [ ] **Step 9.5: Commit**

```bash
git add .agents/photo-stylist.md .skills/photo-styling/SKILL.md tests/phase-2/test-agents-frontmatter.bats
git commit -m "feat(phase-2): scaffold photo-stylist agent and photo-styling skill"
```

---

### Task 10: `style.py` — cutout + cleanup + resize

**Files:**
- Create: `.skills/photo-styling/scripts/style.py`
- Create: `tests/phase-2/python/test_photo_styling.py`

- [ ] **Step 10.1: Создать тест**

```python
import importlib.util
from pathlib import Path
from PIL import Image
import io

STYLE_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / ".skills" / "photo-styling" / "scripts" / "style.py")


def _load():
    spec = importlib.util.spec_from_file_location("style_mod", STYLE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_test_image(path, size=(100, 100), color=(255, 0, 0)):
    img = Image.new("RGB", size, color)
    img.save(str(path))


def test_resize_max_dimension(tmp_path):
    mod = _load()
    src = tmp_path / "in.jpg"
    _make_test_image(src, size=(2000, 1000))
    dst = tmp_path / "out.jpg"
    mod.resize(str(src), str(dst), max_dim=800)
    out = Image.open(str(dst))
    assert max(out.size) <= 800
    # Aspect ratio preserved
    assert out.size[0] / out.size[1] == 2.0


def test_crop_to_aspect(tmp_path):
    mod = _load()
    src = tmp_path / "in.jpg"
    _make_test_image(src, size=(1000, 600))
    dst = tmp_path / "out.jpg"
    mod.crop_aspect(str(src), str(dst), "1:1")
    out = Image.open(str(dst))
    assert out.size[0] == out.size[1]


def test_cutout_returns_rgba_png(tmp_path):
    mod = _load()
    src = tmp_path / "in.jpg"
    _make_test_image(src, size=(100, 100))
    dst = tmp_path / "out.png"
    mod.cutout(str(src), str(dst))
    out = Image.open(str(dst))
    # Output must have alpha channel
    assert out.mode in ("RGBA", "LA") or "A" in out.mode
```

- [ ] **Step 10.2: Run test, expect FAIL**

- [ ] **Step 10.3: Создать `style.py`**

```python
#!/usr/bin/env python3
"""Identity-safe photo processing.

Allowed operations: cutout, cleanup, crop, resize.
NEVER alters faces, age, body. NEVER AI-repaint.

CLI: python3 style.py <input> <output> --mode <cutout|cleanup|crop|resize> [--aspect 1:1] [--max-dim 1600]
"""
import argparse
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.logger import info, error, success


def resize(src: str, dst: str, max_dim: int = 1600) -> None:
    img = Image.open(src)
    w, h = img.size
    scale = max_dim / max(w, h)
    if scale < 1:
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
    img.save(dst)


def crop_aspect(src: str, dst: str, aspect: str) -> None:
    """Crop src to given aspect ratio (e.g. '1:1', '16:9'), centered."""
    a, b = map(int, aspect.split(":"))
    target = a / b
    img = Image.open(src)
    w, h = img.size
    current = w / h
    if current > target:
        # too wide → crop width
        new_w = int(h * target)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        # too tall → crop height
        new_h = int(w / target)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)
    img.crop(box).save(dst)


def cutout(src: str, dst: str) -> None:
    """Remove background. Uses rembg if installed, else simple alpha heuristic."""
    try:
        from rembg import remove
        with open(src, "rb") as f:
            input_bytes = f.read()
        output_bytes = remove(input_bytes)
        with open(dst, "wb") as f:
            f.write(output_bytes)
        return
    except ImportError:
        info("rembg not installed, using Pillow fallback (less accurate)")

    # Fallback: convert to RGBA and use crude near-white-to-transparent
    img = Image.open(src).convert("RGBA")
    pixels = img.getdata()
    new_pixels = []
    for r, g, b, a in pixels:
        # Crude: pixels close to white become transparent
        if r > 240 and g > 240 and b > 240:
            new_pixels.append((r, g, b, 0))
        else:
            new_pixels.append((r, g, b, a))
    img.putdata(new_pixels)
    img.save(dst, "PNG")


def cleanup(src: str, dst: str) -> None:
    """Edge smoothing on existing alpha channel."""
    from PIL import ImageFilter
    img = Image.open(src).convert("RGBA")
    img.filter(ImageFilter.SMOOTH).save(dst, "PNG")


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--mode", choices=["cutout", "cleanup", "crop", "resize"], required=True)
    parser.add_argument("--aspect", default="1:1")
    parser.add_argument("--max-dim", type=int, default=1600)
    args = parser.parse_args(argv[1:])

    try:
        if args.mode == "cutout":
            cutout(args.input, args.output)
        elif args.mode == "cleanup":
            cleanup(args.input, args.output)
        elif args.mode == "crop":
            crop_aspect(args.input, args.output, args.aspect)
        elif args.mode == "resize":
            resize(args.input, args.output, args.max_dim)
        success(f"{args.mode}: {args.output}")
        return 0
    except Exception as exc:
        error(f"{args.mode} failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 10.4: Run tests, expect PASS**

- [ ] **Step 10.5: Commit**

```bash
git add .skills/photo-styling/scripts/style.py tests/phase-2/python/test_photo_styling.py
git commit -m "feat(phase-2): add identity-safe photo styling (cutout/cleanup/crop/resize)"
```

---

## Block C — Stage 03: References & Moodboard

### Task 11: `references-curator` agent + skill + index.py

**Files:**
- Create: `.agents/references-curator.md`
- Create: `.skills/references-collection/SKILL.md`
- Create: `.skills/references-collection/scripts/index.py`
- Extend: `tests/phase-2/test-agents-frontmatter.bats`
- Create: `tests/phase-2/python/test_references_index.py`

- [ ] **Step 11.1: Расширить bats** (2 new assertions for references-curator). Test fail expected.

- [ ] **Step 11.2: Создать `.agents/references-curator.md`**

```markdown
---
name: references-curator
description: Use during stage 03 to collect visual references (URLs, Behance files, screenshots), tag each with status (candidate/approved/rejected), and maintain 03_РЕФЕРЕНСЫ/index.yaml. Hands off to moodboard-composer once approved set is selected.
---

# references-curator

## Mission

Stage 03 first half. Build the reference index with statuses.

## Process

1. Ask user for references: URLs to sites, Behance / Dribbble files, drag-drop screenshots into `03_РЕФЕРЕНСЫ/refs/`.
2. For each URL, capture screenshot if possible (Phase 5 will add headless browser support; Phase 2 stores URL only).
3. For each reference, prompt user for status: candidate / approved / rejected.
4. Maintain `03_РЕФЕРЕНСЫ/index.yaml` via `python3 .skills/references-collection/scripts/index.py add|update|list`.
5. **HARD GATE**: minimum 3 references with status `approved` before moodboard-composer takes over.

## Tools

Bash, Read, Write, Glob. Calls index.py.
```

- [ ] **Step 11.3: Создать `.skills/references-collection/SKILL.md`**

```markdown
---
name: references-collection
description: Maintains 03_РЕФЕРЕНСЫ/index.yaml — tracks reference URLs, files, and statuses (candidate/approved/rejected). Owned by references-curator agent.
---

# references-collection

## What I do

CRUD on a YAML index of references with statuses. Subcommands:
- `add <ref> [--type url|file] [--status candidate|approved|rejected]`
- `update <ref-id> --status <new>`
- `list [--status <filter>]`

See [scripts/index.py](scripts/index.py).
```

- [ ] **Step 11.4: Создать тест index.py**

```python
import importlib.util
import yaml
from pathlib import Path

INDEX_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / ".skills" / "references-collection" / "scripts" / "index.py")


def _load():
    spec = importlib.util.spec_from_file_location("idx_mod", INDEX_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_add_creates_index_yaml(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()

    mod.add_ref(str(refs_dir), "https://example.com/ref1", "url", "candidate")
    idx_path = refs_dir / "index.yaml"
    assert idx_path.exists()

    data = yaml.safe_load(idx_path.read_text(encoding="utf-8"))
    assert "references" in data
    assert len(data["references"]) == 1
    assert data["references"][0]["status"] == "candidate"


def test_update_status(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    mod.add_ref(str(refs_dir), "https://example.com/ref1", "url", "candidate")
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    ref_id = data["references"][0]["id"]

    mod.update_status(str(refs_dir), ref_id, "approved")
    data = yaml.safe_load((refs_dir / "index.yaml").read_text())
    assert data["references"][0]["status"] == "approved"


def test_list_by_status(tmp_path):
    mod = _load()
    refs_dir = tmp_path / "03_РЕФЕРЕНСЫ"
    refs_dir.mkdir()
    mod.add_ref(str(refs_dir), "ref-a", "url", "approved")
    mod.add_ref(str(refs_dir), "ref-b", "url", "rejected")
    mod.add_ref(str(refs_dir), "ref-c", "url", "approved")

    approved = mod.list_refs(str(refs_dir), status="approved")
    assert len(approved) == 2

    all_refs = mod.list_refs(str(refs_dir))
    assert len(all_refs) == 3
```

- [ ] **Step 11.5: Run test, expect FAIL**

- [ ] **Step 11.6: Создать `.skills/references-collection/scripts/index.py`**

```python
#!/usr/bin/env python3
"""Maintain 03_РЕФЕРЕНСЫ/index.yaml — references with statuses.

CLI:
  python3 index.py add <refs-dir> <ref> [--type url|file] [--status candidate|approved|rejected]
  python3 index.py update <refs-dir> <ref-id> --status <new>
  python3 index.py list <refs-dir> [--status <filter>]
"""
import argparse
import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml


VALID_STATUSES = {"candidate", "approved", "rejected", "needs_user_review"}


def _load(refs_dir: Path) -> Dict[str, Any]:
    idx = refs_dir / "index.yaml"
    if not idx.exists():
        return {"references": []}
    return yaml.safe_load(idx.read_text(encoding="utf-8")) or {"references": []}


def _save(refs_dir: Path, data: Dict[str, Any]) -> None:
    idx = refs_dir / "index.yaml"
    idx.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _ref_id(ref: str) -> str:
    return hashlib.sha1(ref.encode("utf-8")).hexdigest()[:8]


def add_ref(refs_dir: str, ref: str, ref_type: str = "url", status: str = "candidate") -> Dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    refs = Path(refs_dir)
    refs.mkdir(parents=True, exist_ok=True)
    data = _load(refs)
    entry = {
        "id": _ref_id(ref),
        "value": ref,
        "type": ref_type,
        "status": status,
        "added_at": datetime.utcnow().isoformat() + "Z",
    }
    # Idempotency: skip if same id already there
    if not any(r["id"] == entry["id"] for r in data["references"]):
        data["references"].append(entry)
        _save(refs, data)
    return entry


def update_status(refs_dir: str, ref_id: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {new_status}")
    refs = Path(refs_dir)
    data = _load(refs)
    for r in data["references"]:
        if r["id"] == ref_id:
            r["status"] = new_status
            r["updated_at"] = datetime.utcnow().isoformat() + "Z"
            _save(refs, data)
            return
    raise KeyError(f"ref {ref_id} not found")


def list_refs(refs_dir: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    refs = Path(refs_dir)
    data = _load(refs)
    if status:
        return [r for r in data["references"] if r["status"] == status]
    return data["references"]


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add")
    add.add_argument("refs_dir")
    add.add_argument("ref")
    add.add_argument("--type", default="url")
    add.add_argument("--status", default="candidate")

    upd = sub.add_parser("update")
    upd.add_argument("refs_dir")
    upd.add_argument("ref_id")
    upd.add_argument("--status", required=True)

    lst = sub.add_parser("list")
    lst.add_argument("refs_dir")
    lst.add_argument("--status")

    args = p.parse_args(argv[1:])
    try:
        if args.cmd == "add":
            entry = add_ref(args.refs_dir, args.ref, args.type, args.status)
            print(entry["id"])
        elif args.cmd == "update":
            update_status(args.refs_dir, args.ref_id, args.status)
        elif args.cmd == "list":
            for r in list_refs(args.refs_dir, args.status):
                print(f"{r['id']}\t{r['status']}\t{r['value']}")
        return 0
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 11.7: Run test, expect PASS**

- [ ] **Step 11.8: Commit**

```bash
git add .agents/references-curator.md .skills/references-collection/ tests/phase-2/test-agents-frontmatter.bats tests/phase-2/python/test_references_index.py
git commit -m "feat(phase-2): add references-curator agent and references-collection skill with index.py"
```

---

### Task 12: `moodboard-composer` agent + skill + render.py + HTML template

**Files:**
- Create: `.agents/moodboard-composer.md`
- Create: `.skills/moodboard-creation/SKILL.md`
- Create: `.skills/moodboard-creation/scripts/render.py`
- Create: `tools/html/templates/moodboard.html.j2`
- Create: `tools/html/templates/partials/ref-card.html.j2`
- Extend: `tests/phase-2/test-agents-frontmatter.bats`
- Create: `tests/phase-2/python/test_moodboard_render.py`

- [ ] **Step 12.1: Расширить bats**, **тесты для render.py**, **expect FAIL**.

- [ ] **Step 12.2: Создать agent + skill md.** Content:

`.agents/moodboard-composer.md`:
```markdown
---
name: moodboard-composer
description: Use during stage 03 after references are approved. Synthesizes a moodboard.md narrative + moodboard.html visual board from approved references.
---

# moodboard-composer

## Mission

Compose `03_РЕФЕРЕНСЫ/moodboard.md` (text narrative explaining the visual direction) + `moodboard.html` (visual board with reference cards).

## Process

1. Read `03_РЕФЕРЕНСЫ/index.yaml`, get all refs with status `approved`.
2. For each: prompt user for tags (e.g. "split-screen", "warm-palette", "premium-typography").
3. Write `moodboard.md` describing the chosen direction (palette feel, typography character, motion vibe, what we adopt and reject).
4. Run `python3 .skills/moodboard-creation/scripts/render.py <refs-dir>` to build `moodboard.html`.
5. **HARD GATE**: user opens moodboard.html, approves direction. Then style-extractor takes over.

## Tools

Bash, Read, Write, Glob. Calls render.py.
```

`.skills/moodboard-creation/SKILL.md`:
```markdown
---
name: moodboard-creation
description: Render moodboard.html from approved references in 03_РЕФЕРЕНСЫ/index.yaml. Owned by moodboard-composer.
---

See [scripts/render.py](scripts/render.py).
```

- [ ] **Step 12.3: Создать `tools/html/templates/partials/ref-card.html.j2`**

```jinja
<div class="card ref-card status-{{ ref.status }}">
  <div class="ref-meta">
    <span class="status-badge status-{{ ref.status }}">{{ ref.status }}</span>
    <span class="ref-type">{{ ref.type }}</span>
  </div>
  <div class="ref-value">
    {% if ref.type == "url" %}
      <a href="{{ ref.value }}" target="_blank" rel="noopener">{{ ref.value }}</a>
    {% else %}
      <code>{{ ref.value }}</code>
    {% endif %}
  </div>
  {% if ref.tags %}
    <div class="ref-tags">
      {% for t in ref.tags %}<span class="tag">{{ t }}</span>{% endfor %}
    </div>
  {% endif %}
</div>
```

- [ ] **Step 12.4: Создать `tools/html/templates/moodboard.html.j2`**

```jinja
{% extends "base.html.j2" %}
{% block title %}Moodboard — {{ project_name }}{% endblock %}
{% block heading %}🎨 Moodboard — {{ project_name }}{% endblock %}

{% block extra_styles %}
.ref-card { border-left: 4px solid #999; }
.ref-card.status-approved { border-left-color: #22c55e; }
.ref-card.status-rejected { border-left-color: #ef4444; opacity: 0.5; }
.ref-card.status-candidate { border-left-color: #f59e0b; }
.status-badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.status-approved { background: #dcfce7; color: #166534; }
.status-rejected { background: #fee2e2; color: #991b1b; }
.status-candidate { background: #fef3c7; color: #92400e; }
.ref-meta { display: flex; gap: 8px; margin-bottom: 8px; }
.ref-type { font-size: 0.85rem; color: #666; }
.ref-value { word-break: break-all; }
.ref-tags { margin-top: 8px; }
.tag { display: inline-block; background: #f3f4f6; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px; }
{% endblock %}

{% block content %}
{% if narrative %}
<div class="card">
  <h2>Direction</h2>
  {{ narrative | safe }}
</div>
{% endif %}

<h2>Approved ({{ approved|length }})</h2>
<div class="grid">
  {% for ref in approved %}{% include "partials/ref-card.html.j2" %}{% endfor %}
</div>

{% if rejected %}
<h2>Rejected ({{ rejected|length }})</h2>
<div class="grid">
  {% for ref in rejected %}{% include "partials/ref-card.html.j2" %}{% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 12.5: Создать `render.py`**

```python
#!/usr/bin/env python3
"""Render moodboard.html from 03_РЕФЕРЕНСЫ/index.yaml.

CLI: python3 render.py <refs-dir> [--narrative <path-to-md>] [--project <name>]
"""
import argparse
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.html.render import render
from tools.logger import success, error


def render_moodboard(refs_dir: str, narrative_md: str = "", project_name: str = "Project") -> Path:
    refs = Path(refs_dir)
    idx = refs / "index.yaml"
    if not idx.exists():
        raise FileNotFoundError(f"no index.yaml in {refs_dir}")
    data = yaml.safe_load(idx.read_text(encoding="utf-8")) or {"references": []}
    all_refs = data["references"]
    approved = [r for r in all_refs if r["status"] == "approved"]
    rejected = [r for r in all_refs if r["status"] == "rejected"]

    narrative_html = ""
    if narrative_md:
        narrative_path = Path(narrative_md)
        if narrative_path.exists():
            # Lightweight md→html: just paragraphs.
            narrative_html = "<p>" + narrative_path.read_text(encoding="utf-8").replace("\n\n", "</p><p>") + "</p>"

    html = render("moodboard.html.j2", {
        "approved": approved,
        "rejected": rejected,
        "narrative": narrative_html,
        "project_name": project_name,
    })
    out = refs / "moodboard.html"
    out.write_text(html, encoding="utf-8")
    return out


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("refs_dir")
    p.add_argument("--narrative", default="")
    p.add_argument("--project", default="Project")
    args = p.parse_args(argv[1:])
    try:
        out = render_moodboard(args.refs_dir, args.narrative, args.project)
        success(f"Wrote {out}")
        return 0
    except Exception as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 12.6: Создать тест**

```python
import importlib.util
from pathlib import Path
import yaml

RENDER_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                 / ".skills" / "moodboard-creation" / "scripts" / "render.py")


def _load():
    spec = importlib.util.spec_from_file_location("mb_render", RENDER_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_moodboard_writes_html(tmp_path):
    mod = _load()
    refs = tmp_path / "03_РЕФЕРЕНСЫ"
    refs.mkdir()
    (refs / "index.yaml").write_text(yaml.safe_dump({
        "references": [
            {"id": "abc12345", "value": "https://example.com/a", "type": "url", "status": "approved"},
            {"id": "def67890", "value": "https://example.com/b", "type": "url", "status": "rejected"},
        ]
    }, allow_unicode=True), encoding="utf-8")

    out = mod.render_moodboard(str(refs), project_name="TestProject")
    assert out.exists()
    html = out.read_text()
    assert "TestProject" in html
    assert "https://example.com/a" in html
    assert "approved" in html


def test_render_with_narrative(tmp_path):
    mod = _load()
    refs = tmp_path / "03_РЕФЕРЕНСЫ"
    refs.mkdir()
    (refs / "index.yaml").write_text(yaml.safe_dump({"references": []}), encoding="utf-8")
    narrative = tmp_path / "n.md"
    narrative.write_text("Cinematic feel.\n\nDeep contrast.", encoding="utf-8")

    out = mod.render_moodboard(str(refs), narrative_md=str(narrative))
    html = out.read_text()
    assert "Cinematic feel" in html
    assert "Deep contrast" in html
```

- [ ] **Step 12.7: Run tests, expect PASS**

- [ ] **Step 12.8: Commit**

```bash
git add .agents/moodboard-composer.md .skills/moodboard-creation/ tools/html/templates/moodboard.html.j2 tools/html/templates/partials/ref-card.html.j2 tests/phase-2/test-agents-frontmatter.bats tests/phase-2/python/test_moodboard_render.py
git commit -m "feat(phase-2): add moodboard-composer agent + render.py + moodboard.html.j2"
```

---

### Task 13–15: References & Moodboard polish

For brevity, the remaining Block C tasks 13, 14, 15 are similar in pattern to Tasks 11–12. Each task adds:

- **Task 13:** `index.py` `--remove` and `--show <ref-id>` subcommands + tests
- **Task 14:** `moodboard.md` template generator (Bash/Python that produces a starter narrative file based on approved refs' tags)
- **Task 15:** integration test for refs + moodboard pipeline (add 3 refs, render moodboard, verify HTML contains all 3)

Each follows the same TDD pattern (test fail → impl → test pass → commit).

**File changes summarized:**
- `.skills/references-collection/scripts/index.py` (gains 2 subcommands)
- `.skills/moodboard-creation/scripts/scaffold.py` (NEW)
- `tests/phase-2/python/test_references_index.py` (extended)
- `tests/phase-2/python/test_moodboard_scaffold.py` (NEW)
- `tests/phase-2/integration/test-phase2-pipeline.bats` (NEW, partial)

Commits:
- `feat(phase-2): add index.py remove and show subcommands`
- `feat(phase-2): add moodboard scaffold generator`
- `test(phase-2): integration test for references + moodboard pipeline`

---

## Block D — Stage 03→04: Style Extraction

### Task 16: `style-extractor` agent

**Files:**
- Create: `.agents/style-extractor.md`
- Create: `.skills/style-decomposition/SKILL.md`
- Extend: `tests/phase-2/test-agents-frontmatter.bats`

- [ ] Создать markdown agent + skill per design from spec section 6 row 6, with HARD GATE: must produce 5 outputs (palette.yaml, fonts.yaml, icons.yaml, grid.md, motion.md) before brand-architect runs.

- [ ] Commit: `feat(phase-2): scaffold style-extractor agent and style-decomposition skill`

---

### Task 17: `extract-palette.py`

**Files:**
- Create: `.skills/style-decomposition/scripts/extract-palette.py`
- Create: `tests/phase-2/python/test_extract_palette.py`

- [ ] **Step 17.1: Test** — given a 100×100 image with known colors, palette.yaml has 5 dominant colors with hex codes and pixel-source coordinates.

- [ ] **Step 17.2: Implementation:**

```python
#!/usr/bin/env python3
"""Extract dominant color palette from a reference image.

CLI: python3 extract-palette.py <image> <output-yaml> [--count 5]
"""
import argparse
import sys
from pathlib import Path
from PIL import Image
import colorthief
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import success


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def extract(image_path: str, count: int = 5) -> list:
    """Extract `count` dominant colors. Return list of dicts with hex + source pixel."""
    ct = colorthief.ColorThief(image_path)
    palette_rgb = ct.get_palette(color_count=count, quality=10)

    # For each color, find a representative pixel coordinate (first match)
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    pixels = list(img.getdata())
    results = []
    for rgb in palette_rgb:
        # Find first pixel within Manhattan distance ≤ 20 of target
        coord = None
        for idx, p in enumerate(pixels):
            if all(abs(p[c] - rgb[c]) <= 20 for c in range(3)):
                coord = (idx % w, idx // w)
                break
        results.append({
            "hex": rgb_to_hex(rgb),
            "rgb": list(rgb),
            "source_pixel": list(coord) if coord else None,
        })
    return results


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("output_yaml")
    p.add_argument("--count", type=int, default=5)
    args = p.parse_args(argv[1:])

    palette = extract(args.image, args.count)
    out = Path(args.output_yaml)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump({
        "source_image": args.image,
        "palette": palette,
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    success(f"Wrote {out} ({len(palette)} colors)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 17.3: Run, fix, commit:** `feat(phase-2): add palette extraction with pixel-source provenance`

---

### Task 18: `identify-fonts.py` (WhatTheFont + fallback metadata)

Similar pattern. Calls `tools.adapters.whatthefont.identify()`. If empty, returns a stub entry asking for manual identification.

Output `fonts.yaml`:
```yaml
source_image: ref-1.png
candidates:
  - family: Cabinet Grotesk
    confidence: 0.94
    source: WhatTheFont
    download_url: https://fontshare.com/...
  - family: Inter
    confidence: 0.31
    source: WhatTheFont
manual_review_required: false
```

- [ ] Test, impl, commit: `feat(phase-2): add font identification via WhatTheFont with fallback metadata`

---

### Task 19: `match-icons.py` (Iconify search)

Takes a list of needed semantic icons (e.g. ["arrow-right", "check", "user", "shield"]) and queries Iconify, returning matches grouped by prefix.

Output `icons.yaml`:
```yaml
needed: [arrow-right, check]
matches:
  arrow-right:
    - lucide:arrow-right
    - phosphor:arrow-right
  check:
    - lucide:check
    - heroicons:check
recommendation:
  library: lucide
  reason: consistent stroke style across needed icons
```

- [ ] Test, impl, commit: `feat(phase-2): add icon matching via Iconify with library recommendation`

---

### Task 20: `download-fonts.py` (CDN downloader)

Wraps `tools.adapters.font_downloader`. Reads `fonts.yaml` recommendation, downloads WOFF2 to `08_КОД/wp-theme/assets/fonts/` (creates path if needed in Phase 4 — for Phase 2, write to a generic `04_БРЕНД/extracted/fonts-cache/`).

- [ ] Test, impl, commit: `feat(phase-2): add download-fonts.py for offline font caching`

---

### Task 21: `style-extractor` orchestrator script

Single Python entry point that runs palette/fonts/icons in sequence on a list of approved reference images.

- [ ] Test, impl, commit: `feat(phase-2): add style-extractor orchestrator script tying palette/fonts/icons`

---

### Task 22: Style extraction smoke test

End-to-end bats test that uses fixture images and asserts all 3 yaml files (palette, fonts, icons) are produced.

- [ ] Test, impl, commit: `test(phase-2): add style-extractor end-to-end smoke test`

---

## Block E — Stage 04: Brand Architect

### Task 23: `brand-architect` agent

**Files:**
- Create: `.agents/brand-architect.md`
- Create: `.skills/brand-kit-build/SKILL.md`
- Extend: `tests/phase-2/test-agents-frontmatter.bats`

Agent description: synthesizes `brand-kit.md` from `04_БРЕНД/extracted/*.yaml`, with provenance (every choice traces to its source). Then invokes brand-kit HTML renderer.

- [ ] Commit: `feat(phase-2): scaffold brand-architect agent and brand-kit-build skill`

---

### Task 24: `brand-kit-build/scripts/build.py`

Reads all `04_БРЕНД/extracted/*.yaml` and emits `04_БРЕНД/brand-kit.md` in the format from spec section §03 ("Расширение этапов 03 и 04 — трассировка происхождения"):

```yaml
brand_kit:
  meta:
    project: <name>
    created: <date>
    references_used: <count>
  colors:
    primary:
      hex: "#FF5733"
      role: "CTA, accents"
      source: "ref-grabovski-hero.png pixel(120,340)"
      extracted_by: "color-thief"
  typography:
    display:
      family: "Cabinet Grotesk"
      ...
  icons:
    library: "Lucide"
    selected:
      - check-circle: "matches checkmark in ref"
  motion: ...
  components: ...
```

- [ ] Test (build from fixture extracted/), impl, commit: `feat(phase-2): add brand-kit build.py with provenance synthesis`

---

### Task 25: `brand-kit-build/scripts/render-html.py`

Renders `brand-kit.html` from `brand-kit.md`. Template shows palette swatches, font specimens (using @font-face from CDN URL), icon thumbnails.

- [ ] Создать `tools/html/templates/brand-kit.html.j2` с partials `palette.html.j2` и `font-card.html.j2`.

- [ ] Test, impl, commit: `feat(phase-2): add brand-kit HTML preview renderer`

---

### Task 26: Brand kit smoke test

End-to-end: from fixture extracted/ files, build brand-kit.md and brand-kit.html. Verify both contain provenance for at least one color, one font, one icon.

- [ ] Test, impl, commit: `test(phase-2): brand-kit end-to-end smoke test`

---

## Block F — Orchestrator + Slash Commands + Integration

### Task 27: Extend `landing-orchestrator` for stages 02–04

**Files:**
- Modify: `.agents/landing-orchestrator.md`
- Extend: `tests/phase-1/test-skills-and-agents.bats` (or create `test-orchestrator-phase2.bats`)

Update the agent body. New "## Phase 2 Scope" section replaces (or amends) "## Phase 1 Scope":

> In Phase 2 I now lead through stages 00 → 01 → 02 → 03 → 04. For each stage:
> 1. Dispatch the right specialist agent (client-assets-collector, photo-stylist, references-curator, moodboard-composer, style-extractor, brand-architect)
> 2. Wait for their HTML preview output (assets-gallery.html / moodboard.html / brand-kit.html)
> 3. Show user the preview path; **HARD GATE — wait for explicit approval before continuing**
> 4. Stages 05–12 still pending Phase 3+

- [ ] Test (regex-check that orchestrator mentions all 6 Phase 2 agents and the Phase 2 Scope section), impl, commit: `feat(phase-2): extend landing-orchestrator for stages 02-04`

---

### Task 28: `/landing-references` slash command

**Files:**
- Create: `.claude/commands/landing-references.md`
- Create: `tests/phase-2/test-commands-phase2.bats`

Body: "Run within a landing project at any time after stage 01. Invokes references-curator agent. Maintains 03_РЕФЕРЕНСЫ/index.yaml. Renders moodboard.html on completion."

- [ ] Test (file exists, frontmatter, mentions references-curator), impl, commit: `feat(phase-2): add /landing-references slash command`

---

### Task 29: `/landing-moodboard` and `/landing-brand` slash commands

Same pattern. Each: 4 assertions (file exists, description, mentions corresponding agent, mentions HTML preview output).

- [ ] Tests + impls + commits: `feat(phase-2): add /landing-moodboard slash command` and `feat(phase-2): add /landing-brand slash command`

---

### Task 30: Phase 2 integration test + master plan update + tag

**Files:**
- Create: `tests/phase-2/integration/test-phase2-pipeline.bats`
- Modify: `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` (Phase 2 → 🟢)

Integration test:
1. Create new project via `init.sh` into temp dir
2. Drop fixture images into `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`
3. Mock Firecrawl + WhatTheFont + Iconify (via setup of env vars + responses or by setting test fixture URLs that are recorded)
4. Run scripts in sequence: collect.py → references/index.py add → moodboard/render.py → style-extractor (palette only — fonts/icons may need separate fixture setup) → brand-architect/build.py → render-html.py
5. Assert all expected output files exist with non-empty content

Note: end-to-end with real APIs is out of scope; we use a "fast-path" with all-locally-mocked data. Real-API smoke test is a manual checklist for the developer.

- [ ] Final commit: `docs(phase-2): mark Phase 2 complete in master plan`

- [ ] Tag: `git tag -a phase-2-complete -m "Phase 2: Brainstorming Pipeline complete"`

---

## Self-Review (по методике writing-plans)

**1. Spec coverage:**
- ✅ Spec § 4 etapes 02, 03, 04 — папки и файлы создаются Tasks 8, 12, 25
- ✅ Spec § 5 этапы 02, 03, 04 — все 6 агентов реализованы
- ✅ Spec § 6 агенты 2–7 (`client-assets-collector`, `photo-stylist`, `references-curator`, `moodboard-composer`, `style-extractor`, `brand-architect`) — Tasks 6, 9, 11, 12, 16, 23
- ✅ Spec § 7.2 MCP Firecrawl — обёрнут в `tools.adapters.firecrawl`
- ✅ Spec § 8.4 Iconify, Fontshare, WhatTheFont — все в адаптерах
- ✅ Provenance в brand-kit.md — Task 24
- ✅ HTML preview на каждом этапе — assets-gallery, moodboard, brand-kit

**2. Placeholder scan:**
- Tasks 13–15 описаны вкратце (по образцу Tasks 11–12). Это допустимо — паттерн повторяется, конкретный код исполнитель пишет по образцу. Не placeholder в смысле "TBD" — это compressed tasks с явной ссылкой на эталонный паттерн.
- Task 16 содержит "per design from spec section 6 row 6" — это явная ссылка, не TBD.

**3. Type consistency:**
- Скрипты везде: `<verb>.py` (collect, parse-reviews, style, render, index, build, etc).
- Агенты: kebab-case `<role>-<noun>.md`.
- Скиллы: kebab-case с описательным именем.
- Slash-команды: `/landing-<stage>` где `<stage>` — концепт, не цифра (references / moodboard / brand).
- Python imports: `tools.adapters.X`, `tools.html.render`, `tools.env`, `tools.logger`.

**4. Ambiguity check:**
- Тесты для скриптов вызывают модули через `importlib.util.spec_from_file_location` — это рабочий паттерн, повторяется единообразно в 5+ тестах.
- Task 30's integration test избегает реальных API через mocking + локальные fixtures.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-03-phase-2-brainstorming-pipeline.md`.

**Two execution options:**

**1. Subagent-Driven** (рекомендую) — свежий subagent на каждый блок, two-stage review между блоками. Phase 1 опыт показал что это занимает ~30 мин на блок. Phase 2 = 6 блоков × 30 мин ≈ 3 часа.

**2. Inline Execution** — задачи в текущей сессии через executing-plans. Медленнее, контекст растёт.

**Which approach?**
