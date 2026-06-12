# S2-E Phase E1 — SEO/Tech Audit Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `seo-tech-audit` skill with `/landing-audit` slash-command that runs 43 HTTP-based checks (HTML/Network/Schema) against single URL or all multisite segments, producing Markdown+JSON reports + stage-11 hard-gate.

**Architecture:** Pure-Python skill (no Lighthouse/Node) using `requests`+`beautifulsoup4`+`python-whois`. Three runner modules (`html_checks.py`, `network_checks.py`, `schema_checks.py`) called by orchestrator `run-audit.py` which auto-discovers multisite hosts from `.landing-state.yaml::audience_segments`. Per-site + aggregate reports written to `11_QA/`. Exit code reflects worst hard-gate status across all sites.

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4`, `lxml`, `PyYAML`, `python-whois`, `jsonschema`, pytest.

**Spec:** [docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md](../specs/2026-05-15-s2e-seo-tech-audit-design.md) (revision §13.2 = E1 scope)

---

## File Structure

```
skills/seo-tech-audit/                                    # NEW directory
├── SKILL.md                                              # NEW — Task 1
├── scripts/
│   ├── run-audit.py                                      # NEW — Task 6 (orchestrator)
│   ├── runners/
│   │   ├── __init__.py                                   # NEW — Task 3
│   │   ├── html_checks.py                                # NEW — Task 3 (25 checks)
│   │   ├── network_checks.py                             # NEW — Task 4 (13 checks)
│   │   └── schema_checks.py                              # NEW — Task 5 (5 checks)
│   └── lib/
│       ├── __init__.py                                   # NEW — Task 2
│       ├── http_client.py                                # NEW — Task 2 (requests wrapper)
│       ├── thresholds.py                                 # NEW — Task 2 (gate loader)
│       ├── report.py                                     # NEW — Task 7 (Markdown + JSON)
│       └── site_discovery.py                             # NEW — Task 8 (multisite hosts)
├── config/
│   └── quality-thresholds.yaml                           # NEW — Task 2 (default gates)
└── tests/
    ├── conftest.py                                       # NEW — Task 3
    ├── fixtures/
    │   ├── good-site.html                                # NEW — Task 3
    │   ├── bad-site.html                                 # NEW — Task 3
    │   ├── state-multisite.yaml                          # NEW — Task 8
    │   └── state-single.yaml                             # NEW — Task 8
    ├── test_html_checks.py                               # NEW — Task 3
    ├── test_network_checks.py                            # NEW — Task 4
    ├── test_schema_checks.py                             # NEW — Task 5
    ├── test_site_discovery.py                            # NEW — Task 8
    ├── test_report.py                                    # NEW — Task 7
    └── test_run_audit_integration.py                     # NEW — Task 9

.claude/commands/
└── landing-audit.md                                      # NEW — Task 10

config/stage-gates.yaml                                   # MODIFY — Task 11
CLAUDE.md                                                 # MODIFY — Task 12
```

---

### Task 1: SKILL.md frontmatter + skeleton dirs

**Files:**
- Create: `skills/seo-tech-audit/SKILL.md`
- Create empty dirs: `skills/seo-tech-audit/{scripts/runners,scripts/lib,config,tests/fixtures}/`

- [ ] **Step 1: Create directory tree**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
mkdir -p skills/seo-tech-audit/scripts/runners \
         skills/seo-tech-audit/scripts/lib \
         skills/seo-tech-audit/config \
         skills/seo-tech-audit/tests/fixtures
```

- [ ] **Step 2: Create SKILL.md**

Path: `skills/seo-tech-audit/SKILL.md`

```markdown
---
name: seo-tech-audit
description: Аудит задеплоенного лендинга — 43 HTTP-проверки (HTML on-page, network/infra, schema/microdata). Multisite-aware (auto-discovers поддомены из .landing-state.yaml). Используется как stage-11 hard-gate. Pure Python, без Lighthouse/Node (E1 scope; Lighthouse Vitals = E2).
---

# seo-tech-audit

Скилл для автоматического аудита задеплоенного лендинга. Запускается через slash-команду `/landing-audit` или напрямую `python scripts/run-audit.py`.

**Что проверяет (E1, 43 check'а):**
- **HTML on-page (25):** title/meta/h1/canonical/lang/img-alt/internal links и т.д.
- **Network/Infra (13):** SSL, redirects, robots.txt, sitemap.xml, 404 page, Whois
- **Schema/Microdata (5):** Open Graph, Twitter Card, JSON-LD, favicon

**Что НЕ проверяет в E1 (отдельные фазы):**
- Lighthouse Web Vitals (LCP/CLS/INP) — E2
- Crawler битых ссылок — E2
- Content metrics RU (тошнота/Flesch) — E3
- AI readiness + auto-fix loop — E4

Spec: [docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md](../../docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md) (§13 — E1 scope)

## Использование

```bash
# Все поддомены проекта (auto-discover из .landing-state.yaml)
python skills/seo-tech-audit/scripts/run-audit.py --project ~/Lendings/dubai-avto-liza

# Конкретный URL (ad-hoc)
python skills/seo-tech-audit/scripts/run-audit.py --url https://dubai-avto-liza.ailexi.ru

# JSON output для CI/orchestrator
python skills/seo-tech-audit/scripts/run-audit.py --project <p> --json
```

Или slash-команда `/landing-audit dubai-avto-liza` из Claude Code.

## Output

```
11_QA/
├── audit-report.md       # Сводный отчёт (все поддомены)
├── audit-report.json     # Машино-читаемый
└── per-site/
    ├── <host1>.md
    ├── <host1>.json
    └── ...
```

## Exit codes

- `0` — все hard-gates ✓ на всех поддоменах
- `1` — хоть один hard-gate fail на любом поддомене
- `2` — system error (project not found, network unreachable)

## Stage-11 gate

`config/stage-gates.yaml::11_qa.hard_checks` включает `seo_audit_pass` который запускает run-audit.py. Stage-11 не закроется пока есть hard-gate failures.
```

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/SKILL.md
git commit -m "feat(s2e-e1): skill scaffold — SKILL.md + dir structure"
```

---

### Task 2: lib/http_client.py + lib/thresholds.py + config/quality-thresholds.yaml

**Files:**
- Create: `skills/seo-tech-audit/scripts/lib/__init__.py`
- Create: `skills/seo-tech-audit/scripts/lib/http_client.py`
- Create: `skills/seo-tech-audit/scripts/lib/thresholds.py`
- Create: `skills/seo-tech-audit/config/quality-thresholds.yaml`

- [ ] **Step 1: Create `scripts/lib/__init__.py`** (empty file)

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
echo '' > skills/seo-tech-audit/scripts/lib/__init__.py
```

- [ ] **Step 2: Create `lib/http_client.py`**

Path: `skills/seo-tech-audit/scripts/lib/http_client.py`

```python
"""HTTP wrapper with retry, timeout, UA — shared across all runners."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "landing-system-audit/1.0 (+https://github.com/landing-system)"
DEFAULT_TIMEOUT = 15  # seconds


def make_session() -> requests.Session:
    """requests.Session with 3 retries on 5xx + 30s connect/read timeout."""
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def fetch(url: str, session: requests.Session | None = None,
          method: str = "GET", allow_redirects: bool = True) -> requests.Response:
    """Fetch URL with default timeout. Caller handles exceptions."""
    if session is None:
        session = make_session()
    return session.request(method, url, timeout=DEFAULT_TIMEOUT,
                           allow_redirects=allow_redirects)
```

- [ ] **Step 3: Create `lib/thresholds.py`**

Path: `skills/seo-tech-audit/scripts/lib/thresholds.py`

```python
"""Load default + project-override thresholds for hard/soft gates."""
from pathlib import Path
import yaml

_DEFAULTS_PATH = Path(__file__).parent.parent.parent / "config" / "quality-thresholds.yaml"


def load_thresholds(project_overrides_path: Path | None = None) -> dict:
    """Load defaults; merge project-specific overrides if file exists.

    Returns: {check_id: {hard: bool, value: any, justification: str|None}}
    """
    if not _DEFAULTS_PATH.exists():
        raise FileNotFoundError(f"defaults not found: {_DEFAULTS_PATH}")
    defaults = yaml.safe_load(_DEFAULTS_PATH.read_text(encoding="utf-8")) or {}

    if project_overrides_path and project_overrides_path.exists():
        overrides = yaml.safe_load(project_overrides_path.read_text(encoding="utf-8")) or {}
        for check_id, cfg in overrides.items():
            if check_id in defaults:
                defaults[check_id].update(cfg)
            else:
                defaults[check_id] = cfg
    return defaults
```

- [ ] **Step 4: Create `config/quality-thresholds.yaml`** (E1 defaults — 43 checks)

Path: `skills/seo-tech-audit/config/quality-thresholds.yaml`

