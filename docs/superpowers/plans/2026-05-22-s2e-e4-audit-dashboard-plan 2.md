# S2-E.4 Audit Dashboard + Head&SEO + AI checks — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Network admin "Аудит" + "Head & SEO" pages to landing-config mu-plugin, extend seo-tech-audit skill with 3 AI checks + `--hosts-file` + `--with-fix-hints`, deep-link each failure to the fix location.

**Architecture:** Python skill stays single source of truth — PHP admin shells out via `shell_exec` to `run-audit.py`. Caches results in `wp_sitemeta`. Cascade for head-seo options follows B2 pattern (`switch_to_blog(NETWORK_BLOG_ID=1)`). Deep-links come from a JSON catalog auto-generated from Python `fix_actions.py`.

**Tech Stack:** Python 3.10+ (`requests`, `bs4`), PHP 7.4+ (mu-plugin), vanilla JS (preview updater), pytest, WordPress multisite APIs (`get_sites`, `switch_to_blog`, `network_admin_menu`, `update_site_option`).

**Spec:** [docs/superpowers/specs/2026-05-22-s2e-e4-audit-dashboard-design.md](../specs/2026-05-22-s2e-e4-audit-dashboard-design.md)

---

## File Structure

```
skills/seo-tech-audit/
├── scripts/
│   ├── runners/
│   │   └── ai_readiness.py                  # NEW Task 1
│   ├── lib/
│   │   └── fix_actions.py                   # NEW Task 2
│   └── run-audit.py                         # MODIFY Task 3, 4
├── config/
│   └── quality-thresholds.yaml              # MODIFY Task 1
└── tests/
    ├── test_ai_readiness.py                 # NEW Task 1
    ├── test_fix_actions.py                  # NEW Task 2
    ├── test_run_audit_integration.py        # MODIFY Task 3, 4
    └── fixtures/
        ├── good-llms.txt                    # NEW Task 1
        ├── bad-llms.txt                     # NEW Task 1
        ├── good-schema.html                 # NEW Task 1
        └── no-js-empty.html                 # NEW Task 1

skills/wp-landing-config/mu-plugin/landing-config/
├── includes/
│   ├── seo-audit/                           # NEW directory
│   │   ├── admin-network.php                # Task 6 (main page + router)
│   │   ├── audit-runner.php                 # Task 5
│   │   ├── deep-links.php                   # Task 7
│   │   ├── fix-actions.json                 # Task 2 (auto-gen from py)
│   │   └── tabs/
│   │       ├── overview.php                 # Task 8
│   │       ├── html.php                     # Task 9
│   │       ├── network.php                  # Task 9
│   │       ├── schema.php                   # Task 9
│   │       └── ai_readiness.php             # Task 9
│   ├── head-seo-admin.php                   # Task 10 (settings + preview)
│   └── head-seo.php                         # MODIFY Task 11 (cascade-aware read)
├── assets/seo-audit/
│   ├── admin.css                            # Task 6
│   ├── preview.js                           # Task 10
│   └── preview.css                          # Task 10
└── landing-config.php                       # MODIFY Task 12 (wire new modules)

skills/wp-landing-config/tests/
├── test_audit_runner_php.php                # NEW Task 5
├── test_deep_links_php.php                  # NEW Task 7
├── test_head_seo_admin_save.php             # NEW Task 10
└── test_head_seo_cascade.php                # NEW Task 11

CLAUDE.md                                     # MODIFY Task 13
```

---

### Task 1: AI readiness runner (AI1 + AI2 + AI3) + thresholds + fixtures

**Files:**
- Create: `skills/seo-tech-audit/scripts/runners/ai_readiness.py`
- Create: `skills/seo-tech-audit/tests/test_ai_readiness.py`
- Create: `skills/seo-tech-audit/tests/fixtures/good-llms.txt`
- Create: `skills/seo-tech-audit/tests/fixtures/bad-llms.txt`
- Create: `skills/seo-tech-audit/tests/fixtures/good-schema.html`
- Create: `skills/seo-tech-audit/tests/fixtures/no-js-empty.html`
- Modify: `skills/seo-tech-audit/config/quality-thresholds.yaml`

- [ ] **Step 1: Add 3 fixtures**

`skills/seo-tech-audit/tests/fixtures/good-llms.txt`:
```markdown
# Example Site

> Short tagline describing the site for LLM consumption.

## Resources

- [Privacy Policy](https://example.com/policy): Our data handling.
- [About Us](https://example.com/about): Who we are.
```

`skills/seo-tech-audit/tests/fixtures/bad-llms.txt`:
```
just some plain text without any markdown structure or links
```

`skills/seo-tech-audit/tests/fixtures/good-schema.html`:
```html
<!doctype html><html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"Acme","url":"https://acme.com"}
</script>
</head><body>Body text content for AI3 sufficient render check, plenty of characters here to exceed the 1KB threshold easily. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium totam rem aperiam eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</body></html>
```

`skills/seo-tech-audit/tests/fixtures/no-js-empty.html`:
```html
<!doctype html><html><head><title>SPA</title></head><body><div id="app"></div><script src="/app.js"></script></body></html>
```

- [ ] **Step 2: Write failing test** at `skills/seo-tech-audit/tests/test_ai_readiness.py`:

```python
"""Tests for ai_readiness runner (AI1/AI2/AI3)."""
from pathlib import Path
from unittest.mock import patch, MagicMock

from runners.ai_readiness import (
    check_llms_txt,
    check_schema_org_types,
    check_no_js_render,
    run_all,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _make_response(status=200, text=""):
    r = MagicMock()
    r.status_code = status
    r.text = text
    return r


def test_ai1_llms_txt_valid():
    good = (FIXTURES / "good-llms.txt").read_text(encoding="utf-8")
    resp = _make_response(200, good)
    with patch("runners.ai_readiness.fetch", return_value=resp):
        r = check_llms_txt("https://x/")
    assert r["id"] == "AI1"
    assert r["passed"] is True


def test_ai1_llms_txt_missing():
    resp = _make_response(404, "")
    with patch("runners.ai_readiness.fetch", return_value=resp):
        r = check_llms_txt("https://x/")
    assert r["passed"] is False


def test_ai1_llms_txt_invalid_format():
    bad = (FIXTURES / "bad-llms.txt").read_text(encoding="utf-8")
    resp = _make_response(200, bad)
    with patch("runners.ai_readiness.fetch", return_value=resp):
        r = check_llms_txt("https://x/")
    assert r["passed"] is False


def test_ai2_schema_org_organization():
    good = (FIXTURES / "good-schema.html").read_text(encoding="utf-8")
    r = check_schema_org_types(good, "https://x/")
    assert r["id"] == "AI2"
    assert r["passed"] is True


def test_ai2_schema_org_missing_org_type():
    html = '<html><head><script type="application/ld+json">{"@type":"Article"}</script></head><body>x</body></html>'
    r = check_schema_org_types(html, "https://x/")
    assert r["passed"] is False


def test_ai3_no_js_sufficient_content():
    good = (FIXTURES / "good-schema.html").read_text(encoding="utf-8")
    r = check_no_js_render(good, "https://x/")
    assert r["id"] == "AI3"
    assert r["passed"] is True


def test_ai3_no_js_blank_spa():
    blank = (FIXTURES / "no-js-empty.html").read_text(encoding="utf-8")
    r = check_no_js_render(blank, "https://x/")
    assert r["passed"] is False


def test_run_all_returns_three_results():
    good_schema = (FIXTURES / "good-schema.html").read_text(encoding="utf-8")
    good_llms = (FIXTURES / "good-llms.txt").read_text(encoding="utf-8")
    resp = _make_response(200, good_llms)
    with patch("runners.ai_readiness.fetch", return_value=resp):
        results = run_all("https://x/", good_schema)
    ids = sorted(r["id"] for r in results)
    assert ids == ["AI1", "AI2", "AI3"]
```

- [ ] **Step 3: Run — verify FAIL**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_ai_readiness.py -v 2>&1 | tail -10
```
Expected: ImportError (module not found).

- [ ] **Step 4: Implement** `skills/seo-tech-audit/scripts/runners/ai_readiness.py`:

```python
"""AI readiness checks (AI1-AI3)."""
import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from lib.http_client import fetch

# Types that satisfy AI2 — at least one must be present in JSON-LD blocks
AI2_TYPES = {"Organization", "LocalBusiness", "Product", "FAQPage"}

# Threshold for AI3 sufficient render — body text (after stripping script/style)
AI3_MIN_BODY_BYTES = 1024


def _result(check_id, passed, evidence="", **extra):
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_llms_txt(url):
    """AI1: /llms.txt valid per llmstxt.org spec.

    Pass: 200 OK AND content has `# <h1>` AND at least one `[label](url)` link.
    """
    target = urljoin(url, "/llms.txt")
    try:
        resp = fetch(target)
    except Exception as e:
        return _result("AI1", False, f"fetch_error: {e.__class__.__name__}")
    if resp.status_code != 200:
        return _result("AI1", False, f"status={resp.status_code}")
    text = resp.text or ""
    has_h1 = bool(re.search(r"^#\s+\S+", text, re.MULTILINE))
    has_link = bool(re.search(r"\[[^\]]+\]\([^)]+\)", text))
    passed = has_h1 and has_link
    return _result(
        "AI1", passed,
        f"size={len(text)}B has_h1={has_h1} has_link={has_link}"
    )


def check_schema_org_types(html, url):
    """AI2: at least one JSON-LD block with @type in AI2_TYPES."""
    soup = BeautifulSoup(html, "lxml")
    blocks = soup.find_all("script", attrs={"type": "application/ld+json"})
    found_types = []
    for b in blocks:
        try:
            data = json.loads(b.get_text("") or "")
        except json.JSONDecodeError:
            continue
        # JSON-LD can be a single object or a list
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            if isinstance(t, list):
                found_types.extend(t)
            elif isinstance(t, str):
                found_types.append(t)
    matched = [t for t in found_types if t in AI2_TYPES]
    return _result(
        "AI2", bool(matched),
        f"found_types={found_types} matched={matched}"
    )


def check_no_js_render(html, url):
    """AI3: body has ≥1KB of text content (or noscript fallback)."""
    soup = BeautifulSoup(html, "lxml")
    # Strip script/style — those don't count as visible content
    for tag in soup(["script", "style"]):
        tag.decompose()
    body = soup.body
    if body is None:
        return _result("AI3", False, "no_body")
    text = body.get_text(" ", strip=True)
    size = len(text.encode("utf-8"))
    passed = size >= AI3_MIN_BODY_BYTES
    return _result("AI3", passed, f"body_text={size}B threshold={AI3_MIN_BODY_BYTES}B")


def run_all(url, html):
    """Run AI1+AI2+AI3. html is already-fetched body for AI2/AI3."""
    return [
        check_llms_txt(url),
        check_schema_org_types(html, url),
        check_no_js_render(html, url),
    ]
```

- [ ] **Step 5: Run — verify PASS** (8 tests):
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_ai_readiness.py -v 2>&1 | tail -12
```

- [ ] **Step 6: Add AI1/AI2/AI3 to thresholds.yaml**

In `skills/seo-tech-audit/config/quality-thresholds.yaml`, append at the end:

```yaml

# === AI Readiness (AI1-AI3) ===
AI1: { hard: false, desc: "llms.txt валиден (llmstxt.org spec)" }
AI2: { hard: false, desc: "JSON-LD Organization/LocalBusiness/Product/FAQPage" }
AI3: { hard: false, desc: "Body содержит ≥1KB текста без JS execution" }
```

- [ ] **Step 7: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/seo-tech-audit/scripts/runners/ai_readiness.py \
        skills/seo-tech-audit/tests/test_ai_readiness.py \
        skills/seo-tech-audit/tests/fixtures/good-llms.txt \
        skills/seo-tech-audit/tests/fixtures/bad-llms.txt \
        skills/seo-tech-audit/tests/fixtures/good-schema.html \
        skills/seo-tech-audit/tests/fixtures/no-js-empty.html \
        skills/seo-tech-audit/config/quality-thresholds.yaml
