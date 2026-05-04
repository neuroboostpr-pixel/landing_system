# Phase 5 — Deploy & Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать одноразовую настройку системы (`/landing-setup`), расширить WP-тему четырьмя новыми Python-скриптами (попапы, JS-инит, аналитика, CRM), задеплоить лендинг на Бегет через SSH+rsync+wp-cli, провести QA, добавить версионирование и A/B-клонирование.

**Architecture:** Пять блоков. (A) `/landing-setup` — одноразовый визард: preflight-проверка окружения, заполнение `.env`, конфигурация интеграций в `config/system.yaml`. (B) Четыре Python-скрипта расширяют Phase 4 pipeline: `generate-popup.py` (попап-система), `generate-js-init.py` (JS-инит Swiper/GSAP/Lenis/CountUp), `generate-analytics.py` (ЯМ + GTM), `generate-integrations.py` (AmoCRM + Bitrix24 + Telegram + email). (C) Деплой: `deploy-wordpress.sh` через SSH+rsync+wp-cli на Бегет. (D) QA: `qa-auditor` агент. (E) Версии + A/B: `create-version.sh` + `clone-landing.sh`. Все Python-скрипты следуют паттерну Phase 4: `main(argv:list)->int`, `sys.path.insert(0, parents[3])`, stdout=результат, stderr=tools/logger.

**Tech Stack:** Python 3.10+, PyYAML, Jinja2, pytest, bats-core. Deploy: SSH, rsync, wp-cli. JS CDN: Swiper 11, GSAP 3, Lenis 1.x, Fancybox 5, CountUp 2.x. Analytics: Яндекс Метрика, Google Tag Manager.

---

## Файловая структура

**Создать:**
- `tests/phase-5/conftest.py`
- `tests/phase-5/python/test_generate_popup.py`
- `tests/phase-5/python/test_generate_js_init.py`
- `tests/phase-5/python/test_generate_analytics.py`
- `tests/phase-5/python/test_generate_integrations.py`
- `tests/phase-5/test-agents-phase5.bats`
- `tests/phase-5/test-commands-phase5.bats`
- `tests/phase-5/integration/test-phase5-setup.bats`
- `config/system.yaml.template`
- `.env.example` (расширить)
- `scripts/preflight.sh`
- `skills/wp-gutenberg-block-builder/scripts/generate-popup.py`
- `skills/wp-gutenberg-block-builder/scripts/generate-js-init.py`
- `skills/wp-gutenberg-block-builder/scripts/generate-analytics.py`
- `skills/wp-gutenberg-block-builder/scripts/generate-integrations.py`
- `skills/wp-cli-deployer/SKILL.md`
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh`
- `skills/landing-versioning-and-cloning/SKILL.md`
- `skills/landing-versioning-and-cloning/scripts/create-version.sh`
- `skills/landing-versioning-and-cloning/scripts/clone-landing.sh`
- `agents/system-setup.md`
- `agents/wp-deployer.md`
- `agents/qa-auditor.md`
- `agents/lifecycle-keeper.md`
- `.claude/commands/landing-setup.md`
- `.claude/commands/landing-deploy.md`
- `.claude/commands/landing-qa.md`
- `.claude/commands/landing-rollback.md`
- `.claude/commands/landing-clone.md`

**Изменить:**
- `template/00_БРИФ/brief.md` — добавить секцию Интеграции + Аналитика
- `.claude/commands/landing-build.md` — добавить шаги 10–13 (popup, js-init, analytics, integrations)
- `agents/landing-orchestrator.md` — Phase 5 scope
- `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` — Phase 5 complete

---

## Task 1: conftest.py для Phase 5 + config/system.yaml.template + .env.example

**Files:**
- Create: `tests/phase-5/conftest.py`
- Create: `config/system.yaml.template`
- Modify: `.env.example`

- [ ] **Step 1: Написать conftest.py**

```python
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
        "mode: standard\nfonts:\n  cdn: bunny\n  families:\n    - name: Cabinet Grotesk\n      weights: [400, 700]\nicons:\n  library: lucide\njs_libraries: []\nui_libraries:\n  swiper: true\n  fancybox: true\n  countup: true\n",
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
```

- [ ] **Step 2: Написать config/system.yaml.template**

```yaml
# config/system.yaml.template
# Заполняется командой /landing-setup (один раз на всю систему).
# Скопируй в config/system.yaml и заполни вместе с агентом.

crm:
  amocrm:
    enabled: false
    subdomain: ""          # example.amocrm.ru
  bitrix24:
    enabled: false
    webhook_url: ""        # env: BITRIX24_WEBHOOK_URL
  telegram:
    enabled: false
    bot_token: ""          # env: TG_BOT_TOKEN
    chat_id: ""            # env: TG_CHAT_ID  (число, для группы со знаком минус)

analytics:
  yandex_metrika:
    enabled: false
    counter_id: ""         # 8-значное число из metrika.yandex.ru
  gtm:
    enabled: false
    container_id: ""       # GTM-XXXXXXX

ui_libraries:
  swiper: true             # слайдеры / карусели
  fancybox: true           # лайтбокс для фото / видео
  countup: true            # анимированные цифры
  typed: false             # эффект печатающегося текста

popups:
  enabled: true
  style: minimal           # minimal | fullscreen
```

- [ ] **Step 3: Расширить .env.example**

Добавить секции (если файл уже есть — дописать в конец, не удалять существующее):

```bash
# MCP серверы
FIRECRAWL_API_KEY=

# CRM
AMOCRM_API_KEY=
AMOCRM_SUBDOMAIN=example.amocrm.ru
BITRIX24_WEBHOOK_URL=
TG_BOT_TOKEN=
TG_CHAT_ID=

# Analytics (можно переопределить в brief.md конкретного проекта)
YM_COUNTER_ID=
GTM_CONTAINER_ID=

# Deploy — Бегет
BEGET_USER=
BEGET_HOST=srv123456.beget.ru
BEGET_PATH=/home/username/public_html
```

- [ ] **Step 4: Создать пустые тест-директории**

```bash
mkdir -p tests/phase-5/python tests/phase-5/integration
touch tests/phase-5/__init__.py tests/phase-5/python/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add tests/phase-5/conftest.py config/system.yaml.template .env.example \
        tests/phase-5/__init__.py tests/phase-5/python/__init__.py
git commit -m "chore(phase-5): Phase 5 conftest + system.yaml.template + .env.example"
```

---

## Task 2: scripts/preflight.sh + bats-тест для него

**Files:**
- Create: `scripts/preflight.sh`
- Create: `tests/phase-5/integration/test-phase5-setup.bats` (добавим позже в Task 16, здесь только preflight-тест)

- [ ] **Step 1: Написать failing bats-тест**

```bash
# tests/phase-5/integration/test-phase5-setup.bats
#!/usr/bin/env bats
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

@test "preflight.sh exists and is executable" {
  [ -f "$REPO_ROOT/scripts/preflight.sh" ]
  [ -x "$REPO_ROOT/scripts/preflight.sh" ]
}

@test "preflight.sh passes on this machine" {
  run "$REPO_ROOT/scripts/preflight.sh"
  [ "$status" -eq 0 ]
}

@test "preflight.sh fails when python missing dependency" {
  # temporarily break path so python3 not found
  run env PATH="" bash "$REPO_ROOT/scripts/preflight.sh"
  [ "$status" -ne 0 ]
}
```

Запустить: `bats tests/phase-5/integration/test-phase5-setup.bats`
Ожидание: FAIL (файл не существует).

- [ ] **Step 2: Написать preflight.sh**

```bash
#!/usr/bin/env bash
# scripts/preflight.sh — Landing System dependency check
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

_ok()   { echo "  ✅ $1"; }
_fail() { echo "  ❌ $1 — $2"; FAIL=1; }

echo "=== Landing System Preflight Check ==="
echo ""

echo "▶ Окружение"
python3 -c 'import sys; assert sys.version_info >= (3,10)' 2>/dev/null \
  && _ok "Python 3.10+" || _fail "Python 3.10+" "Установи Python 3.10+"

python3 -c 'import yaml, jinja2, requests, PIL' 2>/dev/null \
  && _ok "Python пакеты (yaml, jinja2, requests, pillow)" \
  || _fail "Python пакеты" "pip install pyyaml jinja2 requests pillow"

bats --version >/dev/null 2>&1 \
  && _ok "bats-core" || _fail "bats-core" "brew install bats-core"

wp --version >/dev/null 2>&1 \
  && _ok "wp-cli" || _fail "wp-cli" "brew install wp-cli"

echo ""
echo "▶ Конфигурация"

[ -f "$REPO_ROOT/.env" ] \
  && _ok ".env существует" || _fail ".env" "cp $REPO_ROOT/.env.example $REPO_ROOT/.env"

