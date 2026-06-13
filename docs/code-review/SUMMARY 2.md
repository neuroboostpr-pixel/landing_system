# Code Review SUMMARY — landing-system

**Дата:** 2026-05-23
**Срок проведения:** 1 рабочий день
**Метод:** статический code-review по playbook'у `docs/code-review/2026-05-23-review-plan.md`
**Инструменты:** code-reviewer skill (Read/Grep/Glob/Write — без правок кода)

---

## TL;DR (для руководства)

Просканировано **723 файла-кандидата** по 15 категориям, ~10 000 файлов индексировано для поиска ссылок. По итогам 8 фаз ревью зафиксировано **53 findings**, из них **6 критичных** (🔴) и **20 важных** (🟠).

**Хорошие новости:**
- **Мёртвого кода почти нет** — реальных orphan-файлов всего **4** (а не 309 как первоначально показала карта Фазы 0, остальные 305 — false-positives из-за непокрытых паттернов: Python imports, PHP dynamic includes, glob).
- **Encryption-модуль реализован правильно** (AES-256-GCM, random IV, auth tag).
- **152-ФЗ согласие реально enforce'нится** на REST endpoint.
- **WP-админка mu-plugin: 0 «висящих» кнопок и 0 ссылок на несуществующие страницы.** Каждый обработчик покрыт nonce + capability check.
- **238 тестов** в проекте — хорошее покрытие.

**Что выглядит блокером для запуска в прод:**
1. **REST endpoint для приёма заявок защищён только honeypot+rate-limit.** Продвинутый бот через прокси-пул легко обходит → засорение CRM/email.
2. **Множественные XSS-векторы** (~20 мест с unescaped `echo $var`). Самые опасные — в публичном `/llms.txt` и в hidden input segment из `$_GET`.
3. **Adapter dispatch для CRM не подключён.** В REST endpoint есть `do_action('landing_config_lead_received')`, но **0 слушателей**. Маркетолог настраивает AmoCRM/Bitrix/Telegram — но **заявки в CRM не уходят**. Документировано в коде как незакрытый PR A5.
4. **Циклическая зависимость в pipeline:** `09_deploy` требует `10_qa` approved, а `10_qa` проверяет deployed-сайт. Сайт уходит в прод **без реальной QA-проверки**.
5. **Auto-fix loop в `/landing-go` без `max_attempts`** — потенциальный бесконечный цикл, расход токенов без предела.
6. **Telegram bot-токен передаётся в URL** → попадает в access-log хостинга. При утечке backup'а — компрометация ботов всех клиентов.

**Решения по каждому пункту — за пользователем после прочтения отчётов.**

---

## Все 🔴 и 🟠 findings по проекту (сводная таблица)