git commit -m "feat(s2e-e4): ai_readiness runner (AI1/AI2/AI3) + 8 tests + 3 thresholds"
```

---

### Task 2: fix_actions.py catalog + JSON export + tests

**Files:**
- Create: `skills/seo-tech-audit/scripts/lib/fix_actions.py`
- Create: `skills/seo-tech-audit/tests/test_fix_actions.py`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/fix-actions.json` (auto-gen)

- [ ] **Step 1: Write failing test** at `skills/seo-tech-audit/tests/test_fix_actions.py`:

```python
"""Tests for fix_actions catalog — 4 cases (one per category)."""
import json

from lib.fix_actions import CATALOG, get_fix_action, export_json


def test_h_category_present():
    """HTML category — H6 maps to head-seo admin page."""
    fa = get_fix_action("H6")
    assert fa is not None
    assert fa["type"] == "admin_page"
    assert fa["page"] == "landing-config-head-seo"


def test_n_category_present():
    """Network — N8 (robots.txt) maps to reading settings."""
    fa = get_fix_action("N8")
    assert fa is not None
    assert fa["type"] == "raw_url"
    assert "options-reading.php" in fa["url"]


def test_s_category_present():
    """Schema — S5 (favicon) maps to customizer site_icon."""
    fa = get_fix_action("S5")
    assert fa is not None
    assert fa["type"] == "raw_url"
    assert "site_icon" in fa["url"]


def test_ai_category_present():
    """AI — AI1 (llms.txt) maps to head-seo admin (anchor)."""
    fa = get_fix_action("AI1")
    assert fa is not None
    # Either raw_url with anchor or admin_page — accept both, just check label
    assert "llms.txt" in fa["label"].lower()


def test_unknown_check_returns_none():
    assert get_fix_action("X99") is None


def test_export_json_round_trip(tmp_path):
    out = tmp_path / "fix-actions.json"
    export_json(out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    # Should contain at least H6, N8, S5, AI1
    for key in ["H6", "N8", "S5", "AI1"]:
        assert key in loaded


def test_catalog_covers_all_43_plus_3():
    """Smoke: catalog must cover at least one entry per category prefix."""
    prefixes = {k[0] for k in CATALOG.keys()}
    assert prefixes >= {"H", "N", "S"}, f"missing prefixes: {prefixes}"
    # AI checks should also be present
    ai_keys = [k for k in CATALOG.keys() if k.startswith("AI")]
    assert len(ai_keys) >= 3
```

- [ ] **Step 2: Run — verify FAIL**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_fix_actions.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement** `skills/seo-tech-audit/scripts/lib/fix_actions.py`:

```python
"""Fix-action catalog: CHECK_ID → metadata for PHP admin deep-links.

type semantics:
  admin_page  → URL = network/admin.php?page=<page>
  post_edit   → URL = post.php?post=<homepage_id>&action=edit
                use_homepage_id=True triggers PHP to substitute
  raw_url     → URL = admin_url(<url>) (PHP prepends admin root)
  suggestion  → no URL, only description plate
"""
import json
from pathlib import Path

CATALOG = {
    # === HTML on-page (H1-H25) ===
    "H1":  {"label": "Открыть страницу в браузере", "type": "raw_url", "url": ""},
    "H2":  {"label": "Оптимизировать TTFB — проверить хостинг/кэш", "type": "suggestion"},
    "H3":  {"label": "Уменьшить размер HTML — code minify", "type": "suggestion"},
    "H4":  {"label": "Заполнить Title (в редакторе главной)", "type": "post_edit", "use_homepage_id": True},
    "H5":  {"label": "Title длина 30-80 символов — изменить в редакторе", "type": "post_edit", "use_homepage_id": True},
    "H6":  {"label": "Заполнить Description", "type": "admin_page", "page": "landing-config-head-seo"},
    "H7":  {"label": "Description длина 70-320 — изменить в Head & SEO", "type": "admin_page", "page": "landing-config-head-seo"},
    "H8":  {"label": "Открыть редактор главной (исправить число H1)", "type": "post_edit", "use_homepage_id": True},
    "H9":  {"label": "Иерархия заголовков — изменить в редакторе", "type": "post_edit", "use_homepage_id": True},
    "H10": {"label": "Установить язык сайта в Settings → General", "type": "raw_url", "url": "options-general.php"},
    "H11": {"label": "UTF-8 declaration — обычно настройка темы", "type": "suggestion"},
    "H12": {"label": "Canonical URL — обычно WP делает автоматически", "type": "raw_url", "url": "options-general.php"},
    "H13": {"label": "Hreflang — если сайт многоязычный, нужен плагин", "type": "suggestion"},
    "H14": {"label": "Поиск разрешён — Settings → Reading", "type": "raw_url", "url": "options-reading.php"},
    "H15": {"label": "Добавить alt-теги ко всем картинкам", "type": "post_edit", "use_homepage_id": True},
    "H16": {"label": "loading=\"lazy\" для below-fold картинок", "type": "suggestion"},
    "H17": {"label": "Задать width/height для картинок (CLS)", "type": "suggestion"},
    "H18": {"label": "Конвертировать картинки в WebP/AVIF — плагин ShortPixel", "type": "suggestion"},
    "H19": {"label": "Inline CSS превышает 10KB — внешний файл", "type": "suggestion"},
    "H20": {"label": "Уменьшить render-blocking resources", "type": "suggestion"},
    "H21": {"label": "Добавить внутренние ссылки в текст страницы", "type": "post_edit", "use_homepage_id": True},
    "H22": {"label": "Добавить rel=\"noopener\" к внешним ссылкам", "type": "post_edit", "use_homepage_id": True},
    "H23": {"label": "Замени «click here»/«тут» на осмысленные анкоры", "type": "post_edit", "use_homepage_id": True},
    "H24": {"label": "Добавить tel: ссылку для мобильных", "type": "post_edit", "use_homepage_id": True},
    "H25": {"label": "Добавить mailto: для email-контактов", "type": "post_edit", "use_homepage_id": True},

    # === Network/Infra (N1-N13) ===
    "N1":  {"label": "SSL невалиден — проверить сертификат у хостера", "type": "suggestion"},
    "N2":  {"label": "SSL истекает <30 дней — renew", "type": "suggestion"},
    "N3":  {"label": "SSL истекает <7 дней — СРОЧНО renew", "type": "suggestion"},
    "N4":  {"label": "HTTP/2 — включить у хостера или CDN", "type": "suggestion"},
    "N5":  {"label": "Security headers — настроить в .htaccess / nginx", "type": "suggestion"},
    "N6":  {"label": "Server header раскрывает версию — скрыть в конфиге", "type": "suggestion"},
    "N7":  {"label": "www/non-www редирект — настроить в .htaccess", "type": "suggestion"},
    "N8":  {"label": "Settings → Reading: разрешить индексацию", "type": "raw_url", "url": "options-reading.php"},
    "N9":  {"label": "Sitemap WP делает автоматически /wp-sitemap.xml — проверь permalinks", "type": "raw_url", "url": "options-permalink.php"},
    "N10": {"label": "Создать llms.txt в Head & SEO", "type": "admin_page", "page": "landing-config-head-seo"},
    "N11": {"label": "404 страница возвращает 200 — нужен фикс в теме", "type": "suggestion"},
    "N12": {"label": "Добавить навигацию в 404.php темы", "type": "suggestion"},
    "N13": {"label": "Whois — info only, не блокирующее", "type": "suggestion"},

    # === Schema (S1-S5) ===
    "S1":  {"label": "Заполнить Open Graph теги", "type": "admin_page", "page": "landing-config-head-seo"},
    "S2":  {"label": "og:image должен быть 1200×630 — изменить в Head & SEO", "type": "admin_page", "page": "landing-config-head-seo"},
    "S3":  {"label": "Twitter Card — заполнить в Head & SEO", "type": "admin_page", "page": "landing-config-head-seo"},
    "S4":  {"label": "Добавить Schema.org JSON-LD — нужен функцiональный код или плагин", "type": "suggestion"},
    "S5":  {"label": "Установить Site Icon (favicon)", "type": "raw_url", "url": "customize.php?autofocus[control]=site_icon"},

    # === AI Readiness (AI1-AI3) ===
    "AI1": {"label": "Создать llms.txt в Head & SEO", "type": "admin_page", "page": "landing-config-head-seo"},
    "AI2": {"label": "Добавить JSON-LD Organization (functions.php темы)", "type": "suggestion"},
    "AI3": {"label": "Сайт пустой без JS — server-side render обязателен", "type": "suggestion"},
}


def get_fix_action(check_id):
    """Returns dict or None if check_id is unknown."""
    return CATALOG.get(check_id)


def export_json(out_path):
    """Write CATALOG as JSON for PHP consumption."""
    Path(out_path).write_text(
        json.dumps(CATALOG, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
```

- [ ] **Step 4: Run — verify PASS** (7 tests):
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_fix_actions.py -v 2>&1 | tail -10
```

- [ ] **Step 5: Generate fix-actions.json for PHP**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
mkdir -p skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit
python -c "
import sys; sys.path.insert(0, 'skills/seo-tech-audit/scripts')
from lib.fix_actions import export_json
export_json('skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/fix-actions.json')
print('exported')
"
```

- [ ] **Step 6: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/seo-tech-audit/scripts/lib/fix_actions.py \
        skills/seo-tech-audit/tests/test_fix_actions.py \
        skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/fix-actions.json
git commit -m "feat(s2e-e4): fix_actions catalog (46 entries) + JSON export for PHP"
```

---

### Task 3: --hosts-file flag in run-audit.py

**Files:**
- Modify: `skills/seo-tech-audit/scripts/run-audit.py`
- Modify: `skills/seo-tech-audit/tests/test_run_audit_integration.py`

- [ ] **Step 1: Append failing test**

Append to `skills/seo-tech-audit/tests/test_run_audit_integration.py`:

```python
def test_cli_hosts_file_mode(tmp_path):
    """--hosts-file reads URLs from text file (one per line)."""
    hosts_file = tmp_path / "hosts.txt"
    hosts_file.write_text("https://example.com\nhttps://example.org\n", encoding="utf-8")
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--hosts-file", str(hosts_file),
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode in (0, 1)
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert data["total_sites"] == 2
    hosts = {s["host"] for s in data["sites"]}
    assert hosts == {"https://example.com", "https://example.org"}


def test_cli_hosts_file_blank_lines_ignored(tmp_path):
    hosts_file = tmp_path / "hosts.txt"
    hosts_file.write_text("\n\nhttps://example.com\n\n", encoding="utf-8")
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--hosts-file", str(hosts_file),
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode in (0, 1)
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert data["total_sites"] == 1


def test_cli_hosts_file_not_found(tmp_path):
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--hosts-file", str(tmp_path / "missing.txt"),
         "--out", str(tmp_path / "out")],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 2
    assert "hosts file" in (r.stderr + r.stdout).lower() or "not found" in (r.stderr + r.stdout).lower()
```

- [ ] **Step 2: Run — verify FAIL** (--hosts-file unknown):
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_run_audit_integration.py::test_cli_hosts_file_mode -v 2>&1 | tail -5
```

- [ ] **Step 3: Modify run-audit.py**

In `skills/seo-tech-audit/scripts/run-audit.py`:

Find the argparse mutex group block, change it from `add_mutually_exclusive_group(required=True)` to include `--hosts-file`:

```python
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--project", help="project root with .landing-state.yaml")
    g.add_argument("--url", help="single ad-hoc URL to audit")
    g.add_argument("--hosts-file", help="text file with URLs, one per line")
```

Find the host-resolution block (after argparse, where `args.url` and `args.project` branches are). Add a new branch BEFORE the `args.url` branch:

```python
    if args.hosts_file:
        hosts_path = Path(args.hosts_file)
        if not hosts_path.exists():
            print(f"ERROR: hosts file not found: {hosts_path}", file=sys.stderr)
            return 2
        raw = hosts_path.read_text(encoding="utf-8").splitlines()
        hosts = [line.strip().rstrip("/") for line in raw if line.strip()]
        if not hosts:
            print(f"ERROR: hosts file is empty: {hosts_path}", file=sys.stderr)
            return 2
        out_root = Path(args.out) if args.out else Path("./11_QA")
    elif args.url:
        hosts = [args.url.rstrip("/")]
        out_root = Path(args.out) if args.out else Path("./11_QA")
    else:
        # (existing --project branch unchanged)
        project = Path(args.project)
        ...
```

- [ ] **Step 4: Run — verify PASS** (3 new tests):
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_run_audit_integration.py -v 2>&1 | tail -15
```

Expected: all 6 integration tests pass.

- [ ] **Step 5: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/seo-tech-audit/scripts/run-audit.py \
        skills/seo-tech-audit/tests/test_run_audit_integration.py
git commit -m "feat(s2e-e4): run-audit.py --hosts-file flag + 3 tests"
```

---

### Task 4: --with-fix-hints flag + AI checks integration in run-audit

**Files:**
- Modify: `skills/seo-tech-audit/scripts/run-audit.py`
- Modify: `skills/seo-tech-audit/tests/test_run_audit_integration.py`

- [ ] **Step 1: Append failing test**

Append to `skills/seo-tech-audit/tests/test_run_audit_integration.py`:

```python
def test_cli_with_fix_hints_enriches_failures(tmp_path):
    """--with-fix-hints adds fix_action to each failure."""
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--url", "https://example.com",
         "--with-fix-hints",
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode in (0, 1)
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    failures = data["sites"][0]["failures"]
    # example.com is missing OG, no meta, etc — should have failures
    assert len(failures) > 0
    # At least one failure has fix_action
    with_fix = [f for f in failures if f.get("fix_action")]
    assert len(with_fix) > 0
    # fix_action has expected shape
    fa = with_fix[0]["fix_action"]
    assert "type" in fa
    assert "label" in fa


def test_cli_includes_ai_checks(tmp_path):
    """Audit results should now include AI1, AI2, AI3."""
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--url", "https://example.com",
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode in (0, 1)
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    ids = {r["id"] for r in data["sites"][0]["results"]}
    assert "AI1" in ids
    assert "AI2" in ids
    assert "AI3" in ids
```

- [ ] **Step 2: Run — verify FAIL**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_run_audit_integration.py::test_cli_with_fix_hints_enriches_failures \
                 skills/seo-tech-audit/tests/test_run_audit_integration.py::test_cli_includes_ai_checks -v 2>&1 | tail -10
```

- [ ] **Step 3: Modify run-audit.py — add AI runner + --with-fix-hints**

In `skills/seo-tech-audit/scripts/run-audit.py`:

Add new import near other runner imports:
```python
from runners.ai_readiness import run_all as run_ai_checks
from lib.fix_actions import get_fix_action
```

Add argparse argument near other flags:
```python
    p.add_argument("--with-fix-hints", action="store_true",
                   help="Enrich each failure with fix_action metadata from fix_actions catalog")
```

Find `audit_one_url(url)` function. Inside the `try` block where `html` is set, add AI checks call AFTER `check_schema`:
```python
        results.extend(check_schema(html, url))
        results.extend(run_ai_checks(url, html))
```

After the audit loop where `site_reports` is built, BEFORE writing JSON, add fix-hints enrichment:
```python
    if args.with_fix_hints:
        for rep in site_reports:
            for f in rep["failures"]:
                fa = get_fix_action(f["id"])
                if fa is not None:
                    f["fix_action"] = fa
```

Note: `audit_one_url` currently might call AI checks only if HTML fetched OK — make sure when fetch fails, AI2/AI3 are not called (they need html). AI1 should still run (hits its own endpoint).

Refactor:
```python
def audit_one_url(url):
    results = []
    html = None
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
        results.append({"id": "H1", "passed": False, "evidence": f"fetch_error: {e}"})

    # AI runner: AI1 always (own endpoint), AI2/AI3 only if html available
    if html is not None:
        results.extend(run_ai_checks(url, html))
    else:
        # AI1 still meaningful (own fetch); AI2/AI3 marked as fetch-error fails
        from runners.ai_readiness import check_llms_txt
        results.append(check_llms_txt(url))
        results.append({"id": "AI2", "passed": False, "evidence": "no_html (fetch failed)"})
        results.append({"id": "AI3", "passed": False, "evidence": "no_html (fetch failed)"})

    results.extend(run_network_checks(url))
    return results
```

- [ ] **Step 4: Run — verify PASS**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/test_run_audit_integration.py -v 2>&1 | tail -15
```

Expected: all 8 integration tests pass (3 existing + 3 hosts-file + 2 new).

- [ ] **Step 5: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/seo-tech-audit/scripts/run-audit.py \
        skills/seo-tech-audit/tests/test_run_audit_integration.py
git commit -m "feat(s2e-e4): run-audit.py --with-fix-hints + integrate AI1/AI2/AI3"
```

---

### Task 5: PHP audit-runner.php (shell_exec wrapper)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/audit-runner.php`
- Create: `skills/wp-landing-config/tests/test_audit_runner_php.php`

- [ ] **Step 1: Write failing test**

Create `skills/wp-landing-config/tests/test_audit_runner_php.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/seo-audit/audit-runner.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: build_python_command — single URL mode
$cmd = \LandingConfig\SEOAudit\Runner\build_python_command(
    ['urls' => ['https://example.com/'], 'out_dir' => '/tmp/x'],
    '/usr/bin/python3',
    '/path/to/run-audit.py'
);
assert_test(strpos($cmd, '--url https://example.com/') !== false,
    'T1a single URL mode has --url');
assert_test(strpos($cmd, '--with-fix-hints') !== false,
    'T1b always includes --with-fix-hints');
assert_test(strpos($cmd, '--json') !== false,
    'T1c always includes --json');

// T2: build_python_command — multi-URL mode via hosts file
$cmd2 = \LandingConfig\SEOAudit\Runner\build_python_command(
    ['urls' => ['https://a.com/', 'https://b.com/'], 'out_dir' => '/tmp/x', 'hosts_file' => '/tmp/h.txt'],
    '/usr/bin/python3',
    '/path/to/run-audit.py'
);
assert_test(strpos($cmd2, '--hosts-file /tmp/h.txt') !== false,
    'T2a multi-URL uses --hosts-file');
assert_test(strpos($cmd2, '--url ') === false,
    'T2b multi-URL does NOT include --url');

// T3: parse_audit_output — valid JSON
$json = json_encode(['sites' => [['host' => 'https://x/', 'passed' => true]],
                    'total_sites' => 1, 'sites_passed' => 1, 'overall_passed' => true]);
$parsed = \LandingConfig\SEOAudit\Runner\parse_audit_output($json);
assert_test($parsed !== null, 'T3a parses valid JSON');
assert_test($parsed['overall_passed'] === true, 'T3b parsed shape correct');

// T4: parse_audit_output — invalid JSON returns null
$bad = \LandingConfig\SEOAudit\Runner\parse_audit_output('not json');
assert_test($bad === null, 'T4 invalid JSON returns null');

// T5: cache key naming
assert_test(\LandingConfig\SEOAudit\Runner\cache_key(0) === 'landing_seo_audit_0',
    'T5a cache_key(0) = network');
assert_test(\LandingConfig\SEOAudit\Runner\cache_key(3) === 'landing_seo_audit_3',
    'T5b cache_key(3) = per-blog');
assert_test(\LandingConfig\SEOAudit\Runner\aggregate_cache_key() === 'landing_seo_audit_aggregate',
    'T5c aggregate cache key');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify FAIL**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_audit_runner_php.php 2>&1 | tail -5
```

- [ ] **Step 3: Implement** `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/audit-runner.php`:

```php
<?php
namespace LandingConfig\SEOAudit\Runner;

if (!defined('ABSPATH')) { exit; }

const PYTHON_BIN_CANDIDATES = ['/usr/local/bin/python3', '/usr/bin/python3', 'python3', 'python'];
const AUDIT_TIMEOUT_SEC     = 180;

/** Build python CLI command for run-audit.py. Pure for testability. */
function build_python_command(array $opts, string $python_bin, string $script_path): string {
    $cmd = escapeshellcmd($python_bin) . ' ' . escapeshellarg($script_path)
         . ' --json --with-fix-hints';

    if (!empty($opts['hosts_file'])) {
        $cmd .= ' --hosts-file ' . escapeshellarg($opts['hosts_file']);
    } elseif (!empty($opts['urls']) && count($opts['urls']) === 1) {
        $cmd .= ' --url ' . escapeshellarg($opts['urls'][0]);
    }
    if (!empty($opts['out_dir'])) {
        $cmd .= ' --out ' . escapeshellarg($opts['out_dir']);
    }
    return $cmd;
}

/** Detect first available python binary. */
function detect_python_bin(): ?string {
    foreach (PYTHON_BIN_CANDIDATES as $bin) {
        $out = @shell_exec($bin . ' --version 2>&1');
        if ($out && stripos($out, 'python') !== false) {
            return $bin;
        }
    }
    return null;
}

/** Parse run-audit.py stdout into associative array. Returns null on invalid JSON. */
function parse_audit_output(string $stdout): ?array {
    $data = json_decode($stdout, true);
    if (!is_array($data)) return null;
    return $data;
}

/** Cache keys for wp_sitemeta. */
function cache_key(int $blog_id): string {
    return 'landing_seo_audit_' . $blog_id;
}

function aggregate_cache_key(): string {
    return 'landing_seo_audit_aggregate';
}

function timestamp_key(int $blog_id): string {
    return 'landing_seo_audit_' . $blog_id . '_ts';
}

/**
 * Run audit for given URLs. Multisite mode if >1 URL.
 *
 * @param string[] $urls
 * @return array{ok:bool, data:?array, error:?string, stderr:?string}
 */
function run_audit_for_urls(array $urls): array {
    if (function_exists('set_time_limit')) {
        \set_time_limit(AUDIT_TIMEOUT_SEC);
    }
    if (!function_exists('shell_exec')) {
        return ['ok' => false, 'data' => null, 'error' => 'shell_exec disabled in php.ini', 'stderr' => null];
    }
    $python = detect_python_bin();
    if ($python === null) {
        return ['ok' => false, 'data' => null, 'error' => 'python3 not found in PATH', 'stderr' => null];
    }

    $script_path = realpath(dirname(__DIR__, 4) . '/seo-tech-audit/scripts/run-audit.py');
    if (!$script_path) {
        // Fallback: assume mu-plugin is deployed alongside skills/ symlinked.
        // Deploy guidance: rsync skills/seo-tech-audit/ to a known path.
        $script_path = sys_get_temp_dir() . '/seo-tech-audit/scripts/run-audit.py';
    }

    $tmp = sys_get_temp_dir() . '/lp-audit-' . wp_generate_password(8, false);
    @mkdir($tmp, 0755, true);

    $opts = ['urls' => $urls, 'out_dir' => $tmp];
    if (count($urls) > 1) {
        $hosts_file = $tmp . '/hosts.txt';
        file_put_contents($hosts_file, implode("\n", $urls));
        $opts['hosts_file'] = $hosts_file;
    }

    $cmd = build_python_command($opts, $python, $script_path) . ' 2>&1';
    $stdout = shell_exec($cmd);

    if ($stdout === null || $stdout === '') {
        return ['ok' => false, 'data' => null, 'error' => 'shell_exec returned no output',
                'stderr' => 'cmd: ' . $cmd];
    }

    $data = parse_audit_output($stdout);
    if ($data === null) {
        // Try reading audit-report.json directly (CLI also writes to file)
        $json_path = $tmp . '/audit-report.json';
        if (file_exists($json_path)) {
            $data = parse_audit_output(file_get_contents($json_path));
        }
    }

    if ($data === null) {
        return ['ok' => false, 'data' => null,
                'error' => 'failed to parse JSON output',
                'stderr' => substr($stdout, 0, 2000)];
    }

    // Cleanup tmp
    if (is_dir($tmp)) {
        foreach (glob($tmp . '/*') as $f) { @unlink($f); }
        @rmdir($tmp);
    }

    return ['ok' => true, 'data' => $data, 'error' => null, 'stderr' => null];
}
```