```yaml
# Default thresholds for E1 (HTML + Network + Schema)
# Each check: hard (boolean) + value (constraint) + optional justification override

# === HTML on-page (H1-H25) ===
H1:  { hard: true,  desc: "HTTP-код = 200" }
H2:  { hard: false, value: { ttfb_max_ms: 800 }, desc: "TTFB" }
H3:  { hard: false, value: { size_max_kb: 150 }, desc: "Размер HTML KB" }
H4:  { hard: true,  desc: "<title> присутствует" }
H5:  { hard: true,  value: { len_min: 30, len_max: 80 }, desc: "<title> длина 30-80" }
H6:  { hard: true,  desc: "<meta description> присутствует" }
H7:  { hard: true,  value: { len_min: 70, len_max: 320 }, desc: "<meta description> длина" }
H8:  { hard: true,  value: { count: 1 }, desc: "Ровно 1× <h1>" }
H9:  { hard: false, desc: "Иерархия H2-H6 (нет скачков уровней)" }
H10: { hard: true,  desc: "<html lang=...> присутствует" }
H11: { hard: true,  desc: "UTF-8 declaration" }
H12: { hard: true,  desc: "<link rel=canonical> валидный" }
H13: { hard: false, desc: "hreflang (если мультиязычно)" }
H14: { hard: true,  desc: "Нет неожиданного meta robots noindex" }
H15: { hard: true,  value: { min_ratio: 0.95 }, desc: "<img alt> ≥95% картинок" }
H16: { hard: false, value: { min_ratio: 0.8 }, desc: "<img loading=lazy> ≥80% below-fold" }
H17: { hard: false, value: { min_ratio: 0.9 }, desc: "<img width/height> для CLS" }
H18: { hard: false, value: { min_ratio: 0.5 }, desc: "WebP/AVIF ≥50% картинок" }
H19: { hard: false, value: { size_max_kb: 10 }, desc: "Inline-CSS ≤10KB" }
H20: { hard: false, value: { max_count: 3 }, desc: "Render-blocking resources ≤3" }
H21: { hard: false, value: { min_count: 5 }, desc: "Внутренних ссылок ≥5" }
H22: { hard: true,  desc: "Внешние ссылки имеют rel=noopener" }
H23: { hard: false, value: { max_ratio: 0.05 }, desc: "Анкоры «click here»/«тут» <5%" }
H24: { hard: false, desc: "tel: links присутствуют" }
H25: { hard: false, desc: "mailto: links если email в тексте" }

# === Network/Infra (N1-N13) ===
N1:  { hard: true,  desc: "SSL валиден" }
N2:  { hard: false, value: { min_days: 30 }, desc: "SSL ≥30 дней" }
N3:  { hard: true,  value: { min_days: 7 }, desc: "SSL ≥7 дней — критично" }
N4:  { hard: false, desc: "HTTP/2 или HTTP/3" }
N5:  { hard: false, value: { min_count: 3 }, desc: "Security headers ≥3 из 4 (HSTS/CSP/XFO/XCTO)" }
N6:  { hard: false, desc: "Server header не раскрывает версию" }
N7:  { hard: true,  desc: "www/non-www → 301 на канонический" }
N8:  { hard: true,  desc: "robots.txt присутствует и валиден" }
N9:  { hard: true,  desc: "sitemap.xml присутствует, валидный XML, упомянут в robots" }
N10: { hard: false, desc: "llms.txt присутствует (AI standard)" }
N11: { hard: true,  desc: "404-страница возвращает 404 (не 200)" }
N12: { hard: false, desc: "404 содержит навигацию (ссылка на главную)" }
N13: { hard: false, desc: "Whois: info-only — возраст/expiry/registrar" }

# === Schema/Microdata (S1-S5) ===
S1: { hard: true,  desc: "Open Graph: og:title/description/image/type/url — все 5" }
S2: { hard: false, value: { width: 1200, height: 630 }, desc: "og:image ≥1200×630 и 200 OK" }
S3: { hard: false, desc: "Twitter Card: card/title/image" }
S4: { hard: false, desc: "Schema.org JSON-LD присутствует и парсится" }
S5: { hard: true,  desc: "Favicon присутствует (32 или 180px)" }
```

- [ ] **Step 5: Smoke test loader**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -c "
import sys; sys.path.insert(0, 'skills/seo-tech-audit/scripts')
from lib.thresholds import load_thresholds
t = load_thresholds()
print(f'Loaded {len(t)} checks; H1={t[\"H1\"]}')
"
```

Expected: `Loaded 43 checks; H1={'hard': True, 'desc': 'HTTP-код = 200'}`

- [ ] **Step 6: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/lib/ skills/seo-tech-audit/config/
git commit -m "feat(s2e-e1): lib/http_client + lib/thresholds + 43-check defaults yaml"
```

---

### Task 3: html_checks.py — 25 проверок + фикстуры + тесты

**Files:**
- Create: `skills/seo-tech-audit/scripts/runners/__init__.py`
- Create: `skills/seo-tech-audit/scripts/runners/html_checks.py`
- Create: `skills/seo-tech-audit/tests/conftest.py`
- Create: `skills/seo-tech-audit/tests/fixtures/good-site.html`
- Create: `skills/seo-tech-audit/tests/fixtures/bad-site.html`
- Create: `skills/seo-tech-audit/tests/test_html_checks.py`

- [ ] **Step 1: Create fixtures**

`skills/seo-tech-audit/tests/fixtures/good-site.html`:

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Эталонный сайт для аудита — 60 символов длиной точно</title>
<meta name="description" content="Это эталонный сайт для тестирования всех 25 HTML-проверок аудита SEO/Tech. Покрывает title, meta, canonical, h1, alt-теги и навигацию.">
<link rel="canonical" href="https://good.example.com/">
<meta property="og:title" content="Good site">
<meta property="og:description" content="Test fixture">
<meta property="og:image" content="https://good.example.com/og.png">
<meta property="og:type" content="website">
<meta property="og:url" content="https://good.example.com/">
<link rel="icon" sizes="32x32" href="/favicon-32.png">
</head>
<body>
<h1>Главный заголовок страницы</h1>
<h2>Раздел 1</h2>
<p>Текст с <a href="/page1">внутренней ссылкой 1</a>,
   <a href="/page2">внутренней 2</a>,
   <a href="/page3">внутренней 3</a>,
   <a href="/page4">внутренней 4</a>,
   <a href="/page5">внутренней 5</a>,
   <a href="https://external.com" rel="noopener">внешней</a>.</p>
<img src="/photo.webp" alt="Описание фото" loading="lazy" width="800" height="600">
<a href="tel:+71234567890">Позвонить</a>
<a href="mailto:info@example.com">Написать</a>
</body>
</html>
```

`skills/seo-tech-audit/tests/fixtures/bad-site.html`:

```html
<!doctype html>
<html>
<head>
<title>X</title>
<meta name="robots" content="noindex">
</head>
<body>
<h1>One H1</h1>
<h1>Duplicate H1</h1>
<img src="/photo.jpg">
<a href="https://external.com">click here</a>
</body>
</html>
```

- [ ] **Step 2: Create runners/__init__.py + conftest.py**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
echo '' > skills/seo-tech-audit/scripts/runners/__init__.py
```

`skills/seo-tech-audit/tests/conftest.py`:

```python
"""Shared pytest fixtures + sys.path setup."""
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def good_html():
    return (FIXTURES / "good-site.html").read_text(encoding="utf-8")


@pytest.fixture
def bad_html():
    return (FIXTURES / "bad-site.html").read_text(encoding="utf-8")
```

- [ ] **Step 3: Write failing test (H1, H4, H5, H8 only — first iteration)**

`skills/seo-tech-audit/tests/test_html_checks.py`:

```python
"""Tests for html_checks runner. Each check has pass+fail case."""
from runners.html_checks import check_html


def _result_by_id(results, check_id):
    return next(r for r in results if r["id"] == check_id)


def test_h1_returns_status_field(good_html):
    results = check_html(good_html, "https://good.example.com/")
    h1 = _result_by_id(results, "H1")
    assert "passed" in h1
    assert "evidence" in h1


def test_h4_title_present_good(good_html):
    results = check_html(good_html, "https://good.example.com/")
    assert _result_by_id(results, "H4")["passed"] is True


def test_h4_title_present_bad():
    html = "<!doctype html><html><head></head><body></body></html>"
    results = check_html(html, "https://x/")
    assert _result_by_id(results, "H4")["passed"] is False


def test_h5_title_length_good(good_html):
    results = check_html(good_html, "https://good.example.com/")
    assert _result_by_id(results, "H5")["passed"] is True


def test_h5_title_length_bad(bad_html):
    # "X" is too short (1 char, need ≥30)
    results = check_html(bad_html, "https://x/")
    assert _result_by_id(results, "H5")["passed"] is False


def test_h8_exactly_one_h1_good(good_html):
    results = check_html(good_html, "https://good.example.com/")
    assert _result_by_id(results, "H8")["passed"] is True


def test_h8_exactly_one_h1_bad_two_h1(bad_html):
    results = check_html(bad_html, "https://x/")
    assert _result_by_id(results, "H8")["passed"] is False
```

