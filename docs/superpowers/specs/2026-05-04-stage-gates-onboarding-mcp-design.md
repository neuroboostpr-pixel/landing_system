# Stage Gates & Onboarding — Design Spec (MVP)

**Дата:** 2026-05-04
**Версия:** 2 (сужен scope до MVP — без расширения агентов, без новых MCP, без 152-ФЗ/multilang/staging)
**Связанные документы:**
- [Базовый дизайн системы](2026-05-03-landing-system-design.md)
- [Master plan](../plans/2026-05-03-landing-system-master-plan.md)

## 1. Задача

Превратить landing-system из «набора агентов с декларативными HARD GATE» в **систему с принудительным workflow**:
1. При первой установке репо — пользователь проходит `/landing-onboarding`, который рассказывает как устроена система и проверяет, что все необходимые инструменты, MCP, скиллы и API-ключи подключены.
2. На каждом этапе каждого проекта — автоматическая проверка готовности (`gate-check`); без зелёного gate переход к следующему этапу запрещён.
3. Перепрыгивать этапы нельзя — даже если пользователь явно просит.

### Зачем

- HARD GATE сейчас существует только в инструкциях агентов — пользователь может попросить «пропусти этап», и агент пропустит.
- При первом клонировании с GitHub новичок не понимает, какие API нужны и где их брать. `preflight.sh` проверяет один `FIRECRAWL_API_KEY`, остальное — на усмотрение.
- Половина ключей из основного spec'а отсутствует в `.env.example` (Pexels, HuggingFace, WhatTheFont, Wordstat, Beget API, Cloudflare и др.).

### Цели

1. На любой машине, клонирующей репо, `/landing-onboarding` за один проход настраивает всё необходимое и валидирует.
2. Запуск любой `/landing-*` команды без пройденного onboarding'а или без gate-check'а — невозможен (`exit 1`).
3. На каждом этапе проекта `.landing-state.yaml` фиксирует статус, и перепрыгивать запрещено механически.

### Не входит (Backlog для будущих spec'ов)

- ❌ Расширение существующих агентов (GTM, sitemap, fallback photo-stylist) — агенты остаются как есть
- ❌ Автоустановка WP-плагинов при деплое
- ❌ `wp db export` бэкап до деплоя
- ❌ 152-ФЗ блок и cookie-баннер
- ❌ Multilang (i18n-engineer)
- ❌ Staging-окружение
- ❌ WP-CLI MCP и DNS MCP (Beget/Cloudflare/Reg.ru)
- ❌ migration-engineer (301-редиректы)

Эти пункты остаются как **soft-checks в gate-check.yaml** — агент спрашивает «есть ли это?», пользователь отвечает yes/no/partial. Реализация фич — позже, отдельными spec'ами.

## 2. Архитектура

### 2.1 Три подсистемы

```
┌──────────────────────────────────────────────────────────────┐
│  ONBOARDING (один раз на машину)                             │
│  /landing-onboarding → docs/SETUP.md → ~/.landing-system/    │
│                                        setup_complete         │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  STAGE GATES (на каждом этапе каждого проекта)               │
│  /landing-* → gate-check.sh --stage N → .landing-state.yaml  │
│   ┌──────────┐  ┌──────────┐                                 │
│   │ HARD     │  │ SOFT     │                                 │
│   │ checks   │  │ checks   │                                 │
│   │ (auto)   │  │ (agent)  │                                 │
│   └──────────┘  └──────────┘                                 │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  WORKFLOW LOCK (.landing-state.yaml в каждом проекте)         │
│  Этапы: locked → in_progress → approved                      │
│  /landing-build блокируется если 02–07 не approved           │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Декларативный YAML — `config/stage-gates.yaml`

Источник истины для всех проверок. `gate-check.sh` читает этот файл.

```yaml
stages:
  "02_assets":
    name: "Сбор материалов клиента"
    hard_checks:
      - id: pexels_or_alt
        type: api_validator_any_of
        validators:
          - tools/api_validators/pexels.py
          - tools/api_validators/unsplash.py
          - tools/api_validators/pixabay.py
        required: true
        fix_hint: "Добавь хотя бы один из ключей: PEXELS_API_KEY / UNSPLASH_ACCESS_KEY / PIXABAY_API_KEY в .env"
      - id: client_assets_folder
        type: file_exists
        path: "{project}/02_МАТЕРИАЛЫ_КЛИЕНТА/"
        required: true
    soft_checks:
      - id: photo_style_consistency
        prompt: "Фото клиента в одном стиле? Если нет — перечисли что нужно перерисовать."
      - id: missing_photos
        prompt: "Каких фото не хватает для лендинга?"

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
        prompt: "Все библиотеки в design-stack.yaml — бесплатные (free tier хватает)?"

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
        prompt: "152-ФЗ блок и cookie-баннер присутствуют в HTML? (если нет — отметить partial и вернуться позже)"

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
```

### 2.3 Workflow lock — `.landing-state.yaml`

Создаётся при `/landing-new` в корне проекта. Обновляется `gate-check.sh` после approve каждого этапа.

```yaml
project: my-landing
created: 2026-05-04
stages:
  "00_brief":      {status: approved, timestamp: 2026-05-04T10:00:00, by: user}
  "01_context":    {status: approved, timestamp: 2026-05-04T10:30:00}
  "02_assets":     {status: in_progress}
  "03_references": {status: locked}
  # ...