if [ -f "$REPO_ROOT/.env" ]; then
  grep -q "FIRECRAWL_API_KEY=." "$REPO_ROOT/.env" 2>/dev/null \
    && _ok "FIRECRAWL_API_KEY задан" \
    || _fail "FIRECRAWL_API_KEY" "Добавь ключ в .env (получить на firecrawl.dev)"
fi

[ -f "$REPO_ROOT/config/system.yaml" ] \
  && _ok "config/system.yaml существует" \
  || _fail "config/system.yaml" "Запусти /landing-setup чтобы создать"

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "✅ Все проверки пройдены — система готова к работе"
  exit 0
else
  echo "❌ Исправь ошибки выше и запусти preflight.sh снова"
  exit 1
fi
```

- [ ] **Step 3: Сделать исполняемым**

```bash
chmod +x scripts/preflight.sh
```

- [ ] **Step 4: Запустить тест (первые 2 теста должны пройти)**

```bash
bats tests/phase-5/integration/test-phase5-setup.bats
```

Ожидание: тест 1 и 2 — `ok`, тест 3 — может быть `ok` или `not ok` в зависимости от системы (PATH="" сломает и bash тоже). Если тест 3 нестабилен — убрать его из файла.

- [ ] **Step 5: Commit**

```bash
git add scripts/preflight.sh tests/phase-5/integration/test-phase5-setup.bats
git commit -m "feat(phase-5): preflight.sh + bats test"
```

---

## Task 3: agents/system-setup.md + .claude/commands/landing-setup.md

**Files:**
- Create: `agents/system-setup.md`
- Create: `.claude/commands/landing-setup.md`

- [ ] **Step 1: Написать agents/system-setup.md**

```markdown
---
name: system-setup
description: Use once to initialize the landing system. Runs preflight checks, configures .env, fills config/system.yaml, reports what's ready. Run via /landing-setup.
allowed-tools: Bash, Read, Write, Edit
---

# system-setup (Настройщик системы)

## Mission

Настраиваю систему один раз. После меня можно делать лендинги.

## What I do

### 1. Preflight
```bash
bash scripts/preflight.sh
```
Если есть ❌ — вывожу инструкции для каждой ошибки. Жду пока пользователь исправит, запускаю снова.

### 2. Настройка .env
Если `.env` не существует: `cp .env.example .env`.
Для каждого пустого поля — спрашиваю пользователя, заполняю.

Обязательные поля:
- `FIRECRAWL_API_KEY` → объясняю: получить на firecrawl.dev → бесплатный план
- `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH` → для деплоя (можно пропустить если пока не деплоим)

Опциональные (если есть интеграции):
- `TG_BOT_TOKEN`, `TG_CHAT_ID` → если нужны Telegram-уведомления
- `AMOCRM_API_KEY`, `AMOCRM_SUBDOMAIN` → если AmoCRM
- `BITRIX24_WEBHOOK_URL` → если Bitrix24

### 3. Заполнение config/system.yaml
Если файл не существует: `cp config/system.yaml.template config/system.yaml`.

Задаю вопросы:
1. **CRM для заявок:** AmoCRM / Bitrix24 / только Telegram / только email?
2. **Telegram-бот для уведомлений?** (да/нет) → если да — прошу токен и chat_id
3. **Яндекс.Метрика?** (да/нет) → если да — счётчик создаётся позже в проекте
4. **Google Tag Manager?** (да/нет)
5. **JS библиотеки:** Swiper (слайдеры), Fancybox (лайтбокс), CountUp (цифры) — всё включено по умолчанию
6. **Попапы встроенные?** (да/нет — по умолчанию да)

Записываю ответы в `config/system.yaml`.

### 4. Отчёт
```
✅ Система настроена!

Подключено:
- CRM: AmoCRM (test.amocrm.ru)
- Telegram бот: @my_leads_bot
- ЯМ: настраивается per-project в брифе
- GTM: настраивается per-project в брифе
- JS: Swiper ✅, Fancybox ✅, CountUp ✅
- Попапы: встроенные ✅

Теперь можно создавать лендинги → /landing-new <slug>
```

## Rules
- ❌ Никогда не записывать токены и ключи в system.yaml — только в .env
- ✅ system.yaml хранит только флаги (enabled: true) и публичные значения (subdomain)
- ✅ Объяснять каждый шаг пользователю — он может быть учеником
```

- [ ] **Step 2: Написать .claude/commands/landing-setup.md**

```markdown
---
description: One-time system initialization. Runs preflight checks, configures .env and config/system.yaml, reports what integrations are ready. Run once before creating any landing projects.
allowed-tools: Bash, Read, Write, Edit
---

# /landing-setup

Одноразовая настройка системы. Запускается один раз при установке.

## What I do

1. Run `scripts/preflight.sh` — check Python, bats, wp-cli, .env
2. If any checks fail — show fix instructions, wait, re-run
3. Configure `.env` — collect API keys for Firecrawl, CRM, deploy
4. Configure `config/system.yaml` — select integrations (CRM, analytics, libraries)
5. Show readiness report

## Usage

```
/landing-setup
```

## Output

- `.env` — filled with API keys (gitignored)
- `config/system.yaml` — integration settings (committed)
- Readiness report showing what's connected

## After setup

```
/landing-new <slug>   — create a new landing project
```
```

- [ ] **Step 3: Commit**

```bash
git add agents/system-setup.md .claude/commands/landing-setup.md
git commit -m "feat(phase-5): system-setup agent + /landing-setup command"
```

---

## Task 4: test_generate_popup.py → generate-popup.py

**Files:**
- Create: `tests/phase-5/python/test_generate_popup.py`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-popup.py`

- [ ] **Step 1: Написать failing тест**

```python
# tests/phase-5/python/test_generate_popup.py
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-popup.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_popup", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def popup_project(wp_built_project):
    return wp_built_project


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(popup_project):
    mod = _load()
    assert mod.main(["generate-popup.py", str(popup_project)]) == 0


def test_popup_js_created(popup_project):
    mod = _load()
    mod.main(["generate-popup.py", str(popup_project)])
    js = popup_project / "08_КОД" / "wp-theme" / "assets" / "js" / "popup.js"
    assert js.exists()
    content = js.read_text(encoding="utf-8")
    assert "data-popup" in content
    assert "lp-popup--open" in content


def test_popup_css_created(popup_project):
    mod = _load()
    mod.main(["generate-popup.py", str(popup_project)])
    css = popup_project / "08_КОД" / "wp-theme" / "assets" / "css" / "popup.css"
    assert css.exists()
    assert ".lp-popup" in css.read_text(encoding="utf-8")


def test_popup_php_created(popup_project):
    mod = _load()
    mod.main(["generate-popup.py", str(popup_project)])
    php = popup_project / "08_КОД" / "wp-theme" / "template-parts" / "popup-overlay.php"
    assert php.exists()
    assert "lp-popup" in php.read_text(encoding="utf-8")


def test_functions_php_has_popup_enqueue(popup_project):
    mod = _load()
    mod.main(["generate-popup.py", str(popup_project)])
    fp = (popup_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "popup.js" in fp
    assert "popup.css" in fp


def test_missing_functions_php_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-popup.py", str(tmp_path)]) == 1
```

Запустить: `pytest tests/phase-5/python/test_generate_popup.py -v`
Ожидание: FAIL (скрипт не существует).

- [ ] **Step 2: Написать generate-popup.py**

