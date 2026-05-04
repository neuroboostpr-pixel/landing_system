# Stage Gates, Onboarding & MCP — Design Spec

**Дата:** 2026-05-04
**Автор:** brainstorming-сессия
**Связанные документы:**
- [Базовый дизайн системы](2026-05-03-landing-system-design.md)
- [Master plan](../plans/2026-05-03-landing-system-master-plan.md)

## 1. Задача

Превратить landing-system из «набора агентов с декларативными HARD GATE» в **систему с принудительным workflow**: на каждом этапе автоматически и через диалог проверяется готовность; без зелёной проверки переход к следующему этапу запрещён. Дополнительно — закрыть дыры в функционале (GTM, sitemap, кеш, безопасность, бэкапы, 152-ФЗ, cookie-баннер, мультиланг, staging, DNS-MCP, WP-CLI MCP) и добавить интерактивный onboarding для первого запуска на новой машине.

### Зачем

- Сейчас HARD GATE существует только в инструкциях агентов — пользователь может попросить «пропусти этап» и агент пропустит.
- При первом клонировании репозитория с GitHub новичок не понимает, какие API нужны и где их брать. `preflight.sh` проверяет один `FIRECRAWL_API_KEY`, остальное — на усмотрение.
- Половина ключей из spec-документа отсутствует в `.env.example` (Pexels, HuggingFace, WhatTheFont, Wordstat, Beget API, Cloudflare и др.).
- В системе нет: GTM-агента, sitemap, 152-ФЗ блока, cookie-баннера, автоустановки плагинов, бэкапа до деплоя, staging-окружения, мультиланга, MCP для DNS и WP-CLI.

### Цели

1. На любой машине, клонирующей репо, `/landing-onboarding` за один проход настраивает всё необходимое и валидирует.
2. Запуск любой `/landing-*` команды без пройденного onboarding'а или без gate-check'а — невозможен (`exit 1`).
3. На каждом этапе проекта `.landing-state.yaml` фиксирует статус, и перепрыгивать запрещено механически.
4. Все недостающие функциональные блоки добавлены и интегрированы в существующих агентов.

### Не входит

- Реальная генерация изображений через HuggingFace Inference API. Реализуется только fallback-режим: photo-stylist выдаёт текстовые промпты для ручной обработки в ChatGPT/Шедеврум. Подключение HF — следующий проект.
- Полноценная CI/CD-инфраструктура (GitHub Actions для тестов). Останется ручной коммит/пуш, как сейчас.
- Backup и восстановление **сайтов клиента** (через `wp db export` бэкап делаем — но восстановление вручную).

## 2. Архитектура

### 2.1 Три новые подсистемы

```
┌──────────────────────────────────────────────────────────────┐
│  ONBOARDING (один раз на машину)                             │
│  /landing-onboarding → docs/SETUP.md → ~/.landing-system/    │
│                                        setup_complete        │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  STAGE GATES (на каждом этапе каждого проекта)               │
│  /landing-* → gate-check.sh --stage N → .landing-state.yaml  │
│                  ↓                                            │
│   ┌──────────┐  ┌──────────┐                                  │
│   │ HARD     │  │ SOFT     │                                  │
│   │ checks   │  │ checks   │                                  │
│   │ (auto)   │  │ (agent)  │                                  │
│   └──────────┘  └──────────┘                                  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  WORKFLOW LOCK (.landing-state.yaml)                         │
│  Этапы: locked → in_progress → approved                      │
│  /landing-build блокируется если 02–07 не approved           │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Декларативный YAML — `config/stage-gates.yaml`

```yaml
# Описывает все проверки для каждого этапа.
# Источник истины — gate-check.sh читает этот файл.