| # | Severity | Фаза | Краткое описание | Ссылка |
|---|---|---|---|---|
| 1 | 🔴 | 2 #1 | Auto-fix loop в `/landing-go` без `max_attempts` — бесконечный цикл, расход токенов | `phase-2-token-hotspots.md` |
| 2 | 🔴 | 3 #1 | Циклическая зависимость 09_deploy ↔ 10_qa — сайт уходит в прод без реальной QA | `phase-3-flow-integrity.md` |
| 3 | 🔴 | 4 #1 | `/landing-help` устарел: 17 команд не упомянуты (включая `/landing-go`, `/landing-start`), 2 несуществующие — упомянуты | `phase-4-ui-completeness.md` |
| 4 | 🔴 | 5 #1 | Wiki-скрипты hard-coded на `~/Lendings/` — на Windows у пользователя `d:/AI_TEAMS/Lendings/`, не работает | `phase-5-correctness.md` |
| 5 | 🔴 | 5 #2 | 18 из 34 bash-скриптов без `set -euo pipefail` (53%) — verify-скрипты могут возвращать ложный pass | `phase-5-correctness.md` |
| 6 | 🔴 | 6B #1 | REST endpoint `/lead` слабая защита (только honeypot+rate-limit per-IP) — обходится прокси-ботом | `phase-6b-security.md` |
| 7 | 🔴 | 6B #2 | ~20 unescaped XSS-векторов через `echo $var`; критичны: `llms-txt-rewrite.php:24`, `admin-snippets.php:553` | `phase-6b-security.md` |
| 8 | 🔴 | 6B #3 | Telegram bot-токен в URL → access-log хостинга → утечка при компрометации backup | `phase-6b-security.md` |
| 9 | 🔴 | 6C #1 | Adapter dispatch для CRM не подключён — заявки **не уходят в AmoCRM/Bitrix/HubSpot/Telegram/WhatsApp** | `phase-6c-admin-flow.md` |
| 10 | 🔴 | 6C #2 | Нет `wpmu_delete_blog` hook — per-blog таблицы leads с ПД не дропаются при удалении subsite (152-ФЗ ст.5) | `phase-6c-admin-flow.md` |
| 11 | 🟠 | 2 #2 | 27/32 агентов имеют retry-логику, 0 явных ограничителей | `phase-2-token-hotspots.md` |
| 12 | 🟠 | 2 #3 | wiki/ (480 файлов) построена как навигационный граф, но **никто не инструктирован по нему ходить** | `phase-2-token-hotspots.md` |
| 13 | 🟠 | 3 #2 | Параллельные `07d_photos` и `07e_visuals` оба `lock: soft` — можно выпустить лендинг с placeholder'ами | `phase-3-flow-integrity.md` |
| 14 | 🟠 | 3 #3 | TODO в главной команде `landing-go`: `legacy_reason` не передаётся, правило безопасности отключено | `phase-3-flow-integrity.md` |
| 15 | 🟠 | 3 #4 | `verify-visual-qa.sh` существует, но не подключён ни к одному gate | `phase-3-flow-integrity.md` |
| 16 | 🟠 | 3 #5 | Дубль verify-проверок 07c ↔ 07f (одни скрипты, один файл) | `phase-3-flow-integrity.md` |
| 17 | 🟠 | 3 #6 | 5 из 7 migration-скриптов не упомянуты в CLAUDE.md | `phase-3-flow-integrity.md` |
| 18 | 🟠 | 4 #2 | help категоризирует команды по «Phase 2+ / Phase 5» (устаревшая схема MVP) | `phase-4-ui-completeness.md` |
| 19 | 🟠 | 4 #3 | Расхождение CLI: 3 команды только в `.claude/commands/`, `landing-clone` разошлась контентом | `phase-4-ui-completeness.md` |
| 20 | 🟠 | 5 #3 | Migration-скрипты без marker-based idempotency — двойной запуск опасен | `phase-5-correctness.md` |
| 21 | 🟠 | 5 #4 | Большие агенты (`niche-analyst` 341, `landing-orchestrator` 317, `wp-builder` 214) смешивают слои | `phase-5-correctness.md` |
| 22 | 🟠 | 5 #5 | 6 близких команд в этапе 07 (content/compose/prototype/wireframe/photos/visuals) — naming overlap | `phase-5-correctness.md` |
| 23 | 🟠 | 6A #1 | Inline `onclick` в `admin-lead-detail.php` — сломается при CSP | `phase-6a-ui-wiring.md` |
| 24 | 🟠 | 6A #2 | 0 AJAX в админке — full-page reload на каждое действие | `phase-6a-ui-wiring.md` |
| 25 | 🟠 | 6A #3 | Нет автоматического теста «форма → handler» | `phase-6a-ui-wiring.md` |
| 26 | 🟠 | 6B #4 | Сырые SQL без `prepare()` в `admin-leads.php:48,197` (паттерн нарушен) | `phase-6b-security.md` |
| 27 | 🟠 | 6B #5 | Bitrix24 endpoint из user-config — потенциальный SSRF | `phase-6b-security.md` |
| 28 | 🟠 | 6B #6 | REST endpoint пишет полный IP/UA в БД без анонимизации — риск штрафа РКН (152-ФЗ ст.7) | `phase-6b-security.md` |
| 29 | 🟠 | 6B #7 | Encryption-ключ зависит от wp-config keys — ротация ломает все credentials | `phase-6b-security.md` |
| 30 | 🟠 | 6C #3 | Audit-runner синхронный `shell_exec` — 30+ сек блокировка PHP-FPM | `phase-6c-admin-flow.md` |
| 31 | 🟠 | 6C #4 | Lead-detail без явной кнопки «вернуться в список» | `phase-6c-admin-flow.md` |
| 32 | 🟠 | 6C #5 | Cascade-flow (CTA/Integrations/Snippets/Lead-statuses) без integration-тестов | `phase-6c-admin-flow.md` |
| 33 | 🟠 | 6C #6 | Cookie-banner: не задокументирована проблема с localStorage при тестировании | `phase-6c-admin-flow.md` |