- [ ] **Step 4: Run — verify FAIL**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_html_checks.py -v 2>&1 | tail -10
```

Expected: ImportError (runners.html_checks not found).

- [ ] **Step 5: Implement `html_checks.py` — all 25 checks**

Path: `skills/seo-tech-audit/scripts/runners/html_checks.py`

```python
"""HTML on-page checks (H1-H25). HTTP-based, returns list[dict]."""
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

# Allowed status: 200 = pass, other = fail for H1; non-fatal info for others
SOFT_REDIR_OK = {301, 302, 307, 308}


def _result(check_id: str, passed: bool, evidence: str = "", **extra) -> dict:
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_html(html: str, url: str, status_code: int = 200,
               response_time_ms: int = 0, content_size_bytes: int = 0) -> list[dict]:
    """Run 25 HTML on-page checks on parsed HTML.

    Args:
        html: response body
        url: canonical URL (for host comparison)
        status_code: HTTP status from response
        response_time_ms: TTFB ms (from response.elapsed)
        content_size_bytes: len(response.content) for H3
    """
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []

    # H1: HTTP 200
    out.append(_result("H1", status_code == 200, f"status={status_code}"))

    # H2: TTFB
    out.append(_result("H2", response_time_ms <= 800, f"ttfb={response_time_ms}ms"))

    # H3: HTML size ≤150KB
    size_kb = content_size_bytes / 1024
    out.append(_result("H3", size_kb <= 150, f"size={size_kb:.1f}KB"))

    # H4: <title> present
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""
    out.append(_result("H4", bool(title_text), f'title="{title_text[:60]}"'))

    # H5: title length 30-80
    out.append(_result("H5", 30 <= len(title_text) <= 80, f"len={len(title_text)}"))

    # H6: meta description present
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_text = (meta_desc.get("content", "") if meta_desc else "").strip()
    out.append(_result("H6", bool(desc_text), f"desc_len={len(desc_text)}"))

    # H7: description length 70-320
    out.append(_result("H7", 70 <= len(desc_text) <= 320, f"desc_len={len(desc_text)}"))

    # H8: exactly 1× <h1>
    h1_count = len(soup.find_all("h1"))
    out.append(_result("H8", h1_count == 1, f"h1_count={h1_count}"))

    # H9: heading hierarchy (no skips H2→H4 without H3)
    headings = [int(t.name[1]) for t in soup.find_all(re.compile(r"^h[1-6]$"))]
    has_skip = False
    for prev, cur in zip(headings, headings[1:]):
        if cur > prev + 1:
            has_skip = True
            break
    out.append(_result("H9", not has_skip, f"headings={headings[:10]}"))

    # H10: <html lang=...> present
    html_tag = soup.find("html")
    lang = (html_tag.get("lang", "") if html_tag else "").strip()
    out.append(_result("H10", bool(lang), f'lang="{lang}"'))

    # H11: UTF-8 declaration
    charset_tag = soup.find("meta", attrs={"charset": True})
    charset = (charset_tag.get("charset", "") if charset_tag else "").lower()
    is_utf8 = "utf-8" in charset or "utf8" in charset
    if not is_utf8:
        # check http-equiv variant
        equiv = soup.find("meta", attrs={"http-equiv": re.compile(r"content-type", re.I)})
        if equiv:
            content = equiv.get("content", "").lower()
            is_utf8 = "utf-8" in content or "utf8" in content
    out.append(_result("H11", is_utf8, f"charset={charset}"))

    # H12: <link rel=canonical> valid
    canonical = soup.find("link", attrs={"rel": "canonical"})
    canonical_href = (canonical.get("href", "") if canonical else "").strip()
    canonical_valid = bool(canonical_href) and canonical_href.startswith(("http://", "https://"))
    out.append(_result("H12", canonical_valid, f'href="{canonical_href}"'))

    # H13: hreflang (info if any) — soft, pass=true if not multilang
    hreflangs = soup.find_all("link", attrs={"rel": "alternate", "hreflang": True})
    out.append(_result("H13", True, f"hreflang_count={len(hreflangs)}"))

    # H14: meta robots — no unexpected noindex
    robots = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    robots_content = (robots.get("content", "") if robots else "").lower()
    has_noindex = "noindex" in robots_content
    out.append(_result("H14", not has_noindex, f'robots="{robots_content}"'))

    # H15: img alt ≥95%
    imgs = soup.find_all("img")
    img_with_alt = sum(1 for i in imgs if i.get("alt", "").strip())
    ratio_alt = img_with_alt / len(imgs) if imgs else 1.0
    out.append(_result("H15", ratio_alt >= 0.95, f"alt_ratio={ratio_alt:.2f} ({img_with_alt}/{len(imgs)})"))

    # H16: img loading=lazy ≥80% (skip if <3 images — no signal)
    lazy_count = sum(1 for i in imgs if i.get("loading", "").lower() == "lazy")
    ratio_lazy = lazy_count / len(imgs) if imgs else 1.0
    out.append(_result("H16", ratio_lazy >= 0.8 or len(imgs) < 3,
                       f"lazy_ratio={ratio_lazy:.2f} ({lazy_count}/{len(imgs)})"))

    # H17: img width/height ≥90%
    sized = sum(1 for i in imgs if i.get("width") and i.get("height"))
    ratio_sized = sized / len(imgs) if imgs else 1.0
    out.append(_result("H17", ratio_sized >= 0.9, f"sized_ratio={ratio_sized:.2f}"))

    # H18: modern formats (webp/avif) ≥50%
    modern = sum(1 for i in imgs if any(
        (i.get("src", "") or "").lower().endswith(ext) for ext in (".webp", ".avif")
    ))
    ratio_modern = modern / len(imgs) if imgs else 1.0
    out.append(_result("H18", ratio_modern >= 0.5, f"modern_ratio={ratio_modern:.2f}"))

    # H19: inline CSS ≤10KB
    style_tags = soup.find_all("style")
    inline_css_size = sum(len(s.get_text("")) for s in style_tags)
    inline_css_kb = inline_css_size / 1024
    out.append(_result("H19", inline_css_kb <= 10, f"inline_css={inline_css_kb:.1f}KB"))

    # H20: render-blocking resources ≤3 (heuristic: <link rel=stylesheet> in head without media print)
    head = soup.find("head")
    rb = 0
    if head:
        for link in head.find_all("link", attrs={"rel": "stylesheet"}):
            media = (link.get("media", "") or "").lower()
            if "print" not in media:
                rb += 1
    out.append(_result("H20", rb <= 3, f"render_blocking={rb}"))

    # H21: internal links ≥5
    host = urlparse(url).netloc
    internal = external = 0
    noopener_issues = []
    anchor_clicks = anchor_total = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        anchor_text = a.get_text(strip=True).lower()
        if anchor_text:
            anchor_total += 1
            if anchor_text in ("click here", "тут", "сюда", "здесь"):
                anchor_clicks += 1
        parsed = urlparse(href)
        target_host = parsed.netloc
        is_external = target_host and target_host != host
        if is_external:
            external += 1
            rel = (a.get("rel") or [])
            if isinstance(rel, str):
                rel = rel.split()
            if "noopener" not in rel:
                noopener_issues.append(href)
        else:
            internal += 1
    out.append(_result("H21", internal >= 5, f"internal={internal}"))

    # H22: external links → rel=noopener
    out.append(_result("H22", not noopener_issues, f"missing_noopener={len(noopener_issues)}"))

    # H23: «click here»/«тут» <5%
    click_ratio = anchor_clicks / anchor_total if anchor_total else 0
    out.append(_result("H23", click_ratio < 0.05, f"click_ratio={click_ratio:.2%}"))

    # H24: tel: links present
    has_tel = bool(soup.find("a", href=re.compile(r"^tel:")))
    out.append(_result("H24", has_tel, f"has_tel={has_tel}"))

    # H25: mailto: links if email in text
    body_text = soup.get_text(" ")
    has_email_in_text = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", body_text))
    has_mailto = bool(soup.find("a", href=re.compile(r"^mailto:")))
    out.append(_result("H25", has_mailto or not has_email_in_text,
                       f"email_in_text={has_email_in_text} mailto={has_mailto}"))

    return out
```

- [ ] **Step 6: Run — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_html_checks.py -v 2>&1 | tail -15
```

Expected: 7/7 PASS.

- [ ] **Step 7: Add coverage for remaining checks** — extend `test_html_checks.py`:

Append to the test file:

```python
def test_h10_lang_present(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H10")["passed"] is True
    assert _result_by_id(bad, "H10")["passed"] is False


def test_h12_canonical_present(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H12")["passed"] is True
    assert _result_by_id(bad, "H12")["passed"] is False


def test_h14_noindex_detected(bad_html):
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(bad, "H14")["passed"] is False


def test_h15_alt_ratio(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H15")["passed"] is True
    assert _result_by_id(bad, "H15")["passed"] is False


def test_h22_noopener_required(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H22")["passed"] is True
    assert _result_by_id(bad, "H22")["passed"] is False


def test_h23_click_here_anchor(bad_html):
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(bad, "H23")["passed"] is False


def test_returns_25_results(good_html):
    results = check_html(good_html, "https://x/")
    ids = sorted(r["id"] for r in results)
    expected = sorted(f"H{i}" for i in range(1, 26))
    assert ids == expected
```