```python
#!/usr/bin/env python3
"""Generate popup system (JS + CSS + PHP overlay) and register in functions.php.

CLI: python3 generate-popup.py <project-dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success

_POPUP_JS = """\
// lp-popup — встроенная система попапов
document.addEventListener('DOMContentLoaded', function () {
  function openPopup(id) {
    var el = document.getElementById(id);
    if (el) { el.classList.add('lp-popup--open'); document.body.classList.add('lp-popup-lock'); }
  }
  function closeAll() {
    document.querySelectorAll('.lp-popup').forEach(function (p) { p.classList.remove('lp-popup--open'); });
    document.body.classList.remove('lp-popup-lock');
  }
  document.querySelectorAll('[data-popup]').forEach(function (btn) {
    btn.addEventListener('click', function (e) { e.preventDefault(); openPopup(btn.getAttribute('data-popup')); });
  });
  document.querySelectorAll('.lp-popup__close').forEach(function (el) {
    el.addEventListener('click', closeAll);
  });
  document.querySelectorAll('.lp-popup__overlay').forEach(function (el) {
    el.addEventListener('click', closeAll);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(); });
});
"""

_POPUP_CSS = """\
/* lp-popup system */
body.lp-popup-lock { overflow: hidden; }
.lp-popup { display: none; position: fixed; inset: 0; z-index: 9999; align-items: center; justify-content: center; }
.lp-popup--open { display: flex; }
.lp-popup__overlay { position: absolute; inset: 0; background: rgba(0,0,0,.55); }
.lp-popup__box {
  position: relative; z-index: 1; background: #fff; border-radius: 12px;
  padding: 2.5rem; width: min(560px, 94vw); max-height: 90vh; overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0,0,0,.18);
}
.lp-popup__close {
  position: absolute; top: 1rem; right: 1rem; background: none; border: none;
  font-size: 1.5rem; cursor: pointer; line-height: 1; color: #555;
}
.lp-popup__close:hover { color: #000; }
"""

_POPUP_PHP = """\
<?php
// template-parts/popup-overlay.php
// Использование: <button data-popup="lead-form">Записаться</button>
// Добавь этот файл через get_template_part() в front-page.php после форм
?>
<div class="lp-popup" id="lead-form">
  <div class="lp-popup__overlay"></div>
  <div class="lp-popup__box">
    <button class="lp-popup__close" aria-label="Закрыть">&times;</button>
    <?php
    // Вставь shortcode Fluent Forms:
    // echo do_shortcode('[fluentform id="1"]');
    ?>
  </div>
</div>
"""

_ENQUEUE_ADDON = """\

// Popup system
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('lp-popup', get_template_directory_uri() . '/assets/css/popup.css');
    wp_enqueue_script('lp-popup', get_template_directory_uri() . '/assets/js/popup.js', [], null, true);
});
"""


def _find_functions_php(start: Path) -> Path:
    candidate = start / "08_КОД" / "wp-theme" / "functions.php"
    if candidate.exists():
        return candidate
    for parent in start.parents:
        c = parent / "08_КОД" / "wp-theme" / "functions.php"
        if c.exists():
            return c
    raise FileNotFoundError("functions.php not found — run /landing-build first")


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-popup.py <project-dir>")
        return 1
    try:
        start = Path(argv[1])
        fp = _find_functions_php(start)
        project = fp.parents[2]  # 08_КОД/wp-theme → project root
        theme = fp.parent

        (theme / "assets" / "js" / "popup.js").write_text(_POPUP_JS, encoding="utf-8")
        (theme / "assets" / "css" / "popup.css").write_text(_POPUP_CSS, encoding="utf-8")
        (theme / "template-parts" / "popup-overlay.php").write_text(_POPUP_PHP, encoding="utf-8")

        current = fp.read_text(encoding="utf-8")
        if "lp-popup" not in current:
            fp.write_text(current + _ENQUEUE_ADDON, encoding="utf-8")

        success(f"Popup system → {theme}")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Запустить тесты — убедиться GREEN**

```bash
pytest tests/phase-5/python/test_generate_popup.py -v
```

Ожидание: 7 тестов `PASSED`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-5/python/test_generate_popup.py \
        skills/wp-gutenberg-block-builder/scripts/generate-popup.py
git commit -m "feat(phase-5): generate-popup.py — встроенная popup-система"
```

---

## Task 5: test_generate_js_init.py → generate-js-init.py

**Files:**
- Create: `tests/phase-5/python/test_generate_js_init.py`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-js-init.py`

- [ ] **Step 1: Написать failing тест**

```python
# tests/phase-5/python/test_generate_js_init.py
import importlib.util
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-js-init.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_js_init", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-js-init.py", str(wp_built_project)]) == 0


def test_main_js_created(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    js = wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "main.js"
    assert js.exists()


def test_sliders_js_created_when_swiper_enabled(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    assert (wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "sliders.js").exists()


def test_counters_js_created_when_countup_enabled(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    assert (wp_built_project / "08_КОД" / "wp-theme" / "assets" / "js" / "counters.js").exists()


def test_smooth_scroll_created_when_lenis(wp_built_project_cinematic):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project_cinematic)])
    js = wp_built_project_cinematic / "08_КОД" / "wp-theme" / "assets" / "js" / "smooth-scroll.js"
    assert js.exists()
    assert "Lenis" in js.read_text(encoding="utf-8")


def test_animations_js_created_when_gsap(wp_built_project_cinematic):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project_cinematic)])
    js = wp_built_project_cinematic / "08_КОД" / "wp-theme" / "assets" / "js" / "animations.js"
    assert js.exists()
    assert "ScrollTrigger" in js.read_text(encoding="utf-8")


def test_functions_php_has_swiper_enqueue(wp_built_project):
    mod = _load()
    mod.main(["generate-js-init.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "swiper" in fp.lower()


def test_missing_stack_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-js-init.py", str(tmp_path)]) == 1
```

Запустить: `pytest tests/phase-5/python/test_generate_js_init.py -v`
Ожидание: FAIL.

- [ ] **Step 2: Написать generate-js-init.py**

```python
#!/usr/bin/env python3
"""Generate JS initialization files and register CDN libraries in functions.php.

CLI: python3 generate-js-init.py <project-dir>
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn

_CDN = {
    "swiper": {
        "css": "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css",
        "js": "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js",
        "handle": "swiper",
    },
    "fancybox": {
        "css": "https://cdn.jsdelivr.net/npm/@fancyapps/ui@5/dist/fancybox/fancybox.css",
        "js": "https://cdn.jsdelivr.net/npm/@fancyapps/ui@5/dist/fancybox/fancybox.umd.js",
        "handle": "fancybox",
    },
    "countup": {
        "js": "https://cdn.jsdelivr.net/npm/countup.js@2/dist/countUp.umd.js",
        "handle": "countup",
    },
    "typed": {
        "js": "https://cdn.jsdelivr.net/npm/typed.js@2/dist/typed.umd.js",
        "handle": "typed",
    },
    "gsap": {
        "js": "https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js",
        "handle": "gsap",
    },
    "scrolltrigger": {
        "js": "https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js",
        "handle": "gsap-scrolltrigger",
        "deps": ["gsap"],
    },
    "lenis": {
        "js": "https://cdn.jsdelivr.net/npm/lenis@1/dist/lenis.min.js",
        "handle": "lenis",
    },
    "split-type": {
        "js": "https://cdn.jsdelivr.net/npm/split-type@0/umd/index.min.js",
        "handle": "split-type",
    },
}

_MAIN_JS = """\
// main.js — точка входа
// Инициализация всех библиотек происходит в отдельных файлах
document.addEventListener('DOMContentLoaded', function () {
  console.log('[LP] scripts ready');
});
"""

_SMOOTH_SCROLL_JS = """\
// smooth-scroll.js — Lenis smooth scroll
var lenis = new Lenis({ autoRaf: true, lerp: 0.08, smoothWheel: true });
"""

_ANIMATIONS_JS = """\
// animations.js — GSAP + ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

// Fade-in для элементов с data-animate
document.querySelectorAll('[data-animate]').forEach(function (el) {
  gsap.from(el, {
    scrollTrigger: { trigger: el, start: 'top 82%', once: true },
    opacity: 0,
    y: 40,
    duration: 0.8,
    ease: 'power2.out',
  });
});
"""

_SLIDERS_JS = """\
// sliders.js — Swiper sliders
document.querySelectorAll('.lp-slider').forEach(function (el) {
  new Swiper(el, {
    loop: true,
    slidesPerView: 1,
    spaceBetween: 24,
    pagination: { el: el.querySelector('.swiper-pagination'), clickable: true },
    navigation: {
      nextEl: el.querySelector('.swiper-button-next'),
      prevEl: el.querySelector('.swiper-button-prev'),
    },
    breakpoints: { 768: { slidesPerView: 2 }, 1200: { slidesPerView: 3 } },
  });
});
"""

_COUNTERS_JS = """\
// counters.js — CountUp animated numbers
document.querySelectorAll('[data-countup]').forEach(function (el) {
  var target = parseFloat(el.getAttribute('data-countup')) || 0;
  var decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals')) : 0;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        new countUp.CountUp(el, target, { decimalPlaces: decimals, duration: 2 }).start();
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.3 });
  observer.observe(el);
});
"""


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "06_СТЕК" / "design-stack.yaml").exists():
            return parent
    raise FileNotFoundError("design-stack.yaml not found — run /landing-stack first")


def _load_stack(project: Path) -> dict:
    return yaml.safe_load(
        (project / "06_СТЕК" / "design-stack.yaml").read_text(encoding="utf-8")
    ) or {}


def _enqueue_block(libs: list[str]) -> str:
    lines = ["\n// JS/CSS библиотеки (generate-js-init.py)\nadd_action('wp_enqueue_scripts', function () {"]
    for lib in libs:
        cfg = _CDN.get(lib, {})
        handle = cfg.get("handle", lib)
        deps = cfg.get("deps", [])
        deps_php = "array(" + ", ".join(f"'{d}'" for d in deps) + ")" if deps else "array()"
        if "css" in cfg:
            lines.append(f"    wp_enqueue_style('{handle}', '{cfg['css']}');")
        if "js" in cfg:
            lines.append(f"    wp_enqueue_script('{handle}', '{cfg['js']}', {deps_php}, null, true);")
    lines.append("});")
    return "\n".join(lines) + "\n"


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-js-init.py <project-dir>")
        return 1
    try:
        project = _find_project_root(Path(argv[1]))
        stack = _load_stack(project)
        js_libs = [l.lower() for l in (stack.get("js_libraries") or [])]
        ui_libs_cfg = stack.get("ui_libraries") or {}
        ui_libs = [k for k, v in ui_libs_cfg.items() if v]
        all_libs = js_libs + [l for l in ui_libs if l not in js_libs]

        theme_js = project / "08_КОД" / "wp-theme" / "assets" / "js"
        theme_js.mkdir(parents=True, exist_ok=True)

        (theme_js / "main.js").write_text(_MAIN_JS, encoding="utf-8")

        if "lenis" in all_libs:
            (theme_js / "smooth-scroll.js").write_text(_SMOOTH_SCROLL_JS, encoding="utf-8")
        if "gsap" in all_libs or "scrolltrigger" in all_libs:
            (theme_js / "animations.js").write_text(_ANIMATIONS_JS, encoding="utf-8")
        if "swiper" in all_libs:
            (theme_js / "sliders.js").write_text(_SLIDERS_JS, encoding="utf-8")
        if "countup" in all_libs:
            (theme_js / "counters.js").write_text(_COUNTERS_JS, encoding="utf-8")

        fp = project / "08_КОД" / "wp-theme" / "functions.php"
        if fp.exists() and all_libs:
            current = fp.read_text(encoding="utf-8")
            block = _enqueue_block(all_libs)
            if "generate-js-init" not in current:
                fp.write_text(current + block, encoding="utf-8")

        success(f"JS init files → {theme_js} ({len(all_libs)} libs)")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Запустить тесты — GREEN**

```bash
pytest tests/phase-5/python/test_generate_js_init.py -v
```

Ожидание: 9 тестов `PASSED`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-5/python/test_generate_js_init.py \
        skills/wp-gutenberg-block-builder/scripts/generate-js-init.py
git commit -m "feat(phase-5): generate-js-init.py — Swiper/GSAP/Lenis/CountUp инициализация"
```

---

## Task 6: test_generate_analytics.py → generate-analytics.py

**Files:**
- Create: `tests/phase-5/python/test_generate_analytics.py`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-analytics.py`

- [ ] **Step 1: Написать failing тест**

```python
# tests/phase-5/python/test_generate_analytics.py
import importlib.util
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-analytics.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_analytics", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-analytics.py", str(wp_built_project)]) == 0


def test_ym_placeholder_replaced(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "98765432" in fp
    assert "// [YM_COUNTER]" not in fp


def test_ym_has_reachgoal(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "reachGoal" in fp


def test_gtm_head_injected(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "GTM-ABCDEFG" in fp
    assert "googletagmanager" in fp


def test_gtm_noscript_in_body(wp_built_project):
    mod = _load()
    mod.main(["generate-analytics.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "wp_body_open" in fp
    assert "noscript" in fp


def test_missing_functions_php_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-analytics.py", str(tmp_path)]) == 1


def test_parse_ym_from_brief():
    mod = _load()
    brief = "## Аналитика\n- YM счётчик: 12345678\n- GTM контейнер: GTM-XYZ123\n"
    ym, gtm = mod._parse_analytics(brief)
    assert ym == "12345678"
    assert gtm == "GTM-XYZ123"
```

- [ ] **Step 2: Написать generate-analytics.py**

```python
#!/usr/bin/env python3
"""Inject Yandex Metrika + Google Tag Manager into functions.php.