---

## Все 🟡 и 🟢 findings по проекту (сводная таблица)

| # | Severity | Фаза | Краткое описание |
|---|---|---|---|
| 34 | 🟡 | 1 #1-2 | 2 docs/standards без подключения к агентам (`stage-agent-preamble.md`, `stage-08-spec-lint.md`) |
| 35 | 🟡 | 1 #3-4 | 2 genuine-orphan: `scripts/refresh-catalog.py`, `scripts/migrate-blocks-to-wireframe-format.py` |
| 36 | 🟡 | 2 #4 | 7 outlier-промптов >3× медианы — кандидаты на references/X.md |
| 37 | 🟡 | 2 #5 | 25 агентов читают одни и те же тяжёлые файлы (tokens.json, composed.html) |
| 38 | 🟡 | 3 #7 | `11_analytics` и `12_seo` оба `lock: soft` — деплой без аналитики/SEO |
| 39 | 🟡 | 3 #8 | `01_context` упомянут в `landing-go`, но отсутствует в `stage-gates.yaml` |
| 40 | 🟡 | 3 #9 | 4 TODO/FIXME-маркера в активных агентах/командах |
| 41 | 🟡 | 4 #4-6 | Photo-board UI inline-JS / wireframe 698 строк / 543 block-library HTML без валидации |
| 42 | 🟡 | 5 #6 | 53% bash-скриптов без `[[ -f ]]` проверки файлов |
| 43 | 🟡 | 5 #7 | 238 тестов классифицированы по PR-X (не by-domain) |
| 44 | 🟡 | 6A #4-7 | Cookie-banner логика разбросана / deep-link каталог без тестов / blog existence / segment-selector usage |
| 45 | 🟡 | 6B #8-10 | `switch_to_blog` в loop / email не throttled / `error_log` audit |
| 46 | 🟡 | 6C #7-10 | Lead-status edge cases / migration registry / bulk-actions N transactions / deep-link tests |
| 47 | 🟢 | Multi | Нет `except: pass` в Python ✅ |
| 48 | 🟢 | 6A | 0 висящих кнопок и 0 ссылок на несуществующие admin-страницы ✅ |
| 49 | 🟢 | 6B | Encryption AES-256-GCM правильный паттерн ✅ |
| 50 | 🟢 | 6B | Snippets через `wp_kses` whitelist ✅ |
| 51 | 🟢 | 6B | 152-ФЗ согласие реально enforce ✅ |
| 52 | 🟢 | 6B | CRM-вызовы с `timeout=10`, sslverify не отключен ✅ |
| 53 | 🟢 | 6C | Migration markers идемпотентны, `escapeshellarg` правильно применён, PRG паттерн ✅ |

---

## Файлы без видимых вызовов

- **Скиллов всего:** 27 / без видимых вызовов: **0** / только в документации: 0
- **Агентов всего:** 32 / без видимых вызовов: **0** / только в документации: 0
- **Команд всего:** 32 (`.claude/commands/`) + 29 (`commands/`) / без видимых вызовов: **0** / расхождений между папками: **4**
- **Скриптов:** ~90 / без видимых вызовов: **2** (`refresh-catalog.py`, `migrate-blocks-to-wireframe-format.py`)
- **docs/standards:** 4 / только в документации: **2** (`stage-agent-preamble.md`, `stage-08-spec-lint.md`)

**Решения по каждому пункту — на согласование.** Подробности — `phase-1-dead-code.md`.

---

## Токены и циклы

