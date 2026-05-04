# Stage Gates & Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a hard-gated workflow on top of landing-system: a one-time onboarding wizard validates every API/dependency, and per-stage gate-checks prevent skipping stages in any project.

**Architecture:** Three pieces — (1) Python API-validators with mocked HTTP unit tests; (2) bash onboarding wizard that aggregates validators and writes a `~/.landing-system/setup_complete` flag; (3) declarative `config/stage-gates.yaml` plus `scripts/gate-check.sh` runner that reads/writes per-project `.landing-state.yaml` and is invoked from every `/landing-*` command.

**Tech Stack:** Python 3.10+ (`requests`, `pytest`, `responses`), bash, bats-core, yq, PyYAML. No new runtime services; everything is local-script.

---

## File Structure

**New files:**
- `tools/api_validators/__init__.py` — re-exports
- `tools/api_validators/base.py` — `ValidationResult` dataclass + helper
- `tools/api_validators/{firecrawl,pexels,unsplash,pixabay,huggingface,whatthefont,yandex_wordstat,yandex_metrika,telegram,amocrm,bitrix24,beget_ssh,beget_api,cloudflare,regru}.py` — 15 validators
- `tools/api_validators/aggregate.py` — runs all validators, returns summary
- `tests/api_validators/test_{service}.py` — 15 test files
- `tests/api_validators/conftest.py` — pytest fixtures
- `scripts/wizard.sh` — interactive onboarding flow
- `scripts/validate-all.sh` — thin shell wrapper around `aggregate.py`
- `scripts/gate-check.sh` — per-stage runner
- `scripts/gate-state.sh` — `.landing-state.yaml` read/write helper
- `scripts/setup-flag.sh` — `~/.landing-system/setup_complete` helper
- `config/stage-gates.yaml` — declarative checks per stage
- `template/.landing-state.yaml` — initial state for new projects
- `commands/landing-onboarding.md` — slash command
- `agents/onboarding-guide.md` — wizard agent
- `skills/landing-onboarding/SKILL.md`
- `docs/SETUP.md` — text tutorial
- `tests/onboarding/test-wizard.bats`
- `tests/gate-check/test-gate-check.bats`
- `tests/gate-check/test-gate-state.bats`
- `tests/e2e/test-skip-prevention.bats`

**Modified files:**
- `.env.example` — add 15+ keys
- `requirements.txt` — add `requests`, `responses`, `pytest`
- `scripts/preflight.sh` — delegate to `gate-check.sh --stage 00`
- `commands/landing-new.md` and 15 other `/landing-*` commands — prepend gate-check call
- `agents/landing-orchestrator.md` — enforce `.landing-state.yaml`
- `README.md`, `CLAUDE.md` — describe onboarding + lock
- `package.json` — add `test:python` and `test:onboarding` scripts (already present, just verify)

---

# Phase 1 — `.env.example` + API Validators

## Task 1.1: Set up Python deps and folder structure

**Files:**
- Modify: `requirements.txt`
- Create: `tools/api_validators/__init__.py`
- Create: `tests/api_validators/__init__.py`
- Create: `tests/api_validators/conftest.py`

- [ ] **Step 1: Add Python deps to `requirements.txt`**

Replace contents of `requirements.txt`:

```
pyyaml>=6.0
jinja2>=3.1
requests>=2.31
pillow>=10.0
pytest>=7.4
responses>=0.24
```

- [ ] **Step 2: Install deps**

Run: `pip install -r requirements.txt`
Expected: all 6 packages installed.

- [ ] **Step 3: Create empty `__init__.py` files**

```bash
mkdir -p tools/api_validators tests/api_validators
touch tools/api_validators/__init__.py tests/api_validators/__init__.py
```

- [ ] **Step 4: Create pytest fixture file**

`tests/api_validators/conftest.py`:

```python
import pytest


@pytest.fixture
def clean_env(monkeypatch):
    """Removes all API-related env vars before test."""
    keys = [
        "FIRECRAWL_API_KEY", "PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY",
        "PIXABAY_API_KEY", "HUGGINGFACE_TOKEN", "WHATTHEFONT_API_KEY",
        "YANDEX_OAUTH_TOKEN", "YANDEX_METRIKA_OAUTH", "YM_COUNTER_ID",
        "TG_BOT_TOKEN", "TG_CHAT_ID", "AMOCRM_API_KEY", "AMOCRM_SUBDOMAIN",
        "BITRIX24_WEBHOOK_URL", "BEGET_USER", "BEGET_HOST",
        "BEGET_API_LOGIN", "BEGET_API_PASSWORD",
        "CLOUDFLARE_API_TOKEN", "REGRU_API_USERNAME", "REGRU_API_PASSWORD",
    ]
    for k in keys:
        monkeypatch.delenv(k, raising=False)
    return monkeypatch
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tools/api_validators/__init__.py tests/api_validators/__init__.py tests/api_validators/conftest.py
git commit -m "chore(phase-1): set up python deps and api_validators skeleton"
```

---

## Task 1.2: Base validator interface

**Files:**
- Create: `tools/api_validators/base.py`
- Create: `tests/api_validators/test_base.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_base.py`:

```python
from tools.api_validators.base import ValidationResult


def test_validation_result_is_dataclass():
    r = ValidationResult(is_valid=True, message="ok", service="x")
    assert r.is_valid is True
    assert r.message == "ok"
    assert r.service == "x"


def test_validation_result_bool():
    assert bool(ValidationResult(True, "ok", "x")) is True
    assert bool(ValidationResult(False, "fail", "x")) is False


def test_validation_result_str():
    r = ValidationResult(True, "OK", "firecrawl")
    assert "firecrawl" in str(r)
    assert "OK" in str(r)
```

- [ ] **Step 2: Run test — should fail**

Run: `pytest tests/api_validators/test_base.py -v`
Expected: `ImportError: No module named 'tools.api_validators.base'`

- [ ] **Step 3: Implement**

`tools/api_validators/base.py`:

```python
from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    message: str
    service: str

    def __bool__(self) -> bool:
        return self.is_valid

    def __str__(self) -> str:
        prefix = "✅" if self.is_valid else "❌"
        return f"{prefix} {self.service}: {self.message}"
```

- [ ] **Step 4: Run test — should pass**

Run: `pytest tests/api_validators/test_base.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/base.py tests/api_validators/test_base.py
git commit -m "feat(phase-1): ValidationResult dataclass with bool/str protocols"
```

---

## Task 1.3: Expand `.env.example`

**Files:**
- Modify: `.env.example`

- [ ] **Step 1: Replace `.env.example` with full version**

Overwrite `.env.example`:

```env
# ─────────── ПАРСИНГ И РЕСЁРЧ ───────────
FIRECRAWL_API_KEY=

# ─────────── СТОКОВЫЕ ФОТО (хотя бы один) ───────────
PEXELS_API_KEY=
UNSPLASH_ACCESS_KEY=
PIXABAY_API_KEY=

# ─────────── ГЕНЕРАЦИЯ КАРТИНОК (опционально) ───────────
HUGGINGFACE_TOKEN=

# ─────────── ШРИФТЫ (опционально) ───────────
WHATTHEFONT_API_KEY=

# ─────────── SEO ───────────
YANDEX_OAUTH_TOKEN=

# ─────────── АНАЛИТИКА ───────────
YM_COUNTER_ID=
YANDEX_METRIKA_OAUTH=
GTM_CONTAINER_ID=

# ─────────── CRM (хотя бы один) ───────────
AMOCRM_API_KEY=
AMOCRM_SUBDOMAIN=
BITRIX24_WEBHOOK_URL=

# ─────────── УВЕДОМЛЕНИЯ ───────────
TG_BOT_TOKEN=
TG_CHAT_ID=

# ─────────── ДЕПЛОЙ — Бегет ───────────
BEGET_USER=
BEGET_HOST=srv123456.beget.ru
BEGET_PATH=/home/username/public_html
BEGET_API_LOGIN=
BEGET_API_PASSWORD=

# ─────────── DNS-альтернативы (опционально) ───────────
CLOUDFLARE_API_TOKEN=
REGRU_API_USERNAME=
REGRU_API_PASSWORD=
```

- [ ] **Step 2: Commit**

```bash
git add .env.example
git commit -m "feat(phase-1): expand .env.example to all spec keys"
```

---

## Task 1.4: Firecrawl validator

**Files:**
- Create: `tools/api_validators/firecrawl.py`
- Create: `tests/api_validators/test_firecrawl.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_firecrawl.py`:

```python
import responses
from tools.api_validators import firecrawl

URL = "https://api.firecrawl.dev/v0/credits"


def test_missing_key(clean_env):
    r = firecrawl.validate()
    assert not r.is_valid
    assert "FIRECRAWL_API_KEY" in r.message


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("FIRECRAWL_API_KEY", "test-key")
    responses.add(responses.GET, URL, json={"credits": 500}, status=200)
    r = firecrawl.validate()
    assert r.is_valid
    assert r.service == "firecrawl"


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("FIRECRAWL_API_KEY", "bad")
    responses.add(responses.GET, URL, status=401)
    r = firecrawl.validate()
    assert not r.is_valid
    assert "401" in r.message
```

- [ ] **Step 2: Run test — should fail**

Run: `pytest tests/api_validators/test_firecrawl.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement**

`tools/api_validators/firecrawl.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.firecrawl.dev/v0/credits"


def validate() -> ValidationResult:
    key = os.getenv("FIRECRAWL_API_KEY")
    if not key:
        return ValidationResult(False, "FIRECRAWL_API_KEY not set in .env", "firecrawl")
    try:
        r = requests.get(URL, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, f"OK ({r.json().get('credits', '?')} credits)", "firecrawl")
        return ValidationResult(False, f"HTTP {r.status_code}: {r.text[:120]}", "firecrawl")
    except Exception as e:
        return ValidationResult(False, str(e), "firecrawl")
```

- [ ] **Step 4: Run test — should pass**

Run: `pytest tests/api_validators/test_firecrawl.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/firecrawl.py tests/api_validators/test_firecrawl.py
git commit -m "feat(phase-1): firecrawl api validator"
```

---

## Task 1.5: Pexels validator

**Files:**
- Create: `tools/api_validators/pexels.py`
- Create: `tests/api_validators/test_pexels.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_pexels.py`:

```python
import responses
from tools.api_validators import pexels

URL = "https://api.pexels.com/v1/search?query=test&per_page=1"


def test_missing_key(clean_env):
    r = pexels.validate()
    assert not r.is_valid
    assert "PEXELS_API_KEY" in r.message


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("PEXELS_API_KEY", "test-key")
    responses.add(responses.GET, URL, json={"photos": []}, status=200)
    r = pexels.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("PEXELS_API_KEY", "bad")
    responses.add(responses.GET, URL, status=401)
    r = pexels.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run test — fail**