- [ ] **Step 8: Run all html_checks tests — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_html_checks.py -v 2>&1 | tail -20
```

Expected: 14 PASS.

- [ ] **Step 9: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/runners/ skills/seo-tech-audit/tests/
git commit -m "feat(s2e-e1): html_checks runner (25 checks) + 14 tests + good/bad fixtures"
```

---

### Task 4: network_checks.py — 13 проверок + тесты

**Files:**
- Create: `skills/seo-tech-audit/scripts/runners/network_checks.py`
- Create: `skills/seo-tech-audit/tests/test_network_checks.py`

These checks hit live URLs — tests use `pytest.mark.skipif(no_network)` + mock-based unit tests for parsing.

- [ ] **Step 1: Write failing test (mocked HTTP)**

`skills/seo-tech-audit/tests/test_network_checks.py`:

```python
"""Tests for network_checks runner — mocked HTTP responses."""
from unittest.mock import MagicMock, patch

from runners.network_checks import (
    check_robots_txt,
    check_sitemap_xml,
    check_404_status,
    check_www_redirect,
    check_security_headers,
)


def _make_response(status=200, text="", headers=None, url=""):
    r = MagicMock()
    r.status_code = status
    r.text = text
    r.headers = headers or {}
    r.url = url
    r.history = []
    return r


def test_robots_txt_present_and_valid():
    resp = _make_response(200, "User-agent: *\nDisallow:\nSitemap: https://x/sitemap.xml")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_robots_txt("https://x/")
    assert res["id"] == "N8"
    assert res["passed"] is True


def test_robots_txt_missing():
    resp = _make_response(404, "")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_robots_txt("https://x/")
    assert res["passed"] is False


def test_sitemap_xml_valid_and_in_robots():
    robots_text = "User-agent: *\nSitemap: https://x/sitemap.xml"
    sitemap_resp = _make_response(200,
        '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>https://x/</loc></url></urlset>')
    with patch("runners.network_checks.fetch", return_value=sitemap_resp):
        res = check_sitemap_xml("https://x/", robots_text=robots_text)
    assert res["id"] == "N9"
    assert res["passed"] is True


def test_sitemap_xml_missing_from_robots():
    robots_text = "User-agent: *\nDisallow:"
    sitemap_resp = _make_response(200, '<?xml version="1.0"?><urlset/>')
    with patch("runners.network_checks.fetch", return_value=sitemap_resp):
        res = check_sitemap_xml("https://x/", robots_text=robots_text)
    assert res["passed"] is False
    assert "robots" in res["evidence"].lower()


def test_404_returns_404():
    resp = _make_response(404, "Not found")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_404_status("https://x/")
    assert res["passed"] is True


def test_404_returns_200_is_bad():
    resp = _make_response(200, "Soft 404")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_404_status("https://x/")
    assert res["passed"] is False


def test_www_redirect_to_canonical():
    # Start at www, redirected to non-www
    final = _make_response(200, "", url="https://x.com/")
    history_redir = MagicMock(status_code=301, url="https://www.x.com/")
    final.history = [history_redir]
    with patch("runners.network_checks.fetch", return_value=final):
        res = check_www_redirect("https://x.com/")
    assert res["passed"] is True


def test_security_headers_3_of_4():
    resp = _make_response(200, "", headers={
        "Strict-Transport-Security": "max-age=31536000",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
    })
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_security_headers("https://x/")
    assert res["passed"] is True
    assert "3" in res["evidence"]


def test_security_headers_only_1_fails():
    resp = _make_response(200, "", headers={"X-Frame-Options": "DENY"})
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_security_headers("https://x/")
    assert res["passed"] is False
```

- [ ] **Step 2: Run — verify FAIL**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_network_checks.py -v 2>&1 | tail -10
```

Expected: ImportError.

- [ ] **Step 3: Implement `network_checks.py`**

Path: `skills/seo-tech-audit/scripts/runners/network_checks.py`

```python
"""Network/Infra checks (N1-N13). HTTP/SSL/Whois-based."""
import socket
import ssl
import uuid
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

from lib.http_client import fetch, make_session

SECURITY_HEADER_KEYS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def _result(check_id: str, passed: bool, evidence: str = "", **extra) -> dict:
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_ssl_valid(url: str) -> dict:
    """N1+N3: SSL valid + ≥7 days to expiry."""
    host = urlparse(url).netloc
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days = (not_after - datetime.now(timezone.utc)).days
        return _result("N1", days > 0, f"expires_in_days={days}", days=days)
    except Exception as e:
        return _result("N1", False, f"error={e.__class__.__name__}")


def check_ssl_critical(url: str) -> dict:
    """N3 explicit: ≥7 days. Calls check_ssl_valid for days."""
    base = check_ssl_valid(url)
    days = base.get("days", -1)
    return _result("N3", days >= 7, f"expires_in_days={days}")


def check_ssl_soon_warning(url: str) -> dict:
    """N2 (soft): ≥30 days."""
    base = check_ssl_valid(url)
    days = base.get("days", -1)
    return _result("N2", days >= 30, f"expires_in_days={days}")


def check_http_version(url: str) -> dict:
    """N4: HTTP/2 or HTTP/3."""
    try:
        resp = fetch(url, method="HEAD")
        # requests doesn't expose protocol version directly — check via raw
        version = "HTTP/" + str(resp.raw.version / 10) if hasattr(resp.raw, "version") else "HTTP/?"
        # version 11 = HTTP/1.1, 20 = HTTP/2 (rare to get via requests)
        is_modern = "/2" in version or "/3" in version
        return _result("N4", is_modern, f"version={version}")
    except Exception as e:
        return _result("N4", False, f"error={e.__class__.__name__}")


def check_security_headers(url: str) -> dict:
    """N5: ≥3 of 4 security headers."""
    try:
        resp = fetch(url, method="HEAD")
    except Exception as e:
        return _result("N5", False, f"error={e.__class__.__name__}")
    present = [h for h in SECURITY_HEADER_KEYS if h in resp.headers]
    return _result("N5", len(present) >= 3, f"present={len(present)}/4: {present}")


def check_server_header_no_version(url: str) -> dict:
    """N6: Server header doesn't expose version."""
    try:
        resp = fetch(url, method="HEAD")
    except Exception as e:
        return _result("N6", False, f"error={e.__class__.__name__}")
    server = resp.headers.get("Server", "")
    # heuristic: digits in server string = version disclosure
    has_version = any(c.isdigit() for c in server)
    return _result("N6", not has_version, f'server="{server}"')


def check_www_redirect(url: str) -> dict:
    """N7: www/non-www → 301 to canonical (without loop)."""
    parsed = urlparse(url)
    host = parsed.netloc
    if host.startswith("www."):
        other_host = host[4:]
    else:
        other_host = "www." + host
    other_url = parsed._replace(netloc=other_host).geturl()
    try:
        resp = fetch(other_url)
    except Exception as e:
        return _result("N7", False, f"error={e.__class__.__name__}")
    # Should land on canonical (any 200 after redirect is OK)
    final_host = urlparse(resp.url).netloc
    redirected_correctly = (final_host == host and len(resp.history) > 0)
    return _result("N7", redirected_correctly,
                   f"history_len={len(resp.history)} final={final_host}")


def check_robots_txt(url: str) -> dict:
    """N8: robots.txt exists and parses."""
    robots_url = urljoin(url, "/robots.txt")
    try:
        resp = fetch(robots_url)
    except Exception as e:
        return _result("N8", False, f"error={e.__class__.__name__}")
    if resp.status_code != 200:
        return _result("N8", False, f"status={resp.status_code}")
    # minimal validity: contains "User-agent" directive
    valid = "user-agent" in resp.text.lower()
    return _result("N8", valid, f"size={len(resp.text)}B valid={valid}",
                   robots_text=resp.text)


def check_sitemap_xml(url: str, robots_text: str = "") -> dict:
    """N9: sitemap.xml exists, valid XML, referenced in robots.txt."""
    sitemap_url = urljoin(url, "/sitemap.xml")
    try:
        resp = fetch(sitemap_url)
    except Exception as e:
        return _result("N9", False, f"error={e.__class__.__name__}")
    if resp.status_code != 200:
        return _result("N9", False, f"status={resp.status_code}")
    try:
        ET.fromstring(resp.text)
    except ET.ParseError as e:
        return _result("N9", False, f"invalid XML: {e}")
    in_robots = "sitemap" in robots_text.lower() and "sitemap.xml" in robots_text.lower()
    return _result("N9", in_robots,
                   f"valid_xml=true in_robots={in_robots}",
                   in_robots=in_robots)