- Файлов промптов всего: **92**
- Файлов в верхнем хвосте размера (>p90 = 102 строк): **9**
- Outlier'ов (>3× медианы = 141 строк): **7**
- Агентов с retry-логикой без явного `max_attempts`: **27 / 32**
- Главный критический loop: `/landing-go --auto-fix yes` без `max_attempts` (🔴)
- Wiki utilization: **480 файлов в wiki/**, **472 концепта с навигационным графом**, **0 агентов инструктированы по нему ходить**

Подробности — `phase-2-token-hotspots.md`.

---

## Целостность флоу (`/landing-go`)

- Этапов в pipeline (по `config/stage-gates.yaml`): **20**
- Из них с обнаруженным разрывом перехода: **1 критичный** (цикл deploy↔qa)
- Параллельных веток с риском пропуска: **2** (07d_photos, 07e_visuals — оба `lock: soft`)
- Verify-скриптов orphan: **1** (`verify-visual-qa.sh`)
- Migration-скриптов не упомянутых в CLAUDE.md: **5 из 7**
- TODO-маркеров в активных файлах: **4** (включая 1 в главной команде `landing-go`)

Состояние **10 заявлений CLAUDE.md проверено** — **5 расхождений** с реальным состоянием кода.

Подробности — `phase-3-flow-integrity.md`.

---

## UI completeness

- HTML-файлов проанализировано: **~554**
- Контролов без обработчика (HTML фронта): **не обнаружено явных** (block-library валидируется в pipeline)
- Команд без видимой реализации: **0**
- Команд отсутствующих в help'е: **17**
- Несуществующих команд упомянутых в help'е: **2** (`landing-redeploy`, `landing-update`)

Подробности — `phase-4-ui-completeness.md`, `phase-6a-ui-wiring.md`.

---

## Безопасность (mu-plugin)

- Критичных находок: **3** (🔴) — REST защита, XSS, Telegram token в URL
- Важных: **4** (🟠) — SQL prepare, SSRF, IP/UA анонимизация, encryption key rotation
- Стоит внимания: **3** (🟡) — N+1 switch_to_blog, email DoS, error_log audit
- Положительных: **7** (🟢) — encryption, kses, 152-ФЗ, sslverify, timeout, switch/restore, sanitize

**Самое серьёзное (одной строкой):** REST endpoint /lead не защищён от продвинутых ботов — целевая атака засорит CRM клиента.

Подробности — `phase-6b-security.md`.

---

## Покрытие зон проверкой

| Зона проекта | Какая фаза покрывает | Запущена? | Что не покрыто |
|---|---|---|---|
| Скиллы / агенты / команды (использование) | Фаза 1 | ✅ | — |
| Скиллы / агенты / команды (петли, токены) | Фаза 2 | ✅ | Detailed retry-аудит каждого из 27 агентов |
| Pipeline `/landing-go` (флоу) | Фаза 3 | ✅ | API-валидаторы (beget_ssh, yandex_metrika, telegram, amocrm, bitrix24) — реализация не проверена |
| HTML лендинга (фронт посетителя) | Фаза 4 | ✅ | 543 block-library HTML без HTML-валидации |
| CLI-команды | Фаза 4 | ✅ | — |
| Качество кода активных компонентов | Фаза 5 | ✅ | Idempotency каждой миграции, pylint/shellcheck |
| WP-админка: интерактивные элементы | Фаза 6A | ✅ | Глубокая проверка nonce-name соответствия (peредано в 6B) |
| WP-админка: безопасность | Фаза 6B | ✅ | Параллельный `/security-review` не запущен; глубокий разбор AmoCRM/HubSpot OAuth |
| WP-админка: связность путей маркетолога | Фаза 6C | ✅ | Real-world performance audit аудита, browser session testing |

**Все 9 зон проекта покрыты ревью. ✅**

---

## Сводная таблица для согласования

Используй эту таблицу как чек-лист: пройди по каждому пункту и пометь решение (✅ принять / ⏸ отложить / ❌ не делать / ❓ обсудить). После согласования эти пункты становятся отдельными задачами в плане доработок.

| # | Severity | Фаза | Краткое описание | Статус |
|---|---|---|---|---|
| 1 | 🔴 | 2 | Auto-fix loop без max_attempts | ☐ на согласовании |
| 2 | 🔴 | 3 | Цикл deploy↔qa | ☐ |
| 3 | 🔴 | 4 | landing-help устарел | ☐ |
| 4 | 🔴 | 5 | Wiki hard-coded `~/Lendings/` | ☐ |
| 5 | 🔴 | 5 | 18/34 bash без `set -e` | ☐ |
| 6 | 🔴 | 6B | REST endpoint слабая защита | ☐ |
| 7 | 🔴 | 6B | 20 XSS-векторов | ☐ |
| 8 | 🔴 | 6B | Telegram token в URL | ☐ |
| 9 | 🔴 | 6C | Adapter dispatch не подключён | ☐ |
| 10 | 🔴 | 6C | Нет cleanup при wpmu_delete_blog | ☐ |
| 11 | 🟠 | 2 | 27 агентов с retry без лимита | ☐ |
| 12 | 🟠 | 2 | Wiki без навигатора | ☐ |
| 13 | 🟠 | 3 | 07d/07e soft — можно пропустить | ☐ |
| 14 | 🟠 | 3 | TODO в landing-go (legacy_reason) | ☐ |
| 15 | 🟠 | 3 | verify-visual-qa.sh не привязан | ☐ |
| 16 | 🟠 | 3 | Дубль verify в 07c/07f | ☐ |
| 17 | 🟠 | 3 | 5 migrate-скриптов без доки | ☐ |
| 18 | 🟠 | 4 | help устаревшая категоризация | ☐ |
| 19 | 🟠 | 4 | Расхождение `.claude/commands/`↔`commands/` | ☐ |
| 20 | 🟠 | 5 | Migrations без marker idempotency | ☐ |
| 21 | 🟠 | 5 | Большие агенты смешивают слои | ☐ |
| 22 | 🟠 | 5 | Naming overlap в этапе 07 | ☐ |
| 23 | 🟠 | 6A | Inline onclick — CSP-issue | ☐ |
| 24 | 🟠 | 6A | 0 AJAX в админке | ☐ |
| 25 | 🟠 | 6A | Нет smoke-тестов admin-форм | ☐ |
| 26 | 🟠 | 6B | Raw SQL без prepare | ☐ |
| 27 | 🟠 | 6B | Bitrix24 SSRF risk | ☐ |
| 28 | 🟠 | 6B | IP/UA без анонимизации (РКН) | ☐ |
| 29 | 🟠 | 6B | Encryption key ротация | ☐ |
| 30 | 🟠 | 6C | Audit-runner синхронный | ☐ |
| 31 | 🟠 | 6C | Lead-detail без back-кнопки | ☐ |
| 32 | 🟠 | 6C | Cascade без integration-тестов | ☐ |
| 33 | 🟠 | 6C | Cookie-banner localStorage doc | ☐ |
| 34-46 | 🟡 | разные | Подробности в фазных отчётах | ☐ |
| 47-53 | 🟢 | разные | Положительные находки — действий не требуется | n/a |

---

## Общий вердикт (нейтрально, без призывов к действию)

Система **landing-system** — production-grade по архитектуре, с 27 скиллами, 32 агентами, 60+ командами в двух папках, mu-plugin'ом из 55 PHP-файлов и каталогом из ~270 блоков. Глубина инженерной работы заметна на каждом уровне: правильная encryption, корректное соблюдение 152-ФЗ согласия, идемпотентные миграции, многолетняя структура тестов (238 файлов), Bilingual Reporting Standard в документации.

При этом **6 критических дефектов и 23 важных** показывают что система находится на стадии «инфраструктура построена быстрее, чем подключение каждой части к pipeline». Самый яркий пример — **CRM adapter dispatch**: 6 адаптеров написаны, encryption ключей реализован, network admin UI готов, но **`add_action('landing_config_lead_received')` нигде не зарегистрирован** — поэтому ни одна заявка реально не доходит до CRM. Аналогичная картина: **wiki/ построена как навигационный граф из 472 концептов**, но **ни один агент не инструктирован по нему ходить** — граф есть, нога не подключена.

Список найденного — выше. Решения по приоритетам и срокам — за пользователем. Каждый пункт — на согласование, никаких действий код-ревьюером не выполнено.

---

## Глоссарий (мастер)

- *AJAX* — асинхронный запрос из браузера на сервер без перезагрузки страницы.
- *AES-256-GCM* — современный алгоритм шифрования с аутентификацией. Лучшая практика.
- *capability* — право пользователя в WP (`manage_options` есть только у админа).
- *cascade resolver* — функция, для blog_id возвращает либо site override либо network default.
- *CRM* — система учёта клиентов (AmoCRM, Bitrix24, HubSpot).
- *CSRF (cross-site request forgery)* — атака подложными запросами от лица залогиненного.
- *CSP (Content Security Policy)* — HTTP-заголовок, ограничивающий какой JS может выполняться.
- *DoS (denial of service)* — атака на отказ в обслуживании.
- *false positive* — файл ошибочно помечен как «неиспользуемый», хотя реально используется через скрытую ссылку.
- *GDPR* — европейский регламент защиты ПД.
- *honeypot* — скрытое поле формы; бот его заполнит, отсекаем.
- *идемпотентность* — повторный запуск даёт тот же результат. Критично для миграций.
- *mu-plugin* (must-use plugin) — WP-плагин, активирован принудительно, не отключается из админки.
- *multisite* — несколько WP-сайтов в одной инсталляции.
- *nonce* — одноразовый токен; WP добавляет в формы для защиты от CSRF.
- *N+1 query* — паттерн «один запрос в loop'е для каждой записи» вместо одного агрегирующего.
- *orphan-файл* — файл без входящих ссылок.
- *outlier* — экстремальное значение, далеко выпадающее из общего распределения.
- *перцентиль (pN)* — отметка, ниже которой остаются N% значений.
- *PoC (proof of concept)* — минимальная демонстрация уязвимости.
- *POST-Redirect-GET (PRG)* — паттерн против re-submit формы при F5.
- *REST endpoint* — URL, по которому браузер/сервер обращается за данными.
- *rate-limit* — ограничение числа запросов с одного IP.
- *SQL injection* — внедрение SQL в запрос через user-input.
- *SSRF (server-side request forgery)* — атакующий заставляет сервер обратиться по своему URL.
- *subsite* — отдельный сайт в multisite (для нас: один сегмент ЦА).
- *switch_to_blog / restore_current_blog* — WP-функции переключения контекста в multisite. Парные.
- *TDD (Test-Driven Development)* — практика «сначала тест, потом код».
- *wikilinks* (`[[concept]]`) — формат навигационных ссылок (Obsidian/Roam).
- *wp_kses* — WP-функция очистки HTML с whitelist разрешённых тегов.
- *XSS (cross-site scripting)* — внедрение JS в страницу; украдёт сессию у жертвы.
- *152-ФЗ* — российский закон о ПД. Нарушение — штраф РКН.

---

## Все артефакты ревью

В папке `docs/code-review/`:

| Файл | Описание |
|---|---|
| `2026-05-23-review-plan.md` | Playbook ревью (исходный документ) |
| `phase-0-reference-map.json` | Карта ссылок (машиночитаемый, 9.4 MB) |
| `phase-0-reference-map.md` | Карта ссылок (human-readable, 1588 строк) |
| `phase-0-reference-map-fixed.json` | Re-классификация 309 doc-only с учётом dynamic includes |
| `phase-0-suspicious-duplicates.md` | 439 пар файлов с пересечениями токенов |
| `phase-1-dead-code.md` | Инвентаризация неиспользуемых файлов |
| `phase-2-token-hotspots.md` | Раздутые промпты, циклы, wiki-utilization, heavy operations |
| `phase-3-flow-integrity.md` | Целостность pipeline, stage-gates, расхождения CLAUDE.md ↔ код |
| `phase-4-ui-completeness.md` | HTML фронта и CLI-команды |
| `phase-5-correctness.md` | Качество кода активных компонентов |
| `phase-6a-ui-wiring.md` | WP-admin: контролы, формы, ссылки |
| `phase-6b-security.md` | WP-admin: capability, nonce, XSS, SQLi, encryption, 152-ФЗ |
| `phase-6c-admin-flow.md` | WP-admin: end-to-end сценарии маркетолога |
| **`SUMMARY.md`** | **Этот файл** |

**Все отчёты написаны на русском по Bilingual Reporting Standard playbook'а.** Каждый finding содержит: что это значит простыми словами / чем грозит бизнесу / оценка срочности / статус «☐ на согласовании» / технические детали с file:line / возможные пути решения (как опции, без рекомендации к действию).