- [ ] **Step 4: Run — verify PASS** (10 assertions):
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_audit_runner_php.php 2>&1 | tail -5
```

- [ ] **Step 5: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/audit-runner.php \
        skills/wp-landing-config/tests/test_audit_runner_php.php
git commit -m "feat(s2e-e4): PHP audit-runner — shell_exec wrapper + cache keys + 10 tests"
```

---

### Task 6: PHP admin-network.php (main page + router + admin.css)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/admin-network.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/admin.css`

- [ ] **Step 1: Create assets/seo-audit/admin.css**:

Path: `skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/admin.css`

```css
/* SEO Audit admin styles */
.lp-audit-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #c3c4c7;
  border-radius: 4px;
}
.lp-audit-header__segment-selector { flex: 1; }
.lp-audit-header__last-run { color: #646970; font-size: 13px; }
.lp-audit-header__btn { white-space: nowrap; }

.lp-audit-tabs {
  border-bottom: 1px solid #c3c4c7;
  margin-bottom: 16px;
}
.lp-audit-tabs a {
  display: inline-block;
  padding: 8px 14px;
  margin-right: 4px;
  text-decoration: none;
  color: #2271b1;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}
.lp-audit-tabs a.is-active {
  background: #fff;
  color: #1d2327;
  border-color: #c3c4c7;
  margin-bottom: -1px;
  font-weight: 600;
}

.lp-audit-table {
  width: 100%;
  background: #fff;
  border-collapse: collapse;
}
.lp-audit-table th,
.lp-audit-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f1;
  vertical-align: top;
}
.lp-audit-table th { background: #f6f7f7; font-weight: 600; }
.lp-audit-table tr.is-hard td { background: #fef2f2; }
.lp-audit-table tr.is-soft td { background: #fffbeb; }
.lp-audit-table .lp-id { font-family: monospace; font-weight: 600; }
.lp-audit-table .lp-evidence {
  font-family: monospace;
  font-size: 12px;
  color: #646970;
  max-width: 400px;
  word-break: break-all;
}
.lp-audit-table .lp-suggestion { color: #646970; font-style: italic; font-size: 13px; }

.lp-audit-empty {
  padding: 32px;
  text-align: center;
  color: #646970;
  background: #fff;
  border: 1px dashed #c3c4c7;
}
```

- [ ] **Step 2: Implement** `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/admin-network.php`:

```php
<?php
namespace LandingConfig\SEOAudit\Admin;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\SEOAudit\Runner\run_audit_for_urls;
use function LandingConfig\SEOAudit\Runner\cache_key;
use function LandingConfig\SEOAudit\Runner\aggregate_cache_key;
use function LandingConfig\SEOAudit\Runner\timestamp_key;

const MENU_SLUG    = 'landing-config-seo-audit';
const VALID_TABS   = ['overview', 'html', 'network', 'schema', 'ai_readiness'];

add_action('network_admin_menu', __NAMESPACE__ . '\\register_menu');
add_action('admin_post_lp_seo_audit_run', __NAMESPACE__ . '\\handle_run');
add_action('admin_enqueue_scripts', __NAMESPACE__ . '\\enqueue_assets');

function register_menu(): void {
    \add_submenu_page(
        'landing-config-network',
        'Аудит',
        'Аудит',
        'manage_network_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function enqueue_assets($hook): void {
    if (strpos((string) $hook, MENU_SLUG) === false) return;
    $url = \plugins_url('assets/seo-audit/admin.css',
                        dirname(dirname(__DIR__)) . '/landing-config.php');
    \wp_enqueue_style('lp-seo-audit-admin', $url, [], '1.0');
}

/** Multisite host list (https://<host>) for all blogs in the network. */
function get_all_hosts(): array {
    $hosts = [];
    foreach (\get_sites(['fields' => 'ids']) as $bid) {
        $url = \get_site_url((int) $bid);
        if ($url) $hosts[] = rtrim($url, '/') . '/';
    }
    return $hosts;
}

function handle_run(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    \check_admin_referer('lp_seo_audit_run');

    $segment = isset($_POST['segment']) ? (string) $_POST['segment'] : '0';

    if ($segment === 'all') {
        $hosts = get_all_hosts();
        $res = run_audit_for_urls($hosts);
        if ($res['ok']) {
            \update_site_option(aggregate_cache_key(), \wp_json_encode($res['data'], JSON_UNESCAPED_UNICODE));
            \update_site_option(timestamp_key(0) . '_aggregate', time());
            // Also save per-site reports from aggregate.sites
            foreach (($res['data']['sites'] ?? []) as $site) {
                $host = $site['host'] ?? '';
                $blog_id = host_to_blog_id($host);
                if ($blog_id !== null) {
                    \update_site_option(cache_key($blog_id), \wp_json_encode($site, JSON_UNESCAPED_UNICODE));
                    \update_site_option(timestamp_key($blog_id), time());
                }
            }
        }
        $redirect_segment = 'all';
    } else {
        $blog_id = (int) $segment;
        $url = \get_site_url($blog_id);
        if (!$url) { wp_die('invalid segment'); }
        $url = rtrim($url, '/') . '/';
        $res = run_audit_for_urls([$url]);
        if ($res['ok']) {
            $site = $res['data']['sites'][0] ?? null;
            if ($site) {
                \update_site_option(cache_key($blog_id), \wp_json_encode($site, JSON_UNESCAPED_UNICODE));
                \update_site_option(timestamp_key($blog_id), time());
            }
        }
        $redirect_segment = (string) $blog_id;
    }

    $tab = isset($_POST['tab']) && in_array($_POST['tab'], VALID_TABS, true) ? $_POST['tab'] : 'overview';
    $args = [
        'page' => MENU_SLUG,
        'tab' => $tab,
        'segment' => $redirect_segment,
        'audited' => $res['ok'] ? 1 : 0,
    ];
    if (!$res['ok']) {
        $args['error'] = urlencode($res['error'] ?? 'unknown');
    }
    \wp_safe_redirect(\add_query_arg($args, \network_admin_url('admin.php')));
    exit;
}

function host_to_blog_id(string $url): ?int {
    $host = parse_url($url, PHP_URL_HOST);
    if (!$host) return null;
    foreach (\get_sites(['fields' => 'ids']) as $bid) {
        $site_host = parse_url(\get_site_url((int) $bid), PHP_URL_HOST);
        if ($site_host === $host) return (int) $bid;
    }
    return null;
}

function load_cached_report(string $segment): ?array {
    if ($segment === 'all') {
        $raw = \get_site_option(aggregate_cache_key());
    } else {
        $raw = \get_site_option(cache_key((int) $segment));
    }
    if (!$raw) return null;
    $data = json_decode($raw, true);
    return is_array($data) ? $data : null;
}

function load_timestamp(string $segment): int {
    if ($segment === 'all') {
        return (int) \get_site_option(timestamp_key(0) . '_aggregate', 0);
    }
    return (int) \get_site_option(timestamp_key((int) $segment), 0);
}

function render_segment_selector(string $current, string $tab): void {
    ?>
    <select onchange="window.location.href='<?php echo esc_js(\network_admin_url('admin.php?page=' . MENU_SLUG . '&tab=' . $tab)); ?>&segment=' + this.value">
        <option value="all" <?php selected($current, 'all'); ?>>Все сегменты (multisite)</option>
        <option value="0" <?php selected($current, '0'); ?>>Network default (root)</option>
        <?php foreach (\get_sites(['fields' => 'ids']) as $bid):
            $url = \get_site_url((int) $bid);
            $val = (string) (int) $bid; ?>
            <option value="<?php echo esc_attr($val); ?>" <?php selected($current, $val); ?>>
                blog #<?php echo (int) $bid; ?> — <?php echo esc_html((string) $url); ?>
            </option>
        <?php endforeach; ?>
    </select>
    <?php
}

function render_page(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    $tab = isset($_GET['tab']) && in_array($_GET['tab'], VALID_TABS, true) ? $_GET['tab'] : 'overview';
    $segment = isset($_GET['segment']) ? (string) $_GET['segment'] : 'all';

    ?>
    <div class="wrap">
        <h1>SEO Аудит</h1>

        <?php if (!empty($_GET['audited'])): ?>
            <div class="notice notice-success is-dismissible"><p>Аудит выполнен.</p></div>
        <?php endif; ?>
        <?php if (!empty($_GET['error'])): ?>
            <div class="notice notice-error is-dismissible">
                <p>Ошибка: <?php echo esc_html(urldecode((string) $_GET['error'])); ?></p>
            </div>
        <?php endif; ?>

        <div class="lp-audit-header">
            <div class="lp-audit-header__segment-selector">
                <label>Сегмент: </label>
                <?php render_segment_selector($segment, $tab); ?>
            </div>
            <div class="lp-audit-header__last-run">
                <?php $ts = load_timestamp($segment);
                if ($ts > 0):
                    $diff = human_time_diff($ts, time()); ?>
                    Последний прогон: <?php echo esc_html($diff); ?> назад
                <?php else: ?>
                    Аудит ещё не запускался
                <?php endif; ?>
            </div>
            <form method="post" action="<?php echo esc_url(\admin_url('admin-post.php')); ?>" style="margin:0;">
                <?php \wp_nonce_field('lp_seo_audit_run'); ?>
                <input type="hidden" name="action" value="lp_seo_audit_run">
                <input type="hidden" name="segment" value="<?php echo esc_attr($segment); ?>">
                <input type="hidden" name="tab" value="<?php echo esc_attr($tab); ?>">
                <button type="submit" class="button button-primary lp-audit-header__btn">
                    <?php echo $segment === 'all' ? 'Запустить для всех сегментов' : 'Запустить для этого сегмента'; ?>
                </button>
            </form>
        </div>

        <div class="lp-audit-tabs">
            <?php
            $tabs = [
                'overview' => 'Обзор',
                'html' => 'HTML / On-page',
                'network' => 'Network / Robots / Sitemap',
                'schema' => 'Schema / Open Graph',
                'ai_readiness' => 'AI readiness',
            ];
            foreach ($tabs as $key => $label):
                $url = \add_query_arg([
                    'page' => MENU_SLUG, 'tab' => $key, 'segment' => $segment,
                ], \network_admin_url('admin.php'));
                $class = $key === $tab ? 'is-active' : ''; ?>
                <a href="<?php echo esc_url($url); ?>" class="<?php echo esc_attr($class); ?>">
                    <?php echo esc_html($label); ?>
                </a>
            <?php endforeach; ?>
        </div>

        <?php
        $tab_file = __DIR__ . '/tabs/' . $tab . '.php';
        if (file_exists($tab_file)) {
            $report = load_cached_report($segment);
            include $tab_file;
        } else {
            echo '<div class="lp-audit-empty">Tab template missing: ' . esc_html($tab) . '</div>';
        }
        ?>
    </div>
    <?php
}
```

- [ ] **Step 3: PHP lint**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/admin-network.php
```

Expected: No syntax errors detected.

- [ ] **Step 4: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/admin-network.php \
        skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/admin.css
git commit -m "feat(s2e-e4): admin-network main page + segment selector + tabs router + admin.css"
```

---

### Task 7: PHP deep-links.php (URL builder from fix-actions.json)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/deep-links.php`
- Create: `skills/wp-landing-config/tests/test_deep_links_php.php`

- [ ] **Step 1: Write failing test**