Run: `pytest tests/api_validators/test_pexels.py -v`

- [ ] **Step 3: Implement**

`tools/api_validators/pexels.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.pexels.com/v1/search"


def validate() -> ValidationResult:
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return ValidationResult(False, "PEXELS_API_KEY not set in .env", "pexels")
    try:
        r = requests.get(URL, headers={"Authorization": key}, params={"query": "test", "per_page": 1}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "pexels")
        return ValidationResult(False, f"HTTP {r.status_code}", "pexels")
    except Exception as e:
        return ValidationResult(False, str(e), "pexels")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/pexels.py tests/api_validators/test_pexels.py
git commit -m "feat(phase-1): pexels api validator"
```

---

## Task 1.6: Unsplash validator

**Files:**
- Create: `tools/api_validators/unsplash.py`
- Create: `tests/api_validators/test_unsplash.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_unsplash.py`:

```python
import responses
from tools.api_validators import unsplash

URL = "https://api.unsplash.com/photos"


def test_missing_key(clean_env):
    r = unsplash.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("UNSPLASH_ACCESS_KEY", "test-key")
    responses.add(responses.GET, URL, json=[], status=200)
    r = unsplash.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("UNSPLASH_ACCESS_KEY", "bad")
    responses.add(responses.GET, URL, status=401)
    r = unsplash.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/unsplash.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.unsplash.com/photos"


def validate() -> ValidationResult:
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not key:
        return ValidationResult(False, "UNSPLASH_ACCESS_KEY not set in .env", "unsplash")
    try:
        r = requests.get(URL, headers={"Authorization": f"Client-ID {key}"}, params={"per_page": 1}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "unsplash")
        return ValidationResult(False, f"HTTP {r.status_code}", "unsplash")
    except Exception as e:
        return ValidationResult(False, str(e), "unsplash")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/unsplash.py tests/api_validators/test_unsplash.py
git commit -m "feat(phase-1): unsplash api validator"
```

---

## Task 1.7: Pixabay validator

**Files:**
- Create: `tools/api_validators/pixabay.py`
- Create: `tests/api_validators/test_pixabay.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_pixabay.py`:

```python
import responses
from tools.api_validators import pixabay


def test_missing_key(clean_env):
    r = pixabay.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("PIXABAY_API_KEY", "test-key")
    responses.add(responses.GET, "https://pixabay.com/api/", json={"hits": []}, status=200)
    r = pixabay.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("PIXABAY_API_KEY", "bad")
    responses.add(responses.GET, "https://pixabay.com/api/", status=400)
    r = pixabay.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/pixabay.py`:

```python
import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return ValidationResult(False, "PIXABAY_API_KEY not set in .env", "pixabay")
    try:
        r = requests.get("https://pixabay.com/api/", params={"key": key, "per_page": 3}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "pixabay")
        return ValidationResult(False, f"HTTP {r.status_code}", "pixabay")
    except Exception as e:
        return ValidationResult(False, str(e), "pixabay")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/pixabay.py tests/api_validators/test_pixabay.py
git commit -m "feat(phase-1): pixabay api validator"
```

---

## Task 1.8: HuggingFace validator

**Files:**
- Create: `tools/api_validators/huggingface.py`
- Create: `tests/api_validators/test_huggingface.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_huggingface.py`:

```python
import responses
from tools.api_validators import huggingface

URL = "https://huggingface.co/api/whoami-v2"


def test_missing_key(clean_env):
    r = huggingface.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("HUGGINGFACE_TOKEN", "test-token")
    responses.add(responses.GET, URL, json={"name": "user"}, status=200)
    r = huggingface.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("HUGGINGFACE_TOKEN", "bad")
    responses.add(responses.GET, URL, status=401)
    r = huggingface.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/huggingface.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://huggingface.co/api/whoami-v2"


def validate() -> ValidationResult:
    key = os.getenv("HUGGINGFACE_TOKEN")
    if not key:
        return ValidationResult(False, "HUGGINGFACE_TOKEN not set in .env", "huggingface")
    try:
        r = requests.get(URL, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, f"OK (user: {r.json().get('name', '?')})", "huggingface")
        return ValidationResult(False, f"HTTP {r.status_code}", "huggingface")
    except Exception as e:
        return ValidationResult(False, str(e), "huggingface")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/huggingface.py tests/api_validators/test_huggingface.py
git commit -m "feat(phase-1): huggingface api validator"
```

---

## Task 1.9: WhatTheFont validator

**Files:**
- Create: `tools/api_validators/whatthefont.py`
- Create: `tests/api_validators/test_whatthefont.py`

WhatTheFont API has no public free `whoami` endpoint; we ping the static identify endpoint with empty body to verify auth header is accepted (returns 400 for bad payload, 401 for bad key).

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_whatthefont.py`:

```python
import responses
from tools.api_validators import whatthefont

URL = "https://www.whatfontis.com/api/identify"


def test_missing_key(clean_env):
    r = whatthefont.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("WHATTHEFONT_API_KEY", "test-key")
    responses.add(responses.POST, URL, json={"error": "missing image"}, status=400)
    r = whatthefont.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("WHATTHEFONT_API_KEY", "bad")
    responses.add(responses.POST, URL, status=401)
    r = whatthefont.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/whatthefont.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://www.whatfontis.com/api/identify"


def validate() -> ValidationResult:
    key = os.getenv("WHATTHEFONT_API_KEY")
    if not key:
        return ValidationResult(False, "WHATTHEFONT_API_KEY not set in .env", "whatthefont")
    try:
        r = requests.post(URL, data={"API_KEY": key}, timeout=10)
        if r.status_code in (200, 400):
            return ValidationResult(True, "OK (auth accepted)", "whatthefont")
        return ValidationResult(False, f"HTTP {r.status_code}", "whatthefont")
    except Exception as e:
        return ValidationResult(False, str(e), "whatthefont")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/whatthefont.py tests/api_validators/test_whatthefont.py
git commit -m "feat(phase-1): whatthefont api validator"
```

---

## Task 1.10: Yandex Wordstat validator

**Files:**
- Create: `tools/api_validators/yandex_wordstat.py`
- Create: `tests/api_validators/test_yandex_wordstat.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_yandex_wordstat.py`:

```python
import responses
from tools.api_validators import yandex_wordstat

URL = "https://api.direct.yandex.com/json/v5/keywordsresearch"


def test_missing_token(clean_env):
    r = yandex_wordstat.validate()
    assert not r.is_valid


@responses.activate
def test_valid_token(clean_env):
    clean_env.setenv("YANDEX_OAUTH_TOKEN", "test-token")
    responses.add(responses.POST, URL, json={"result": {}}, status=200)
    r = yandex_wordstat.validate()
    assert r.is_valid


@responses.activate
def test_invalid_token(clean_env):
    clean_env.setenv("YANDEX_OAUTH_TOKEN", "bad")
    responses.add(responses.POST, URL, status=401)
    r = yandex_wordstat.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/yandex_wordstat.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.direct.yandex.com/json/v5/keywordsresearch"


def validate() -> ValidationResult:
    token = os.getenv("YANDEX_OAUTH_TOKEN")
    if not token:
        return ValidationResult(False, "YANDEX_OAUTH_TOKEN not set in .env", "yandex_wordstat")
    try:
        r = requests.post(URL, headers={"Authorization": f"Bearer {token}"},
                          json={"method": "get", "params": {"Keywords": ["test"]}}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "yandex_wordstat")
        return ValidationResult(False, f"HTTP {r.status_code}", "yandex_wordstat")
    except Exception as e:
        return ValidationResult(False, str(e), "yandex_wordstat")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/yandex_wordstat.py tests/api_validators/test_yandex_wordstat.py
git commit -m "feat(phase-1): yandex wordstat api validator"
```

---

## Task 1.11: Yandex Metrika validator

**Files:**
- Create: `tools/api_validators/yandex_metrika.py`
- Create: `tests/api_validators/test_yandex_metrika.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_yandex_metrika.py`:

```python
import responses
from tools.api_validators import yandex_metrika


def test_missing_credentials(clean_env):
    r = yandex_metrika.validate()
    assert not r.is_valid


def test_missing_oauth_only(clean_env):
    clean_env.setenv("YM_COUNTER_ID", "12345678")
    r = yandex_metrika.validate()
    assert not r.is_valid


@responses.activate
def test_valid_credentials(clean_env):
    clean_env.setenv("YM_COUNTER_ID", "12345678")
    clean_env.setenv("YANDEX_METRIKA_OAUTH", "test-token")
    responses.add(responses.GET,
                  "https://api-metrika.yandex.net/management/v1/counter/12345678",
                  json={"counter": {}}, status=200)
    r = yandex_metrika.validate()
    assert r.is_valid