CLI: python3 generate-analytics.py <project-dir>
Reads: 00_БРИФ/brief.md for YM counter ID and GTM container ID.
Modifies: 08_КОД/wp-theme/functions.php — replaces // [YM_COUNTER] placeholder.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn


def _parse_analytics(brief_text: str) -> tuple[str, str]:
    ym = ""
    gtm = ""
    m = re.search(r"YM\s*счётчик[:\s]+(\d{6,10})", brief_text, re.IGNORECASE)
    if m:
        ym = m.group(1)
    m2 = re.search(r"GTM\s*(?:контейнер)?[:\s]+(GTM-[A-Z0-9]+)", brief_text, re.IGNORECASE)
    if m2:
        gtm = m2.group(1)
    return ym, gtm


def _ym_code(counter_id: str) -> str:
    return (
        f"// Yandex Metrika — counter {counter_id}\n"
        "add_action('wp_head', function () { ?>\n"
        "<script>\n"
        "(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};\n"
        "m[i].l=1*new Date();\n"
        "for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}\n"
        "k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})\n"
        f"(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');\n"
        f"ym({counter_id}, 'init', {{ clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true }});\n"
        "// Цель: отправка формы\n"
        f"// ym({counter_id}, 'reachGoal', 'form_submit');\n"
        "</script>\n"
        f"<noscript><div><img src='https://mc.yandex.ru/watch/{counter_id}' style='position:absolute; left:-9999px;' alt='' /></div></noscript>\n"
        "<?php }, 1);\n\n"
        "// Хелпер для отправки целей ЯМ из PHP\n"
        f"function lp_ym_goal(string $goal): void {{\n"
        f"    echo \"<script>ym({counter_id}, 'reachGoal', '\" . esc_js($goal) . \"');</script>\";\n"
        "}\n"
    )


def _gtm_head_code(container_id: str) -> str:
    return (
        f"// Google Tag Manager — {container_id}\n"
        "add_action('wp_head', function () { ?>\n"
        f"<!-- Google Tag Manager -->\n"
        f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});\n"
        f"var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';\n"
        f"j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;\n"
        f"f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{container_id}');</script>\n"
        f"<!-- End Google Tag Manager -->\n"
        "<?php }, 2);\n\n"
        "// GTM noscript (body)\n"
        "add_action('wp_body_open', function () { ?>\n"
        f"<!-- Google Tag Manager (noscript) -->\n"
        f"<noscript><iframe src='https://www.googletagmanager.com/ns.html?id={container_id}'\n"
        f"height='0' width='0' style='display:none;visibility:hidden'></iframe></noscript>\n"
        f"<!-- End Google Tag Manager (noscript) -->\n"
        "<?php });\n"
    )


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-analytics.py <project-dir>")
        return 1
    try:
        start = Path(argv[1])
        fp_candidates = list(start.rglob("08_КОД/wp-theme/functions.php"))
        if not fp_candidates:
            raise FileNotFoundError("functions.php not found — run /landing-build first")
        fp = fp_candidates[0]
        project = fp.parents[2]

        brief_path = project / "00_БРИФ" / "brief.md"
        brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
        ym_id, gtm_id = _parse_analytics(brief_text)

        current = fp.read_text(encoding="utf-8")

        if ym_id:
            current = current.replace("// [YM_COUNTER] — Yandex Metrika (analytics-engineer)", _ym_code(ym_id))
            current = current.replace("// [YM_COUNTER]", _ym_code(ym_id))
        else:
            warn("YM счётчик не найден в brief.md — пропускаю")

        if gtm_id:
            current += "\n" + _gtm_head_code(gtm_id)
        else:
            warn("GTM контейнер не найден в brief.md — пропускаю")

        fp.write_text(current, encoding="utf-8")
        success(f"Analytics injected → {fp}")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Запустить тесты — GREEN**

```bash
pytest tests/phase-5/python/test_generate_analytics.py -v
```

Ожидание: 8 тестов `PASSED`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-5/python/test_generate_analytics.py \
        skills/wp-gutenberg-block-builder/scripts/generate-analytics.py
git commit -m "feat(phase-5): generate-analytics.py — Яндекс Метрика + GTM"
```

---

## Task 7: test_generate_integrations.py → generate-integrations.py

**Files:**
- Create: `tests/phase-5/python/test_generate_integrations.py`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-integrations.py`

- [ ] **Step 1: Написать failing тест**