`skills/wp-landing-config/tests/test_deep_links_php.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/seo-audit/deep-links.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// Mock get_option for show_on_front / page_on_front
$GLOBALS['_mock_options']['show_on_front'] = 'page';
$GLOBALS['_mock_options']['page_on_front'] = '96';

$ROOT = 'https://example.com/wp-admin/';

// HTML category: H6 → admin_page
$h6 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('H6', 1, $ROOT);
assert_test($h6 !== null, 'T1 H6 returns deep link');
assert_test($h6['type'] === 'admin_page', 'T1a H6 type=admin_page');
assert_test(strpos($h6['url'], 'landing-config-head-seo') !== false,
    'T1b H6 url contains target page');

// Network: N8 → raw_url
$n8 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('N8', 1, $ROOT);
assert_test(strpos($n8['url'], 'options-reading.php') !== false,
    'T2 N8 url is options-reading');

// Schema: S5 → raw_url with anchor
$s5 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('S5', 1, $ROOT);
assert_test(strpos($s5['url'], 'site_icon') !== false,
    'T3 S5 url contains site_icon');

// AI: AI1 → admin_page
$ai1 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('AI1', 1, $ROOT);
assert_test($ai1 !== null, 'T4 AI1 returns deep link');
assert_test(strpos($ai1['label'], 'llms.txt') !== false, 'T4a AI1 label mentions llms.txt');

// post_edit with use_homepage_id=true
$h4 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('H4', 1, $ROOT);
assert_test($h4['type'] === 'post_edit', 'T5 H4 type=post_edit');
assert_test(strpos($h4['url'], 'post.php?post=96') !== false,
    'T5a H4 substitutes homepage id 96');

// suggestion: no URL
$h11 = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('H11', 1, $ROOT);
assert_test($h11['type'] === 'suggestion', 'T6 H11 type=suggestion');
assert_test(!isset($h11['url']) || $h11['url'] === '', 'T6a suggestion has no url');

// Unknown check returns null
$unknown = \LandingConfig\SEOAudit\DeepLinks\build_deep_link('Z99', 1, $ROOT);
assert_test($unknown === null, 'T7 unknown returns null');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify FAIL**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_deep_links_php.php 2>&1 | tail -5
```

- [ ] **Step 3: Implement** `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/deep-links.php`:

```php
<?php
namespace LandingConfig\SEOAudit\DeepLinks;

if (!defined('ABSPATH')) { exit; }

/** Path to PHP-consumed fix-actions JSON (auto-gen from Python). */
const CATALOG_PATH = __DIR__ . '/fix-actions.json';

function load_catalog(): array {
    if (!file_exists(CATALOG_PATH)) return [];
    $raw = file_get_contents(CATALOG_PATH);
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

/**
 * Build deep-link metadata for a given check_id.
 *
 * @param int $blog_id Blog context (for switch_to_blog if homepage_id needed per-site)
 * @param string $admin_root Base admin URL (e.g. https://x/wp-admin/)
 * @return array{label:string, type:string, url?:string}|null
 */
function build_deep_link(string $check_id, int $blog_id, string $admin_root): ?array {
    $catalog = load_catalog();
    $entry = $catalog[$check_id] ?? null;
    if (!$entry) return null;

    $type = $entry['type'] ?? 'suggestion';
    $label = $entry['label'] ?? $check_id;
    $out = ['label' => $label, 'type' => $type];

    switch ($type) {
        case 'admin_page':
            $page = $entry['page'] ?? '';
            $out['url'] = rtrim($admin_root, '/') . '/admin.php?page=' . urlencode($page);
            break;
        case 'post_edit':
            $homepage_id = (int) (\get_option('page_on_front', 0) ?: 0);
            if (!empty($entry['use_homepage_id']) && $homepage_id > 0) {
                $out['url'] = rtrim($admin_root, '/') . '/post.php?post=' . $homepage_id . '&action=edit';
            } else {
                // Fallback: link to all pages list
                $out['url'] = rtrim($admin_root, '/') . '/edit.php?post_type=page';
            }
            break;
        case 'raw_url':
            $url = (string) ($entry['url'] ?? '');
            $out['url'] = rtrim($admin_root, '/') . '/' . ltrim($url, '/');
            break;
        case 'suggestion':
        default:
            // No URL
            break;
    }
    return $out;
}
```

- [ ] **Step 4: Run — verify PASS**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_deep_links_php.php 2>&1 | tail -5
```

Expected: `10 tests, 0 failures`.

- [ ] **Step 5: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/deep-links.php \
        skills/wp-landing-config/tests/test_deep_links_php.php
git commit -m "feat(s2e-e4): PHP deep-links builder — reads fix-actions.json + 10 tests"
```

---

### Task 8: Overview tab (matrix segments × categories)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/overview.php`

- [ ] **Step 1: Implement overview.php**

Path: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/overview.php`

```php
<?php
/**
 * Overview tab — used by admin-network::render_page().
 * Available variables (from caller): $report (?array), $segment (string), $tab (string).
 */
if (!defined('ABSPATH')) { exit; }

use function LandingConfig\SEOAudit\Admin\load_cached_report;

/** Categorize check IDs into groups. */
function _lp_categorize_results(array $results): array {
    $out = ['HTML' => [], 'Network' => [], 'Schema' => [], 'AI' => []];
    foreach ($results as $r) {
        $id = (string) ($r['id'] ?? '');
        if (str_starts_with($id, 'H')) {
            $out['HTML'][] = $r;
        } elseif (str_starts_with($id, 'N')) {
            $out['Network'][] = $r;
        } elseif (str_starts_with($id, 'S')) {
            $out['Schema'][] = $r;
        } elseif (str_starts_with($id, 'AI')) {
            $out['AI'][] = $r;
        }
    }
    return $out;
}

function _lp_score(array $checks): array {
    $hard_total = 0; $hard_pass = 0;
    $soft_total = 0; $soft_pass = 0;
    foreach ($checks as $c) {
        if (!empty($c['_hard'])) {
            $hard_total++;
            if ($c['passed']) $hard_pass++;
        } else {
            $soft_total++;
            if ($c['passed']) $soft_pass++;
        }
    }
    return [
        'hard_pass' => $hard_pass, 'hard_total' => $hard_total,
        'soft_pass' => $soft_pass, 'soft_total' => $soft_total,
    ];
}

if ($report === null) {
    echo '<div class="lp-audit-empty">Аудит ещё не запускался для этого сегмента. Нажми «Запустить» выше.</div>';
    return;
}

// Determine if aggregate (multisite — has "sites" array) or single-site report
if (isset($report['sites']) && is_array($report['sites'])) {
    // Multisite aggregate
    ?>
    <h2>Сводка по сегментам</h2>
    <table class="lp-audit-table">
        <thead>
            <tr>
                <th>Сегмент</th>
                <th>HTML</th>
                <th>Network</th>
                <th>Schema</th>
                <th>AI</th>
                <th>Hard total</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($report['sites'] as $site):
                // Inject _hard flag from thresholds inline (we have failures with severity but
                // need full hard/total counts — fall back to site-level counts).
                $h = (int) ($site['hard_passed'] ?? 0);
                $ht = (int) ($site['hard_total'] ?? 0);
                $passed = !empty($site['passed']);
                $icon = $passed ? '✅' : '❌';
                ?>
                <tr>
                    <td>
                        <a href="<?php echo esc_url(\add_query_arg([
                            'page' => \LandingConfig\SEOAudit\Admin\MENU_SLUG,
                            'tab' => 'html',
                            'segment' => (string) \LandingConfig\SEOAudit\Admin\host_to_blog_id($site['host'] ?? ''),
                        ], \network_admin_url('admin.php'))); ?>">
                            <?php echo esc_html($site['host'] ?? '?'); ?>
                        </a>
                    </td>
                    <?php
                    $by_cat = _lp_categorize_results($site['results'] ?? []);
                    foreach (['HTML', 'Network', 'Schema', 'AI'] as $cat):
                        $checks = $by_cat[$cat];
                        $total = count($checks);
                        $passed_n = count(array_filter($checks, static fn($c) => !empty($c['passed'])));
                        ?>
                        <td><?php echo $passed_n; ?>/<?php echo $total; ?></td>
                    <?php endforeach; ?>
                    <td><?php echo $icon . ' ' . $h . '/' . $ht; ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <?php
} else {
    // Single-site report
    $by_cat = _lp_categorize_results($report['results'] ?? []);
    $h = (int) ($report['hard_passed'] ?? 0);
    $ht = (int) ($report['hard_total'] ?? 0);
    $passed = !empty($report['passed']);
    ?>
    <h2><?php echo esc_html($report['host'] ?? ''); ?></h2>
    <p>
        <?php echo $passed ? '✅ <strong>PASS</strong>' : '❌ <strong>FAIL</strong>'; ?> —
        Hard gates: <strong><?php echo $h . '/' . $ht; ?></strong>
    </p>

    <table class="lp-audit-table">
        <thead><tr><th>Категория</th><th>Pass / Total</th></tr></thead>
        <tbody>
            <?php foreach (['HTML', 'Network', 'Schema', 'AI'] as $cat):
                $checks = $by_cat[$cat];
                $total = count($checks);
                $passed_n = count(array_filter($checks, static fn($c) => !empty($c['passed'])));
                $tab_key = strtolower($cat === 'AI' ? 'ai_readiness' : $cat);
                ?>
                <tr>
                    <td>
                        <a href="<?php echo esc_url(\add_query_arg([
                            'page' => \LandingConfig\SEOAudit\Admin\MENU_SLUG,
                            'tab' => $tab_key,
                            'segment' => $segment,
                        ], \network_admin_url('admin.php'))); ?>">
                            <?php echo esc_html($cat); ?>
                        </a>
                    </td>
                    <td><?php echo $passed_n . '/' . $total; ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <?php
}
```

- [ ] **Step 2: PHP lint**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/overview.php
```

- [ ] **Step 3: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/overview.php
git commit -m "feat(s2e-e4): overview tab — multisite matrix + per-site summary"
```

---

### Task 9: Category tabs (html / network / schema / ai_readiness)

**Files:**
- Create: 4 files in `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/`

All 4 tabs share identical structure — only filter prefix differs. We use a helper template.

- [ ] **Step 1: Implement html.php**

Path: `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/html.php`

```php
<?php
if (!defined('ABSPATH')) { exit; }

use function LandingConfig\SEOAudit\DeepLinks\build_deep_link;

$prefix_filter = 'H';
$cat_label = 'HTML on-page (H1-H25)';

if ($report === null) {
    echo '<div class="lp-audit-empty">Аудит ещё не запускался. Нажми «Запустить».</div>';
    return;
}

// Resolve results — if aggregate, find the right site (or merge all)
if (isset($report['sites']) && is_array($report['sites'])) {
    // Aggregate: show failures from all sites grouped by host
    $sites = $report['sites'];
} else {
    $sites = [$report];
}

$admin_root = is_multisite() ? \network_site_url('wp-admin/') : \admin_url();

?>
<h2><?php echo esc_html($cat_label); ?></h2>