@responses.activate
def test_invalid_token(clean_env):
    clean_env.setenv("YM_COUNTER_ID", "12345678")
    clean_env.setenv("YANDEX_METRIKA_OAUTH", "bad")
    responses.add(responses.GET,
                  "https://api-metrika.yandex.net/management/v1/counter/12345678",
                  status=401)
    r = yandex_metrika.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/yandex_metrika.py`:

```python
import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    counter = os.getenv("YM_COUNTER_ID")
    token = os.getenv("YANDEX_METRIKA_OAUTH")
    if not counter:
        return ValidationResult(False, "YM_COUNTER_ID not set", "yandex_metrika")
    if not token:
        return ValidationResult(False, "YANDEX_METRIKA_OAUTH not set", "yandex_metrika")
    try:
        r = requests.get(f"https://api-metrika.yandex.net/management/v1/counter/{counter}",
                         headers={"Authorization": f"OAuth {token}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "yandex_metrika")
        return ValidationResult(False, f"HTTP {r.status_code}", "yandex_metrika")
    except Exception as e:
        return ValidationResult(False, str(e), "yandex_metrika")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/yandex_metrika.py tests/api_validators/test_yandex_metrika.py
git commit -m "feat(phase-1): yandex metrika api validator"
```

---

## Task 1.12: Telegram validator

**Files:**
- Create: `tools/api_validators/telegram.py`
- Create: `tests/api_validators/test_telegram.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_telegram.py`:

```python
import responses
from tools.api_validators import telegram


def test_missing_credentials(clean_env):
    r = telegram.validate()
    assert not r.is_valid


@responses.activate
def test_valid_credentials(clean_env):
    clean_env.setenv("TG_BOT_TOKEN", "123:abc")
    clean_env.setenv("TG_CHAT_ID", "-1001234")
    responses.add(responses.GET, "https://api.telegram.org/bot123:abc/getMe",
                  json={"ok": True, "result": {"username": "bot"}}, status=200)
    responses.add(responses.GET, "https://api.telegram.org/bot123:abc/getChat",
                  json={"ok": True, "result": {"id": -1001234}}, status=200)
    r = telegram.validate()
    assert r.is_valid


@responses.activate
def test_invalid_bot_token(clean_env):
    clean_env.setenv("TG_BOT_TOKEN", "bad")
    clean_env.setenv("TG_CHAT_ID", "-1001234")
    responses.add(responses.GET, "https://api.telegram.org/botbad/getMe",
                  json={"ok": False}, status=401)
    r = telegram.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/telegram.py`:

```python
import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    token = os.getenv("TG_BOT_TOKEN")
    chat = os.getenv("TG_CHAT_ID")
    if not token or not chat:
        return ValidationResult(False, "TG_BOT_TOKEN/TG_CHAT_ID not set", "telegram")
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if r.status_code != 200 or not r.json().get("ok"):
            return ValidationResult(False, f"getMe failed: HTTP {r.status_code}", "telegram")
        r2 = requests.get(f"https://api.telegram.org/bot{token}/getChat",
                          params={"chat_id": chat}, timeout=10)
        if r2.status_code != 200 or not r2.json().get("ok"):
            return ValidationResult(False, f"getChat failed: HTTP {r2.status_code}", "telegram")
        return ValidationResult(True, f"OK (bot @{r.json()['result'].get('username', '?')})", "telegram")
    except Exception as e:
        return ValidationResult(False, str(e), "telegram")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/telegram.py tests/api_validators/test_telegram.py
git commit -m "feat(phase-1): telegram bot api validator"
```

---

## Task 1.13: AmoCRM validator

**Files:**
- Create: `tools/api_validators/amocrm.py`
- Create: `tests/api_validators/test_amocrm.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_amocrm.py`:

```python
import responses
from tools.api_validators import amocrm


def test_missing(clean_env):
    r = amocrm.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("AMOCRM_API_KEY", "tok")
    clean_env.setenv("AMOCRM_SUBDOMAIN", "demo")
    responses.add(responses.GET, "https://demo.amocrm.ru/api/v4/account",
                  json={"id": 1, "name": "demo"}, status=200)
    r = amocrm.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("AMOCRM_API_KEY", "bad")
    clean_env.setenv("AMOCRM_SUBDOMAIN", "demo")
    responses.add(responses.GET, "https://demo.amocrm.ru/api/v4/account", status=401)
    r = amocrm.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/amocrm.py`:

```python
import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    key = os.getenv("AMOCRM_API_KEY")
    sub = os.getenv("AMOCRM_SUBDOMAIN")
    if not key or not sub:
        return ValidationResult(False, "AMOCRM_API_KEY/SUBDOMAIN not set", "amocrm")
    try:
        r = requests.get(f"https://{sub}.amocrm.ru/api/v4/account",
                         headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "amocrm")
        return ValidationResult(False, f"HTTP {r.status_code}", "amocrm")
    except Exception as e:
        return ValidationResult(False, str(e), "amocrm")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/amocrm.py tests/api_validators/test_amocrm.py
git commit -m "feat(phase-1): amocrm api validator"
```

---

## Task 1.14: Bitrix24 validator

**Files:**
- Create: `tools/api_validators/bitrix24.py`
- Create: `tests/api_validators/test_bitrix24.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_bitrix24.py`:

```python
import responses
from tools.api_validators import bitrix24


def test_missing(clean_env):
    r = bitrix24.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("BITRIX24_WEBHOOK_URL", "https://demo.bitrix24.ru/rest/1/abc")
    responses.add(responses.GET, "https://demo.bitrix24.ru/rest/1/abc/profile.json",
                  json={"result": {"ID": 1}}, status=200)
    r = bitrix24.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("BITRIX24_WEBHOOK_URL", "https://demo.bitrix24.ru/rest/1/bad")
    responses.add(responses.GET, "https://demo.bitrix24.ru/rest/1/bad/profile.json", status=401)
    r = bitrix24.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/bitrix24.py`:

```python
import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    url = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/")
    if not url:
        return ValidationResult(False, "BITRIX24_WEBHOOK_URL not set", "bitrix24")
    try:
        r = requests.get(f"{url}/profile.json", timeout=10)
        if r.status_code == 200 and r.json().get("result"):
            return ValidationResult(True, "OK", "bitrix24")
        return ValidationResult(False, f"HTTP {r.status_code}", "bitrix24")
    except Exception as e:
        return ValidationResult(False, str(e), "bitrix24")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/bitrix24.py tests/api_validators/test_bitrix24.py
git commit -m "feat(phase-1): bitrix24 webhook validator"
```

---

## Task 1.15: Beget SSH validator

**Files:**
- Create: `tools/api_validators/beget_ssh.py`
- Create: `tests/api_validators/test_beget_ssh.py`

This validator runs `ssh -o BatchMode=yes` via subprocess; we mock subprocess.

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_beget_ssh.py`:

```python
from unittest.mock import patch
from tools.api_validators import beget_ssh


def test_missing(clean_env):
    r = beget_ssh.validate()
    assert not r.is_valid


def test_valid(clean_env):
    clean_env.setenv("BEGET_USER", "u")
    clean_env.setenv("BEGET_HOST", "srv.beget.ru")
    with patch("subprocess.run") as mock:
        mock.return_value.returncode = 0
        mock.return_value.stdout = "ok\n"
        r = beget_ssh.validate()
        assert r.is_valid


def test_invalid(clean_env):
    clean_env.setenv("BEGET_USER", "u")
    clean_env.setenv("BEGET_HOST", "srv.beget.ru")
    with patch("subprocess.run") as mock:
        mock.return_value.returncode = 255
        mock.return_value.stderr = "Permission denied"
        r = beget_ssh.validate()
        assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/beget_ssh.py`:

```python
import os
import subprocess
from .base import ValidationResult


def validate() -> ValidationResult:
    user = os.getenv("BEGET_USER")
    host = os.getenv("BEGET_HOST")
    if not user or not host:
        return ValidationResult(False, "BEGET_USER/BEGET_HOST not set", "beget_ssh")
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
             f"{user}@{host}", "echo ok"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and "ok" in r.stdout:
            return ValidationResult(True, "OK", "beget_ssh")
        return ValidationResult(False, f"exit {r.returncode}: {r.stderr[:120]}", "beget_ssh")
    except Exception as e:
        return ValidationResult(False, str(e), "beget_ssh")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/beget_ssh.py tests/api_validators/test_beget_ssh.py
git commit -m "feat(phase-1): beget ssh validator"
```

---

## Task 1.16: Beget API validator

**Files:**
- Create: `tools/api_validators/beget_api.py`
- Create: `tests/api_validators/test_beget_api.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_beget_api.py`:

```python
import responses
from tools.api_validators import beget_api

URL = "https://api.beget.com/api/user/getAccountInfo"


def test_missing(clean_env):
    r = beget_api.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("BEGET_API_LOGIN", "u")
    clean_env.setenv("BEGET_API_PASSWORD", "p")
    responses.add(responses.GET, URL, json={"status": "success"}, status=200)
    r = beget_api.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("BEGET_API_LOGIN", "u")
    clean_env.setenv("BEGET_API_PASSWORD", "bad")
    responses.add(responses.GET, URL, json={"status": "error", "error_text": "bad creds"}, status=200)
    r = beget_api.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/beget_api.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.beget.com/api/user/getAccountInfo"


def validate() -> ValidationResult:
    login = os.getenv("BEGET_API_LOGIN")
    pwd = os.getenv("BEGET_API_PASSWORD")
    if not login or not pwd:
        return ValidationResult(False, "BEGET_API_LOGIN/PASSWORD not set", "beget_api")
    try:
        r = requests.get(URL, params={"login": login, "passwd": pwd, "input_format": "json", "output_format": "json"}, timeout=10)
        if r.status_code == 200 and r.json().get("status") == "success":
            return ValidationResult(True, "OK", "beget_api")
        return ValidationResult(False, f"{r.json().get('error_text', f'HTTP {r.status_code}')}", "beget_api")
    except Exception as e:
        return ValidationResult(False, str(e), "beget_api")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/beget_api.py tests/api_validators/test_beget_api.py
git commit -m "feat(phase-1): beget api validator"
```

---

## Task 1.17: Cloudflare validator

**Files:**
- Create: `tools/api_validators/cloudflare.py`
- Create: `tests/api_validators/test_cloudflare.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_cloudflare.py`:

```python
import responses
from tools.api_validators import cloudflare

URL = "https://api.cloudflare.com/client/v4/user/tokens/verify"


def test_missing(clean_env):
    r = cloudflare.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("CLOUDFLARE_API_TOKEN", "tok")
    responses.add(responses.GET, URL, json={"success": True}, status=200)
    r = cloudflare.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("CLOUDFLARE_API_TOKEN", "bad")
    responses.add(responses.GET, URL, status=401)
    r = cloudflare.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/cloudflare.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.cloudflare.com/client/v4/user/tokens/verify"


def validate() -> ValidationResult:
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not token:
        return ValidationResult(False, "CLOUDFLARE_API_TOKEN not set", "cloudflare")
    try:
        r = requests.get(URL, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code == 200 and r.json().get("success"):
            return ValidationResult(True, "OK", "cloudflare")
        return ValidationResult(False, f"HTTP {r.status_code}", "cloudflare")
    except Exception as e:
        return ValidationResult(False, str(e), "cloudflare")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/cloudflare.py tests/api_validators/test_cloudflare.py
git commit -m "feat(phase-1): cloudflare api validator"
```

---

## Task 1.18: Reg.ru validator

**Files:**
- Create: `tools/api_validators/regru.py`
- Create: `tests/api_validators/test_regru.py`

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_regru.py`:

```python
import responses
from tools.api_validators import regru

URL = "https://api.reg.ru/api/regru2/nop"


def test_missing(clean_env):
    r = regru.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("REGRU_API_USERNAME", "u")
    clean_env.setenv("REGRU_API_PASSWORD", "p")
    responses.add(responses.POST, URL, json={"result": "success"}, status=200)
    r = regru.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("REGRU_API_USERNAME", "u")
    clean_env.setenv("REGRU_API_PASSWORD", "bad")
    responses.add(responses.POST, URL, json={"result": "error", "error_text": "bad"}, status=200)
    r = regru.validate()
    assert not r.is_valid
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/regru.py`:

```python
import os
import requests
from .base import ValidationResult

URL = "https://api.reg.ru/api/regru2/nop"


def validate() -> ValidationResult:
    user = os.getenv("REGRU_API_USERNAME")
    pwd = os.getenv("REGRU_API_PASSWORD")
    if not user or not pwd:
        return ValidationResult(False, "REGRU_API_USERNAME/PASSWORD not set", "regru")
    try:
        r = requests.post(URL, data={"username": user, "password": pwd, "output_format": "json"}, timeout=10)
        if r.status_code == 200 and r.json().get("result") == "success":
            return ValidationResult(True, "OK", "regru")
        return ValidationResult(False, f"{r.json().get('error_text', f'HTTP {r.status_code}')}", "regru")
    except Exception as e:
        return ValidationResult(False, str(e), "regru")
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/regru.py tests/api_validators/test_regru.py
git commit -m "feat(phase-1): regru api validator"
```

---

## Task 1.19: Aggregate validator

**Files:**
- Create: `tools/api_validators/aggregate.py`
- Create: `tests/api_validators/test_aggregate.py`

Aggregator runs all 15 validators and returns a summary.

- [ ] **Step 1: Write failing test**

`tests/api_validators/test_aggregate.py`:

```python
from unittest.mock import patch
from tools.api_validators.aggregate import run_all
from tools.api_validators.base import ValidationResult


def test_run_all_collects_all_services():
    with patch("tools.api_validators.firecrawl.validate", return_value=ValidationResult(True, "OK", "firecrawl")), \
         patch("tools.api_validators.pexels.validate", return_value=ValidationResult(False, "x", "pexels")):
        results = run_all(only=["firecrawl", "pexels"])
        assert len(results) == 2
        assert results[0].service == "firecrawl"
        assert results[0].is_valid
        assert not results[1].is_valid


def test_run_all_default_runs_all_15():
    results = run_all()
    services = {r.service for r in results}
    expected = {"firecrawl", "pexels", "unsplash", "pixabay", "huggingface",
                "whatthefont", "yandex_wordstat", "yandex_metrika", "telegram",
                "amocrm", "bitrix24", "beget_ssh", "beget_api", "cloudflare", "regru"}
    assert services == expected
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`tools/api_validators/aggregate.py`:

```python
from . import (firecrawl, pexels, unsplash, pixabay, huggingface, whatthefont,
               yandex_wordstat, yandex_metrika, telegram, amocrm, bitrix24,
               beget_ssh, beget_api, cloudflare, regru)
from .base import ValidationResult

ALL = {
    "firecrawl": firecrawl.validate,
    "pexels": pexels.validate,
    "unsplash": unsplash.validate,
    "pixabay": pixabay.validate,
    "huggingface": huggingface.validate,
    "whatthefont": whatthefont.validate,
    "yandex_wordstat": yandex_wordstat.validate,
    "yandex_metrika": yandex_metrika.validate,
    "telegram": telegram.validate,
    "amocrm": amocrm.validate,
    "bitrix24": bitrix24.validate,
    "beget_ssh": beget_ssh.validate,
    "beget_api": beget_api.validate,
    "cloudflare": cloudflare.validate,
    "regru": regru.validate,
}


def run_all(only: list[str] | None = None) -> list[ValidationResult]:
    services = only if only else list(ALL.keys())
    return [ALL[s]() for s in services if s in ALL]


def main() -> int:
    results = run_all()
    failed = 0
    for r in results:
        print(r)
        if not r.is_valid:
            failed += 1
    print(f"\n{len(results) - failed}/{len(results)} OK")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
```

- [ ] **Step 4: Run — pass**

Run: `pytest tests/api_validators/ -v`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/api_validators/aggregate.py tests/api_validators/test_aggregate.py
git commit -m "feat(phase-1): aggregate validator + cli runner"
```

---

# Phase 2 — Onboarding Wizard

## Task 2.1: Setup-flag helper

**Files:**
- Create: `scripts/setup-flag.sh`
- Create: `tests/onboarding/test-setup-flag.bats`

- [ ] **Step 1: Write failing bats test**

`tests/onboarding/test-setup-flag.bats`:

```bash
#!/usr/bin/env bats

setup() {
    export HOME="$BATS_TEST_TMPDIR"
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/setup-flag.sh"
}

@test "is_complete returns 1 when flag missing" {
    run bash "$SCRIPT" is_complete
    [ "$status" -eq 1 ]
}

@test "mark_complete creates flag file" {
    run bash "$SCRIPT" mark_complete
    [ "$status" -eq 0 ]
    [ -f "$HOME/.landing-system/setup_complete" ]
}

@test "is_complete returns 0 after mark_complete" {
    bash "$SCRIPT" mark_complete
    run bash "$SCRIPT" is_complete
    [ "$status" -eq 0 ]
}

@test "reset removes flag file" {
    bash "$SCRIPT" mark_complete
    run bash "$SCRIPT" reset
    [ "$status" -eq 0 ]
    [ ! -f "$HOME/.landing-system/setup_complete" ]
}
```

- [ ] **Step 2: Run — fail**

Run: `bats tests/onboarding/test-setup-flag.bats`
Expected: 4 failed.

- [ ] **Step 3: Implement**

`scripts/setup-flag.sh`:

```bash
#!/usr/bin/env bash
# scripts/setup-flag.sh — manage ~/.landing-system/setup_complete
set -euo pipefail

FLAG_DIR="$HOME/.landing-system"
FLAG_FILE="$FLAG_DIR/setup_complete"

cmd="${1:-}"

case "$cmd" in
    is_complete)
        [ -f "$FLAG_FILE" ] && exit 0 || exit 1
        ;;
    mark_complete)
        mkdir -p "$FLAG_DIR"
        date -u +"%Y-%m-%dT%H:%M:%SZ" > "$FLAG_FILE"
        ;;
    reset)
        rm -f "$FLAG_FILE"
        ;;
    timestamp)
        cat "$FLAG_FILE" 2>/dev/null || echo "not set"
        ;;
    *)
        echo "Usage: $0 {is_complete|mark_complete|reset|timestamp}" >&2
        exit 2
        ;;