stages:
  "02_assets":
    name: "Сбор материалов клиента"
    hard_checks:
      - id: pexels_api
        type: api_validator
        validator: tools/api_validators/pexels.py
        required: true
        fix_hint: "Зарегистрируйся на pexels.com/api и добавь PEXELS_API_KEY в .env"
      - id: huggingface_api
        type: api_validator
        validator: tools/api_validators/huggingface.py
        required: false
        fix_hint: "Опционально для генерации картинок. Без ключа — fallback с промптами."
      - id: client_assets_folder
        type: file_exists
        path: "{project}/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/"
        required: true
    soft_checks:
      - id: photo_style_consistency
        agent: client-assets-collector
        question: "Фото клиента в одном стиле? Если нет — перечислить, какие нужно перерисовать или сгенерировать."
      - id: missing_photos
        agent: client-assets-collector
        question: "Каких фото не хватает для лендинга?"

  "06_stack":
    name: "Подбор стека"
    hard_checks:
      - id: cdn_iconify
        type: http_ping
        url: "https://api.iconify.design/lucide/check.svg"
      - id: cdn_bunny_fonts
        type: http_ping
        url: "https://fonts.bunny.net"
      - id: cdn_gsap
        type: http_ping
        url: "https://cdn.jsdelivr.net/npm/gsap@3"
    soft_checks:
      - id: free_libraries_only
        agent: stack-planner
        question: "Все библиотеки в design-stack.yaml — бесплатные (free tier хватает)?"

  "08_build":
    name: "Сборка WordPress"
    require_approved:
      - "02_assets"
      - "03_references"
      - "04_brand"
      - "05_design"
      - "06_stack"
      - "07_content"
    hard_checks:
      - id: design_md_exists
        type: file_exists
        path: "{project}/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
      - id: final_copy_exists
        type: file_exists
        path: "{project}/07_КОНТЕНТ/final-copy.md"
    soft_checks:
      - id: legal_blocks_present
        agent: wp-builder
        question: "152-ФЗ блок согласия и cookie-баннер присутствуют в HTML?"

  "09_deploy":
    name: "Деплой на Бегет"
    require_approved:
      - "08_build"
    hard_checks:
      - id: ssh_to_beget
        type: ssh_check
        target: "${BEGET_USER}@${BEGET_HOST}"
      - id: wp_cli_remote
        type: remote_command
        command: "wp --version"
      - id: ym_counter
        type: api_validator
        validator: tools/api_validators/yandex_metrika.py
      - id: telegram_bot
        type: api_validator
        validator: tools/api_validators/telegram.py
      - id: crm_webhook
        type: api_validator_any_of
        validators:
          - tools/api_validators/amocrm.py
          - tools/api_validators/bitrix24.py
      - id: db_backup
        type: command
        command: "ssh ${BEGET_USER}@${BEGET_HOST} 'wp db export /tmp/backup-$(date +%s).sql --path=${BEGET_PATH}'"
      - id: required_plugins_installed
        type: wp_plugin_check
        plugins_from: "{project}/06_СТЕК/design-stack.yaml"
```

### 2.3 Workflow lock — `.landing-state.yaml`

```yaml
# Создаётся при /landing-new в корне проекта
# Обновляется gate-check.sh после approve каждого этапа

project: my-landing
created: 2026-05-04
stages:
  "00_brief":
    status: approved        # locked | in_progress | approved | failed
    timestamp: 2026-05-04T10:00:00
    approved_by: user
    gate_log: ".landing-state-log/00_brief.log"
  "01_context":
    status: approved
    timestamp: 2026-05-04T10:30:00
  "02_assets":
    status: in_progress
  "03_references":
    status: locked
  "04_brand":
    status: locked
  "05_design":
    status: locked
  "06_stack":
    status: locked
  "07_content":
    status: locked
  "08_build":
    status: locked
  "09_deploy":
    status: locked
  "10_qa":
    status: locked
  "11_analytics":
    status: locked
  "12_seo":
    status: locked
```

### 2.4 Поток выполнения команды (пример `/landing-build`)

```
/landing-build
  ↓
1. Проверка ~/.landing-system/setup_complete существует? Нет → отправить на /landing-onboarding
  ↓
2. bash gate-check.sh --stage 08_build --project <slug>
   ↓
   2a. Читает config/stage-gates.yaml → секция 08_build
   2b. Проверяет require_approved: 02–07 в .landing-state.yaml = approved? Иначе exit 1
   2c. Запускает все hard_checks параллельно через api_validators/
   2d. Если хоть один failed → exit 1, выводит fix_hint
  ↓
