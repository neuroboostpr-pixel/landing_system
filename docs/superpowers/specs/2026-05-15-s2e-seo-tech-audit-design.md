# S2-E: SEO / Tech / Vitals Audit Skill (`/landing-audit`)

**Дата:** 2026-05-15
**Owner:** Спец 2
**Roadmap:** [2026-05-15-specialist-2-roadmap.md](2026-05-15-specialist-2-roadmap.md)
**Источник:** п.6 «финальная авто-проверка сайта» из ПЛАН-ДОРАБОТОК + benchmark 10 инструментов pr-cy.ru
**Статус:** brainstorm complete, **PENDING REVISION** под multisite (см. [roadmap](2026-05-15-specialist-2-roadmap.md) — S2-CD делается первым).

**Что требует ревизии после S2-CD:**
- `--batch` режим: автодетекция всех поддоменов сетки через `wp site list --field=url` и прогон audit по каждому.
- Output `11_QA/audit-report.md` — сводный отчёт с разбивкой по поддоменам (главный + N сегментов).
- Гейты stage-11 — все поддомены должны быть зелёные перед approval, не только главный.

---

## 1. Цель

Заменить ручную проверку маркетологом перед сдачей лендинга клиенту на автоматический аудит из ~65 проверок, эквивалентный публичному отчёту pr-cy.ru (за вычетом платных backlinks/SERP-данных). Результат — стандартизованный отчёт + блокирующий гейт stage-11: лендинг не показывается клиенту, пока hard-gates красные.

## 2. Архитектура

Скилл `seo-tech-audit/` + slash-команда `/landing-audit [<slug>|<url>] [--batch <file>] [--with-yandex-webmaster] [--with-gsc]`.

**Принципы:**
- Read-only по отношению к сайту (только HTTP GET + Lighthouse прогон). Без правок, без коммитов, без деплоев.
- Self-contained: никаких платных API в P0. Опциональные runner-ы под платные/OAuth-сервисы — gated флагами.
- Output машино-читаемый (JSON) + человеко-читаемый (Markdown, HTML).
- Параллельный запуск runner-ов через `concurrent.futures.ThreadPoolExecutor` — целевое время ≤90 секунд для одного URL.

**Entry point:** `scripts/run-audit.py <url> --out 11_QA/`. Оркеструет runner-ы, собирает в `lib/report.py::build_report()`, сравнивает с `quality-thresholds.yaml`, пишет три файла.

## 3. Каталог проверок (65 локальных + opt-in внешние)

Структурировано так, чтобы маркетолог мог открыть отчёт pr-cy и сразу сопоставить с нашим.

### 3.1 `html_checks.py` — HTML on-page (25 проверок)

| # | Проверка | Hard gate | Источник pr-cy |
|---|---|---|---|
| H1 | HTTP-код = 200 | ✓ | Анализ сайта |
| H2 | Time-to-first-byte | (soft) | Анализ сайта |
| H3 | Размер HTML (KB) | (soft, warn >150) | Анализ сайта |
| H4 | `<title>` присутствует | ✓ | Контент-анализ |
| H5 | `<title>` длина 30-80 | ✓ | Контент-анализ |
| H6 | `<meta description>` присутствует | ✓ | Контент-анализ |
| H7 | `<meta description>` длина 70-320 | ✓ | Контент-анализ |
| H8 | Ровно 1× `<h1>` | ✓ | Анализ сайта (баг ed.iqido.ru: 0 H1) |
| H9 | Иерархия H2-H6 (нет скачков) | (soft) | Анализ сайта |
| H10 | `<html lang=...>` присутствует | ✓ | — |
| H11 | UTF-8 declaration | ✓ | Контент-анализ |
| H12 | `<link rel=canonical>` присутствует и валиден | ✓ | Контент-анализ |
| H13 | `hreflang` (если мультиязычно) | (soft) | — |
| H14 | Robots-meta (нет неожиданного noindex) | ✓ | Анализ сайта |
| H15 | `<img alt>` — ≥95% картинок имеют alt | ✓ | Контент-анализ |
| H16 | `<img>` имеют `loading=lazy` (≥80% below-fold) | (soft) | Анализ сайта |
| H17 | `<img>` размеры заданы (width/height для CLS) | (soft) | Web Vitals |
| H18 | Современные форматы изображений (WebP/AVIF) | (soft) | Анализ сайта |
| H19 | Inline-CSS размер ≤10 KB | (soft) | Анализ сайта |
| H20 | Render-blocking resources count ≤3 | (soft) | Web Vitals |
| H21 | Внутренних ссылок ≥5 | (soft) | Контент-анализ |
| H22 | Внешние ссылки имеют `rel=noopener` | ✓ | Анализ сайта |
| H23 | Текст-анкоры «click here»/«тут» — <5% | (soft) | Контент-анализ |
| H24 | Phone-links `tel:` присутствуют (мобильность) | (soft) | — |
| H25 | Mailto-links если контактные данные в тексте | (soft) | — |