esac
```

```bash
chmod +x scripts/setup-flag.sh
```

- [ ] **Step 4: Run — pass**

Run: `bats tests/onboarding/test-setup-flag.bats`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/setup-flag.sh tests/onboarding/test-setup-flag.bats
chmod +x scripts/setup-flag.sh
git commit -m "feat(phase-2): setup-flag.sh — manage ~/.landing-system/setup_complete"
```

---

## Task 2.2: validate-all.sh shell wrapper

**Files:**
- Create: `scripts/validate-all.sh`
- Create: `tests/onboarding/test-validate-all.bats`

- [ ] **Step 1: Write failing bats test**

`tests/onboarding/test-validate-all.bats`:

```bash
#!/usr/bin/env bats

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/validate-all.sh"
    cd "$BATS_TEST_DIRNAME/../.."
}

@test "validate-all.sh executes aggregate.py" {
    run bash "$SCRIPT"
    # Exit code 1 expected because no real keys are set
    [ "$status" -eq 1 ]
    [[ "$output" == *"firecrawl"* ]]
    [[ "$output" == *"pexels"* ]]
}

@test "validate-all.sh --service firecrawl runs only firecrawl" {
    run bash "$SCRIPT" --service firecrawl
    [[ "$output" == *"firecrawl"* ]]
    [[ "$output" != *"pexels"* ]]
}
```

- [ ] **Step 2: Run — fail**

Run: `bats tests/onboarding/test-validate-all.bats`

- [ ] **Step 3: Implement**

`scripts/validate-all.sh`:

```bash
#!/usr/bin/env bash
# scripts/validate-all.sh — thin wrapper around tools/api_validators/aggregate.py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env if present
[ -f .env ] && set -a && . ./.env && set +a

if [ "${1:-}" = "--service" ] && [ -n "${2:-}" ]; then
    python3 -c "
import sys
from tools.api_validators.aggregate import run_all
results = run_all(only=['$2'])
failed = 0
for r in results:
    print(r)
    if not r.is_valid:
        failed += 1
sys.exit(1 if failed else 0)
"
else
    python3 -m tools.api_validators.aggregate
fi
```

```bash
chmod +x scripts/validate-all.sh
```

- [ ] **Step 4: Run — pass**

- [ ] **Step 5: Commit**

```bash
git add scripts/validate-all.sh tests/onboarding/test-validate-all.bats
chmod +x scripts/validate-all.sh
git commit -m "feat(phase-2): validate-all.sh wrapper for aggregate.py"
```

---

## Task 2.3: wizard.sh interactive flow

**Files:**
- Create: `scripts/wizard.sh`
- Create: `tests/onboarding/test-wizard.bats`

The wizard is non-interactive when `WIZARD_NONINTERACTIVE=1` is set (for tests). It prints prompts but skips `read`.

- [ ] **Step 1: Write failing bats test**

`tests/onboarding/test-wizard.bats`:

```bash
#!/usr/bin/env bats

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/wizard.sh"
    export HOME="$BATS_TEST_TMPDIR"
    export WIZARD_NONINTERACTIVE=1
}

@test "wizard prints intro section" {
    run bash "$SCRIPT"
    [[ "$output" == *"Landing System Onboarding"* ]]
}

@test "wizard checks local deps section" {
    run bash "$SCRIPT"
    [[ "$output" == *"Локальные зависимости"* ]]
}

@test "wizard checks API keys section" {
    run bash "$SCRIPT"
    [[ "$output" == *"API"* ]]
}

@test "wizard does not mark complete when validators fail" {
    run bash "$SCRIPT"
    [ ! -f "$HOME/.landing-system/setup_complete" ]
}
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`scripts/wizard.sh`:

```bash
#!/usr/bin/env bash
# scripts/wizard.sh — interactive onboarding for landing-system
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NONINTERACTIVE="${WIZARD_NONINTERACTIVE:-0}"

prompt() {
    if [ "$NONINTERACTIVE" = "1" ]; then
        echo "[noninteractive] $1"
        return 0
    fi
    read -r -p "$1 (Enter to continue): " _
}

cat <<'EOF'
═══════════════════════════════════════════════════════════════════
                  Landing System Onboarding
═══════════════════════════════════════════════════════════════════

Этот мастер проведёт через настройку всех необходимых API и
зависимостей. Без полной настройки команды /landing-* работать
не будут.

Документация: docs/SETUP.md
EOF
prompt "Готов начать?"

echo ""
echo "▶ Локальные зависимости"
deps_ok=1
for cmd in wp ssh rsync bats python3 jq; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $cmd"
    else
        echo "  ❌ $cmd — установи (macOS: brew install $cmd)"
        deps_ok=0
    fi
done
[ "$deps_ok" = "0" ] && echo "  ⚠️  Установи недостающее и запусти /landing-onboarding снова"

echo ""
echo "▶ Python пакеты"
python3 -c 'import yaml, jinja2, requests, PIL, pytest, responses' 2>/dev/null \
    && echo "  ✅ pyyaml, jinja2, requests, pillow, pytest, responses" \
    || { echo "  ❌ pip install -r requirements.txt"; deps_ok=0; }