def check_llms_txt(url: str) -> dict:
    """N10: llms.txt (AI standard)."""
    try:
        resp = fetch(urljoin(url, "/llms.txt"))
    except Exception:
        return _result("N10", False, "fetch error")
    return _result("N10", resp.status_code == 200, f"status={resp.status_code}")


def check_404_status(url: str) -> dict:
    """N11: random /404-test-xyz returns 404 (not soft 200)."""
    test_url = urljoin(url, f"/test-404-{uuid.uuid4().hex[:8]}")
    try:
        resp = fetch(test_url)
    except Exception as e:
        return _result("N11", False, f"error={e.__class__.__name__}")
    return _result("N11", resp.status_code == 404, f"status={resp.status_code}")


def check_404_has_nav(url: str) -> dict:
    """N12: 404 page contains navigation (link to home)."""
    test_url = urljoin(url, f"/test-404-{uuid.uuid4().hex[:8]}")
    try:
        resp = fetch(test_url)
    except Exception:
        return _result("N12", False, "fetch error")
    has_home_link = bool(resp.text) and ('href="/"' in resp.text or "href='/'" in resp.text)
    return _result("N12", has_home_link, f"has_home_link={has_home_link}")


def check_whois(url: str) -> dict:
    """N13: Whois — info-only. Always passes; embeds data."""
    try:
        import whois  # python-whois
    except ImportError:
        return _result("N13", True, "python-whois not installed (info skipped)")
    host = urlparse(url).netloc.replace("www.", "")
    try:
        w = whois.whois(host)
        created = str(w.creation_date)[:10] if w.creation_date else "?"
        expires = str(w.expiration_date)[:10] if w.expiration_date else "?"
        return _result("N13", True, f"created={created} expires={expires}")
    except Exception as e:
        return _result("N13", True, f"whois error: {e.__class__.__name__}")


def run_all(url: str) -> list[dict]:
    """Run all N1-N13. Order matters: robots.txt result is reused for sitemap."""
    out: list[dict] = []
    out.append(check_ssl_valid(url))
    out.append(check_ssl_soon_warning(url))
    out.append(check_ssl_critical(url))
    out.append(check_http_version(url))
    out.append(check_security_headers(url))
    out.append(check_server_header_no_version(url))
    out.append(check_www_redirect(url))
    robots_res = check_robots_txt(url)
    out.append(robots_res)
    out.append(check_sitemap_xml(url, robots_text=robots_res.get("robots_text", "")))
    out.append(check_llms_txt(url))
    out.append(check_404_status(url))
    out.append(check_404_has_nav(url))
    out.append(check_whois(url))
    return out
```

- [ ] **Step 4: Run tests — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_network_checks.py -v 2>&1 | tail -15
```

Expected: 9 PASS.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/runners/network_checks.py \
        skills/seo-tech-audit/tests/test_network_checks.py
git commit -m "feat(s2e-e1): network_checks runner (13 checks) + 9 mocked tests"
```

---

### Task 5: schema_checks.py — 5 проверок + тесты

**Files:**
- Create: `skills/seo-tech-audit/scripts/runners/schema_checks.py`
- Create: `skills/seo-tech-audit/tests/test_schema_checks.py`

- [ ] **Step 1: Write failing test**

`skills/seo-tech-audit/tests/test_schema_checks.py`:

```python
"""Tests for schema_checks runner — Open Graph, Twitter Card, JSON-LD, favicon."""
from runners.schema_checks import check_schema


def _by(results, check_id):
    return next(r for r in results if r["id"] == check_id)


def test_s1_og_all_five_present(good_html):
    results = check_schema(good_html, "https://x/")
    assert _by(results, "S1")["passed"] is True


def test_s1_og_missing_image_fails():
    html = """<html><head>
    <meta property="og:title" content="x">
    <meta property="og:description" content="x">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://x/">
    </head><body></body></html>"""
    results = check_schema(html, "https://x/")
    s1 = _by(results, "S1")
    assert s1["passed"] is False
    assert "og:image" in s1["evidence"]


def test_s3_twitter_card_absent_is_soft_fail():
    html = "<html><head><title>x</title></head><body></body></html>"
    results = check_schema(html, "https://x/")
    assert _by(results, "S3")["passed"] is False


def test_s4_json_ld_present():
    html = """<html><head>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"X"}</script>
    </head><body></body></html>"""
    results = check_schema(html, "https://x/")
    assert _by(results, "S4")["passed"] is True


def test_s4_json_ld_invalid_fails():
    html = """<html><head>
    <script type="application/ld+json">{invalid json</script>
    </head><body></body></html>"""
    results = check_schema(html, "https://x/")
    assert _by(results, "S4")["passed"] is False


def test_s5_favicon_present(good_html):
    results = check_schema(good_html, "https://x/")
    assert _by(results, "S5")["passed"] is True


def test_s5_favicon_missing_fails():
    html = "<html><head><title>x</title></head><body></body></html>"
    results = check_schema(html, "https://x/")
    assert _by(results, "S5")["passed"] is False


def test_returns_5_results(good_html):
    results = check_schema(good_html, "https://x/")
    ids = sorted(r["id"] for r in results)
    assert ids == ["S1", "S2", "S3", "S4", "S5"]
```

- [ ] **Step 2: Run — verify FAIL**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_schema_checks.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement `schema_checks.py`**

Path: `skills/seo-tech-audit/scripts/runners/schema_checks.py`

```python
"""Schema/microdata checks (S1-S5)."""
import json

from bs4 import BeautifulSoup

REQUIRED_OG = {"og:title", "og:description", "og:image", "og:type", "og:url"}
REQUIRED_TWITTER = {"twitter:card", "twitter:title", "twitter:image"}


def _result(check_id: str, passed: bool, evidence: str = "", **extra) -> dict:
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_schema(html: str, url: str) -> list[dict]:
    """Run 5 schema checks on HTML."""
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []

    # S1: OG — all 5 required
    og_props = {m.get("property", ""): (m.get("content", "") or "").strip()
                for m in soup.find_all("meta", attrs={"property": True})}
    present = {k for k in REQUIRED_OG if og_props.get(k)}
    missing = REQUIRED_OG - present
    out.append(_result("S1", not missing,
                       f"present={len(present)}/5 missing={sorted(missing) if missing else 'none'}",
                       og_props=og_props))

    # S2: og:image valid (URL 200, ≥1200×630) — without HTTP check, we only verify URL format
    # Full image validation needs HTTP HEAD + image dimensions — soft check in E1.
    og_image_url = og_props.get("og:image", "")
    out.append(_result("S2", bool(og_image_url) and og_image_url.startswith(("http://", "https://")),
                       f'url="{og_image_url}"'))

    # S3: Twitter Card — at least card/title/image
    tw_names = {m.get("name", ""): (m.get("content", "") or "").strip()
                for m in soup.find_all("meta", attrs={"name": True})
                if (m.get("name", "") or "").startswith("twitter:")}
    tw_present = {k for k in REQUIRED_TWITTER if tw_names.get(k)}
    tw_missing = REQUIRED_TWITTER - tw_present
    out.append(_result("S3", not tw_missing,
                       f"present={len(tw_present)}/3 missing={sorted(tw_missing) if tw_missing else 'none'}"))

    # S4: JSON-LD present and parses
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    parsed_count = 0
    parse_errors = []
    for s in scripts:
        try:
            json.loads(s.get_text(""))
            parsed_count += 1
        except json.JSONDecodeError as e:
            parse_errors.append(str(e)[:80])
    out.append(_result("S4", parsed_count > 0,
                       f"valid_json_ld={parsed_count}/{len(scripts)} errors={parse_errors[:2]}"))

    # S5: Favicon present (any size)
    favicon = soup.find("link", attrs={"rel": lambda r: r and "icon" in r.lower() if isinstance(r, str) else (
        any("icon" in x.lower() for x in (r or []))
    )})
    out.append(_result("S5", bool(favicon),
                       f"href={(favicon.get('href','') if favicon else '')}"))

    return out
```

- [ ] **Step 4: Run — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_schema_checks.py -v 2>&1 | tail -15
```

Expected: 8 PASS.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/runners/schema_checks.py \
        skills/seo-tech-audit/tests/test_schema_checks.py
git commit -m "feat(s2e-e1): schema_checks runner (5 checks) + 8 tests"
```

---

### Task 6: lib/site_discovery.py + tests

**Files:**
- Create: `skills/seo-tech-audit/scripts/lib/site_discovery.py`
- Create: `skills/seo-tech-audit/tests/fixtures/state-multisite.yaml`
- Create: `skills/seo-tech-audit/tests/fixtures/state-single.yaml`
- Create: `skills/seo-tech-audit/tests/test_site_discovery.py`

- [ ] **Step 1: Create fixtures**

`skills/seo-tech-audit/tests/fixtures/state-multisite.yaml`:

```yaml
project:
  slug: ailexi
  primary_domain: ailexi.ru
multisite: true
audience_segments:
  - slug: russian
    host: russian.ailexi.ru
    blog_id: 2
  - slug: dubai-avto-liza
    host: dubai-avto-liza.ailexi.ru
    blog_id: 3