### 3.2 `content_metrics.py` — текст-метрики (7 проверок)

| # | Проверка | Hard gate | Источник pr-cy |
|---|---|---|---|
| C1 | Объём текста — слов ≥300 | ✓ | Контент-анализ |
| C2 | Объём текста — символов | (info) | Контент-анализ |
| C3 | Тошнота 4-6% (TF-IDF плотность) | (soft) | Контент-анализ |
| C4 | Водность (% стоп-слов) — норма ≤30% | (soft) | Контент-анализ |
| C5 | Читаемость Flesch-Kincaid RU/EN | (info) | — |
| C6 | Точные вхождения ключа в title/h1/text | (soft, требует keywords из brief) | Контент-анализ |
| C7 | Плотность ключа в body 1-3% | (soft) | Контент-анализ |

Ключи берём из `01_БРИФ/brief.yaml` или `08_КОД/seo-keywords.yaml` (опциональный артефакт).

### 3.3 `network_checks.py` — infra + Whois (13 проверок)

| # | Проверка | Hard gate | Источник pr-cy |
|---|---|---|---|
| N1 | SSL валиден | ✓ | Анализ сайта |
| N2 | SSL ≥30 дней до истечения | (soft) | Анализ сайта |
| N3 | SSL ≥7 дней — hard gate | ✓ | Анализ сайта |
| N4 | HTTP/2 или HTTP/3 | (soft) | — |
| N5 | Security headers: HSTS, CSP, X-Frame-Options, X-Content-Type-Options | (soft, 3 из 4) | Анализ сайта |
| N6 | Server header не раскрывает версию | (soft) | — |
| N7 | www / non-www → 301 на канонический | ✓ (есть редирект, без петель) | Анализ сайта |
| N8 | `robots.txt` присутствует и валиден | ✓ | Анализ сайта |
| N9 | `sitemap.xml` присутствует, валидный XML, упомянут в robots.txt | ✓ | Анализ сайта |
| N10 | `llms.txt` присутствует (новый стандарт AI) | (soft) | — |
| N11 | 404-страница возвращает 404 (не 200) | ✓ | Анализ сайта |
| N12 | 404 содержит навигацию (хотя бы ссылку на главную) | (soft) | Анализ сайта |
| N13 | Whois: возраст домена, expiry, регистратор, NS — info-only | (info) | Whois |

Whois через Python `python-whois` локально, без внешних API.

### 3.4 `vitals.py` — Lighthouse CLI wrapper (11 метрик × 2 устройства)