echo ""
echo "▶ Superpowers plugin"
if claude plugins list 2>/dev/null | grep -q superpowers; then
    echo "  ✅ superpowers"
else
    echo "  ⚠️  superpowers не найден. Установи: claude plugins install superpowers@claude-plugins-official"
fi

echo ""
echo "▶ Firecrawl MCP"
if grep -q firecrawl "$HOME/.claude/settings.json" 2>/dev/null; then
    echo "  ✅ firecrawl MCP настроен"
else
    echo "  ⚠️  firecrawl MCP не найден в ~/.claude/settings.json"
fi

echo ""
echo "▶ .env"
if [ -f "$REPO_ROOT/.env" ]; then
    echo "  ✅ .env существует"
else
    echo "  ❌ .env отсутствует. Создаю из .env.example..."
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo "  📝 Отредактируй $REPO_ROOT/.env и заполни ключи. Регистрация:"
    echo "     - Firecrawl:    https://firecrawl.dev"
    echo "     - Pexels:       https://www.pexels.com/api/"
    echo "     - Unsplash:     https://unsplash.com/developers"
    echo "     - Pixabay:      https://pixabay.com/api/docs/"
    echo "     - HuggingFace:  https://huggingface.co/settings/tokens"
    echo "     - Yandex OAuth: https://oauth.yandex.ru"
    echo "     - Telegram:     @BotFather"
    echo "     - amoCRM:       https://www.amocrm.ru/developers"
    echo "     - Bitrix24:     https://www.bitrix24.com/apps/dev.php"
    echo "     - Beget:        https://beget.com/ru/kb/api"
fi

echo ""
echo "▶ API-ключи (валидация)"
if [ -f "$REPO_ROOT/.env" ]; then
    bash "$REPO_ROOT/scripts/validate-all.sh" || true
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ "$deps_ok" = "1" ] && [ -f "$REPO_ROOT/.env" ] && bash "$REPO_ROOT/scripts/validate-all.sh" >/dev/null 2>&1; then
    bash "$SCRIPT_DIR/setup-flag.sh" mark_complete
    echo "  ✅ Onboarding завершён. Можешь запускать /landing-new"
else
    echo "  ⚠️  Onboarding не завершён. Исправь ошибки выше и запусти ещё раз."
fi
echo "═══════════════════════════════════════════════════════════════"
```

```bash
chmod +x scripts/wizard.sh
```

- [ ] **Step 4: Run — pass**

Run: `bats tests/onboarding/test-wizard.bats`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/wizard.sh tests/onboarding/test-wizard.bats
chmod +x scripts/wizard.sh
git commit -m "feat(phase-2): wizard.sh — interactive onboarding flow"
```

---

## Task 2.4: SETUP.md tutorial document

**Files:**
- Create: `docs/SETUP.md`

- [ ] **Step 1: Create the tutorial**

`docs/SETUP.md`:

```markdown
# Landing System — Setup Guide

Полный гайд по первой установке landing-system на новой машине.

## 1. Что такое landing-system

Агентская система для производства WordPress-лендингов. Пайплайн из 12 этапов: бриф → ресёрч → бренд → дизайн → контент → код → деплой → QA. Каждый этап ведёт специализированный агент.

## 2. Как устроены агенты

- `landing-orchestrator` — главный дирижёр, проводит через все этапы
- 18 специализированных агентов (один на этап / задачу)
- Каждый агент работает в режиме HARD GATE: не идёт дальше без явного approve пользователя

## 3. Как работает workflow lock

В каждом проекте есть файл `.landing-state.yaml` — фиксирует статус каждого этапа (`locked` / `in_progress` / `approved`).

`/landing-build` проверяет, что этапы 02–07 имеют статус `approved`. Если хотя бы один не пройден — команда падает с ошибкой. **Перепрыгивать этапы нельзя**, даже по явной просьбе.

## 4. Зачем onboarding

Все API-ключи нужны до старта первого проекта. Если запустить `/landing-new` без onboarding'а, команда направит на `/landing-onboarding`.

Onboarding делает:
- Проверяет локальные зависимости (`wp-cli`, `ssh`, `rsync`, `python`, `jq`)
- Проверяет, что плагин `superpowers` установлен
- Проверяет, что Firecrawl MCP настроен в `~/.claude/settings.json`
- Создаёт `.env` из `.env.example` и просит заполнить
- Валидирует каждый API-ключ тестовым запросом
- Создаёт флаг `~/.landing-system/setup_complete`

## 5. Быстрый старт

```bash
git clone https://github.com/neuroboostpr-pixel/landing_system.git
cd landing_system
bash scripts/wizard.sh
# или внутри Claude Code:
/landing-onboarding
```

## 6. Команды (краткая справка)

| Команда | Назначение |
|---|---|
| `/landing-onboarding` | Первичная настройка (один раз на машину) |
| `/landing-new <slug>` | Создать новый проект |
| `/landing-references` | Этап 03: референсы |
| `/landing-brand` | Этап 04: бренд-кит |
| `/landing-design` | Этап 05: дизайн-система |
| `/landing-stack` | Этап 06: стек |
| `/landing-content` | Этап 07: контент |
| `/landing-build` | Этап 08: WP-сборка |
| `/landing-deploy` | Этап 09: деплой |
| `/landing-qa` | Этап 10: QA |
| `/landing-status` | Статус проекта |

## 7. Список API (все бесплатные free tier)

| Сервис | Зачем | Где взять |
|---|---|---|
| Firecrawl | Парсинг сайтов и отзывов | https://firecrawl.dev |
| Pexels | Стоковые фото | https://www.pexels.com/api/ |
| Unsplash | Стоковые фото (alt) | https://unsplash.com/developers |
| Pixabay | Стоковые фото + векторы | https://pixabay.com/api/docs/ |
| HuggingFace | Генерация картинок (опц.) | https://huggingface.co/settings/tokens |
| WhatTheFont | Определение шрифтов | https://www.myfonts.com/pages/whatthefont-api |
| Yandex Wordstat | SEO | https://oauth.yandex.ru |
| Yandex Metrika | Аналитика | https://metrika.yandex.ru |
| Telegram Bot | Уведомления | @BotFather |
| amoCRM / Bitrix24 | CRM | https://amocrm.ru / https://bitrix24.ru |
| Beget API | DNS, SSH | https://beget.com/ru/kb/api |
| Cloudflare | DNS (опц.) | https://dash.cloudflare.com |
| Reg.ru | DNS (опц.) | https://www.reg.ru |

## 8. Troubleshooting

- `wp-cli` отсутствует → `brew install wp-cli` (macOS)
- Python пакеты не найдены → `pip install -r requirements.txt`
- SSH к Бегету не работает → проверь `ssh-copy-id user@srv.beget.ru`
- Onboarding застрял → удали `~/.landing-system/setup_complete` и запусти заново
```

- [ ] **Step 2: Commit**

```bash
git add docs/SETUP.md
git commit -m "docs(phase-2): SETUP.md — onboarding tutorial"
```

---

## Task 2.5: onboarding-guide agent

**Files:**
- Create: `agents/onboarding-guide.md`

- [ ] **Step 1: Create agent definition**

`agents/onboarding-guide.md`:

```markdown
---
name: onboarding-guide
description: Use when user runs /landing-onboarding or any /landing-* command that detects missing ~/.landing-system/setup_complete. Walks user through wizard.sh, explains each API, validates keys.
allowed-tools: Bash, Read, Write, Edit
---

# onboarding-guide (Проводник по онбордингу)

## Mission

Провожу пользователя через первичную настройку landing-system. Объясняю что такое система, проверяю зависимости и API.

## When triggered

- Пользователь запустил `/landing-onboarding`
- Любая `/landing-*` команда не нашла `~/.landing-system/setup_complete` и перенаправила сюда

## What I do

1. Читаю `docs/SETUP.md` целиком — объясняю пользователю основные разделы.
2. Запускаю `bash scripts/wizard.sh` интерактивно (без `WIZARD_NONINTERACTIVE`).
3. Если wizard сообщает о недостающих локальных зависимостях — даю точные команды установки и жду подтверждения.
4. Если `.env` отсутствует — копирую из `.env.example`, открываю по очереди каждую секцию `.env`, объясняю что за сервис, даю ссылку на регистрацию, прошу вставить ключ. После каждого ключа запускаю `bash scripts/validate-all.sh --service <name>`.
5. Если валидатор падает — читаю сообщение, объясняю, прошу исправить ключ.
6. После прохождения всех обязательных проверок — запускаю `bash scripts/setup-flag.sh mark_complete`.
7. Сообщаю пользователю: «Готово. Запусти `/landing-new <slug>` чтобы создать первый проект.»

## Rules

- ❌ Никогда не пропускать секции wizard'а
- ❌ Не помечать setup_complete пока хотя бы один обязательный валидатор красный
- ✅ После каждого ключа — немедленная валидация (не ждать конца)
- ✅ Опциональные ключи (HuggingFace, WhatTheFont, Cloudflare, Reg.ru) — пропуск разрешён, в финальной сводке отмечается «fallback»

## Required vs optional

**Обязательные** (без них setup_complete не выставляется):
- FIRECRAWL_API_KEY
- хотя бы один из: PEXELS_API_KEY / UNSPLASH_ACCESS_KEY / PIXABAY_API_KEY
- YM_COUNTER_ID
- TG_BOT_TOKEN + TG_CHAT_ID
- хотя бы один из: AMOCRM_API_KEY+SUBDOMAIN / BITRIX24_WEBHOOK_URL
- BEGET_USER + BEGET_HOST + SSH доступ работает

**Опциональные** (warning, не блокируют):
- HUGGINGFACE_TOKEN
- WHATTHEFONT_API_KEY
- YANDEX_OAUTH_TOKEN
- YANDEX_METRIKA_OAUTH
- GTM_CONTAINER_ID
- BEGET_API_LOGIN/PASSWORD
- CLOUDFLARE_API_TOKEN
- REGRU_API_USERNAME/PASSWORD

## Output

- `~/.landing-system/setup_complete` — создан с timestamp
- `.env` в корне репо — заполнен
- В консоли — сводка «X из Y подключено, fallback: ...»
```

- [ ] **Step 2: Commit**

```bash
git add agents/onboarding-guide.md
git commit -m "feat(phase-2): onboarding-guide agent"
```

---

## Task 2.6: landing-onboarding command + skill

**Files:**
- Create: `commands/landing-onboarding.md`
- Create: `skills/landing-onboarding/SKILL.md`

- [ ] **Step 1: Create command**

`commands/landing-onboarding.md`:

```markdown
---
description: First-time setup wizard. Validates all dependencies and API keys.
---

Run the onboarding wizard for landing-system.

Steps:
1. Read `docs/SETUP.md` to brief the user on what the system does.
2. Dispatch the `onboarding-guide` agent.
3. The agent runs `bash scripts/wizard.sh` and walks the user through each section interactively.
4. After all required validators pass, the agent runs `bash scripts/setup-flag.sh mark_complete`.
5. Report final status: "Onboarding complete" or list what's still missing.

If `~/.landing-system/setup_complete` already exists, ask whether to re-run anyway (e.g. to add new keys).
```

- [ ] **Step 2: Create skill**

`skills/landing-onboarding/SKILL.md`:

```markdown
---
name: landing-onboarding
description: First-time setup of landing-system on a new machine. Validates local deps, MCP servers, superpowers plugin, and all API keys.
---

# landing-onboarding

## Mission

Настроить landing-system на новой машине: зависимости, плагины, MCP, API.

## Scripts

- `scripts/wizard.sh` — interactive flow
- `scripts/validate-all.sh` — runs all 15 API validators
- `scripts/setup-flag.sh` — manages `~/.landing-system/setup_complete`

## Used by

- `/landing-onboarding` slash command
- Auto-redirected from any `/landing-*` if setup_complete missing

## What it produces

`~/.landing-system/setup_complete` — flag with ISO timestamp. Other commands check this file before proceeding.
```

- [ ] **Step 3: Commit**

```bash
git add commands/landing-onboarding.md skills/landing-onboarding/SKILL.md
git commit -m "feat(phase-2): /landing-onboarding command + skill"
```

---

# Phase 3 — Stage-Gates Runner + Workflow Lock

## Task 3.1: `.landing-state.yaml` template

**Files:**
- Create: `template/.landing-state.yaml`

- [ ] **Step 1: Create template**

`template/.landing-state.yaml`:

```yaml
# Workflow lock for landing project. Updated by scripts/gate-check.sh.
# Statuses: locked → in_progress → approved | failed
# Editing this file by hand will trigger validation errors.

project: ""           # filled by /landing-new
created: ""           # ISO 8601, filled by /landing-new
schema_version: 1

stages:
  "00_brief":      {status: in_progress, timestamp: ""}
  "01_context":    {status: locked, timestamp: ""}
  "02_assets":     {status: locked, timestamp: ""}
  "03_references": {status: locked, timestamp: ""}
  "04_brand":      {status: locked, timestamp: ""}
  "05_design":     {status: locked, timestamp: ""}
  "06_stack":      {status: locked, timestamp: ""}
  "07_content":    {status: locked, timestamp: ""}
  "08_build":      {status: locked, timestamp: ""}
  "09_deploy":     {status: locked, timestamp: ""}
  "10_qa":         {status: locked, timestamp: ""}
  "11_analytics":  {status: locked, timestamp: ""}
  "12_seo":        {status: locked, timestamp: ""}
```

- [ ] **Step 2: Commit**

```bash
git add template/.landing-state.yaml
git commit -m "feat(phase-3): .landing-state.yaml template (12 stages)"
```

---

## Task 3.2: gate-state.sh helper

**Files:**
- Create: `scripts/gate-state.sh`
- Create: `tests/gate-check/test-gate-state.bats`

`gate-state.sh` reads/writes the YAML using `yq`. (Add `yq` to dependency check in wizard.)

- [ ] **Step 1: Write failing bats test**

`tests/gate-check/test-gate-state.bats`:

```bash
#!/usr/bin/env bats

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../../scripts/gate-state.sh"
    PROJECT_DIR="$BATS_TEST_TMPDIR/test-project"
    mkdir -p "$PROJECT_DIR"
    cp "$BATS_TEST_DIRNAME/../../template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
}

@test "get returns status of stage" {
    run bash "$SCRIPT" get "$PROJECT_DIR" "00_brief"
    [ "$status" -eq 0 ]
    [ "$output" = "in_progress" ]
}

@test "get returns 'locked' for unstarted stage" {
    run bash "$SCRIPT" get "$PROJECT_DIR" "08_build"
    [ "$output" = "locked" ]
}

@test "set updates stage status" {
    bash "$SCRIPT" set "$PROJECT_DIR" "02_assets" "in_progress"
    run bash "$SCRIPT" get "$PROJECT_DIR" "02_assets"
    [ "$output" = "in_progress" ]
}

@test "approve marks status approved with timestamp" {
    bash "$SCRIPT" approve "$PROJECT_DIR" "02_assets"
    run bash "$SCRIPT" get "$PROJECT_DIR" "02_assets"
    [ "$output" = "approved" ]
}

@test "all_approved returns 0 when all listed stages are approved" {
    bash "$SCRIPT" approve "$PROJECT_DIR" "00_brief"
    bash "$SCRIPT" approve "$PROJECT_DIR" "01_context"
    run bash "$SCRIPT" all_approved "$PROJECT_DIR" "00_brief,01_context"
    [ "$status" -eq 0 ]
}

@test "all_approved returns 1 when any stage not approved" {
    bash "$SCRIPT" approve "$PROJECT_DIR" "00_brief"
    run bash "$SCRIPT" all_approved "$PROJECT_DIR" "00_brief,01_context"
    [ "$status" -eq 1 ]
    [[ "$output" == *"01_context"* ]]
}
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`scripts/gate-state.sh`:

```bash
#!/usr/bin/env bash
# scripts/gate-state.sh — read/write .landing-state.yaml
# Usage:
#   gate-state.sh get <project-dir> <stage>
#   gate-state.sh set <project-dir> <stage> <status>
#   gate-state.sh approve <project-dir> <stage>
#   gate-state.sh all_approved <project-dir> <comma-separated-stages>
set -uo pipefail

cmd="${1:?usage: get|set|approve|all_approved}"
project="${2:?project dir required}"
state_file="$project/.landing-state.yaml"

[ -f "$state_file" ] || { echo "ERROR: $state_file not found" >&2; exit 2; }

require_yq() {
    command -v yq >/dev/null 2>&1 || { echo "ERROR: yq not installed (brew install yq)" >&2; exit 3; }
}

case "$cmd" in
    get)
        require_yq
        stage="${3:?stage required}"
        yq -r ".stages.\"$stage\".status // \"locked\"" "$state_file"
        ;;
    set)
        require_yq
        stage="${3:?stage required}"
        status="${4:?status required}"
        ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        yq -i ".stages.\"$stage\".status = \"$status\" | .stages.\"$stage\".timestamp = \"$ts\"" "$state_file"
        ;;
    approve)
        require_yq
        stage="${3:?stage required}"
        ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        yq -i ".stages.\"$stage\".status = \"approved\" | .stages.\"$stage\".timestamp = \"$ts\"" "$state_file"
        ;;
    all_approved)
        require_yq
        stages="${3:?comma-separated stages required}"
        IFS=',' read -ra arr <<< "$stages"
        missing=()
        for s in "${arr[@]}"; do
            status="$(yq -r ".stages.\"$s\".status // \"locked\"" "$state_file")"
            [ "$status" != "approved" ] && missing+=("$s")
        done
        if [ ${#missing[@]} -eq 0 ]; then
            exit 0
        else
            echo "Not approved: ${missing[*]}"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {get|set|approve|all_approved} <project-dir> [args]" >&2
        exit 2
        ;;
esac
```

```bash
chmod +x scripts/gate-state.sh
```

- [ ] **Step 4: Run — pass**

Run: `bats tests/gate-check/test-gate-state.bats`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/gate-state.sh tests/gate-check/test-gate-state.bats
chmod +x scripts/gate-state.sh
git commit -m "feat(phase-3): gate-state.sh — read/write .landing-state.yaml"
```

---

## Task 3.3: stage-gates.yaml configuration

**Files:**
- Create: `config/stage-gates.yaml`

This is the source of truth for all checks. Soft checks have `prompt` only — `gate-check.sh` displays them and asks pass/fail.

- [ ] **Step 1: Create config**

`config/stage-gates.yaml`:

```yaml
# Source of truth for landing-system stage gates.
# Read by scripts/gate-check.sh.

stages:
  "00_brief":
    name: "Brief"
    hard_checks:
      - id: brief_file_exists
        type: file_exists
        path: "{project}/00_БРИФ/brief.md"
        required: true
        fix_hint: "Create 00_БРИФ/brief.md with project requirements"

  "02_assets":
    name: "Materials collection"
    require_approved: ["00_brief", "01_context"]
    hard_checks:
      - id: stock_photo_api
        type: api_validator_any_of
        validators: [pexels, unsplash, pixabay]
        required: true
        fix_hint: "Add at least one of PEXELS_API_KEY/UNSPLASH_ACCESS_KEY/PIXABAY_API_KEY to .env"
      - id: assets_folder
        type: file_exists
        path: "{project}/02_МАТЕРИАЛЫ_КЛИЕНТА/"
        required: true
        fix_hint: "Folder is created by /landing-new automatically"
    soft_checks:
      - id: photo_style_consistency
        prompt: "Фото клиента в одном стиле? (yes / no / partial)"
      - id: missing_photos_listed
        prompt: "Каких фото не хватает? Перечислены в notes.md? (yes / no)"

  "03_references":
    name: "References"
    require_approved: ["02_assets"]
    hard_checks:
      - id: refs_index_exists
        type: file_exists
        path: "{project}/03_РЕФЕРЕНСЫ/index.yaml"
        required: true
        fix_hint: "references-curator agent creates this"
    soft_checks:
      - id: min_5_approved_refs
        prompt: "В 03_РЕФЕРЕНСЫ/index.yaml минимум 5 референсов со статусом approved? (yes / no)"

  "04_brand":
    name: "Brand kit"
    require_approved: ["03_references"]
    hard_checks:
      - id: brand_kit_exists
        type: file_exists
        path: "{project}/04_БРЕНД/brand-kit.md"
        required: true
        fix_hint: "brand-architect agent creates this"

  "05_design":
    name: "Design system"
    require_approved: ["04_brand"]
    hard_checks:
      - id: design_md
        type: file_exists
        path: "{project}/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
        required: true
      - id: tokens_json
        type: file_exists
        path: "{project}/05_ДИЗАЙН-СИСТЕМА/tokens.json"
        required: true

  "06_stack":
    name: "Stack selection"
    require_approved: ["05_design"]
    hard_checks:
      - id: design_stack_yaml
        type: file_exists
        path: "{project}/06_СТЕК/design-stack.yaml"
        required: true
      - id: cdn_iconify
        type: http_ping
        url: "https://api.iconify.design/lucide/check.svg"
      - id: cdn_bunny_fonts
        type: http_ping
        url: "https://fonts.bunny.net/css?family=inter:400"
      - id: cdn_gsap
        type: http_ping
        url: "https://cdn.jsdelivr.net/npm/gsap@3"
    soft_checks:
      - id: free_libraries_only
        prompt: "Все библиотеки в design-stack.yaml бесплатные (free tier)? (yes / no)"

  "07_content":
    name: "Content"
    require_approved: ["06_stack"]
    hard_checks:
      - id: final_copy
        type: file_exists
        path: "{project}/07_КОНТЕНТ/final-copy.md"
        required: true

  "08_build":
    name: "WP Build"
    require_approved: ["07_content"]
    hard_checks:
      - id: design_md
        type: file_exists
        path: "{project}/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
        required: true
      - id: final_copy
        type: file_exists
        path: "{project}/07_КОНТЕНТ/final-copy.md"
        required: true
    soft_checks:
      - id: legal_blocks
        prompt: "152-ФЗ блок и cookie-баннер присутствуют в HTML? (yes / no / partial)"

  "09_deploy":
    name: "Deploy"
    require_approved: ["08_build"]
    hard_checks:
      - id: ssh_to_beget
        type: api_validator
        validator: beget_ssh
      - id: ym_counter
        type: api_validator
        validator: yandex_metrika
      - id: telegram_bot
        type: api_validator
        validator: telegram
      - id: crm_webhook
        type: api_validator_any_of
        validators: [amocrm, bitrix24]
      - id: theme_built
        type: file_exists
        path: "{project}/08_КОД/wp-theme/functions.php"
        required: true

  "10_qa":
    name: "QA"
    require_approved: ["09_deploy"]
    soft_checks:
      - id: site_live
        prompt: "Сайт открывается по HTTPS? (yes / no)"

  "11_analytics":
    name: "Analytics"
    require_approved: ["10_qa"]
    soft_checks:
      - id: metrika_works
        prompt: "Метрика принимает события (проверено в Вебвизоре)? (yes / no)"

  "12_seo":
    name: "SEO"
    require_approved: ["11_analytics"]
    hard_checks:
      - id: meta_tags_yaml
        type: file_exists
        path: "{project}/12_SEO/meta-tags.yaml"
        required: true
```

- [ ] **Step 2: Commit**

```bash
git add config/stage-gates.yaml
git commit -m "feat(phase-3): stage-gates.yaml — declarative checks for 12 stages"
```

---

## Task 3.4: gate-check.sh runner

**Files:**
- Create: `scripts/gate-check.sh`
- Create: `tests/gate-check/test-gate-check.bats`

The runner reads the YAML, executes hard_checks, then prompts soft_checks (or skips them in `--auto` mode for tests).

- [ ] **Step 1: Write failing bats test**

`tests/gate-check/test-gate-check.bats`:

```bash
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/gate-check.sh"
    PROJECT_DIR="$BATS_TEST_TMPDIR/test-project"
    mkdir -p "$PROJECT_DIR/00_БРИФ"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
    export GATE_AUTO=1
}

@test "fails when require_approved stages not approved" {
    # 02_assets requires 00_brief + 01_context
    run bash "$SCRIPT" --stage 02_assets --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
    [[ "$output" == *"00_brief"* || "$output" == *"01_context"* ]]
}

@test "fails when hard_check file_exists fails" {
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "00_brief"
    bash "$REPO_ROOT/scripts/gate-state.sh" approve "$PROJECT_DIR" "01_context"
    # 02_assets requires PEXELS/UNSPLASH/PIXABAY ENV — none set in tests
    run bash "$SCRIPT" --stage 02_assets --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
}

@test "passes when stage 00_brief has brief.md" {
    echo "test brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    run bash "$SCRIPT" --stage 00_brief --project "$PROJECT_DIR"
    [ "$status" -eq 0 ]
}

@test "approve flag sets status to approved" {
    echo "test brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    bash "$SCRIPT" --stage 00_brief --project "$PROJECT_DIR" --approve
    run bash "$REPO_ROOT/scripts/gate-state.sh" get "$PROJECT_DIR" "00_brief"
    [ "$output" = "approved" ]
}
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Implement**

`scripts/gate-check.sh`:

```bash
#!/usr/bin/env bash
# scripts/gate-check.sh — per-stage gate runner.
# Reads config/stage-gates.yaml, executes hard_checks, prompts soft_checks.
# Usage: gate-check.sh --stage <id> --project <dir> [--approve] [--auto]
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GATES_YAML="$REPO_ROOT/config/stage-gates.yaml"
GATE_STATE="$REPO_ROOT/scripts/gate-state.sh"

stage=""
project=""
approve=0
auto="${GATE_AUTO:-0}"

while [ $# -gt 0 ]; do
    case "$1" in
        --stage) stage="$2"; shift 2 ;;
        --project) project="$2"; shift 2 ;;
        --approve) approve=1; shift ;;
        --auto) auto=1; shift ;;
        *) shift ;;
    esac