stages:
  09_deploy: {status: approved}
```

`skills/seo-tech-audit/tests/fixtures/state-single.yaml`:

```yaml
project:
  slug: simple-project
  primary_domain: simple-project.example.com
multisite: false
stages:
  09_deploy: {status: approved}
```

- [ ] **Step 2: Write failing test**

`skills/seo-tech-audit/tests/test_site_discovery.py`:

```python
"""Tests for site_discovery — parsing .landing-state.yaml for hosts."""
from pathlib import Path
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
    import pytest
    with pytest.raises(FileNotFoundError):
        discover_hosts(FIXTURES / "nonexistent.yaml")


def test_filter_segment(tmp_path):
    # Multisite + --site filter
    hosts = discover_hosts(FIXTURES / "state-multisite.yaml",
                            filter_host="dubai-avto-liza.ailexi.ru")
    assert hosts == ["https://dubai-avto-liza.ailexi.ru"]


def test_filter_unknown_segment_raises():
    import pytest
    with pytest.raises(ValueError):
        discover_hosts(FIXTURES / "state-multisite.yaml", filter_host="nonexistent.com")
```

- [ ] **Step 3: Run — verify FAIL**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_site_discovery.py -v 2>&1 | tail -10
```

- [ ] **Step 4: Implement `lib/site_discovery.py`**

Path: `skills/seo-tech-audit/scripts/lib/site_discovery.py`

```python
"""Discover hosts to audit from .landing-state.yaml."""
from pathlib import Path
import yaml


def discover_hosts(state_path: Path, filter_host: str | None = None) -> list[str]:
    """Return list of https://<host> URLs to audit.

    - multisite=true → primary_domain + each segment.host
    - multisite=false (or missing) → only primary_domain
    - filter_host → return only matching host (with leading https://); raise ValueError if unknown
    """
    state_path = Path(state_path)
    if not state_path.exists():
        raise FileNotFoundError(f"state file not found: {state_path}")

    data = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}

    primary = (data.get("project") or {}).get("primary_domain", "").strip()
    if not primary:
        raise ValueError(f"primary_domain missing in {state_path}")

    is_multisite = bool(data.get("multisite"))
    hosts = [primary]
    if is_multisite:
        for seg in data.get("audience_segments") or []:
            host = (seg.get("host") or "").strip()
            if host and host not in hosts:
                hosts.append(host)

    if filter_host:
        matched = [h for h in hosts if h == filter_host]
        if not matched:
            raise ValueError(f"host {filter_host!r} not found in state. Known: {hosts}")
        hosts = matched

    return [f"https://{h}" for h in hosts]
```

- [ ] **Step 5: Run — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_site_discovery.py -v 2>&1 | tail -10
```

Expected: 5 PASS.

- [ ] **Step 6: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/lib/site_discovery.py \
        skills/seo-tech-audit/tests/fixtures/state-*.yaml \
        skills/seo-tech-audit/tests/test_site_discovery.py
git commit -m "feat(s2e-e1): site_discovery — multisite host enumeration from state.yaml"
```

---

### Task 7: lib/report.py — Markdown + JSON renderer

**Files:**
- Create: `skills/seo-tech-audit/scripts/lib/report.py`
- Create: `skills/seo-tech-audit/tests/test_report.py`

- [ ] **Step 1: Write failing test**

`skills/seo-tech-audit/tests/test_report.py`:

```python
"""Tests for report.py — Markdown + JSON serialization."""
from lib.report import build_site_report, build_aggregate_report, render_markdown


SAMPLE_RESULTS = [
    {"id": "H1", "passed": True, "evidence": "status=200"},
    {"id": "H4", "passed": False, "evidence": "title=\"\""},
    {"id": "N8", "passed": True, "evidence": "size=512B"},
]

THRESHOLDS = {
    "H1": {"hard": True, "desc": "HTTP 200"},
    "H4": {"hard": True, "desc": "<title> present"},
    "N8": {"hard": True, "desc": "robots.txt"},
}


def test_site_report_structure():
    rep = build_site_report("https://x/", SAMPLE_RESULTS, THRESHOLDS)
    assert rep["host"] == "https://x/"
    assert rep["hard_total"] == 3
    assert rep["hard_passed"] == 2  # H1 + N8 pass; H4 fails
    assert rep["all_total"] == 3
    assert rep["passed"] is False  # 1 hard fail


def test_aggregate_report_combines_sites():
    a = build_site_report("https://a/", SAMPLE_RESULTS, THRESHOLDS)
    b = build_site_report("https://b/", [
        {"id": "H1", "passed": True, "evidence": ""},
        {"id": "H4", "passed": True, "evidence": ""},
        {"id": "N8", "passed": True, "evidence": ""},
    ], THRESHOLDS)
    agg = build_aggregate_report([a, b])
    assert agg["total_sites"] == 2
    assert agg["sites_passed"] == 1
    assert agg["overall_passed"] is False


def test_markdown_contains_summary_table():
    rep = build_site_report("https://x/", SAMPLE_RESULTS, THRESHOLDS)
    md = render_markdown([rep])
    assert "# Audit Report" in md
    assert "https://x/" in md
    assert "H4" in md  # failed check shown
    assert "❌" in md or "FAIL" in md


def test_markdown_multisite_aggregate():
    a = build_site_report("https://a/", SAMPLE_RESULTS, THRESHOLDS)
    b = build_site_report("https://b/", SAMPLE_RESULTS, THRESHOLDS)
    md = render_markdown([a, b])
    assert "https://a/" in md
    assert "https://b/" in md
```

- [ ] **Step 2: Run — verify FAIL**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_report.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement `lib/report.py`**

Path: `skills/seo-tech-audit/scripts/lib/report.py`

```python
"""Build site + aggregate reports; render Markdown."""
from datetime import datetime


def build_site_report(host: str, results: list[dict], thresholds: dict) -> dict:
    """Aggregate one site's results with hard/soft split."""
    hard_total = hard_passed = soft_total = soft_passed = 0
    fails: list[dict] = []
    for r in results:
        check_id = r["id"]
        threshold = thresholds.get(check_id, {})
        is_hard = bool(threshold.get("hard", False))
        if is_hard:
            hard_total += 1
            if r["passed"]:
                hard_passed += 1
            else:
                fails.append({**r, "desc": threshold.get("desc", ""), "severity": "hard"})
        else:
            soft_total += 1
            if r["passed"]:
                soft_passed += 1
            elif not r["passed"]:
                fails.append({**r, "desc": threshold.get("desc", ""), "severity": "soft"})
    return {
        "host": host,
        "checked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "all_total": len(results),
        "hard_total": hard_total,
        "hard_passed": hard_passed,
        "soft_total": soft_total,
        "soft_passed": soft_passed,
        "passed": hard_passed == hard_total,  # hard-gate determines pass/fail
        "results": results,
        "failures": fails,
    }


def build_aggregate_report(site_reports: list[dict]) -> dict:
    """Combine per-site reports into an aggregate."""
    total = len(site_reports)
    passed = sum(1 for s in site_reports if s["passed"])
    return {
        "checked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "total_sites": total,
        "sites_passed": passed,
        "overall_passed": passed == total,
        "sites": site_reports,
    }


def render_markdown(site_reports: list[dict]) -> str:
    """Render Markdown report covering one OR many sites."""
    lines: list[str] = []
    lines.append("# Audit Report")
    lines.append("")
    lines.append(f"**Date:** {datetime.utcnow().isoformat(timespec='seconds')}Z")
    lines.append("")

    if len(site_reports) > 1:
        agg = build_aggregate_report(site_reports)
        status = "✅ PASS" if agg["overall_passed"] else "❌ FAIL"
        lines.append(f"**Overall:** {status} ({agg['sites_passed']}/{agg['total_sites']} sites passed)")
        lines.append("")
        lines.append("## Сводная таблица")
        lines.append("")
        lines.append("| Host | Status | Hard gates | Soft gates |")
        lines.append("|---|---|---|---|")
        for s in site_reports:
            icon = "✅" if s["passed"] else "❌"
            lines.append(f"| {s['host']} | {icon} | {s['hard_passed']}/{s['hard_total']} | {s['soft_passed']}/{s['soft_total']} |")
        lines.append("")

    for s in site_reports:
        status = "✅ PASS" if s["passed"] else "❌ FAIL"
        lines.append(f"## {s['host']} — {status}")
        lines.append("")
        lines.append(f"- Hard gates: **{s['hard_passed']}/{s['hard_total']}**")
        lines.append(f"- Soft gates: {s['soft_passed']}/{s['soft_total']}")
        lines.append("")
        if s["failures"]:
            lines.append("### Failed checks")
            lines.append("")
            lines.append("| ID | Severity | Desc | Evidence |")
            lines.append("|---|---|---|---|")
            for f in s["failures"]:
                sev_icon = "🔴" if f["severity"] == "hard" else "🟡"
                ev = (f.get("evidence", "") or "")[:120].replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {f['id']} | {sev_icon} {f['severity']} | {f.get('desc', '')} | {ev} |")
            lines.append("")
        else:
            lines.append("Все проверки пройдены.")
            lines.append("")

    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Run — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_report.py -v 2>&1 | tail -10
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/lib/report.py skills/seo-tech-audit/tests/test_report.py
git commit -m "feat(s2e-e1): report.py — Markdown+JSON renderer + 4 tests"
```