| # | Метрика | Hard gate (desktop) | Hard gate (mobile) | Источник pr-cy |
|---|---|---|---|---|
| V1 | Performance score | ≥70 | ≥40 | Web Vitals |
| V2 | Accessibility score | ≥85 | ≥85 | Анализ сайта |
| V3 | Best Practices score | ≥85 | ≥85 | Анализ сайта |
| V4 | SEO score (lighthouse) | ≥90 | ≥90 | Анализ сайта |
| V5 | LCP | ≤2.5s | ≤4s | Web Vitals |
| V6 | FCP | ≤1.8s | ≤3s | Web Vitals |
| V7 | TTFB | ≤0.8s | ≤1.5s | Web Vitals |
| V8 | CLS | ≤0.1 | ≤0.25 | Web Vitals |
| V9 | INP | ≤200ms | ≤200ms | Web Vitals |
| V10 | TBT | ≤300ms | ≤600ms | Web Vitals |
| V11 | Speed Index | ≤3.4s | ≤5.8s | Web Vitals |

Lighthouse гоняется дважды (desktop preset, mobile preset). Используется `--throttling.cpuSlowdownMultiplier=4` для mobile (стандарт).

### 3.5 `schema_checks.py` — микроразметка (5 проверок)

| # | Проверка | Hard gate |
|---|---|---|
| S1 | Open Graph: og:title, og:description, og:image, og:type, og:url — все 5 | ✓ |
| S2 | og:image валиден (URL отдаёт 200, размер ≥1200×630) | (soft) |
| S3 | Twitter Card: card, title, image | (soft) |
| S4 | Schema.org JSON-LD присутствует, парсится | (soft) |
| S5 | Favicon присутствует, размеры 32/180 | ✓ |

### 3.6 `crawler.py` — битые ссылки (depth=2)

| # | Проверка | Hard gate |
|---|---|---|
| CR1 | 0 битых внутренних ссылок (HTTP 4xx/5xx) | ✓ |
| CR2 | 0 битых картинок (`<img src>` → 4xx) | ✓ |
| CR3 | 0 битых внешних ссылок | (soft, warn) |

Max-pages = 50 (защита от больших сайтов), respect robots.txt.

### 3.7 `ai_readiness.py` — bonus, не в pr-cy (3 проверки)