done

[ -z "$stage" ] && { echo "ERROR: --stage required" >&2; exit 2; }
[ -z "$project" ] && { echo "ERROR: --project required" >&2; exit 2; }
[ -f "$GATES_YAML" ] || { echo "ERROR: $GATES_YAML missing" >&2; exit 2; }

# Load .env
[ -f "$REPO_ROOT/.env" ] && set -a && . "$REPO_ROOT/.env" && set +a

echo "═══ Gate check: stage=$stage project=$(basename "$project") ═══"

# 1. Check require_approved
required="$(yq -r ".stages.\"$stage\".require_approved // [] | join(\",\")" "$GATES_YAML")"
if [ -n "$required" ]; then
    if ! bash "$GATE_STATE" all_approved "$project" "$required"; then
        echo "❌ Previous stages not approved. Cannot run $stage."
        exit 1
    fi
    echo "✅ Required prior stages approved: $required"
fi

# 2. Run hard_checks
fail=0
checks_count="$(yq -r ".stages.\"$stage\".hard_checks // [] | length" "$GATES_YAML")"
for i in $(seq 0 $((checks_count - 1))); do
    check_id="$(yq -r ".stages.\"$stage\".hard_checks[$i].id" "$GATES_YAML")"
    check_type="$(yq -r ".stages.\"$stage\".hard_checks[$i].type" "$GATES_YAML")"
    fix_hint="$(yq -r ".stages.\"$stage\".hard_checks[$i].fix_hint // \"\"" "$GATES_YAML")"

    case "$check_type" in
        file_exists)
            path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
            if [ -e "$path" ]; then
                echo "  ✅ $check_id ($path)"
            else
                echo "  ❌ $check_id: missing $path"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        http_ping)
            url="$(yq -r ".stages.\"$stage\".hard_checks[$i].url" "$GATES_YAML")"
            if curl -sfI --max-time 10 "$url" >/dev/null 2>&1; then
                echo "  ✅ $check_id ($url)"
            else
                echo "  ❌ $check_id: $url unreachable"
                fail=1
            fi
            ;;
        api_validator)
            svc="$(yq -r ".stages.\"$stage\".hard_checks[$i].validator" "$GATES_YAML")"
            if bash "$REPO_ROOT/scripts/validate-all.sh" --service "$svc" >/dev/null 2>&1; then
                echo "  ✅ $check_id ($svc)"
            else
                echo "  ❌ $check_id: $svc validator failed"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        api_validator_any_of)
            services="$(yq -r ".stages.\"$stage\".hard_checks[$i].validators | join(\" \")" "$GATES_YAML")"
            any_ok=0
            for svc in $services; do
                if bash "$REPO_ROOT/scripts/validate-all.sh" --service "$svc" >/dev/null 2>&1; then
                    any_ok=1
                    echo "  ✅ $check_id ($svc)"
                    break
                fi
            done
            if [ "$any_ok" = "0" ]; then
                echo "  ❌ $check_id: none of [$services] valid"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
        *)
            echo "  ⚠️  $check_id: unknown type $check_type" >&2
            ;;
    esac
done

if [ "$fail" = "1" ]; then
    echo "❌ Gate failed for $stage"
    exit 1
fi

# 3. Soft checks (only when interactive and not --auto)
soft_count="$(yq -r ".stages.\"$stage\".soft_checks // [] | length" "$GATES_YAML")"
if [ "$soft_count" -gt 0 ] && [ "$auto" != "1" ]; then
    echo ""
    echo "▶ Soft checks (please answer):"
    for i in $(seq 0 $((soft_count - 1))); do
        prompt="$(yq -r ".stages.\"$stage\".soft_checks[$i].prompt" "$GATES_YAML")"
        check_id="$(yq -r ".stages.\"$stage\".soft_checks[$i].id" "$GATES_YAML")"
        read -r -p "  [$check_id] $prompt " ans
        case "$ans" in
            yes|y) echo "    ✅ confirmed" ;;
            no|n)  echo "    ❌ not satisfied"; fail=1 ;;
            *)     echo "    ⚠️  partial / skipped" ;;
        esac
    done
fi

if [ "$fail" = "1" ]; then
    echo "❌ Gate failed (soft check unsatisfied)"
    exit 1
fi

# 4. Mark in_progress or approve
if [ "$approve" = "1" ]; then
    bash "$GATE_STATE" approve "$project" "$stage"
    echo "✅ Stage $stage approved"
else
    bash "$GATE_STATE" set "$project" "$stage" "in_progress"
    echo "✅ Gate passed for $stage (status: in_progress)"
fi
```

```bash
chmod +x scripts/gate-check.sh
```

- [ ] **Step 4: Run — pass**

Run: `bats tests/gate-check/test-gate-check.bats`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/gate-check.sh tests/gate-check/test-gate-check.bats
chmod +x scripts/gate-check.sh
git commit -m "feat(phase-3): gate-check.sh — runs hard+soft checks per stage"
```

---

## Task 3.5: e2e skip-prevention test

**Files:**
- Create: `tests/e2e/test-skip-prevention.bats`

- [ ] **Step 1: Write the test**

`tests/e2e/test-skip-prevention.bats`:

```bash
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    PROJECT_DIR="$BATS_TEST_TMPDIR/skip-prevention"
    mkdir -p "$PROJECT_DIR/00_БРИФ" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА" "$PROJECT_DIR/07_КОНТЕНТ" "$PROJECT_DIR/08_КОД/wp-theme"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$PROJECT_DIR/.landing-state.yaml"
    echo "brief" > "$PROJECT_DIR/00_БРИФ/brief.md"
    echo "design" > "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
    echo "copy" > "$PROJECT_DIR/07_КОНТЕНТ/final-copy.md"
    echo "<?php" > "$PROJECT_DIR/08_КОД/wp-theme/functions.php"
    export GATE_AUTO=1
}

@test "08_build refuses when 02-07 not approved" {
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
    [[ "$output" == *"not approved"* || "$output" == *"02_assets"* || "$output" == *"07_content"* ]]
}

@test "09_deploy refuses when 08_build not approved" {
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 09_deploy --project "$PROJECT_DIR"
    [ "$status" -ne 0 ]
    [[ "$output" == *"08_build"* ]]
}
```