---

### Task 8: run-audit.py CLI orchestrator + integration test

**Files:**
- Create: `skills/seo-tech-audit/scripts/run-audit.py`
- Create: `skills/seo-tech-audit/tests/test_run_audit_integration.py`

- [ ] **Step 1: Write integration test**

`skills/seo-tech-audit/tests/test_run_audit_integration.py`:

```python
"""Integration test: run-audit.py CLI end-to-end with mocked HTTP."""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
RUN_AUDIT = SKILL_ROOT / "scripts" / "run-audit.py"
FIXTURES = SKILL_ROOT / "tests" / "fixtures"


def test_cli_help():
    r = subprocess.run([sys.executable, str(RUN_AUDIT), "--help"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "--project" in r.stdout
    assert "--url" in r.stdout
    assert "--site" in r.stdout


def test_cli_url_mode_produces_report(tmp_path):
    """--url mode hits real network; mark as live test, skip if unreachable.
    We use example.com which is always up.
    """
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--url", "https://example.com",
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=60,
    )
    # exit code may be 0 or 1 depending on example.com SEO state
    assert r.returncode in (0, 1), f"unexpected exit: {r.returncode}, stderr={r.stderr}"
    assert (out_dir / "audit-report.json").exists()
    assert (out_dir / "audit-report.md").exists()
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert "sites" in data
    assert len(data["sites"]) == 1
    assert data["sites"][0]["host"] == "https://example.com"


def test_cli_project_with_multisite(tmp_path):
    """--project mode with multisite state.yaml runs all hosts."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / ".landing-state.yaml").write_text(
        (FIXTURES / "state-single.yaml").read_text(encoding="utf-8"),
        encoding="utf-8"
    )
    out_dir = project_dir / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--project", str(project_dir),
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    # primary_domain in single-site fixture is "simple-project.example.com" — unreachable.
    # Audit should still produce a report (with all-fail), not crash.
    assert r.returncode in (1, 2), f"expected non-zero for unreachable host, got {r.returncode}"
    if (out_dir / "audit-report.json").exists():
        data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
        assert data["sites"][0]["host"] == "https://simple-project.example.com"
```

- [ ] **Step 2: Run — verify FAIL**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_run_audit_integration.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement `run-audit.py`**

Path: `skills/seo-tech-audit/scripts/run-audit.py`

```python
#!/usr/bin/env python3
"""seo-tech-audit CLI orchestrator (E1).

Usage:
    run-audit.py --url <url>                 # single ad-hoc URL
    run-audit.py --project <dir>             # auto-discover hosts from .landing-state.yaml
    run-audit.py --project <dir> --site <host>   # only one host of a multisite project
    --out <dir>   override output dir (default: <project>/11_QA or ./11_QA)
    --json        suppress Markdown rendering (JSON only)

Exit codes:
    0 = all hard-gates pass on all sites
    1 = at least one hard-gate failed
    2 = system error (project not found, etc.)
"""
import argparse
import json
import sys
from pathlib import Path

# Make `lib.*` and `runners.*` importable
SKILL_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_SCRIPTS))

from lib.http_client import fetch
from lib.report import build_aggregate_report, build_site_report, render_markdown
from lib.site_discovery import discover_hosts
from lib.thresholds import load_thresholds
from runners.html_checks import check_html
from runners.network_checks import run_all as run_network_checks
from runners.schema_checks import check_schema


def audit_one_url(url: str) -> list[dict]:
    """Fetch URL once, run all 3 runner modules."""
    results: list[dict] = []
    try:
        resp = fetch(url)
        html = resp.text
        elapsed_ms = int(resp.elapsed.total_seconds() * 1000) if resp.elapsed else 0
        size = len(resp.content) if resp.content else 0
        results.extend(check_html(html, url,
                                   status_code=resp.status_code,
                                   response_time_ms=elapsed_ms,
                                   content_size_bytes=size))
        results.extend(check_schema(html, url))
    except Exception as e:
        # network total failure — mark H1 as fail and proceed with network checks
        results.append({"id": "H1", "passed": False, "evidence": f"fetch_error: {e}"})
    # network checks always run (they hit different endpoints)
    results.extend(run_network_checks(url))
    return results


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="run-audit.py")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--project", help="project root with .landing-state.yaml")
    g.add_argument("--url", help="single ad-hoc URL to audit")
    p.add_argument("--site", help="filter: only this host (with --project)")
    p.add_argument("--out", help="output directory (default: <project>/11_QA or ./11_QA)")
    p.add_argument("--json", action="store_true", help="JSON only, skip Markdown")
    args = p.parse_args(argv[1:])

    # Resolve hosts
    if args.url:
        hosts = [args.url.rstrip("/")]
        out_root = Path(args.out) if args.out else Path("./11_QA")
    else:
        project = Path(args.project)
        state_path = project / ".landing-state.yaml"
        if not state_path.exists():
            print(f"ERROR: state file not found: {state_path}", file=sys.stderr)
            return 2
        try:
            hosts = discover_hosts(state_path, filter_host=args.site)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        out_root = Path(args.out) if args.out else (project / "11_QA")

    out_root.mkdir(parents=True, exist_ok=True)
    per_site_dir = out_root / "per-site"
    per_site_dir.mkdir(exist_ok=True)

    # Load thresholds
    thresholds = load_thresholds()

    # Audit each host
    site_reports: list[dict] = []
    for host in hosts:
        print(f"▶ Auditing {host}", flush=True)
        results = audit_one_url(host)
        rep = build_site_report(host, results, thresholds)
        site_reports.append(rep)

        # Per-site JSON + MD
        host_key = host.replace("https://", "").replace("http://", "").rstrip("/")
        (per_site_dir / f"{host_key}.json").write_text(
            json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        if not args.json:
            single_md = render_markdown([rep])
            (per_site_dir / f"{host_key}.md").write_text(single_md, encoding="utf-8")
        print(f"  {'✅' if rep['passed'] else '❌'} hard={rep['hard_passed']}/{rep['hard_total']} "
              f"soft={rep['soft_passed']}/{rep['soft_total']}", flush=True)

    # Aggregate
    agg = build_aggregate_report(site_reports)
    (out_root / "audit-report.json").write_text(
        json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.json:
        md = render_markdown(site_reports)
        (out_root / "audit-report.md").write_text(md, encoding="utf-8")

    print(f"\n{'✅' if agg['overall_passed'] else '❌'} "
          f"{agg['sites_passed']}/{agg['total_sites']} sites passed", flush=True)
    print(f"Reports: {out_root}", flush=True)

    return 0 if agg["overall_passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run integration tests — verify PASS**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/test_run_audit_integration.py -v 2>&1 | tail -10
```

Expected: 3 PASS (test_cli_url_mode_produces_report needs internet to example.com — mark as `pytest.mark.network` if it fails locally, but should pass in normal env).

- [ ] **Step 5: Manual smoke on dubai-avto-liza**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python skills/seo-tech-audit/scripts/run-audit.py \
    --url https://dubai-avto-liza.ailexi.ru \
    --out /tmp/audit-test
cat /tmp/audit-test/audit-report.md | head -40
```

Expected: report rendered, ≥1 hard-gate (likely H1=pass, H5=maybe fail, N8/N9 depending on robots/sitemap existence).

- [ ] **Step 6: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add skills/seo-tech-audit/scripts/run-audit.py \
        skills/seo-tech-audit/tests/test_run_audit_integration.py
git commit -m "feat(s2e-e1): run-audit.py CLI — multisite orchestrator + integration tests"
```

---

### Task 9: /landing-audit slash-command

**Files:**
- Create: `.claude/commands/landing-audit.md`

- [ ] **Step 1: Create command file**

Path: `.claude/commands/landing-audit.md`

```markdown
---
description: SEO/Tech аудит лендинга — 43 HTTP-проверки (HTML+Network+Schema). Multisite-aware. Stage-11 hard-gate.
---

# /landing-audit

Запускает `skills/seo-tech-audit/scripts/run-audit.py` для проверки задеплоенного лендинга.

## Использование

```
/landing-audit                                  # audit текущего проекта (cwd)
/landing-audit <project-slug>                   # audit любого проекта по slug в ~/Lendings/
/landing-audit <url>                            # ad-hoc URL (без проекта)
/landing-audit <project-slug> --site <host>     # один поддомен мультисайта
```

## Что делает

1. Определяет режим:
   - URL начинается с `http(s)://` → `--url` (ad-hoc)
   - Иначе → ищет `~/Lendings/<arg>` или текущий cwd → `--project`