| # | Проверка | Hard gate |
|---|---|---|
| AI1 | `llms.txt` соответствует [llms.txt spec](https://llmstxt.org) | (soft) |
| AI2 | Schema.org `Organization`, `Product` или `FAQ` для AI-сниппетов | (soft) |
| AI3 | Сайт рендерится без JS (curl/no-JS режим даёт основной контент) | (soft) |

### 3.8 `external_apis.py` — opt-in платные/OAuth (gated)

| Флаг | Что добавляет | pr-cy аналог |
|---|---|---|
| `--with-pagespeed` | Google PageSpeed Insights API (real-user RUM) | Web Vitals (real users) |
| `--with-yandex-webmaster` | ИКС, индексация в Яндексе | Анализ сайта, ИКС tool |
| `--with-gsc` | Индексация Google, impressions, clicks | Indexing tool |

При отсутствии ключей в `.env` — runner пропускается с warning, не блокирует.

### 3.9 Out of scope

- Backlinks / ссылочный профиль (Ahrefs/Majestic = платно)
- Similar websites / конкуренты (SimilarWeb = платно)
- AI SERP visibility (видны ли в ChatGPT/Perplexity) — отдельный S2-F проект, требует браузер-автоматизации.
- Keyword rank tracking (позиции в выдаче) — SERP API платный, ad-hoc парсинг = риск ToS.
- Adult-content detection — теоретически просто, но out of scope для нашей ниши (B2C услуги).

## 4. Структура артефактов

```
skills/seo-tech-audit/
├── SKILL.md
├── scripts/
│   ├── run-audit.py                 # entry point, оркестратор
│   ├── runners/
│   │   ├── html_checks.py
│   │   ├── content_metrics.py
│   │   ├── network_checks.py
│   │   ├── vitals.py                # lighthouse wrapper
│   │   ├── schema_checks.py
│   │   ├── crawler.py
│   │   ├── ai_readiness.py
│   │   └── external_apis.py
│   ├── lib/
│   │   ├── report.py                # сборка JSON + render Markdown/HTML
│   │   ├── thresholds.py            # читает quality-thresholds.yaml
│   │   ├── http_client.py           # requests-сессия с retry/timeout/UA
│   │   └── russian_text.py          # тошнота/водность/Flesch RU
│   └── templates/
│       └── audit-report.html.j2
├── config/
│   └── quality-thresholds.yaml      # дефолтные гейты
└── tests/
    ├── fixtures/
    │   ├── good-site.html           # эталон со всеми passes
    │   ├── bad-site.html            # дыры по 10 категориям
    │   └── ed-iqido-snapshot.html   # реальный кейс с багом «0 H1»
    └── test_runners.py

template/11_QA/
└── audit-overrides.example.yaml     # авторский override порогов

.claude/commands/
└── landing-audit.md

docs/standards/
└── audit-checklist-mapping.md       # маппинг наших 65 проверок ← pr-cy 80
```

## 5. Гейты

Дефолтные пороги в `skills/seo-tech-audit/config/quality-thresholds.yaml` (см. таблицы §3). Маркетолог может переопределить per-проект через `<project>/11_QA/audit-overrides.yaml`. Override-механизм:
- Можно ужесточить (понизить ceiling, повысить floor).
- Можно ослабить только с `justification: "<reason>"` обязательным полем (фиксируется в отчёте).

## 6. Output

`11_QA/audit-report.md` — структурирован по 8 секциям-аналогам инструментов pr-cy:

```markdown
# Audit Report — example.com

**Date:** 2026-05-15 14:30
**Overall score:** 87/100 (PASS)
**Hard gates:** 28/28 ✓
**Soft gates:** 18/22 (4 warnings)

## 1. HTML & On-page (25 checks)  → 24 ✓ / 1 warn
## 2. Content Metrics (7 checks)  → 7 ✓
## 3. Network & Infra (13 checks) → 13 ✓
## 4. Core Web Vitals (22 checks) → 19 ✓ / 3 warn
   ### Desktop
   ### Mobile  ← CLS=0.18 (target ≤0.25, OK but >0.1)
## 5. Microdata (5 checks)        → 5 ✓
## 6. Broken Links (3 checks)     → 3 ✓
## 7. AI Readiness (3 checks)     → 3 ✓
## 8. External APIs (opt-in)      → skipped (no keys)

## Recommendations (auto-prioritized)
1. [P1] Mobile CLS could be improved...
2. ...
```

`audit-report.json` — машино-читаемый, используется orchestrator-ом для auto-fix решений.
`audit-report.html` — single-file HTML с inline CSS для шаринга клиенту/маркетологу.

## 7. Интеграция в pipeline

**Stage 11 (QA) — обязательный gate:**

Скилл `seo-tech-audit` только **диагностирует** (возвращает JSON + exit-code). Логика auto-fix живёт в `agents/landing-orchestrator.md` и `agents/qa-auditor.md` — они читают `audit-report.json`, мапят `failed_check_id → fix_action`, вызывают соответствующего исполнителя.

```
deploy success → wait 30s → /landing-audit <slug>
   ├─ exit 0 → stage-11 PASS, можно показывать клиенту
   ├─ hard_gate fail → orchestrator читает audit-report.json и предлагает auto-fix:
   │     missing H1     → block-composer добавляет H1 в hero (+ smoke gate из S2-A!)
   │     missing OG     → wp-builder заполняет дефолты в landing-config
   │     ssl expired    → wp-deployer запускает certbot renew
   │     CLS too high   → frontend-builder проверяет width/height на картинках
   │     broken links   → content-writer чинит ссылки
   └─ rerun audit → если опять fail → ESCALATE к человеку
```

**Ad-hoc:** `/landing-audit https://example.com` для любого URL, в том числе чужого (research-инструмент по конкурентам).

**Batch:** `/landing-audit --batch urls.txt --out reports/` — для проверки всех задеплоенных лендингов агентства разом.

## 8. Lazy Blocks safety

Сам скилл S2-E **не трогает** Lazy Blocks — он только HTTP-клиент к задеплоенному сайту. Smoke-gate из S2-A здесь **не требуется**.

**НО:** если auto-fix решение приводит к вызову `block-composer` (например, добавить H1) — это меняет блоки, поэтому **обязательно**:
1. Прогнать `tests/integration/test_lazy_blocks_smoke.sh` после правки `block-spec.yaml`.
2. Перегенерировать тему + redeploy.
3. Повторно прогнать `/landing-audit`.

Эта последовательность зашита в orchestrator-логику auto-fix.

## 9. Зависимости

- Python 3.11+, `requests`, `beautifulsoup4`, `lxml`, `PyYAML`, `python-whois`, `jsonschema`, `jinja2`.
- Node.js 20+, `lighthouse` CLI (npm global).
- Опционально: API-ключи для PageSpeed/Yandex Webmaster/GSC в `.env`.

`scripts/check-deps.sh` расширяется: проверяет наличие `lighthouse --version`. `landing-onboarding` добавляет шаг «Установка lighthouse CLI».

## 10. Testing

### 10.1 Unit
- `tests/test_runners.py` — каждый runner на фикстуре `good-site.html` (все pass) и `bad-site.html` (все fail).
- `tests/test_thresholds.py` — override механизм.
- `tests/test_report.py` — JSON структура, Markdown rendering.
- `tests/test_russian_text.py` — тошнота, водность, Flesch на эталонных текстах.

### 10.2 Integration
- `tests/integration/test_audit_e2e.sh` — поднимает локальный nginx с `good-site.html`, гоняет `/landing-audit`, проверяет exit 0 и наличие отчёта.
- `tests/integration/test_audit_bad.sh` — то же с `bad-site.html`, проверяет exit 1 и список проблем.

### 10.3 Regression
- Snapshot `ed-iqido-snapshot.html` (реальный кейс с pr-cy багом «0 H1») — должен поймать тот же баг (H8 = fail).

## 11. Out of scope

- A/B-сравнение двух URL.
- Watch-mode (continuous audit).
- Webhook-нотификации в Slack/Telegram при падении score — отложим до S2-A интеграции с TG.
- PDF-экспорт отчёта (HTML + браузерный print достаточен).

## 12. Open questions для имплементации

- Где хранить snapshot отчётов для динамики (audit-2026-05-15.json, audit-2026-05-22.json и т.д.)? **Предложение:** `11_QA/history/<timestamp>.json`, плюс git-commit каждого.
- Использовать ли `lighthouse-ci` для регрессии (сравнение текущего с предыдущим)? **Предложение:** в P0 — нет; в S2-E.1 — да.
- Парсить ли pr-cy.ru параллельно как «второе мнение» (без зависимости от него)? **Предложение:** нет, как обсуждено — лишняя fragile зависимость.

Решения принимаются на этапе писания плана.

---

## 13. Revision (2026-05-22) — Multisite + Фазы

Дополнение к исходному spec'у. Не меняет п.1-12, добавляет multisite batch-mode и явно фиксирует поэтапную реализацию.

### 13.1 Multisite batch-mode

После [S2-CD](2026-05-18-s2cd-multisite-cloning-design.md) проект может иметь N поддоменов сегментов
(например `ailexi.ru`, `russian.ailexi.ru`, `dubai-avto-liza.ailexi.ru`). Audit должен уметь:

**CLI:**
```bash
/landing-audit <project-slug>                 # все поддомены проекта (default в multisite-mode)
/landing-audit <project-slug> --site <host>   # один конкретный поддомен
/landing-audit <url>                          # любой URL (ad-hoc, как было)
/landing-audit <project-slug> --batch         # явный батч-режим, синоним default'а
```

**Discovery поддоменов:**
- `.landing-state.yaml::audience_segments[]` (от S2-CD) — список `{slug, host}` сегментов
- Главный домен — из `.landing-state.yaml::project::primary_domain`
- Резерв: `wp site list --field=url` через SSH+wp-cli

**Output структура для multisite:**
```
11_QA/
  audit-report.md                  # сводный отчёт (главный + все сегменты, таблица сравнения)
  audit-report.json                # { sites: [{host, score, hard_gates, soft_gates, checks: {...}}] }
  audit-report.html                # single-file HTML
  per-site/
    ailexi.ru.json
    ailexi.ru.md
    russian.ailexi.ru.json
    russian.ailexi.ru.md
    dubai-avto-liza.ailexi.ru.json
    dubai-avto-liza.ailexi.ru.md
  history/
    <timestamp>/                   # каждый запуск — отдельный snapshot
      audit-report.json
      per-site/...
```

**Stage-11 gate в multisite:**
- Hard-gates должны быть зелёные **на каждом** поддомене, не только на главном.
- Если хоть один поддомен красный — stage-11 не закрывается.
- Сводный отчёт показывает таблицу «домен → score → failed checks count».

**Парallelism:** N сайтов × M runners — изначально последовательно по сайтам, параллельно по runners (как уже описано в §2). Параллельный batch добавим только если время прогона на N=10 сайтах превысит 10 минут.

### 13.2 Поэтапная реализация (E1 → E2 → E3 → E4)

Реализация бьётся на 4 фазы. Каждая фаза = отдельный plan + worktree + merge.

| Фаза | Содержимое | Покрывает проверки из §3 | Размер |
|---|---|---|---|
| **E1 (P0, эта итерация)** | Каркас `seo-tech-audit/` skill, `run-audit.py` оркестратор, `html_checks.py` (25), `network_checks.py` (13), `schema_checks.py` (5), Markdown + JSON отчёт, **multisite batch-mode**, `/landing-audit` slash-команда, stage-11 gate integration без auto-fix | §3.1, §3.3, §3.5 (43 проверки) | ~600 SLOC, 1-2 дня |
| **E2** | `vitals.py` (Lighthouse CLI), `crawler.py` (битые ссылки), HTML отчёт (`audit-report.html`), `tests/integration/test_audit_e2e.sh` | §3.4, §3.6 (25 проверок) | ~400 SLOC, 1-2 дня |
| **E3** | `content_metrics.py` (тошнота/вода/Flesch RU), `lib/russian_text.py`, snapshot history (`11_QA/history/<ts>/`) | §3.2 (7 проверок) | ~250 SLOC, 1 день |
| **E4** | `ai_readiness.py` (llms.txt, schema, no-JS render), `external_apis.py` (opt-in PageSpeed/GSC/Yandex Webmaster), auto-fix логика в orchestrator | §3.7, §3.8 (3+3 проверок + AI fix-loop) | ~400 SLOC, 2 дня |

**Что E1 НЕ делает (явно out of scope этой фазы):**
- Lighthouse Web Vitals (E2)
- Crawler битых ссылок (E2)
- HTML-версия отчёта (E2)
- Content-metrics RU (E3)
- Snapshot history (E3 для динамики, но в E1 можно класть `11_QA/audit-report.{md,json}` без history)
- AI-readiness и external APIs (E4)
- Auto-fix логика в orchestrator (E4 — в E1 stage-11 gate просто `fail/pass` без auto-recovery)

**Acceptance E1:**
- `/landing-audit dubai-avto-liza` запускает audit по всем поддоменам ailexi.ru сети (ailexi.ru + dubai-avto-liza.ailexi.ru), пишет `11_QA/audit-report.md` со сводной таблицей
- Все 43 проверки (HTML/Network/Schema) реально выполняются и попадают в отчёт
- Hard-gates корректно идентифицируют failed checks
- `tests/test_runners.py` — каждый runner покрыт unit-тестами на фикстурах good/bad
- exit 0 если все hard-gates ✓, exit 1 если хоть один fail (на любом поддомене)
- Без зависимости от Lighthouse / Node.js (E1 = pure Python)