- [ ] **Step 2: Run — pass (already implemented in Task 3.4)**

Run: `bats tests/e2e/test-skip-prevention.bats`
Expected: 2 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/e2e/test-skip-prevention.bats
git commit -m "test(phase-3): e2e skip-prevention test"
```

---

# Phase 4 — Integration into Slash-Commands

## Task 4.1: Replace preflight.sh with gate-check delegate

**Files:**
- Modify: `scripts/preflight.sh`

- [ ] **Step 1: Read current preflight.sh**

Run: `cat scripts/preflight.sh`

- [ ] **Step 2: Replace with delegating version**

Overwrite `scripts/preflight.sh`:

```bash
#!/usr/bin/env bash
# scripts/preflight.sh — system-wide preflight check
# Delegates to setup-flag.sh + validate-all.sh
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)/.."
cd "$REPO_ROOT" || exit 2

echo "=== Landing System Preflight Check ==="

if ! bash scripts/setup-flag.sh is_complete; then
    echo "❌ Onboarding не пройден. Запусти /landing-onboarding"
    exit 1
fi

bash scripts/validate-all.sh
```

- [ ] **Step 3: Sanity-run**

Run: `bash scripts/preflight.sh`
Expected: prints onboarding-not-complete error in fresh env, or runs all validators if flag exists.

- [ ] **Step 4: Commit**

```bash
git add scripts/preflight.sh
git commit -m "refactor(phase-4): preflight.sh delegates to setup-flag + validate-all"
```

---

## Task 4.2: Add gate-check to landing-new

**Files:**
- Modify: `commands/landing-new.md`

- [ ] **Step 1: Read current landing-new.md**

Run: `cat commands/landing-new.md`

- [ ] **Step 2: Prepend onboarding check**

Edit `commands/landing-new.md` — add this block at the top of the body (before existing instructions):

```markdown
## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Continue with existing flow below.

## Post-creation

After project folder is created from template:
1. Copy `template/.landing-state.yaml` to `<project>/.landing-state.yaml`
2. Set `project: <slug>` and `created: <ISO timestamp>` fields via yq
3. Run `bash scripts/gate-check.sh --stage 00_brief --project <project>` to verify brief.md exists.
```

- [ ] **Step 3: Commit**

```bash
git add commands/landing-new.md
git commit -m "feat(phase-4): /landing-new enforces onboarding + initializes .landing-state.yaml"
```

---

## Task 4.3: Add gate-check to stage commands (references → content)

**Files:**
- Modify: `commands/landing-references.md`
- Modify: `commands/landing-moodboard.md`
- Modify: `commands/landing-brand.md`
- Modify: `commands/landing-design.md`
- Modify: `commands/landing-stack.md`
- Modify: `commands/landing-content.md`

For each of these files, prepend identical block. The mapping:

| Command | Stage |
|---|---|
| landing-references.md | 03_references |
| landing-moodboard.md | 03_references |
| landing-brand.md | 04_brand |
| landing-design.md | 05_design |
| landing-stack.md | 06_stack |
| landing-content.md | 07_content |

- [ ] **Step 1: Modify each command file**

For each file, prepend after the frontmatter:

```markdown
## Pre-flight

1. Run `bash scripts/setup-flag.sh is_complete`. If exit 1 → reply "Onboarding не пройден. Запусти /landing-onboarding" and stop.
2. Determine project dir from `<project>` argument or current `landing.project` config.
3. Run: `bash scripts/gate-check.sh --stage <STAGE_ID> --project <project>`.
   If exit 1 → relay the gate error to the user (which previous stage is missing) and stop.
4. Continue with existing flow below.

## Post-completion

When the agent reports stage finished and user approves, run:
`bash scripts/gate-check.sh --stage <STAGE_ID> --project <project> --approve`
```

Replace `<STAGE_ID>` with the stage from the table.

- [ ] **Step 2: Verify all six files modified**

Run: `grep -l "scripts/gate-check.sh" commands/*.md | wc -l`
Expected: at least 7 (these 6 + landing-new from Task 4.2).

- [ ] **Step 3: Commit**

```bash
git add commands/landing-references.md commands/landing-moodboard.md commands/landing-brand.md commands/landing-design.md commands/landing-stack.md commands/landing-content.md
git commit -m "feat(phase-4): gate-check pre/post-flight in 6 stage commands"
```

---

## Task 4.4: Add gate-check to landing-build

**Files:**
- Modify: `commands/landing-build.md`

- [ ] **Step 1: Prepend pre/post-flight block**

Same as Task 4.3 with `<STAGE_ID> = 08_build`.

- [ ] **Step 2: Commit**

```bash
git add commands/landing-build.md
git commit -m "feat(phase-4): /landing-build enforces 02-07 approved"
```

---

## Task 4.5: Add gate-check to deploy + qa

**Files:**
- Modify: `commands/landing-deploy.md`
- Modify: `commands/landing-qa.md`

- [ ] **Step 1: Prepend pre/post-flight block to landing-deploy.md**

Same template, `<STAGE_ID> = 09_deploy`.

- [ ] **Step 2: Prepend pre/post-flight block to landing-qa.md**

Same template, `<STAGE_ID> = 10_qa`.

- [ ] **Step 3: Commit**

```bash
git add commands/landing-deploy.md commands/landing-qa.md
git commit -m "feat(phase-4): gate-check in /landing-deploy and /landing-qa"
```

---

## Task 4.6: Update landing-orchestrator to enforce state

**Files:**
- Modify: `agents/landing-orchestrator.md`

- [ ] **Step 1: Read current orchestrator**

Run: `cat agents/landing-orchestrator.md`

- [ ] **Step 2: Add Workflow Lock section**

Append (or insert before existing Rules) section:

```markdown
## Workflow lock — `.landing-state.yaml`

Before running any specialist agent, I:

1. Read `<project>/.landing-state.yaml`
2. If the requested stage's `require_approved` list (from `config/stage-gates.yaml`) has any entry not in `approved` status — refuse with: "Этап X требует прохождения этапа Y. Запусти `/landing-Y` сначала."
3. Never honor user requests like "пропусти этап" or "сразу к деплою". Workflow is enforced mechanically.
4. After a stage's specialist agent finishes and the user approves the output, run:
   `bash scripts/gate-check.sh --stage <stage> --project <project> --approve`

I do **not** approve a stage on the user's behalf. The user must explicitly approve via the slash command.
```

- [ ] **Step 3: Commit**

```bash
git add agents/landing-orchestrator.md
git commit -m "feat(phase-4): orchestrator enforces .landing-state.yaml lock"
```

---

# Phase 5 — Documentation + Push

## Task 5.1: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Onboarding section**

Insert after the "Quick Start" heading:

```markdown
## Первый запуск (onboarding)

После клонирования репо запусти:

```bash
bash scripts/wizard.sh
# или внутри Claude Code:
/landing-onboarding
```

Onboarding:
- проверяет локальные зависимости (wp-cli, ssh, rsync, python, jq)
- проверяет, что плагин `superpowers` установлен
- проверяет, что Firecrawl MCP настроен
- создаёт `.env` и валидирует все API-ключи
- создаёт флаг `~/.landing-system/setup_complete`

Без пройденного onboarding'а команды `/landing-*` не запускаются.

## Workflow Lock

Каждый проект содержит `.landing-state.yaml`, который фиксирует статус 13 этапов. `/landing-build` не запустится без одобренных 02–07; `/landing-deploy` — без одобренного 08. Этапы перепрыгивать нельзя.

Полный гайд: [`docs/SETUP.md`](docs/SETUP.md)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs(phase-5): README — onboarding + workflow lock sections"
```

---

## Task 5.2: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add lock note**

Append a new section after "Правила работы":

```markdown
## Workflow Lock (новое)

С 2026-05-04 система использует принудительный workflow:

- Перед `/landing-*` командой нужен пройденный onboarding (`~/.landing-system/setup_complete`)
- Каждый проект имеет `.landing-state.yaml`, фиксирующий статус 13 этапов
- `scripts/gate-check.sh` проверяет каждый этап (hard+soft checks)
- `landing-orchestrator` НЕ пропускает этапы, даже если пользователь просит

Подробнее: [`docs/SETUP.md`](docs/SETUP.md), [`docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md`](docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md)
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(phase-5): CLAUDE.md — note workflow lock"
```

---

## Task 5.3: Final integration sanity check + push

**Files:**
- All

- [ ] **Step 1: Run full Python test suite**

Run: `pytest tests/api_validators/ -v`
Expected: all pass.

- [ ] **Step 2: Run full bats suite**

Run: `bats tests/onboarding/ tests/gate-check/ tests/e2e/`
Expected: all pass.

- [ ] **Step 3: Run preflight**

Run: `bash scripts/preflight.sh`
Expected: prints status (will say onboarding incomplete in fresh env, that's OK).

- [ ] **Step 4: Verify git log shows reasonable progression**

Run: `git log --oneline | head -40`
Expected: ~30 commits in phase-1..5 sequence.

- [ ] **Step 5: Push to GitHub**

Run: `git push origin main`
Expected: all commits pushed.

- [ ] **Step 6: Final commit (if needed) — release notes**

If anything was tweaked, make a wrap-up commit:

```bash
git add -A
git diff --cached --quiet || git commit -m "chore(phase-5): final integration sanity check"
git push origin main
```

---

# Self-Review Notes (after writing)

**Spec coverage check:**
- Section 2 (architecture) → covered by Tasks 3.1–3.5 (state.yaml, gate-state, stage-gates.yaml, gate-check.sh) and Task 4.* (integration into commands)
- Section 3 (onboarding) → covered by Tasks 2.1–2.6 (wizard, setup-flag, validate-all, agent, command, skill, SETUP.md)
- Section 4 (API validators) → covered by Tasks 1.1–1.19 (15 validators + base + aggregate)
- Section 5 (.env.example) → Task 1.3
- Section 6 (phases 1-5) → matches plan phases 1-5
- Section 7 (testing) → covered: api_validators tests in 1.4–1.19, onboarding tests in 2.1–2.3, gate-check tests in 3.2 + 3.4 + 3.5, e2e in 3.5
- Section 9 (acceptance criteria) → all 7 covered (1: redirect to onboarding via Task 4.2; 2: setup_complete created via Task 2.3 wizard; 3: .landing-state.yaml init via Task 4.2; 4: skip-prevention via Task 3.4 + 3.5; 5: soft-checks via Task 3.4; 6: bats tests in Task 5.3; 7: push in Task 5.3)

**Placeholder scan:** no TBD/TODO/"implement later" — every code block is complete.

**Type consistency:** `ValidationResult(is_valid, message, service)` is used consistently across all validators and `aggregate.py`. Stage IDs are quoted strings in YAML (e.g., `"02_assets"`) consistently.