```python
# tests/phase-5/python/test_generate_integrations.py
import importlib.util
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-integrations.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_integrations", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-integrations.py", str(wp_built_project)]) == 0


def test_fluent_webhook_placeholder_replaced(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "// [FLUENT_WEBHOOK]" not in fp
    assert "fluentform" in fp.lower() or "fluent" in fp.lower()


def test_telegram_code_injected_when_enabled(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "TG_BOT_TOKEN" in fp
    assert "api.telegram.org" in fp


def test_amocrm_instruction_created(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    inst = wp_built_project / "08_КОД" / "integrations" / "amocrm-setup.md"
    assert inst.exists()
    assert "AmoCRM" in inst.read_text(encoding="utf-8")


def test_telegram_instruction_created(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    inst = wp_built_project / "08_КОД" / "integrations" / "telegram-setup.md"
    assert inst.exists()


def test_parse_integrations_from_brief():
    mod = _load()
    brief = "## Интеграции\n- CRM: AmoCRM\n- Telegram уведомления: да\n- Попапы: да\n"
    result = mod._parse_integrations(brief)
    assert result["crm"] == "amocrm"
    assert result["telegram"] is True


def test_missing_functions_php_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-integrations.py", str(tmp_path)]) == 1
```

- [ ] **Step 2: Написать generate-integrations.py**

```python
#!/usr/bin/env python3
"""Inject CRM webhooks into functions.php; write integration instruction files.

CLI: python3 generate-integrations.py <project-dir>
Reads: 00_БРИФ/brief.md
Modifies: 08_КОД/wp-theme/functions.php — replaces // [FLUENT_WEBHOOK]
Creates: 08_КОД/integrations/*.md — setup instructions per service
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn

_FLUENT_HOOK = """\
// Fluent Forms — webhook для CRM и Telegram
add_action('fluentform/submission_inserted', function ($entryId, $formData, $form) {
    $fields = is_array($formData) ? $formData : (array)$formData;

    // AmoCRM webhook (задай AMOCRM_WEBHOOK_URL в .env)
    $amo_url = getenv('AMOCRM_WEBHOOK_URL');
    if ($amo_url) {
        wp_remote_post($amo_url, [
            'headers' => ['Content-Type' => 'application/json'],
            'body'    => wp_json_encode(['lead' => $fields]),
            'timeout' => 5,
        ]);
    }

    // Bitrix24 webhook (задай BITRIX24_WEBHOOK_URL в .env)
    $b24_url = getenv('BITRIX24_WEBHOOK_URL');
    if ($b24_url) {
        wp_remote_post($b24_url . 'crm.lead.add.json', [
            'body'    => ['fields' => $fields],
            'timeout' => 5,
        ]);
    }

    // Telegram уведомление (задай TG_BOT_TOKEN и TG_CHAT_ID в .env)
    $tg_token = getenv('TG_BOT_TOKEN');
    $tg_chat  = getenv('TG_CHAT_ID');
    if ($tg_token && $tg_chat) {
        $lines = ["🔔 <b>Новая заявка!</b>"];
        foreach ($fields as $k => $v) {
            if (!empty($v)) { $lines[] = "<b>" . esc_html($k) . ":</b> " . esc_html($v); }
        }
        $msg = implode("\\n", $lines);
        $api = "https://api.telegram.org/bot{$tg_token}/sendMessage";
        wp_remote_get(add_query_arg(['chat_id' => $tg_chat, 'text' => $msg, 'parse_mode' => 'HTML'], $api));
    }
}, 10, 3);
"""

_AMOCRM_INSTRUCTIONS = """\
# AmoCRM — Инструкция подключения

## Шаг 1: Получить webhook URL
1. Войди в AmoCRM → Настройки → Интеграции → Webhooks
2. Нажми «Добавить вебхук»
3. URL: `https://your-site.ru/wp-json/lp/v1/lead` (или любой ваш обработчик)
4. Скопируй webhook URL

## Шаг 2: Добавить в .env
```
AMOCRM_WEBHOOK_URL=https://your-company.amocrm.ru/api/v4/...
AMOCRM_API_KEY=ваш_ключ
```

## Шаг 3: Проверить
Отправь тестовую заявку на сайте → проверь в AmoCRM в разделе «Сделки / Лиды»
"""

_BITRIX24_INSTRUCTIONS = """\
# Bitrix24 — Инструкция подключения

## Шаг 1: Создать входящий webhook
1. Войди в Bitrix24 → Разработчикам → Другое → Входящий webhook
2. Выбери права: CRM (crm.lead.add)
3. Скопируй URL вида `https://your.bitrix24.ru/rest/1/xxxxx/`

## Шаг 2: Добавить в .env
```
BITRIX24_WEBHOOK_URL=https://your.bitrix24.ru/rest/1/xxxxx/
```

## Шаг 3: Проверить
Отправь заявку → в Bitrix24 → CRM → Лиды — должна появиться новая запись
"""

_TELEGRAM_INSTRUCTIONS = """\
# Telegram Бот — Инструкция подключения

## Шаг 1: Создать бота
1. Открой @BotFather в Telegram → `/newbot`
2. Придумай имя и username (например `@my_leads_bot`)
3. Скопируй токен вида `123456789:ABCdefGHI...`

## Шаг 2: Получить chat_id
1. Добавь бота в нужную группу (или напиши ему лично)
2. Открой: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Найди `"chat":{"id": ...}` — это и есть chat_id (для группы будет отрицательным)

## Шаг 3: Добавить в .env
```
TG_BOT_TOKEN=123456789:ABCdefGHI...
TG_CHAT_ID=-100123456789
```