2. Запускает `run-audit.py` с обнаруженными аргументами.
3. Пишет отчёт в `<project>/11_QA/audit-report.{md,json}` + `per-site/<host>.{md,json}`.
4. Возвращает exit-code 0 (все hard-gates ✓) / 1 (есть fails) / 2 (system error).
5. Печатает в чат сводку: какие сайты прошли, какие — нет, краткий список failed hard-gates.

## Покрытие (E1)

43 проверки за один прогон по каждому поддомену:
- HTML on-page (25): title/meta/h1/canonical/lang/img-alt/anchors
- Network/Infra (13): SSL, redirects, robots.txt, sitemap.xml, 404, Whois
- Schema (5): Open Graph, Twitter Card, JSON-LD, favicon

Не включено в E1 (будет в E2-E4): Lighthouse Web Vitals (LCP/CLS/INP), crawler битых ссылок, content metrics RU (тошнота/Flesch), AI readiness, auto-fix loop.

## Stage-11 gate

`config/stage-gates.yaml::11_qa.hard_checks::seo_audit_pass` — этот же скрипт.
Stage-11 не закрывается пока есть hard-gate failures.

## Зависимости

- Python 3.10+, `requests`, `beautifulsoup4`, `lxml`, `PyYAML`, `python-whois` (опционально, для N13)
```

- [ ] **Step 2: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add .claude/commands/landing-audit.md
git commit -m "feat(s2e-e1): /landing-audit slash-command"
```

---

### Task 10: Stage-11 gate integration

**Files:**
- Modify: `config/stage-gates.yaml`

- [ ] **Step 1: Find stage-11 section**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
grep -nE "^[[:space:]]+(11_qa|10_qa):" config/stage-gates.yaml
```

Note the exact stage key (likely `10_qa` or `11_qa`).

- [ ] **Step 2: Add seo_audit_pass hard_check**

Inside the QA stage section (probably `11_qa:` or `10_qa:` block), add to `hard_checks:`:

```yaml
    - id: seo_audit_pass
      title: "SEO/Tech audit — 43 проверки (HTML+Network+Schema)"
      type: script
      command: "python skills/seo-tech-audit/scripts/run-audit.py --project {project} --json"
      fix_hint: "Открой 11_QA/audit-report.md — список failed checks с описанием. Чтобы запустить руками: python skills/seo-tech-audit/scripts/run-audit.py --project <path>"
```

If existing entries use a different format (e.g. `prompt:` field), match that — keep the new entry consistent.

- [ ] **Step 3: Verify YAML still parses**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -c "import yaml; print(yaml.safe_load(open('config/stage-gates.yaml')))" >/dev/null
echo "yaml OK"
```

- [ ] **Step 4: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add config/stage-gates.yaml
git commit -m "feat(s2e-e1): stage-11 gate — seo_audit_pass hard_check"
```

---

### Task 11: CLAUDE.md docs

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Find latest existing section**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
grep -n "^### B2 \|^## " CLAUDE.md | tail -5
```

Find where to insert (after B2 section, before any closing matter).

- [ ] **Step 2: Append S2-E section**

After the B2 section's last line, append:

```markdown

### S2-E.1 — SEO/Tech Audit Skill (2026-05-22)

Skill `seo-tech-audit` + slash-команда `/landing-audit` запускают аудит задеплоенного лендинга — 43 HTTP-проверки (HTML on-page, network/infra, schema). Multisite-aware: auto-discovery поддоменов из `.landing-state.yaml::audience_segments`.

**Что проверяется (E1):**
- HTML (25): title/meta/h1/canonical/lang/img-alt/anchor-noopener
- Network (13): SSL валиден ≥7 дней, www→non-www 301, robots.txt + sitemap.xml + ссылка из robots, 404 не soft-200, security headers ≥3/4, Whois (info)
- Schema (5): Open Graph 5 свойств, Twitter Card, JSON-LD парсится, favicon

**Что НЕ в E1 (отдельные итерации):**
- Lighthouse Web Vitals (LCP/CLS/INP) — E2
- Crawler битых ссылок — E2
- Content metrics RU (тошнота/Flesch/водность) — E3
- AI readiness (llms.txt extended) + auto-fix loop в orchestrator — E4

**Использование:**
```bash
/landing-audit dubai-avto-liza             # все поддомены проекта
/landing-audit https://example.com         # ad-hoc URL
/landing-audit dubai-avto-liza --site russian.ailexi.ru
```

**Output:**
```
<project>/11_QA/
├── audit-report.md       # сводный (все поддомены, таблица)
├── audit-report.json     # машино-читаемый
└── per-site/
    └── <host>.{md,json}
```

**Stage-11 gate:** `seo_audit_pass` в `config/stage-gates.yaml`. Stage-11 не закрывается пока hard-gate fails на любом поддомене.

**Pure Python:** без зависимости от Lighthouse/Node (`requests`+`beautifulsoup4`+`lxml`+`python-whois`).

См. [spec §13](docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md) и [plan E1](docs/superpowers/plans/2026-05-22-s2e-e1-seo-audit-skill-plan.md).
```

- [ ] **Step 3: Commit**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
git add CLAUDE.md
git commit -m "docs(s2e-e1): CLAUDE.md секция SEO/Tech Audit Skill"
```

---

### Task 12: Full regression + merge to main

- [ ] **Step 1: Full test sweep**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m pytest skills/seo-tech-audit/tests/ -v 2>&1 | tail -10
```

Expected: ≥40 tests (14 html + 9 network + 8 schema + 5 site_discovery + 4 report + 3 integration), 0 failures.

- [ ] **Step 2: Lint check**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python -m py_compile skills/seo-tech-audit/scripts/run-audit.py \
    skills/seo-tech-audit/scripts/runners/*.py \
    skills/seo-tech-audit/scripts/lib/*.py
echo "all compile clean"
```

- [ ] **Step 3: Smoke on dubai-avto-liza**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-audit-skill
python skills/seo-tech-audit/scripts/run-audit.py \
    --project D:/AI_TEAMS/Lendings/dubai-avto-liza 2>&1 | tail -15
```

Expected: 2 hosts audited (ailexi.ru + dubai-avto-liza.ailexi.ru), report written to `D:/AI_TEAMS/Lendings/dubai-avto-liza/11_QA/`.

- [ ] **Step 4: Merge to main**

```bash
cd D:/AI_TEAMS/landing_system
git checkout main
git merge --no-ff s2e-audit-skill -m "merge: S2-E.1 — SEO/Tech Audit Skill (43 checks, multisite)"
git push origin main
```

---

## Self-Review

**Spec coverage (§13.2 acceptance E1):**
- ✅ Каркас skill `seo-tech-audit/` — Task 1
- ✅ `run-audit.py` orchestrator — Task 8
- ✅ `html_checks.py` (25 checks H1-H25) — Task 3
- ✅ `network_checks.py` (13 checks N1-N13) — Task 4
- ✅ `schema_checks.py` (5 checks S1-S5) — Task 5
- ✅ Markdown + JSON отчёт — Task 7
- ✅ Multisite batch-mode (discovery + per-site + aggregate) — Task 6 + 8
- ✅ `/landing-audit` slash-команда — Task 9
- ✅ Stage-11 gate integration — Task 10
- ✅ Pure Python (без Lighthouse/Node) — соблюдено
- ✅ exit 0/1/2 корректно — Task 8 (run-audit.py)
- ✅ Unit-тесты good/bad fixtures — Tasks 3-7
- ✅ Integration test e2e — Task 8

**Out-of-scope соблюдено:**
- ❌ Lighthouse Vitals — нет (E2)
- ❌ Crawler битых ссылок — нет (E2)
- ❌ HTML version отчёта — нет (E2)
- ❌ Content RU (тошнота/Flesch) — нет (E3)
- ❌ AI/llms.txt extended + auto-fix — нет (E4, N10 минимальный есть в E1)
- ❌ Snapshot history `11_QA/history/<ts>/` — нет (E3)

**Placeholder scan:** нет TBD/TODO. Каждый шаг содержит полный код или команду.

**Type consistency:**
- `check_html(html, url, ...)`, `check_schema(html, url)` — обе возвращают `list[dict]` с `{id, passed, evidence}` — единообразно в html_checks + schema_checks + tests.
- `run_all(url)` в network_checks возвращает `list[dict]` — тот же формат.
- `_result(check_id, passed, evidence, **extra)` хелпер используется во всех 3 runners — одинаковая сигнатура.
- `build_site_report(host, results, thresholds)` принимает плоский list[dict] — соответствует output runners.
- `discover_hosts(state_path, filter_host=None)` возвращает `list[str]` URLs с `https://` префиксом — потребляется в `run-audit.py` без дополнительной обработки.
- Threshold YAML keys `H1`..`H25`, `N1`..`N13`, `S1`..`S5` — совпадают с check_id во всех runners.
- Exit codes (0/1/2) задокументированы одинаково в SKILL.md, run-audit.py docstring, CLAUDE.md, /landing-audit.md.