```

Статусы: `locked` → `in_progress` → `approved` (или `failed`).

### 2.4 Поток выполнения команды

```
/landing-build
  ↓
1. Проверка ~/.landing-system/setup_complete существует?
   Нет → редирект на /landing-onboarding
  ↓
2. bash gate-check.sh --stage 08_build --project <slug>
   2a. Читает config/stage-gates.yaml → секция 08_build
   2b. Проверяет require_approved: 02–07 в .landing-state.yaml = approved? Иначе exit 1
   2c. Запускает все hard_checks параллельно через api_validators/
   2d. Если хоть один failed → exit 1, выводит fix_hint
  ↓
3. Передача управления в landing-orchestrator (без изменений)
  ↓
4. После завершения этапа → soft_checks (агент задаёт вопросы пользователю)
  ↓
5. После approve пользователя → gate-check.sh --approve 08_build → пишет status: approved
```

## 3. Onboarding-система

### 3.1 Команда `/landing-onboarding`

Запускается:
- Автоматически при первом запуске любой `/landing-*` команды, если нет `~/.landing-system/setup_complete`
- Вручную в любое время для повторной проверки/добавления ключей

### 3.2 Структура мастера (короткая, не более 10–15 минут)

**Секция A — Туториал (5 минут чтения)**
Краткое описание `docs/SETUP.md`:
1. Что такое landing-system — пайплайн 12 этапов
2. Как устроены агенты — orchestrator + специализированные
3. Как работает HARD GATE — `.landing-state.yaml`, нельзя перепрыгивать
4. Зачем onboarding — все ключи нужны до старта проекта

**Секция B — Setup wizard (короткий, без обучения, только проверка)**

1. **Локальные зависимости** — `wp-cli`, `ssh`, `rsync`, `bats`, `python3.10+`, `pip` пакеты. При отсутствии — выводится команда установки.
2. **MCP-серверы** — проверка наличия Firecrawl MCP в `.claude/settings.json` (или глобальных Claude Code settings). Если нет — инструкция установки.
3. **Superpowers-плагин** — проверка что плагин `superpowers` установлен (`claude plugins list | grep superpowers`).
4. **API-ключи** — пошагово, каждый блок:
   - Пояснение «зачем» (1 строка)
   - Прямая ссылка на регистрацию
   - Поле ввода ключа
   - Тестовый запрос для валидации (через `tools/api_validators/<service>.py`)
   - Запись в `.env`

**Секция C — Финал**
- Все обязательные ключи валидированы → создаётся `~/.landing-system/setup_complete` с timestamp
- Сводка: что подключено, что в опциональном fallback, что пропущено
- Предложение: «Готово. Теперь можешь запустить `/landing-new <slug>`»

### 3.3 Файлы

- `commands/landing-onboarding.md` — slash-команда (точка входа)
- `agents/onboarding-guide.md` — агент-проводник через wizard (новый, единственный новый агент)
- `skills/landing-onboarding/SKILL.md` + `scripts/wizard.sh` + `scripts/validate-all.sh`
- `tools/api_validators/*.py` — по одному файлу на каждый сервис (см. раздел 4)
- `docs/SETUP.md` — текстовая версия туториала

## 4. API-валидаторы

`tools/api_validators/` — Python-модули, по одному на каждый сервис. Все используют только free tier эндпоинты (например, для Firecrawl — `/credits`, не `/scrape`, чтобы не тратить квоту).

**Базовый интерфейс** (`tools/api_validators/base.py`):
```python
def validate(api_key: str | dict) -> tuple[bool, str]:
    """Returns (is_valid, message)."""
    ...
```

**Список валидаторов:**
- `firecrawl.py` — `GET https://api.firecrawl.dev/v0/credits`
- `pexels.py` — `GET https://api.pexels.com/v1/search?query=test&per_page=1` с заголовком
- `unsplash.py` — `GET https://api.unsplash.com/photos?per_page=1` с client_id
- `pixabay.py` — `GET https://pixabay.com/api/?key=...&per_page=3`
- `huggingface.py` — `GET https://huggingface.co/api/whoami-v2` с токеном
- `whatthefont.py` — пинг сервиса
- `yandex_wordstat.py` — `POST https://api.wordstat.yandex.net/api/SearchPhrase` с OAuth-токеном
- `yandex_metrika.py` — `GET https://api-metrika.yandex.net/management/v1/counter/{id}` с OAuth
- `telegram.py` — `GET https://api.telegram.org/bot{token}/getMe` + `getChat?chat_id={id}`
- `amocrm.py` — `GET https://{subdomain}.amocrm.ru/api/v4/account` с токеном
- `bitrix24.py` — `GET <webhook_url>/profile/`
- `beget_ssh.py` — `ssh -o BatchMode=yes -o ConnectTimeout=5 ${BEGET_USER}@${BEGET_HOST} 'echo ok'`
- `beget_api.py` — `POST https://api.beget.com/api/user/getAccountInfo`
- `cloudflare.py` — `GET https://api.cloudflare.com/client/v4/user/tokens/verify`
- `regru.py` — `POST https://api.reg.ru/api/regru2/nop` с username/password

Каждый валидатор имеет соответствующий unit-тест с mock'ом HTTP в `tests/api_validators/test_<service>.py`.

## 5. Полный `.env.example`

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

## 6. Реализация по фазам

### Phase 1 — `.env.example` + API-валидаторы
- Полный `.env.example` (со всеми ключами выше)
- `tools/api_validators/base.py` (interface) + 15 валидаторов
- `tests/api_validators/` — unit-тесты с mock'ом HTTP для каждого валидатора

### Phase 2 — Onboarding wizard
- `agents/onboarding-guide.md`
- `commands/landing-onboarding.md`
- `skills/landing-onboarding/SKILL.md`, `scripts/wizard.sh`, `scripts/validate-all.sh`
- `docs/SETUP.md` (туториал)
- Создание/проверка `~/.landing-system/setup_complete` flag-механизма
- bats-тест: `tests/onboarding/test-wizard.bats`

### Phase 3 — Stage-gates runner + workflow lock
- `config/stage-gates.yaml` (с проверками для всех 12 этапов)
- `scripts/gate-check.sh` (runner — читает yaml, исполняет hard_checks, обновляет .landing-state.yaml)
- `scripts/gate-state.sh` (мини-утилита: get/set status в .landing-state.yaml)
- `template/.landing-state.yaml`
- bats-тесты: `tests/gate-check/`

### Phase 4 — Интеграция в slash-команды
- В каждой `/landing-*` (16 файлов) — добавить вызов `gate-check.sh --stage N` в начале
- Заменить `scripts/preflight.sh` (теперь делегирует в `gate-check.sh --stage 00`)
- Дополнить `agents/landing-orchestrator.md` инструкцией читать `.landing-state.yaml` и enforce порядка

### Phase 5 — Документация и пуш на GitHub
- Обновить `README.md` (раздел про onboarding)
- Обновить `CLAUDE.md` (упомянуть `.landing-state.yaml` lock)
- Финальный sanity-чек (bats всех уровней)
- Коммит + `git push origin main`

## 7. Тестирование

- **`tests/api_validators/`** — unit-тесты Python (mock HTTP через `responses` или `pytest-httpx`)
- **`tests/onboarding/`** — bats-тесты wizard-flow
- **`tests/gate-check/`** — bats-тесты с фикстурами `.landing-state.yaml`
- **`tests/e2e/`** — один сквозной тест: `/landing-new test` → попытка `/landing-build` без 02–07 → должен падать

TDD-протокол: каждая фаза начинается с failing-теста, реализация — после.

## 8. Риски и решения

| Риск | Решение |
|---|---|
| Onboarding слишком длинный → бросают на середине | Короткий (10–15 мин), `--resume` для продолжения с места остановки |
| API-валидатор тратит квоту | Все эндпоинты — только free/info (например, /credits, /whoami) |
| `.landing-state.yaml` повреждён вручную | gate-check валидирует структуру, флаг `--reset-state` для сброса |
| Soft-check субъективен | Прямые yes/no/partial вопросы, ответ записывается в `.landing-state.yaml.log` |

## 9. Acceptance criteria

1. Свежий клон репо → `/landing-new test` → отказ с предложением `/landing-onboarding`
2. После прохождения onboarding → `~/.landing-system/setup_complete` создан, все обязательные ключи валидны
3. `/landing-new test` создаёт проект с `.landing-state.yaml`, все этапы кроме `00_brief` в `locked`
4. `/landing-build` без approved 02–07 → `exit 1` с сообщением «Этап 02 не пройден»
5. На этапе 02 агент задаёт soft-вопросы про фото; ответ пользователя записывается; этап переходит в `approved`
6. Bats-тесты всех уровней проходят
7. Изменения закоммичены и запушены в `neuroboostpr-pixel/landing_system`

## 10. Что остаётся как Backlog

После сдачи MVP — отдельные spec'и для:
1. Расширение существующих агентов (analytics+GTM, seo+sitemap, photo-stylist+fallback, deployer+бэкап+плагины)
2. 152-ФЗ + cookie-баннер + legal pages
3. Multilang (i18n-engineer + Polylang)
4. Staging-окружение (`deploy.sh --env`)
5. WP-CLI MCP
6. DNS MCP (Beget/Cloudflare/Reg.ru)
7. migration-engineer (301-редиректы)

Каждый — небольшой, инкрементальный, легко добавляется поверх MVP.

## 11. Следующие шаги

После approve этого spec'а — переход в `superpowers:writing-plans` для создания детального implementation plan по 5 фазам.