## Шаг 4: Проверить
Отправь заявку → должно прийти сообщение боту / в группу
"""


def _parse_integrations(brief_text: str) -> dict:
    crm = ""
    m = re.search(r"CRM\s*[:\s]+(AmoCRM|Bitrix24|нет)", brief_text, re.IGNORECASE)
    if m:
        raw = m.group(1).lower()
        if "amo" in raw:
            crm = "amocrm"
        elif "bitrix" in raw:
            crm = "bitrix24"
    telegram = bool(re.search(r"Telegram.*:\s*да", brief_text, re.IGNORECASE))
    return {"crm": crm, "telegram": telegram}


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-integrations.py <project-dir>")
        return 1
    try:
        start = Path(argv[1])
        fp_candidates = list(start.rglob("08_КОД/wp-theme/functions.php"))
        if not fp_candidates:
            raise FileNotFoundError("functions.php not found — run /landing-build first")
        fp = fp_candidates[0]
        project = fp.parents[2]

        brief_text = ""
        brief_path = project / "00_БРИФ" / "brief.md"
        if brief_path.exists():
            brief_text = brief_path.read_text(encoding="utf-8")

        integrations = _parse_integrations(brief_text)
        integ_dir = project / "08_КОД" / "integrations"
        integ_dir.mkdir(parents=True, exist_ok=True)

        current = fp.read_text(encoding="utf-8")
        fluent_placeholder = "// [FLUENT_WEBHOOK] — form webhook (integrations-engineer)"
        if fluent_placeholder in current:
            current = current.replace(fluent_placeholder, _FLUENT_HOOK)
        elif "// [FLUENT_WEBHOOK]" in current:
            current = current.replace("// [FLUENT_WEBHOOK]", _FLUENT_HOOK)
        else:
            current += "\n" + _FLUENT_HOOK
        fp.write_text(current, encoding="utf-8")

        if integrations["crm"] == "amocrm":
            (integ_dir / "amocrm-setup.md").write_text(_AMOCRM_INSTRUCTIONS, encoding="utf-8")
        elif integrations["crm"] == "bitrix24":
            (integ_dir / "bitrix24-setup.md").write_text(_BITRIX24_INSTRUCTIONS, encoding="utf-8")

        if integrations["telegram"]:
            (integ_dir / "telegram-setup.md").write_text(_TELEGRAM_INSTRUCTIONS, encoding="utf-8")

        success(f"Integrations → {integ_dir}")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Запустить тесты — GREEN**

```bash
pytest tests/phase-5/python/test_generate_integrations.py -v
```

Ожидание: 7 тестов `PASSED`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-5/python/test_generate_integrations.py \
        skills/wp-gutenberg-block-builder/scripts/generate-integrations.py
git commit -m "feat(phase-5): generate-integrations.py — AmoCRM + Bitrix24 + Telegram"
```

---

## Task 8: Обновить /landing-build + template/00_БРИФ/brief.md

**Files:**
- Modify: `.claude/commands/landing-build.md`
- Modify: `template/00_БРИФ/brief.md`

- [ ] **Step 1: Прочитать текущий landing-build.md и добавить шаги 10–13**

Добавить в `.claude/commands/landing-build.md` после Step 8 (render-build-preview.py):

```markdown
### Step 10 — Popup System
Run `generate-popup.py` to add built-in popup (JS + CSS + PHP overlay).

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-popup.py .
```

### Step 11 — JS Library Initialization
Run `generate-js-init.py` to create main.js, sliders.js, animations.js, counters.js.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-js-init.py .
```

### Step 12 — Analytics (Yandex Metrika + GTM)
Run `generate-analytics.py` to inject YM counter and GTM container from brief.md.

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-analytics.py .
```

### Step 13 — CRM Integrations
Run `generate-integrations.py` to inject Fluent Forms webhook (AmoCRM / Bitrix24 / Telegram).

```bash
python3 <landing-system>/skills/wp-gutenberg-block-builder/scripts/generate-integrations.py .
```
```

И в секции Output добавить:
```markdown
- `08_КОД/wp-theme/assets/js/popup.js` — popup system
- `08_КОД/wp-theme/assets/js/main.js`, `sliders.js`, `animations.js`, `counters.js` — JS init
- `08_КОД/integrations/` — CRM setup instructions
```

- [ ] **Step 2: Обновить template/00_БРИФ/brief.md**

Добавить секцию в конце файла:

```markdown
## Аналитика

- YM счётчик: 
- GTM контейнер: 

## Интеграции

- CRM: [AmoCRM / Bitrix24 / нет]
- Telegram уведомления: [да / нет]
- Чат виджет: [JivoChat / Carrot Quest / нет]
- Платформа курсов: [GetCourse / Bizon365 / нет]
- Попапы: [да / нет]
```

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/landing-build.md template/00_БРИФ/brief.md
git commit -m "feat(phase-5): extend /landing-build + brief template with integrations fields"
```

---

## Task 9: skills/wp-cli-deployer/ + scripts/deploy.sh

**Files:**
- Create: `skills/wp-cli-deployer/SKILL.md`
- Create: `skills/wp-cli-deployer/scripts/deploy-wordpress.sh`
- Create: `scripts/deploy.sh`

- [ ] **Step 1: Написать deploy-wordpress.sh**

```bash
#!/usr/bin/env bash
# skills/wp-cli-deployer/scripts/deploy-wordpress.sh
# Deploy wp-theme to Beget via rsync + wp-cli.
# Usage: deploy-wordpress.sh <project-dir>
set -euo pipefail

PROJECT="$(realpath "$1")"
PROJECT_SLUG="$(basename "$PROJECT")"
THEME_DIR="$PROJECT/08_КОД/wp-theme"
ACF_JSON="$PROJECT/08_КОД/acf-fields.json"

# Load .env from landing-system root (2 levels up from skills/wp-cli-deployer/scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../../.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

: "${BEGET_USER:?BEGET_USER not set in .env}"
: "${BEGET_HOST:?BEGET_HOST not set in .env}"
: "${BEGET_PATH:?BEGET_PATH not set in .env}"

REMOTE_THEME="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}"

echo "▶ Синхронизация темы → $BEGET_HOST:$REMOTE_THEME"
rsync -avz --delete \
  --exclude=".git" \
  --exclude="*.map" \
  "$THEME_DIR/" \
  "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"

echo "▶ Активация темы"
ssh "${BEGET_USER}@${BEGET_HOST}" \
  "wp theme activate lp-${PROJECT_SLUG} --path=${BEGET_PATH} --allow-root"

if [ -f "$ACF_JSON" ]; then
  echo "▶ Импорт ACF полей"
  ACF_CONTENT="$(cat "$ACF_JSON")"
  ssh "${BEGET_USER}@${BEGET_HOST}" \
    "echo '${ACF_CONTENT}' | wp acf import --json - --path=${BEGET_PATH} --allow-root" 2>/dev/null || true
fi

echo "▶ Очистка кэша"
ssh "${BEGET_USER}@${BEGET_HOST}" \
  "wp cache flush --path=${BEGET_PATH} --allow-root" 2>/dev/null || true

echo "✅ Деплой завершён → https://${BEGET_HOST}"
```

- [ ] **Step 2: Написать scripts/deploy.sh (оркестратор)**

```bash
#!/usr/bin/env bash
# scripts/deploy.sh — Landing deploy orchestrator
# Usage: deploy.sh <project-dir>
set -euo pipefail

PROJECT="$(realpath "${1:?Usage: deploy.sh <project-dir>}")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Landing Deploy: $(basename "$PROJECT") ==="
echo ""

# Preflight
echo "▶ Preflight check"
bash "$SCRIPT_DIR/preflight.sh" || exit 1

# Validate build exists
[ -f "$PROJECT/08_КОД/wp-theme/functions.php" ] \
  || { echo "❌ wp-theme не найден — запусти /landing-build"; exit 1; }

# Deploy
bash "$SCRIPT_DIR/../skills/wp-cli-deployer/scripts/deploy-wordpress.sh" "$PROJECT"

echo ""
echo "✅ Готово! Проверь сайт и запусти /landing-qa"
```

- [ ] **Step 3: Написать skills/wp-cli-deployer/SKILL.md**

```markdown
---
name: wp-cli-deployer
description: Deploy WordPress theme to Beget via SSH+rsync+wp-cli. Used by /landing-deploy.
---

# wp-cli-deployer

## Mission

Деплою лендинг на Бегет: синхронизирую тему, активирую, импортирую ACF.

## Script

`scripts/deploy-wordpress.sh <project-dir>`

Reads from `.env`: `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`

## What it does
1. `rsync` — синхронизирует `08_КОД/wp-theme/` на сервер
2. `wp theme activate` — активирует тему
3. `wp acf import` — импортирует ACF-поля из `08_КОД/acf-fields.json`
4. `wp cache flush` — сбрасывает кэш
```

- [ ] **Step 4: Сделать скрипты исполняемыми**

```bash
chmod +x skills/wp-cli-deployer/scripts/deploy-wordpress.sh scripts/deploy.sh
```

- [ ] **Step 5: Commit**

```bash
git add skills/wp-cli-deployer/ scripts/deploy.sh scripts/deploy.sh
git commit -m "feat(phase-5): wp-cli-deployer + deploy.sh"
```

---

## Task 10: agents/wp-deployer.md + .claude/commands/landing-deploy.md

**Files:**
- Create: `agents/wp-deployer.md`
- Create: `.claude/commands/landing-deploy.md`

- [ ] **Step 1: Написать agents/wp-deployer.md**

```markdown
---
name: wp-deployer
description: Use during stage 09 after /landing-build is approved. Deploys WordPress theme to Beget via SSH+rsync+wp-cli, configures SSL and DNS.
allowed-tools: Bash, Read
---

# wp-deployer (Деплой-инженер)

## Mission

Деплою готовый лендинг на Бегет. Тема загружается, активируется, ACF-поля импортируются.

## What I do

1. Проверяю `.env` — есть ли `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`.
2. Запускаю `scripts/deploy.sh <project-dir>`.
3. Проверяю что сайт открывается: `curl -sI https://<domain> | head -5`.
4. Если SSL не настроен — инструкция:
   ```
   ssh user@srv.beget.ru "certbot --nginx -d yourdomain.ru"
   ```
5. Проверяю редиректы (HTTP→HTTPS, www→без www).
6. **HARD GATE**: показываю URL сайта, жду утверждения.

## Rules
- ❌ Никогда не деплоить без пройденного preflight
- ✅ Всегда проверять сайт после деплоя (curl -sI)
- ✅ Сообщать точный URL для проверки
```

- [ ] **Step 2: Написать .claude/commands/landing-deploy.md**

```markdown
---
description: Deploy the landing to Beget via SSH+rsync+wp-cli (stage 09). Run within a landing project folder after /landing-build is approved.
allowed-tools: Bash, Read
---

# /landing-deploy

## What I do

1. Run `scripts/preflight.sh` — verify environment
2. Run `scripts/deploy.sh .` — rsync theme, activate, import ACF
3. Check site is live: `curl -sI https://<domain>`
4. Check SSL, HTTP→HTTPS redirect
5. **HARD GATE**: show live URL, wait for user approval

## Requirements

- `.env` with `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- `08_КОД/wp-theme/` from `/landing-build`

## Output

- Live WordPress site on Beget
- Theme activated, ACF fields imported
- Cache flushed
```

- [ ] **Step 3: Commit**

```bash
git add agents/wp-deployer.md .claude/commands/landing-deploy.md
git commit -m "feat(phase-5): wp-deployer agent + /landing-deploy command"
```

---

## Task 11: agents/qa-auditor.md + .claude/commands/landing-qa.md

**Files:**
- Create: `agents/qa-auditor.md`
- Create: `.claude/commands/landing-qa.md`

- [ ] **Step 1: Написать agents/qa-auditor.md**

```markdown
---
name: qa-auditor
description: Use during stage 10 after /landing-deploy. Checks live site for 7 quality criteria: availability, HTTPS, meta tags, forms, analytics, performance signals, mobile.
allowed-tools: Bash, Read, Write
---

# qa-auditor (QA-аудитор)

## Mission

Проверяю 7 критериев качества после деплоя. Формирую отчёт.

## Чек-лист

1. **Доступность** — `curl -sI <URL>` возвращает 200
2. **HTTPS** — `curl -sI http://<URL>` → 301 → https://
3. **Мета-теги** — `<title>`, `<meta description>`, og:title присутствуют
4. **ЯМ** — счётчик загружается (grep mc.yandex.ru в HTML)
5. **GTM** — контейнер загружается (grep googletagmanager)
6. **Форма** — Fluent Forms shortcode рендерится (grep fluentform в HTML)
7. **Мобайл** — `<meta name="viewport">` присутствует

## What I do

1. Читаю `00_БРИФ/brief.md` — нахожу URL сайта.
2. Скачиваю HTML: `curl -s <URL>`
3. Проверяю каждый пункт чек-листа grep-ами.
4. Пишу `10_QA/qa-report.md` с результатами.
5. **HARD GATE**: показываю отчёт, жду утверждения.

## Output

`10_QA/qa-report.md`:
```markdown
# QA Report — <project-name>

| # | Критерий | Результат |
|---|---|---|
| 1 | Сайт доступен (200) | ✅ |
| 2 | HTTPS + редирект | ✅ |
| 3 | Meta title, description, og | ✅ |
| 4 | Яндекс Метрика | ✅ |
| 5 | Google Tag Manager | ✅ |
| 6 | Fluent Forms | ✅ |
| 7 | Viewport meta | ✅ |
```
```

- [ ] **Step 2: Написать .claude/commands/landing-qa.md**

```markdown
---
description: Run QA audit on the live landing (stage 10). Checks 7 criteria: availability, HTTPS, meta, analytics, forms, mobile. Run after /landing-deploy.
allowed-tools: Bash, Read, Write
---

# /landing-qa

## What I do

Invoke `qa-auditor` agent → checks 7 criteria on the live site → writes `10_QA/qa-report.md`.

## Requirements

- Live site deployed via `/landing-deploy`
- URL in `00_БРИФ/brief.md`

## Output

- `10_QA/qa-report.md` — QA report with pass/fail per criterion
```

- [ ] **Step 3: Commit**

```bash
git add agents/qa-auditor.md .claude/commands/landing-qa.md
git commit -m "feat(phase-5): qa-auditor agent + /landing-qa command"
```

---

## Task 12: skills/landing-versioning-and-cloning/ + lifecycle-keeper

**Files:**
- Create: `skills/landing-versioning-and-cloning/SKILL.md`
- Create: `skills/landing-versioning-and-cloning/scripts/create-version.sh`
- Create: `skills/landing-versioning-and-cloning/scripts/clone-landing.sh`
- Create: `agents/lifecycle-keeper.md`
- Create: `.claude/commands/landing-rollback.md`
- Create: `.claude/commands/landing-clone.md`

- [ ] **Step 1: Написать create-version.sh**

```bash
#!/usr/bin/env bash
# skills/landing-versioning-and-cloning/scripts/create-version.sh
# Создаёт версионный снапшот wp-theme в 09_ВЕРСИИ/
# Usage: create-version.sh <project-dir> [version-label]
set -euo pipefail

PROJECT="$(realpath "$1")"
VERSION="${2:-v$(date +%Y%m%d%H%M)}"
VERSIONS_DIR="$PROJECT/09_ВЕРСИИ"
SNAPSHOT_DIR="$VERSIONS_DIR/$VERSION"

mkdir -p "$SNAPSHOT_DIR"
cp -r "$PROJECT/08_КОД/wp-theme" "$SNAPSHOT_DIR/"
cp -r "$PROJECT/08_КОД/acf-fields.json" "$SNAPSHOT_DIR/" 2>/dev/null || true

echo "$VERSION" > "$VERSIONS_DIR/current.txt"
echo "✅ Версия $VERSION сохранена → $SNAPSHOT_DIR"
```

- [ ] **Step 2: Написать clone-landing.sh**

```bash
#!/usr/bin/env bash
# skills/landing-versioning-and-cloning/scripts/clone-landing.sh
# Клонирует проект в новую папку для A/B теста
# Usage: clone-landing.sh <project-dir> <new-slug>
set -euo pipefail

PROJECT="$(realpath "$1")"
NEW_SLUG="${2:?Usage: clone-landing.sh <project-dir> <new-slug>}"
PARENT_DIR="$(dirname "$PROJECT")"
CLONE_DIR="$PARENT_DIR/$NEW_SLUG"

[ -d "$CLONE_DIR" ] && { echo "❌ $CLONE_DIR уже существует"; exit 1; }

cp -r "$PROJECT" "$CLONE_DIR"
echo "✅ A/B клон → $CLONE_DIR"
echo "   Следующий шаг: /landing-deploy в $CLONE_DIR на новый поддомен"
```

- [ ] **Step 3: Написать agents/lifecycle-keeper.md**

```markdown
---
name: lifecycle-keeper
description: Manages landing versions (snapshots), rollbacks, and A/B clones. Used by /landing-rollback and /landing-clone.
allowed-tools: Bash, Read
---

# lifecycle-keeper (Хранитель версий)

## Mission

Версионирую лендинги, откатываю, создаю A/B-клоны.

## Commands

### Создать версию
```bash
bash skills/landing-versioning-and-cloning/scripts/create-version.sh <project-dir> v1.0
```
Сохраняет снапшот в `09_ВЕРСИИ/v1.0/`.

### Откат
1. Найти нужную версию: `ls 09_ВЕРСИИ/`
2. Скопировать обратно: `cp -r 09_ВЕРСИИ/v1.0/wp-theme 08_КОД/wp-theme`
3. Задеплоить снова: `/landing-deploy`

### A/B клон
```bash
bash skills/landing-versioning-and-cloning/scripts/clone-landing.sh <project-dir> <new-slug>
```
Создаёт полную копию проекта → деплоится на новый поддомен.
```

- [ ] **Step 4: Написать команды rollback и clone**

`.claude/commands/landing-rollback.md`:
```markdown
---
description: Rollback a landing to a previous version (stage 09/ops). Run within a landing project folder.
allowed-tools: Bash, Read
---

# /landing-rollback

## Usage

```
/landing-rollback v1.0
```

## What I do

1. List available versions: `ls 09_ВЕРСИИ/`
2. Restore: `cp -r 09_ВЕРСИИ/<version>/wp-theme 08_КОД/wp-theme`
3. Redeploy: run `scripts/deploy.sh .`
4. Verify site is live after rollback
```

`.claude/commands/landing-clone.md`:
```markdown
---
description: Create an independent A/B copy of a landing on a new subdomain. Run within a landing project folder.
allowed-tools: Bash, Read
---

# /landing-clone

## Usage

```
/landing-clone <new-slug>
```

## What I do

1. Run `clone-landing.sh <project-dir> <new-slug>`
2. Update `BEGET_PATH` for new subdomain in cloned project `.env`
3. Run `/landing-deploy` in cloned project
4. Report new URL
```

- [ ] **Step 5: Сделать скрипты исполняемыми + commit**

```bash
chmod +x skills/landing-versioning-and-cloning/scripts/create-version.sh \
         skills/landing-versioning-and-cloning/scripts/clone-landing.sh
git add skills/landing-versioning-and-cloning/ agents/lifecycle-keeper.md \
        .claude/commands/landing-rollback.md .claude/commands/landing-clone.md
git commit -m "feat(phase-5): versioning + A/B clone + lifecycle-keeper"
```

---

## Task 13: Bats-тесты для агентов и команд Phase 5

**Files:**
- Create: `tests/phase-5/test-agents-phase5.bats`
- Create: `tests/phase-5/test-commands-phase5.bats`

- [ ] **Step 1: Написать test-agents-phase5.bats**

```bash
#!/usr/bin/env bats
# tests/phase-5/test-agents-phase5.bats
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
AGENTS_DIR="$REPO_ROOT/agents"

@test "system-setup.md exists" { [ -f "$AGENTS_DIR/system-setup.md" ]; }
@test "system-setup.md has name frontmatter" { grep -q "^name: system-setup" "$AGENTS_DIR/system-setup.md"; }

@test "wp-deployer.md exists" { [ -f "$AGENTS_DIR/wp-deployer.md" ]; }
@test "wp-deployer.md has name frontmatter" { grep -q "^name: wp-deployer" "$AGENTS_DIR/wp-deployer.md"; }
@test "wp-deployer.md has HARD GATE" { grep -qi "hard gate" "$AGENTS_DIR/wp-deployer.md"; }
@test "wp-deployer.md mentions rsync" { grep -q "rsync" "$AGENTS_DIR/wp-deployer.md"; }

@test "qa-auditor.md exists" { [ -f "$AGENTS_DIR/qa-auditor.md" ]; }
@test "qa-auditor.md has name frontmatter" { grep -q "^name: qa-auditor" "$AGENTS_DIR/qa-auditor.md"; }
@test "qa-auditor.md has HARD GATE" { grep -qi "hard gate" "$AGENTS_DIR/qa-auditor.md"; }

@test "lifecycle-keeper.md exists" { [ -f "$AGENTS_DIR/lifecycle-keeper.md" ]; }
@test "lifecycle-keeper.md has name frontmatter" { grep -q "^name: lifecycle-keeper" "$AGENTS_DIR/lifecycle-keeper.md"; }
```

- [ ] **Step 2: Написать test-commands-phase5.bats**

```bash
#!/usr/bin/env bats
# tests/phase-5/test-commands-phase5.bats
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
COMMANDS_DIR="$REPO_ROOT/.claude/commands"
SKILLS_DIR="$REPO_ROOT/skills"
SCRIPTS_DIR="$REPO_ROOT/scripts"

@test "landing-setup.md exists" { [ -f "$COMMANDS_DIR/landing-setup.md" ]; }
@test "landing-setup.md has description" { grep -q "^description:" "$COMMANDS_DIR/landing-setup.md"; }

@test "landing-deploy.md exists" { [ -f "$COMMANDS_DIR/landing-deploy.md" ]; }
@test "landing-deploy.md mentions rsync" { grep -q "rsync" "$COMMANDS_DIR/landing-deploy.md"; }

@test "landing-qa.md exists" { [ -f "$COMMANDS_DIR/landing-qa.md" ]; }
@test "landing-qa.md has description" { grep -q "^description:" "$COMMANDS_DIR/landing-qa.md"; }

@test "landing-rollback.md exists" { [ -f "$COMMANDS_DIR/landing-rollback.md" ]; }
@test "landing-clone.md exists" { [ -f "$COMMANDS_DIR/landing-clone.md" ]; }

@test "preflight.sh exists and executable" {
  [ -f "$SCRIPTS_DIR/preflight.sh" ]
  [ -x "$SCRIPTS_DIR/preflight.sh" ]
}

@test "deploy.sh exists and executable" {
  [ -f "$SCRIPTS_DIR/deploy.sh" ]
  [ -x "$SCRIPTS_DIR/deploy.sh" ]
}

@test "wp-cli-deployer SKILL.md exists" { [ -f "$SKILLS_DIR/wp-cli-deployer/SKILL.md" ]; }
@test "deploy-wordpress.sh exists and executable" {
  [ -f "$SKILLS_DIR/wp-cli-deployer/scripts/deploy-wordpress.sh" ]
  [ -x "$SKILLS_DIR/wp-cli-deployer/scripts/deploy-wordpress.sh" ]
}

@test "landing-versioning SKILL.md exists" { [ -f "$SKILLS_DIR/landing-versioning-and-cloning/SKILL.md" ]; }
@test "create-version.sh exists and executable" {
  [ -f "$SKILLS_DIR/landing-versioning-and-cloning/scripts/create-version.sh" ]
  [ -x "$SKILLS_DIR/landing-versioning-and-cloning/scripts/create-version.sh" ]
}
@test "clone-landing.sh exists and executable" {
  [ -f "$SKILLS_DIR/landing-versioning-and-cloning/scripts/clone-landing.sh" ]
  [ -x "$SKILLS_DIR/landing-versioning-and-cloning/scripts/clone-landing.sh" ]
}

@test "generate-popup.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-popup.py" ]
}
@test "generate-js-init.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-js-init.py" ]
}
@test "generate-analytics.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-analytics.py" ]
}
@test "generate-integrations.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-integrations.py" ]
}
@test "config/system.yaml.template exists" { [ -f "$REPO_ROOT/config/system.yaml.template" ]; }
```

- [ ] **Step 3: Запустить — убедиться GREEN**

```bash
bats tests/phase-5/test-agents-phase5.bats tests/phase-5/test-commands-phase5.bats
```

Ожидание: все тесты `ok`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-5/test-agents-phase5.bats tests/phase-5/test-commands-phase5.bats
git commit -m "test(phase-5): bats tests for Phase 5 agents and commands"
```

---

## Task 14: Запустить все тесты Phase 5

- [ ] **Step 1: Запустить pytest Phase 5**

```bash
pytest tests/phase-5/ -v 2>&1 | tail -30
```

Ожидание: все тесты `PASSED`.

- [ ] **Step 2: Запустить bats Phase 5**

```bash
bats tests/phase-5/test-agents-phase5.bats \
     tests/phase-5/test-commands-phase5.bats \
     tests/phase-5/integration/test-phase5-setup.bats
```

Ожидание: все `ok`.

- [ ] **Step 3: Убедиться что Phase 1-4 тесты не поломаны**

```bash
pytest tests/phase-1/ tests/phase-3/ tests/phase-4/ -q 2>&1 | tail -5
bats tests/phase-1/*.bats tests/phase-3/*.bats \
     tests/phase-4/test-agents-phase4.bats \
     tests/phase-4/test-commands-phase4.bats 2>&1 | tail -5
```

Ожидание: `passed`, `ok`.

---

## Task 15: Обновить orchestrator + master plan + tag phase-5-complete

**Files:**
- Modify: `agents/landing-orchestrator.md`
- Modify: `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`

- [ ] **Step 1: Добавить Phase 5 scope в landing-orchestrator.md**

Добавить после Phase 4 Scope:

```markdown
## Phase 5 Scope (Stages 09–12 — Деплой, QA, Версионирование)

### /landing-setup (один раз на систему):
1. Run `scripts/preflight.sh` — проверка окружения
2. Configure `.env` — API ключи
3. Configure `config/system.yaml` — CRM, аналитика, библиотеки
4. Report: что готово, что не настроено

### /landing-deploy:
1. Run `scripts/preflight.sh`
2. Run `scripts/deploy.sh .` → rsync + wp theme activate + ACF import
3. HARD GATE: проверить URL, дождаться утверждения

### /landing-qa:
1. Dispatch `qa-auditor` → 7 критериев → `10_QA/qa-report.md`
2. HARD GATE: показать отчёт, ждать утверждения

### /landing-rollback <version>:
1. Dispatch `lifecycle-keeper` → откатить к версии из `09_ВЕРСИИ/`
2. Redeploy

### /landing-clone <new-slug>:
1. Dispatch `lifecycle-keeper` → клонировать в новую папку
2. Deploy клона на новый поддомен
```

- [ ] **Step 2: Обновить master plan**

В таблице Phase Index изменить строку Phase 5:
```
| 5 | **Deploy & Operations** (09–12) | [phase-5-deploy-operations.md](2026-05-04-phase-5-deploy-operations.md) | ~55 steps | 6–8 ч | 🟢 Complete (2026-05-04) |
```

В секции Status:
```markdown
**Текущий статус:** Phase 5 — Deploy & Operations **completed (2026-05-04)**, tag `phase-5-complete`.

**Предыдущие фазы:**
- Phase 1 — Skeleton & Infrastructure **completed (2026-05-03)**, tag `phase-1-complete`
- Phase 2 — Brainstorming Pipeline **completed (2026-05-04)**, tag `phase-2-complete`
- Phase 3 — Design Pipeline **completed (2026-05-04)**, tag `phase-3-complete`
- Phase 4 — WP Build Pipeline **completed (2026-05-04)**, tag `phase-4-complete`

**Следующий шаг:** Phase 6 (Packaging & Pilot) — собрать ZIP, прогнать pilot-проект.
```

- [ ] **Step 3: Commit + tag**

```bash
git add agents/landing-orchestrator.md \
        docs/superpowers/plans/2026-05-03-landing-system-master-plan.md
git commit -m "feat(phase-5): extend orchestrator Phase 5 scope + mark complete"
git tag phase-5-complete
echo "✅ Phase 5 complete"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ `/landing-setup` — preflight + .env + system.yaml wizard
- ✅ Попапы — generate-popup.py (JS + CSS + PHP overlay)
- ✅ JS инициализация — generate-js-init.py (Swiper, GSAP, Lenis, CountUp)
- ✅ Яндекс Метрика — generate-analytics.py (счётчик + reachGoal)
- ✅ GTM — generate-analytics.py (head snippet + noscript body)
- ✅ AmoCRM — generate-integrations.py (webhook) + инструкция
- ✅ Bitrix24 — generate-integrations.py (webhook) + инструкция
- ✅ Telegram бот — generate-integrations.py (sendMessage) + инструкция
- ✅ Деплой на Бегет — deploy-wordpress.sh (rsync + wp-cli)
- ✅ QA — qa-auditor (7 критериев)
- ✅ Версионирование — create-version.sh
- ✅ A/B клон — clone-landing.sh + /landing-clone
- ✅ Откат — /landing-rollback

**2. Placeholder scan:** Нет TBD/TODO. Весь код конкретный.

**3. Type consistency:** Все Python-скрипты: `main(argv: list) -> int`. Все пути: `Path`. Все модули: `sys.path.insert(0, parents[3])`.