<?php foreach ($sites as $site): ?>
    <h3 style="margin-top:24px;"><?php echo esc_html($site['host'] ?? '?'); ?></h3>
    <?php
    $blog_id = \LandingConfig\SEOAudit\Admin\host_to_blog_id($site['host'] ?? '') ?? 0;
    $results = $site['results'] ?? [];
    $cat_results = array_filter($results, static fn($r) =>
        str_starts_with((string)($r['id'] ?? ''), $prefix_filter));
    $cat_failures = array_filter($cat_results, static fn($r) => empty($r['passed']));
    if (empty($cat_failures)):
        ?>
        <p>✅ Все проверки этой категории пройдены.</p>
    <?php else: ?>
        <table class="lp-audit-table">
            <thead><tr>
                <th>ID</th><th>Severity</th><th>Описание</th><th>Evidence</th><th>Действие</th>
            </tr></thead>
            <tbody>
            <?php foreach ($cat_failures as $f):
                $deep_link = build_deep_link((string) $f['id'], $blog_id, $admin_root);
                // Severity comes from inline 'severity' field if site_report has it,
                // else fallback to fix_action.type
                $is_hard = !empty($f['severity']) && $f['severity'] === 'hard';
                $row_class = $is_hard ? 'is-hard' : 'is-soft';
                ?>
                <tr class="<?php echo esc_attr($row_class); ?>">
                    <td class="lp-id"><?php echo esc_html((string) $f['id']); ?></td>
                    <td><?php echo $is_hard ? '🔴 hard' : '🟡 soft'; ?></td>
                    <td><?php echo esc_html((string) ($f['desc'] ?? '')); ?></td>
                    <td class="lp-evidence"><?php echo esc_html((string) ($f['evidence'] ?? '')); ?></td>
                    <td>
                        <?php if ($deep_link && !empty($deep_link['url'])): ?>
                            <a class="button" href="<?php echo esc_url($deep_link['url']); ?>" target="_blank">
                                <?php echo esc_html((string) $deep_link['label']); ?>
                            </a>
                        <?php elseif ($deep_link): ?>
                            <span class="lp-suggestion"><?php echo esc_html((string) $deep_link['label']); ?></span>
                        <?php else: ?>
                            <span class="lp-suggestion">—</span>
                        <?php endif; ?>
                    </td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    <?php endif; ?>
<?php endforeach; ?>
```

- [ ] **Step 2: Create network.php, schema.php, ai_readiness.php**

These are near-identical copies of `html.php` — only `$prefix_filter` and `$cat_label` differ.

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
TABS_DIR=skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs
cp "$TABS_DIR/html.php" "$TABS_DIR/network.php"
cp "$TABS_DIR/html.php" "$TABS_DIR/schema.php"
cp "$TABS_DIR/html.php" "$TABS_DIR/ai_readiness.php"

# network.php
sed -i "s/\$prefix_filter = 'H';/\$prefix_filter = 'N';/" "$TABS_DIR/network.php"
sed -i "s/'HTML on-page (H1-H25)'/'Network \/ Infra (N1-N13)'/" "$TABS_DIR/network.php"

# schema.php
sed -i "s/\$prefix_filter = 'H';/\$prefix_filter = 'S';/" "$TABS_DIR/schema.php"
sed -i "s/'HTML on-page (H1-H25)'/'Schema \/ Open Graph (S1-S5)'/" "$TABS_DIR/schema.php"

# ai_readiness.php
sed -i "s/\$prefix_filter = 'H';/\$prefix_filter = 'AI';/" "$TABS_DIR/ai_readiness.php"
sed -i "s/'HTML on-page (H1-H25)'/'AI Readiness (AI1-AI3)'/" "$TABS_DIR/ai_readiness.php"
```

Verify each has correct prefix and label:
```bash
grep -E "prefix_filter|cat_label" $TABS_DIR/*.php
```

Expected: 4 rows for each variable, one per file, with correct values.

- [ ] **Step 3: PHP lint all 4**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
for f in skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/*.php; do
    php -l "$f"
done
```

- [ ] **Step 4: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/
git commit -m "feat(s2e-e4): 4 category tabs (html/network/schema/ai_readiness) with deep-links"
```

---

### Task 10: head-seo-admin.php (settings + OG card + SERP preview)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/preview.js`
- Create: `skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/preview.css`
- Create: `skills/wp-landing-config/tests/test_head_seo_admin_save.php`

- [ ] **Step 1: Write failing test for save handler**

`skills/wp-landing-config/tests/test_head_seo_admin_save.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/head-seo-admin.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: save_settings_for_segment writes options
$saved = \LandingConfig\HeadSEOAdmin\save_settings_for_segment(1, [
    'description' => 'Test description here at least 70 chars long for spec compliance check yes yes',
    'og_image' => 'https://x/og.png',
    'og_type' => 'website',
    'twitter_card' => 'summary_large_image',
    'llms_txt' => "# Test\n\n- [Link](https://x/)",
]);
assert_test($saved === true, 'T1 save_settings returns true');
assert_test(\get_option('landing_seo_description') === 'Test description here at least 70 chars long for spec compliance check yes yes',
    'T1a description saved');
assert_test(\get_option('landing_seo_og_image') === 'https://x/og.png',
    'T1b og_image saved');

// T2: invalid og_type rejected
$saved2 = \LandingConfig\HeadSEOAdmin\save_settings_for_segment(1, [
    'og_type' => 'evil-injected-value',
]);
assert_test(\get_option('landing_seo_og_type') === 'website',
    'T2 invalid og_type defaults to website');

// T3: invalid twitter_card rejected
\LandingConfig\HeadSEOAdmin\save_settings_for_segment(1, ['twitter_card' => 'evil']);
assert_test(\get_option('landing_seo_twitter_card') === 'summary_large_image',
    'T3 invalid twitter_card defaults');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify FAIL**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_head_seo_admin_save.php 2>&1 | tail -5
```

- [ ] **Step 3: Implement head-seo-admin.php**

Path: `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php`

```php
<?php
namespace LandingConfig\HeadSEOAdmin;

if (!defined('ABSPATH')) { exit; }

const MENU_SLUG = 'landing-config-head-seo';
const NETWORK_BLOG_ID = 1;

const VALID_OG_TYPES      = ['website', 'article', 'product'];
const VALID_TWITTER_CARDS = ['summary', 'summary_large_image'];

add_action('network_admin_menu', __NAMESPACE__ . '\\register_menu');
add_action('admin_post_lp_head_seo_save', __NAMESPACE__ . '\\handle_save');
add_action('admin_enqueue_scripts', __NAMESPACE__ . '\\enqueue_assets');

function register_menu(): void {
    \add_submenu_page(
        'landing-config-network',
        'Head & SEO',
        'Head & SEO',
        'manage_network_options',
        MENU_SLUG,
        __NAMESPACE__ . '\\render_page'
    );
}

function enqueue_assets($hook): void {
    if (strpos((string) $hook, MENU_SLUG) === false) return;
    $base = \plugins_url('assets/seo-audit', dirname(__DIR__) . '/landing-config.php');
    \wp_enqueue_style('lp-head-seo-preview', $base . '/preview.css', [], '1.0');
    \wp_enqueue_script('lp-head-seo-preview', $base . '/preview.js', [], '1.0', true);
    \wp_enqueue_media();
}

/**
 * Pure save logic. Sanitizes input. Writes to wp_options in given segment's blog.
 *
 * @return bool always true on success
 */
function save_settings_for_segment(int $segment, array $input): bool {
    $target_blog = ($segment === 0) ? NETWORK_BLOG_ID : $segment;
    $current_blog = \get_current_blog_id();
    $switched = false;
    if (function_exists('switch_to_blog') && $target_blog !== $current_blog) {
        \switch_to_blog($target_blog);
        $switched = true;
    }

    if (isset($input['description'])) {
        \update_option('landing_seo_description', \sanitize_textarea_field((string) $input['description']));
    }
    if (isset($input['og_image'])) {
        \update_option('landing_seo_og_image', \esc_url_raw((string) $input['og_image']));
    }
    if (isset($input['og_type'])) {
        $og_type = (string) $input['og_type'];
        if (!in_array($og_type, VALID_OG_TYPES, true)) $og_type = 'website';
        \update_option('landing_seo_og_type', $og_type);
    }
    if (isset($input['twitter_card'])) {
        $tw = (string) $input['twitter_card'];
        if (!in_array($tw, VALID_TWITTER_CARDS, true)) $tw = 'summary_large_image';
        \update_option('landing_seo_twitter_card', $tw);
    }
    if (isset($input['llms_txt'])) {
        \update_option('landing_seo_llms_txt', (string) $input['llms_txt']);
    }

    if ($switched) \restore_current_blog();
    return true;
}

function load_settings_for_segment(int $segment): array {
    $target_blog = ($segment === 0) ? NETWORK_BLOG_ID : $segment;
    $current_blog = \get_current_blog_id();
    $switched = false;
    if (function_exists('switch_to_blog') && $target_blog !== $current_blog) {
        \switch_to_blog($target_blog);
        $switched = true;
    }
    $out = [
        'description'  => (string) \get_option('landing_seo_description', ''),
        'og_image'     => (string) \get_option('landing_seo_og_image', ''),
        'og_type'      => (string) \get_option('landing_seo_og_type', 'website'),
        'twitter_card' => (string) \get_option('landing_seo_twitter_card', 'summary_large_image'),
        'llms_txt'     => (string) \get_option('landing_seo_llms_txt', ''),
    ];
    if ($switched) \restore_current_blog();
    return $out;
}

function handle_save(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    \check_admin_referer('lp_head_seo_save');
    $segment = (int) ($_POST['segment'] ?? 0);

    save_settings_for_segment($segment, [
        'description'  => $_POST['description']  ?? '',
        'og_image'     => $_POST['og_image']     ?? '',
        'og_type'      => $_POST['og_type']      ?? '',
        'twitter_card' => $_POST['twitter_card'] ?? '',
        'llms_txt'     => $_POST['llms_txt']     ?? '',
    ]);

    \wp_safe_redirect(\add_query_arg([
        'page' => MENU_SLUG, 'segment' => $segment, 'saved' => 1,
    ], \network_admin_url('admin.php')));
    exit;
}

function render_segment_selector(int $current): void {
    ?>
    <select name="segment_selector" onchange="window.location.href='<?php echo esc_js(\network_admin_url('admin.php?page=' . MENU_SLUG)); ?>&segment=' + this.value">
        <option value="0" <?php selected($current, 0); ?>>Network default</option>
        <?php foreach (\get_sites(['fields' => 'ids']) as $bid):
            $url = \get_site_url((int) $bid); ?>
            <option value="<?php echo (int) $bid; ?>" <?php selected($current, (int) $bid); ?>>
                blog #<?php echo (int) $bid; ?> — <?php echo esc_html((string) $url); ?>
            </option>
        <?php endforeach; ?>
    </select>
    <?php
}