3. Передача управления landing-orchestrator → wp-builder
  ↓
4. После завершения wp-builder → soft_checks (агент задаёт вопросы пользователю)
  ↓
5. После approve пользователя → gate-check.sh --approve 08_build → пишет status: approved
```

## 3. Onboarding-система

### 3.1 Команда `/landing-onboarding`

Запускается:
- Автоматически при первом запуске любой `/landing-*` команды, если нет `~/.landing-system/setup_complete`
- Вручную в любое время для повторной проверки

### 3.2 Структура мастера

**Секция A — Туториал (5 минут чтения)**
1. «Что такое landing-system» — пайплайн 12 этапов
2. «Как устроены агенты» — что такое orchestrator, специализированные агенты, HARD GATE
3. «Как работает workflow» — `.landing-state.yaml`, нельзя перепрыгивать этапы
4. «Что такое onboarding и зачем» — почему все ключи нужны до старта проекта
5. Краткое описание каждой команды

**Секция B — Setup wizard**

По блокам, на каждом — пояснение «зачем это», прямая ссылка на регистрацию, поле ввода ключа, тестовый запрос для валидации:

1. **Локальные зависимости** (`brew install bats-core wp-cli rsync python@3.11 jq`, `pip install pyyaml jinja2 pillow requests`)
2. **Стоковые фото и иконки**
   - Pexels API (обязательно): https://www.pexels.com/api/
   - Unsplash API (alt): https://unsplash.com/developers
   - Pixabay API (alt): https://pixabay.com/api/docs/
   - Iconify (без ключа, проверка ping)
3. **Шрифты**
   - Bunny Fonts CDN (без ключа, ping)
   - WhatTheFont API (опционально): https://www.myfonts.com/pages/whatthefont-api
4. **Парсинг**
   - Firecrawl (обязательно): https://firecrawl.dev (free 500/мес)
5. **SEO**
   - Yandex Wordstat OAuth: https://oauth.yandex.ru
6. **Аналитика**
   - Yandex Metrika ID: https://metrika.yandex.ru (создать счётчик)
   - Yandex Metrika OAuth для API: https://oauth.yandex.ru
   - GTM Container: https://tagmanager.google.com (опционально)
7. **Уведомления**
   - Telegram Bot через @BotFather + chat_id
8. **CRM** (хотя бы одно)
   - amoCRM API
   - Bitrix24 webhook
9. **Деплой**
   - Beget SSH (логин, хост, путь, SSH-ключ)
   - Beget API (для DNS): https://beget.com/ru/kb/api
   - Cloudflare API (alt DNS, опционально)
   - Reg.ru API (alt DNS, опционально)
10. **Генерация картинок (опционально)**
    - HuggingFace token: https://huggingface.co/settings/tokens
    - Если пропустить — система перейдёт в fallback-режим (промпты для ChatGPT)

**Секция C — Финал**
- Все ключи валидированы — создаётся `~/.landing-system/setup_complete`
- Выводится сводка: что подключено, что в fallback, что пропущено
- Предложение `/landing-new my-first-landing`

### 3.3 Файлы

- `commands/landing-onboarding.md` — команда
- `agents/onboarding-guide.md` — агент-проводник через wizard
- `skills/landing-onboarding/SKILL.md` + `scripts/wizard.sh` + `scripts/validate-all.sh`
- `tools/api_validators/*.py` — по одному файлу на каждый сервис
- `docs/SETUP.md` — текстовая версия туториала

## 4. Расширение существующих агентов

| Агент | Что добавить |
|---|---|
| `analytics-engineer` | GTM-вставка в `functions.php` рядом с Метрикой; чтение `GTM_CONTAINER_ID` из `.env` |
| `seo-optimizer` | Генерация `sitemap.xml` (статичная, перечисляет URL лендинга и legal-страницы) |
| `wp-deployer` | Запуск `wp db export` бэкап до rsync; чтение списка плагинов из `design-stack.yaml` и `wp plugin install --activate` |
| `photo-stylist` | Если нет `HUGGINGFACE_TOKEN` → fallback: на каждое нужное изображение генерируется текстовый промпт с brand-style референсами для ручной обработки в ChatGPT/Шедеврум, выгружается в `02_МАТЕРИАЛЫ_КЛИЕНТА/photo-prompts.md` |
| `client-assets-collector` | Soft-check: оценка единства стиля фото, список того, что нужно догенерировать |
| `stack-planner` | Расширить дефолтный список плагинов: WP Rocket / LiteSpeed Cache, ShortPixel, Wordfence, UpdraftPlus, Limit Login Attempts, Redirection, Really Simple SSL, Cookie Notice, Polylang |
| `wp-builder` | Шаблон `template-parts/legal-block.php` (152-ФЗ согласие на обработку ПД), шаблон `cookie-banner.php` |

## 5. Новые агенты

### 5.1 `agents/migration-engineer.md`
Используется в этапе 09 при переносе с существующего сайта. Задачи:
- Сбор списка старых URL у клиента
- Генерация `redirects.csv` для импорта в плагин Redirection
- Активация плагина Redirection при деплое
- Импорт CSV через wp-cli

### 5.2 `agents/i18n-engineer.md`
Опциональный агент, активируется флагом `multilang: true` в `00_БРИФ/brief.md`. Задачи:
- Установка Polylang (free) при деплое
- Создание языковых версий каждого блока в `07_КОНТЕНТ/`
- Копия `template-parts/*.php` для каждого языка
- Настройка переключателя языка в шапке

### 5.3 `agents/onboarding-guide.md`
Проводит пользователя через `/landing-onboarding`. Задачи описаны в разделе 3.

## 6. MCP-серверы

### 6.1 `mcp/wp-cli-mcp/`
**Зачем:** удалённое управление WordPress через MCP без ручного `ssh+wp` в каждой команде.
**Инструменты:**
- `wp_plugin_install(plugins, activate)`
- `wp_plugin_list()`
- `wp_theme_activate(slug)`
- `wp_acf_import(json)`
- `wp_db_export(path)`
- `wp_cache_flush()`

**Авторизация:** SSH-ключ из `.env`. Сервер на Node.js, оборачивает SSH+wp-cli.

### 6.2 `mcp/beget-dns-mcp/`
**Зачем:** автоматическое создание A-записи и привязка домена при деплое.
**Инструменты:**
- `dns_list_records(domain)`
- `dns_create_a_record(domain, ip)`
- `dns_create_cname(domain, target)`
- `dns_delete_record(record_id)`

**Авторизация:** `BEGET_API_LOGIN/PASSWORD` из `.env`.

### 6.3 `mcp/cloudflare-dns-mcp/` и `mcp/regru-dns-mcp/`
Аналогичный набор инструментов как у Beget DNS MCP, но для Cloudflare и Reg.ru.

### 6.4 Регистрация MCP в системе
- Каждый MCP имеет свой `package.json` и `index.js`
- В `.claude/settings.json` добавить блок `"mcpServers": { ... }`
- В onboarding-wizard — пункт «Установить локальные MCP» (`npm install` в каждой папке)

## 7. Staging-окружение

### 7.1 Изменения в `scripts/deploy.sh`
```bash
deploy.sh <project-dir> [--env staging|prod]
```
- По умолчанию `staging`
- Для `prod` требуется `--env prod` явно + `--confirm`
- staging использует поддомен `staging.<domain>` или отдельный путь на Бегете

### 7.2 Конфиг `template/09_ДЕПЛОЙ/deploy-targets.yaml`
```yaml
staging:
  domain: staging.example.com
  path: /home/user/staging.example.com/public_html
prod:
  domain: example.com
  path: /home/user/example.com/public_html
```

### 7.3 Бэкап до prod-деплоя
- `wp db export` обязательно перед `rsync` в prod
- Бэкап сохраняется в `09_ДЕПЛОЙ/backups/` локально и `/tmp/backup-<ts>.sql` на сервере

## 8. 152-ФЗ + cookie-баннер

### 8.1 Блок 152-ФЗ
Шаблон `template/08_КОД/legal-block.php` — компонент «Согласен с обработкой персональных данных» под формой:
- Чекбокс (по умолчанию выключен, обязательный)
- Ссылка на «Политику конфиденциальности» (`/policy/`)
- Ссылка на «Согласие на обработку ПД» (`/consent/`)

### 8.2 Cookie-баннер
Шаблон `template/08_КОД/cookie-banner.php` + JS — нативный, без плагина:
- Появляется при первом визите
- Кнопки «Принять» / «Только обязательные» / «Подробнее»
- Запись в localStorage
- Блокирует загрузку Метрики/GTM до согласия (если выбран строгий режим)

### 8.3 Страницы Policy + Consent
Авто-создание `template/08_КОД/legal-pages/`:
- `policy.html` — шаблон политики конфиденциальности
- `consent.html` — шаблон согласия на обработку ПД
- `wp-deployer` импортирует как страницы WP

## 9. Полный `.env.example`

```env
# ────────────────────────────────────────
# ПАРСИНГ И РЕСЁРЧ
# ────────────────────────────────────────
FIRECRAWL_API_KEY=

# ────────────────────────────────────────
# СТОКОВЫЕ ФОТО (хотя бы один)
# ────────────────────────────────────────
PEXELS_API_KEY=
UNSPLASH_ACCESS_KEY=
PIXABAY_API_KEY=

# ────────────────────────────────────────
# ШРИФТЫ (опционально)
# ────────────────────────────────────────
WHATTHEFONT_API_KEY=

# ────────────────────────────────────────
# ГЕНЕРАЦИЯ КАРТИНОК (опционально, иначе fallback)
# ────────────────────────────────────────
HUGGINGFACE_TOKEN=

# ────────────────────────────────────────
# SEO
# ────────────────────────────────────────
YANDEX_OAUTH_TOKEN=

# ────────────────────────────────────────
# АНАЛИТИКА
# ────────────────────────────────────────
YM_COUNTER_ID=
YANDEX_METRIKA_OAUTH=
GTM_CONTAINER_ID=

# ────────────────────────────────────────
# CRM (хотя бы один)
# ────────────────────────────────────────
AMOCRM_API_KEY=
AMOCRM_SUBDOMAIN=
BITRIX24_WEBHOOK_URL=

# ────────────────────────────────────────
# УВЕДОМЛЕНИЯ
# ────────────────────────────────────────
TG_BOT_TOKEN=
TG_CHAT_ID=

# ────────────────────────────────────────
# ДЕПЛОЙ — Бегет
# ────────────────────────────────────────
BEGET_USER=
BEGET_HOST=srv123456.beget.ru
BEGET_PATH=/home/username/public_html
BEGET_API_LOGIN=
BEGET_API_PASSWORD=

# ────────────────────────────────────────
# DNS-альтернативы (опционально)
# ────────────────────────────────────────
CLOUDFLARE_API_TOKEN=
REGRU_API_USERNAME=
REGRU_API_PASSWORD=
```

## 10. Реализация по фазам

### Phase 1 — `.env.example` + API-валидаторы + onboarding wizard (skeleton)
- Полный `.env.example`
- `tools/api_validators/*.py` для всех сервисов
- `commands/landing-onboarding.md` + `agents/onboarding-guide.md`
- `docs/SETUP.md`
- `~/.landing-system/setup_complete` flag-механизм

### Phase 2 — Stage-gates runner + workflow lock
- `config/stage-gates.yaml`
- `scripts/gate-check.sh`
- `template/.landing-state.yaml`
- Интеграция вызова `gate-check.sh` в каждую slash-команду
- `landing-orchestrator.md` enforce состояний

### Phase 3 — Расширение существующих агентов
- `analytics-engineer` (GTM), `seo-optimizer` (sitemap), `wp-deployer` (бэкап + плагины), `photo-stylist` (fallback), `client-assets-collector` (soft-check), `stack-planner` (расширенный список плагинов), `wp-builder` (legal-блоки)

### Phase 4 — WP-CLI MCP
- `mcp/wp-cli-mcp/` (Node.js)
- Регистрация в `.claude/settings.json`
- Замена ручных `ssh+wp` вызовов на MCP-инструменты в `wp-cli-deployer`

### Phase 5 — DNS MCP
- `mcp/beget-dns-mcp/`, `mcp/cloudflare-dns-mcp/`, `mcp/regru-dns-mcp/`
- Интеграция в `wp-deployer`

### Phase 6 — 152-ФЗ + cookie + автоустановка плагинов
- `template/08_КОД/legal-block.php`, `cookie-banner.php`, `legal-pages/`
- Soft-check `legal_blocks_present` в gate
- Автоустановка плагинов через WP-CLI MCP

### Phase 7 — Multilang + staging
- `agents/i18n-engineer.md`
- Polylang интеграция
- `scripts/deploy.sh` с флагом `--env`
- `template/09_ДЕПЛОЙ/deploy-targets.yaml`

### Phase 8 — Migration-engineer
- `agents/migration-engineer.md`
- `redirects.csv` шаблон
- Интеграция плагина Redirection

### Phase 9 — Документация + git push
- Обновление `README.md`, `CLAUDE.md`
- Финальная проверка `bash scripts/preflight.sh` (вызывает теперь `gate-check.sh`)
- Коммит всех изменений
- `git push origin main` в репо `neuroboostpr-pixel/landing_system`

## 11. Тестирование

### Уровни тестов

- **`tests/api_validators/`** — Python unit-тесты для каждого валидатора (mock HTTP)
- **`tests/gate-check.bats`** — bats-тесты для gate-check.sh с фикстурами `.landing-state.yaml`
- **`tests/onboarding.bats`** — тесты wizard-flow
- **`tests/mcp/`** — интеграционные тесты MCP-серверов (mock SSH/WP-CLI)
- **`tests/e2e/`** — один сквозной тест: `/landing-new` → попытка `/landing-build` без 02–07 → должен падать

### TDD-протокол

Каждая фаза начинается с failing-теста, реализация — после.

## 12. Риски и решения

| Риск | Решение |
|---|---|
| Onboarding слишком длинный, новичок бросает на середине | Туториал отделён от wizard; wizard поддерживает `--resume` (продолжить с места остановки) |
| API-валидатор делает реальный платный запрос | Все валидаторы используют только free tier endpoints (например, Firecrawl /credits, не /scrape) |
| Soft-check агента субъективен | Агент задаёт конкретный вопрос с вариантами; пользователь явно отвечает yes/no/partial |
| `.landing-state.yaml` повреждён вручную | gate-check.sh валидирует структуру и предлагает `--reset-state` |
| MCP-сервер падает | Fallback на ручные `ssh+wp` команды (старый путь сохраняется) |
| Реализация всех 9 фаз — большой объём | Каждая фаза — отдельный коммит; можно мерджить инкрементально |

## 13. Acceptance criteria

1. Свежий клон репо → `/landing-new test` → отказ с предложением `/landing-onboarding`
2. После прохождения onboarding → `~/.landing-system/setup_complete` создан, все ключи валидны
3. `/landing-new test` создаёт проект с `.landing-state.yaml`, все этапы кроме `00_brief` в `locked`
4. `/landing-build` без approved 02–07 → `exit 1` с сообщением «Этап 02 не пройден»
5. На этапе 02 агент задаёт soft-вопросы про фото; ответ пользователя записывается; этап переходит в `approved`
6. `/landing-deploy` без `--env` → деплоит на staging; с `--env prod --confirm` → бэкап → rsync → прод
7. Все плагины из `design-stack.yaml` устанавливаются автоматически
8. 152-ФЗ блок + cookie-баннер видимы на сайте
9. GTM и Метрика подключены, при выключенных cookies — не загружаются
10. WP-CLI MCP отвечает на `wp_plugin_list()` без явного `ssh`

## 14. Следующие шаги

После approve этого spec'а — переход в `superpowers:writing-plans` для создания детального implementation plan по 9 фазам.