function render_page(): void {
    if (!\current_user_can('manage_network_options')) wp_die('forbidden');
    $segment = isset($_GET['segment']) ? (int) $_GET['segment'] : 0;
    $settings = load_settings_for_segment($segment);
    $site_name = \get_bloginfo('name');
    ?>
    <div class="wrap">
        <h1>Head & SEO</h1>

        <?php if (!empty($_GET['saved'])): ?>
            <div class="notice notice-success is-dismissible"><p>Сохранено.</p></div>
        <?php endif; ?>

        <div style="margin-bottom: 16px;">
            <label>Сегмент: </label>
            <?php render_segment_selector($segment); ?>
        </div>

        <div style="display:flex; gap:24px; align-items:flex-start;">
          <div style="flex: 1 1 60%; min-width:0;">
            <form method="post" action="<?php echo esc_url(\admin_url('admin-post.php')); ?>">
                <?php \wp_nonce_field('lp_head_seo_save'); ?>
                <input type="hidden" name="action" value="lp_head_seo_save">
                <input type="hidden" name="segment" value="<?php echo (int) $segment; ?>">

                <h2>Description</h2>
                <textarea name="description" rows="3" class="large-text" id="lp-input-description"
                          placeholder="≥70 символов"><?php echo esc_textarea($settings['description']); ?></textarea>
                <p class="description"><span id="lp-char-count">0</span> символов (рекомендация: 70-320)</p>

                <h2>Open Graph Image</h2>
                <input type="text" name="og_image" id="lp-input-og-image" class="regular-text"
                       value="<?php echo esc_attr($settings['og_image']); ?>"
                       placeholder="https://example.com/og.png">
                <button type="button" class="button" id="lp-pick-og-image">Выбрать из медиа</button>

                <h2>Open Graph Type</h2>
                <select name="og_type" id="lp-input-og-type">
                    <?php foreach (VALID_OG_TYPES as $t): ?>
                        <option value="<?php echo esc_attr($t); ?>" <?php selected($settings['og_type'], $t); ?>>
                            <?php echo esc_html($t); ?>
                        </option>
                    <?php endforeach; ?>
                </select>

                <h2>Twitter Card</h2>
                <select name="twitter_card">
                    <?php foreach (VALID_TWITTER_CARDS as $t): ?>
                        <option value="<?php echo esc_attr($t); ?>" <?php selected($settings['twitter_card'], $t); ?>>
                            <?php echo esc_html($t); ?>
                        </option>
                    <?php endforeach; ?>
                </select>

                <h2 id="llms-txt">llms.txt content</h2>
                <p class="description">Markdown по <a href="https://llmstxt.org" target="_blank">llmstxt.org spec</a>.
                   Пусто → /llms.txt не отдаётся.</p>
                <textarea name="llms_txt" rows="10" class="large-text"
                          placeholder="# Site name&#10;&#10;> Description&#10;&#10;## Resources&#10;- [Title](URL): Note"><?php echo esc_textarea($settings['llms_txt']); ?></textarea>

                <p style="margin-top: 20px;">
                    <button type="submit" class="button button-primary">Сохранить</button>
                </p>
            </form>
          </div>

          <aside style="flex: 0 0 380px;">
            <h2>Preview</h2>

            <h3>OG-карточка</h3>
            <div class="lp-preview-og-card">
                <div class="lp-preview-og-image" id="lp-preview-og-image-area"
                     <?php if ($settings['og_image']): ?>
                       style="background-image:url('<?php echo esc_url($settings['og_image']); ?>')"
                     <?php endif; ?>>
                </div>
                <div class="lp-preview-og-meta">
                    <div class="lp-preview-og-domain"><?php echo esc_html(parse_url(\home_url(), PHP_URL_HOST) ?? ''); ?></div>
                    <div class="lp-preview-og-title" id="lp-preview-og-title"><?php echo esc_html($site_name); ?></div>
                    <div class="lp-preview-og-desc" id="lp-preview-og-desc"><?php echo esc_html($settings['description']); ?></div>
                </div>
            </div>

            <h3 style="margin-top: 24px;">SERP-сниппет</h3>
            <div class="lp-preview-serp">
                <div class="lp-preview-serp-breadcrumb"><?php echo esc_html(parse_url(\home_url(), PHP_URL_HOST) ?? ''); ?></div>
                <div class="lp-preview-serp-title" id="lp-preview-serp-title"><?php echo esc_html($site_name); ?></div>
                <div class="lp-preview-serp-desc" id="lp-preview-serp-desc"><?php echo esc_html($settings['description']); ?></div>
            </div>
          </aside>
        </div>
    </div>
    <?php
}
```

- [ ] **Step 4: Create preview.css**

Path: `skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/preview.css`

```css
/* OG card — Facebook/Telegram style */
.lp-preview-og-card {
  background: #fff;
  border: 1px solid #dadce0;
  border-radius: 8px;
  overflow: hidden;
  max-width: 380px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.lp-preview-og-image {
  width: 100%;
  height: 200px;
  background: #f0f0f1 center/cover no-repeat;
  position: relative;
}
.lp-preview-og-image:empty::after {
  content: "Нет изображения";
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 13px;
}
.lp-preview-og-meta { padding: 12px 14px; }
.lp-preview-og-domain {
  text-transform: uppercase;
  color: #6b7280;
  font-size: 11px;
  letter-spacing: 0.05em;
}
.lp-preview-og-title {
  margin: 4px 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.lp-preview-og-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* SERP — Google style */
.lp-preview-serp {
  font-family: arial, sans-serif;
  max-width: 600px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #dadce0;
  border-radius: 8px;
}
.lp-preview-serp-breadcrumb {
  color: #006621;
  font-size: 12px;
}
.lp-preview-serp-title {
  color: #1a0dab;
  font-size: 18px;
  font-weight: 400;
  line-height: 1.3;
  margin: 4px 0 4px;
  cursor: pointer;
}
.lp-preview-serp-title:hover { text-decoration: underline; }
.lp-preview-serp-desc {
  color: #4d5156;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

- [ ] **Step 5: Create preview.js**

Path: `skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/preview.js`

```javascript
/* Live preview updater for Head & SEO admin */
(function () {
    'use strict';
    var $desc = document.getElementById('lp-input-description');
    var $ogImage = document.getElementById('lp-input-og-image');
    var $ogTitleOut = document.getElementById('lp-preview-og-title');
    var $ogDescOut = document.getElementById('lp-preview-og-desc');
    var $ogImageOut = document.getElementById('lp-preview-og-image-area');
    var $serpTitleOut = document.getElementById('lp-preview-serp-title');
    var $serpDescOut = document.getElementById('lp-preview-serp-desc');
    var $charCount = document.getElementById('lp-char-count');
    var $pickBtn = document.getElementById('lp-pick-og-image');

    function update() {
        var descText = $desc ? $desc.value : '';
        if ($ogDescOut) $ogDescOut.textContent = descText.slice(0, 200);
        if ($serpDescOut) $serpDescOut.textContent = descText.slice(0, 200);
        if ($charCount) $charCount.textContent = String(descText.length);

        var imgUrl = $ogImage ? $ogImage.value : '';
        if ($ogImageOut) {
            if (imgUrl) {
                $ogImageOut.style.backgroundImage = "url('" + imgUrl.replace(/'/g, "%27") + "')";
            } else {
                $ogImageOut.style.backgroundImage = '';
            }
        }
    }

    if ($desc) $desc.addEventListener('input', update);
    if ($ogImage) $ogImage.addEventListener('input', update);

    // Media picker — uses wp.media (loaded via wp_enqueue_media)
    if ($pickBtn && window.wp && window.wp.media) {
        $pickBtn.addEventListener('click', function (e) {
            e.preventDefault();
            var frame = wp.media({
                title: 'Выбрать OG-image',
                button: { text: 'Использовать это изображение' },
                multiple: false,
                library: { type: 'image' },
            });
            frame.on('select', function () {
                var att = frame.state().get('selection').first().toJSON();
                if ($ogImage) {
                    $ogImage.value = att.url;
                    update();
                }
            });
            frame.open();
        });
    }

    update();
})();
```

- [ ] **Step 6: Run — verify PASS** (3 tests):
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_head_seo_admin_save.php 2>&1 | tail -5
```

- [ ] **Step 7: PHP + JS lint**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php
node -c skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/preview.js
```

- [ ] **Step 8: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php \
        skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit/preview.{css,js} \
        skills/wp-landing-config/tests/test_head_seo_admin_save.php
git commit -m "feat(s2e-e4): head-seo admin page + OG card + SERP preview + 3 tests"
```

---

### Task 11: head-seo.php injector → cascade-aware read (+ tests)

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php`
- Create: `skills/wp-landing-config/tests/test_head_seo_cascade.php`

- [ ] **Step 1: Write failing test**

`skills/wp-landing-config/tests/test_head_seo_cascade.php`:

```php
<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once dirname(__DIR__) . '/mu-plugin/landing-config/includes/head-seo.php';

$tests = 0; $failures = 0;
function assert_test($cond, $msg) {
    global $tests, $failures;
    $tests++;
    if (!$cond) { $failures++; echo "FAIL: $msg\n"; }
    else { echo "PASS: $msg\n"; }
}

// T1: resolve_setting_cascade — site-only wins
$GLOBALS['_mock_blog_options'][3]['landing_seo_description'] = 'site-3-desc';
$GLOBALS['_mock_blog_options'][1]['landing_seo_description'] = 'network-desc';
$val = \LandingConfig\HeadSEO\resolve_setting_cascade('landing_seo_description', 3);
assert_test($val === 'site-3-desc', 'T1 site value wins over network');

// T2: empty site → network fallback
unset($GLOBALS['_mock_blog_options'][3]['landing_seo_description']);
$val2 = \LandingConfig\HeadSEO\resolve_setting_cascade('landing_seo_description', 3);
assert_test($val2 === 'network-desc', 'T2 falls back to network when site empty');

// T3: both empty → empty string
unset($GLOBALS['_mock_blog_options'][1]['landing_seo_description']);
$val3 = \LandingConfig\HeadSEO\resolve_setting_cascade('landing_seo_description', 3);
assert_test($val3 === '', 'T3 returns empty when nothing set');

echo "$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
```

- [ ] **Step 2: Run — verify FAIL**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_head_seo_cascade.php 2>&1 | tail -5
```

- [ ] **Step 3: Modify head-seo.php to add cascade reader**

In `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php`, add at the top (after namespace + constants):

```php
const NETWORK_BLOG_ID = 1;

/**
 * Cascade-aware read: site override → network default → empty.
 *
 * @param string $option_key e.g. 'landing_seo_description'
 * @param int $blog_id Current blog id
 * @return string Always a string (empty if nothing set)
 */
function resolve_setting_cascade(string $option_key, int $blog_id): string {
    // 1. Try site override
    if ($blog_id !== NETWORK_BLOG_ID && function_exists('switch_to_blog')) {
        \switch_to_blog($blog_id);
        $site_val = (string) \get_option($option_key, '');
        \restore_current_blog();
        if ($site_val !== '') return $site_val;
    } else {
        $site_val = (string) \get_option($option_key, '');
        if ($site_val !== '') return $site_val;
    }

    // 2. Fall back to network default
    if (function_exists('switch_to_blog')) {
        \switch_to_blog(NETWORK_BLOG_ID);
        $network_val = (string) \get_option($option_key, '');
        \restore_current_blog();
        return $network_val;
    }
    return '';
}
```

Then in the `emit()` function, replace direct `get_option` calls with `resolve_setting_cascade`:

Find:
```php
    $description = (string) \get_option(OPTION_DESCRIPTION, '');
```
Replace with:
```php
    $description = resolve_setting_cascade(OPTION_DESCRIPTION, \get_current_blog_id());
```

Same for `OPTION_OG_IMAGE`, `OPTION_OG_TYPE`, `OPTION_TW_CARD`:

```php
    $og_image = resolve_setting_cascade(OPTION_OG_IMAGE, \get_current_blog_id());
    if ($og_image === '') {
        $site_icon = \get_site_icon_url(512);
        if ($site_icon) $og_image = $site_icon;
    }
    $og_type = resolve_setting_cascade(OPTION_OG_TYPE, \get_current_blog_id()) ?: 'website';
    $tw_card = resolve_setting_cascade(OPTION_TW_CARD, \get_current_blog_id()) ?: 'summary_large_image';
```

- [ ] **Step 4: Run — verify PASS**:
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php skills/wp-landing-config/tests/test_head_seo_cascade.php 2>&1 | tail -5
```

- [ ] **Step 5: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php \
        skills/wp-landing-config/tests/test_head_seo_cascade.php
git commit -m "feat(s2e-e4): head-seo cascade read — site override → network default + 3 tests"
```

---

### Task 12: Wire new modules into landing-config.php loader

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`

- [ ] **Step 1: Find loader location**

```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
grep -n "head-seo.php\|cookie-banner" skills/wp-landing-config/mu-plugin/landing-config/landing-config.php | head -8
```

Note: there should already be `require_once __DIR__ . '/includes/head-seo.php';` from previous commit. We add new modules around that line.

- [ ] **Step 2: Add SEO Audit + Head-SEO admin requires**

In `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`, find the line:
```php
// SEO head injector (meta description + Open Graph + favicon)
require_once __DIR__ . '/includes/head-seo.php';
```

Replace with:
```php
// SEO head injector (meta description + Open Graph + favicon)
require_once __DIR__ . '/includes/head-seo.php';

// S2-E.4: SEO Audit dashboard + Head & SEO admin
require_once __DIR__ . '/includes/seo-audit/audit-runner.php';
require_once __DIR__ . '/includes/seo-audit/deep-links.php';
if (\is_admin() || \is_network_admin()) {
    require_once __DIR__ . '/includes/seo-audit/admin-network.php';
    require_once __DIR__ . '/includes/head-seo-admin.php';
}
```

- [ ] **Step 3: PHP lint**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php -l skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
```

- [ ] **Step 4: Run all PHP tests — regression**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
for t in skills/wp-landing-config/tests/test_*.php; do
    echo "=== $(basename $t) ==="
    php "$t" 2>&1 | tail -1
done
```

Expected: existing pre-S2-E.4 tests still pass (no regression).

- [ ] **Step 5: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(s2e-e4): wire seo-audit + head-seo-admin in mu-plugin loader"
```

---

### Task 13: CLAUDE.md docs

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Find S2-E.1 section**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
grep -n "S2-E.1" CLAUDE.md
```

- [ ] **Step 2: Append S2-E.4 section after S2-E.1**

Find the line ending S2-E.1 section (likely `См. [spec...](docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md)` or similar). Insert after:

```markdown

### S2-E.4 — Audit Dashboard + Head & SEO Settings (2026-05-22)

Network admin интерфейс для запуска audit и редактирования SEO-параметров:

- **Меню `Лендинг → Аудит`** с табами Обзор / HTML / Network / Schema / AI readiness.
  Селектор сегмента (all/0/N) переключает между multisite-aggregate, network default
  и конкретными subsites. Кнопка «Запустить» — shell_exec в Python skill `seo-tech-audit`.
- **Меню `Лендинг → Head & SEO`** — settings page (description, OG image picker,
  OG type, Twitter card, llms.txt content) с **live preview** OG-карточки
  (стиль Facebook/Telegram) и SERP-сниппета (стиль Google).
- **Cascade** для head-seo settings (network default + per-site override) — тот же
  паттерн что Cookie-banner (`switch_to_blog(NETWORK_BLOG_ID)`).
- **Deep-links на failures** — каждый failed check в admin получает кнопку «Открыть»
  ведущую в нужное место WP admin (settings page / post editor / Customizer).
  Каталог fix-actions: 46 записей (43 + AI1/AI2/AI3), генерится Python'ом в JSON
  для PHP consumption.
- **AI readiness (3 проверки)** — `AI1` llms.txt валиден, `AI2` JSON-LD
  Organization/Product/FAQ, `AI3` body содержит ≥1KB текста без JS.
  Добавлено в Python skill `seo-tech-audit`.
- **CLI расширение:** `run-audit.py --hosts-file <file>` (multisite batch
  без `.landing-state.yaml`), `--with-fix-hints` (enrich failures с
  fix_action metadata).
- **Out of scope (S2-E.4):** auto-fix кнопки (только deep-links), cron,
  history snapshots, page-level overrides.

См. [spec](docs/superpowers/specs/2026-05-22-s2e-e4-audit-dashboard-design.md)
и [plan](docs/superpowers/plans/2026-05-22-s2e-e4-audit-dashboard-plan.md).
```

- [ ] **Step 3: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add CLAUDE.md
git commit -m "docs(s2e-e4): CLAUDE.md секция Audit Dashboard + Head&SEO Settings"
```

---

### Task 14: Final regression + merge to main

- [ ] **Step 1: Full Python test sweep**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
python -m pytest skills/seo-tech-audit/tests/ -v 2>&1 | tail -15
```

Expected: original 43 tests + 8 new AI + 7 fix_actions + 5 hosts-file/fix-hints = ~63 tests, 0 failures.

- [ ] **Step 2: Full PHP test sweep**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
for t in skills/wp-landing-config/tests/test_*.php; do
    echo "=== $(basename $t) ==="
    php "$t" 2>&1 | tail -1
done
```

Expected: all new SeOAudit tests pass, no regression in cookie-banner/cta/integrations/lead tests.

- [ ] **Step 3: PHP lint all new files**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
for f in skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/*.php \
         skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/*.php \
         skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php; do
    php -l "$f"
done
```

Expected: all "No syntax errors".

- [ ] **Step 4: Merge to main + push**
```bash
cd D:/AI_TEAMS/landing_system
git checkout main
git merge --no-ff s2e-e4-audit-dashboard -m "merge: S2-E.4 — Audit Dashboard + Head&SEO Settings + AI checks"
git push origin main
```

- [ ] **Step 5: Deploy mu-plugin updates to dubai-avto-liza (manual verification)**

```bash
cd D:/AI_TEAMS/Lendings/dubai-avto-liza
source .env
# scp the changed mu-plugin files
scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no -r \
    D:/AI_TEAMS/landing_system/skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit \
    "$BEGET_USER@$BEGET_HOST:$BEGET_PATH/wp-content/mu-plugins/landing-config/includes/"
scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no \
    D:/AI_TEAMS/landing_system/skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php \
    D:/AI_TEAMS/landing_system/skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php \
    D:/AI_TEAMS/landing_system/skills/wp-landing-config/mu-plugin/landing-config/landing-config.php \
    "$BEGET_USER@$BEGET_HOST:$BEGET_PATH/wp-content/mu-plugins/landing-config/includes/"
scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no -r \
    D:/AI_TEAMS/landing_system/skills/wp-landing-config/mu-plugin/landing-config/assets/seo-audit \
    "$BEGET_USER@$BEGET_HOST:$BEGET_PATH/wp-content/mu-plugins/landing-config/assets/"
# Also rsync the python skill so audit-runner.php can find it
rsync_dest="$BEGET_PATH/wp-content/mu-plugins/landing-config/../seo-tech-audit/"
ssh -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no "$BEGET_USER@$BEGET_HOST" "mkdir -p $rsync_dest"
scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no -r \
    D:/AI_TEAMS/landing_system/skills/seo-tech-audit/{scripts,config} \
    "$BEGET_USER@$BEGET_HOST:$rsync_dest"
ssh -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no "$BEGET_USER@$BEGET_HOST" \
    "cd $BEGET_PATH && /usr/local/bin/php8.2 /usr/local/bin/wp-cli.phar --url=$WP_SUBSITE_URL cache flush"
```

Manual smoke (browser):
1. Open `https://ailexi.ru/wp-admin/network/admin.php?page=landing-config-seo-audit`
2. Verify menu and tabs render
3. Click «Запустить для этого сегмента» → expect spinner ~60-120 сек → results
4. Verify deep-link buttons on at least one failure
5. Open `https://ailexi.ru/wp-admin/network/admin.php?page=landing-config-head-seo`
6. Verify form + live preview (type in description → SERP/OG updates)

---

## Self-Review

**Spec coverage check:**

| Spec section | Plan task | Covered? |
|---|---|---|
| §Architecture · Python ai_readiness.py | T1 | ✅ |
| §Architecture · fix_actions.py + JSON export | T2 | ✅ |
| §Architecture · run-audit.py --hosts-file | T3 | ✅ |
| §Architecture · run-audit.py --with-fix-hints + AI integration | T4 | ✅ |
| §Architecture · PHP audit-runner.php (shell_exec) | T5 | ✅ |
| §Architecture · admin-network.php + admin.css | T6 | ✅ |
| §Architecture · deep-links.php | T7 | ✅ |
| §Architecture · tabs/overview.php | T8 | ✅ |
| §Architecture · tabs/{html,network,schema,ai_readiness}.php | T9 | ✅ |
| §Architecture · head-seo-admin.php + preview.{js,css} | T10 | ✅ |
| §Architecture · head-seo.php cascade-aware | T11 | ✅ |
| §Architecture · loader wiring | T12 | ✅ |
| §Acceptance · Меню «Аудит» 5 tabs | T6 + T8 + T9 | ✅ |
| §Acceptance · Селектор сегмента all/0/N | T6 | ✅ |
| §Acceptance · multisite-run обходит все subsites | T6 (get_all_hosts) | ✅ |
| §Acceptance · per-failure deep-link | T7 + T9 | ✅ |
| §Acceptance · Head & SEO menu + cascade | T10 + T11 | ✅ |
| §Acceptance · OG + SERP preview live | T10 (preview.js) | ✅ |
| §Acceptance · cascade save в правильный blog | T10 (save_settings_for_segment) | ✅ |
| §Acceptance · Python --hosts-file + --with-fix-hints | T3 + T4 | ✅ |
| §Acceptance · 3 AI checks + 6 unit tests | T1 (8 tests) | ✅ exceeded |
| §Acceptance · dubai-avto-liza manual smoke | T14 step 5 | ✅ |
| §Acceptance · stage-11 gate regression | T12 step 4 + T14 step 2 | ✅ |
| §llms.txt rewrite rule | **GAP** | ❌ |

**Gap found:** Spec §"llms.txt rewrite rule" says mu-plugin should register `add_rewrite_rule` to serve `/llms.txt` from `landing_seo_llms_txt` option. Plan doesn't include this. **Adding Task 11.5 — но проще встроить в head-seo-admin.php Task 10. Поскольку Task 10 уже большой, добавляю Task 11.5 ниже.**

### Task 11.5: llms.txt rewrite rule

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/llms-txt-rewrite.php`

- [ ] **Step 1: Create file**

Path: `skills/wp-landing-config/mu-plugin/landing-config/includes/llms-txt-rewrite.php`

```php
<?php
namespace LandingConfig\LlmsTxt;

if (!defined('ABSPATH')) { exit; }

add_action('init', __NAMESPACE__ . '\\register_rewrite');
add_filter('query_vars', __NAMESPACE__ . '\\add_query_var');
add_action('template_redirect', __NAMESPACE__ . '\\serve');

function register_rewrite(): void {
    \add_rewrite_rule('^llms\\.txt$', 'index.php?lp_llms_txt=1', 'top');
}

function add_query_var(array $vars): array {
    $vars[] = 'lp_llms_txt';
    return $vars;
}

function serve(): void {
    if (!\get_query_var('lp_llms_txt')) return;
    $content = (string) \get_option('landing_seo_llms_txt', '');
    if ($content === '') {
        \status_header(404);
        exit;
    }
    \status_header(200);
    \header('Content-Type: text/markdown; charset=utf-8');
    echo $content;
    exit;
}
```

- [ ] **Step 2: Wire in loader**

In `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`, after the head-seo require, add:

```php
require_once __DIR__ . '/includes/llms-txt-rewrite.php';
```

- [ ] **Step 3: PHP lint**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
php -l skills/wp-landing-config/mu-plugin/landing-config/includes/llms-txt-rewrite.php
```

- [ ] **Step 4: Commit**
```bash
cd D:/AI_TEAMS/landing_system/.worktrees/s2e-e4-audit-dashboard
git add skills/wp-landing-config/mu-plugin/landing-config/includes/llms-txt-rewrite.php \
        skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(s2e-e4): llms.txt rewrite rule — serves landing_seo_llms_txt option content"
```

NOTE: After deploy, run `wp rewrite flush` once on the server (or visit Settings → Permalinks → Save).

---

**Placeholder scan:** no TBD/TODO. Each step has concrete code or command.

**Type consistency:**
- `build_python_command($opts, $python_bin, $script_path)` — signature consistent in T5
- `build_deep_link($check_id, $blog_id, $admin_root)` — consistent T7
- `save_settings_for_segment($segment, $input)` — consistent T10
- `resolve_setting_cascade($option_key, $blog_id)` — consistent T11
- `cache_key($blog_id)`, `aggregate_cache_key()`, `timestamp_key($blog_id)` — consistent T5
- `MENU_SLUG` constants — namespaced per module, no collision (`landing-config-seo-audit`, `landing-config-head-seo`)
- `VALID_TABS` — consistent set in admin-network.php (T6) and used in tabs/ files (T9)
- Python `CHECK_ID` keys (H1-H25, N1-N13, S1-S5, AI1-AI3) — consistent across thresholds.yaml (T1), fix_actions.py CATALOG (T2), ai_readiness.py (T1)
- Storage option names (`landing_seo_*`) — consistent T10 / T11 / T11.5 / head-seo.php (pre-existing)
