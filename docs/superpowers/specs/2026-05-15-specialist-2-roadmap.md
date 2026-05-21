# Roadmap — Специалист 2 (WordPress / админка / интеграции / аудит)

**Дата:** 2026-05-15
**Источник:** [docs/planning/2026-05-15-plan-dorabotok.md](../../planning/2026-05-15-plan-dorabotok.md) (Кирилл + Валерия)
**Owner:** Спец 2

Документ-каркас: разделяет всю часть Спеца 2 из ПЛАН-ДОРАБОТОК.md на 5 под-проектов. Каждый под-проект получает свой spec → plan → implementation цикл.

---

## Сводка под-проектов

> **Изменение порядка от 2026-05-15:** по решению юзера S2-CD (multisite + клонирование) делается **первым**, потому что архитектурно перестраивать single-site код под multisite потом дороже, чем сразу проектировать с учётом multisite. Спеки S2-A и S2-E помечены `pending-revision` — после approval S2-CD их надо пересмотреть (network-activated mu-plugin, audit-batch по поддоменам).

| ID | Название | Покрывает пункты ПЛАН-ДОРАБОТОК | Приоритет | Зависимости |
|---|---|---|---|---|
| **S2-CD** | Multisite + Segment Cloning (объединённый) | п.6 Клонирование, п.7 Поддомены/мультисайт | **P0 — СЕЙЧАС, фундамент** | Stage-08 Lazy Blocks миграция должна работать |
| **S2-A** | Pre-deploy & Admin Config (mu-plugin `landing-config`) | п.1 Интеграции, п.2 Head/SEO, п.3 Маршрутизация заявок, п.4 CTA-routing | P0 — после S2-CD | `pending-revision`: переписать под network mode |
| **S2-E** | SEO / Tech / Vitals Audit Skill (`/landing-audit`) | п.6 спеца 1 «финальная авто-проверка» + новое | P0 — параллельно с S2-A | `pending-revision`: batch-mode по всем поддоменам сайта |
| **S2-B** | Block Editability Levels (editable / semi-editable / hardcoded) | п.5 | P1 | После S2-A |

**Out of scope текущей итерации (P2):** п.8 SEO для многостраничных, п.9 маркетинговые сценарии.

## Почему S2-CD сначала

1. **mu-plugin `landing-config`** (S2-A) кардинально по-разному устроен в single vs network mode:
   - single: `wp_options` per-site
   - network: `wp_sitemeta` (общие) + `wp_options` (per-site override)
   - Переписать после = почти полная рерайт.
2. **CTA-пресеты, head/SEO**: в multisite клиент хочет общие пресеты на network уровне + override на конкретный поддомен. Это решение влияет на схему `landing-config.yaml` и UI.
3. **`/landing-audit`** должен уметь `--batch` по всем поддоменам мультисайта одной командой (требование из п.6 ПЛАН-ДОРАБОТОК: «после деплоя — авто-проверка всего сайта»). Single-site audit реализовать тривиально, но потом расширять до batch — пересмотр output формата.
4. **Клонирование** (`/landing-clone`) — в single mode это копия всего инстанса (rsync + db dump), в network — добавление сайта в существующую сетку (`wp site create`). Подход разный, и S2-CD выбирает который мы используем.

---

## Lazy Blocks Safety Gate (обязательно для всех под-проектов)

Stage-08 находится в активной миграции с ACF Blocks на Lazy Blocks Free (см. [план миграции](../plans/2026-05-13-stage08-lazy-blocks-migration.md)). Любой под-проект Спеца 2, который трогает:

- `block-spec.yaml` схему
- генераторы `generate-lzb-*.py`
- `block.php` шаблоны
- `mu-plugins/` или `wp-content/themes/`

— **обязан** прогонять `tests/integration/test_lazy_blocks_smoke.sh` **после каждого Task** в плане. Если smoke красный — следующий Task не стартует.

**Что проверяет smoke (см. S2-A спек, секция Testing):**

1. Генераторы stage-08 отрабатывают на фикстуре без ошибок.
2. wp-env поднимается с темой + Lazy Blocks плагином.
3. `wp post create` для front-page возвращает ID.
4. `curl /` → HTTP 200.
5. HTML содержит ≥1 класс `lazyblock-`.
6. PHP error.log пустой за последние 30 секунд.
7. `landing_get_cta('primary')` (после внедрения S2-A) возвращает не пустую строку.
8. Custom-table `wp_landing_leads` существует.

Скрипт принимает `--project <slug>` для регрессии на реальном проекте (по умолчанию `dubai-avto-liza` согласно CLAUDE.md).

---

## S2-A — Pre-deploy & Admin Config

См. [полный спек](2026-05-15-s2a-pre-deploy-admin-config-design.md).

**Что закрывает из ПЛАН-ДОРАБОТОК:**

- **п.1 Интерфейс интеграций** — admin-страница «Интеграции» с подключением AmoCRM / Bitrix24 / HubSpot / Telegram / WhatsApp / Email через WP Settings API. Кнопка «Test connection» у каждого ключа.
- **п.2 Head / SEO без программиста** — admin-страница со структурированными полями (GA4 ID, Yandex.Metrika, FB Pixel, GSC verification, OG image/title/desc, favicon upload, Google Fonts URL) + raw-textarea с `wp_kses` whitelist.
- **п.3 Маршрутизация заявок** — единый REST `/wp-json/landing/v1/lead`, custom-table `wp_landing_leads` (заявки никогда не теряются), email-fallback, async-retry упавших доставок CRM через `wp_schedule_single_event`.
- **п.4 CTA-routing** — 5 глобальных пресетов (`primary`, `whatsapp`, `phone`, `form_modal`, `learn_more`) + per-block override через `cta_slot` в `block-spec.yaml`. Helper `landing_get_cta()` в темах.

**Артефакт:** must-use plugin `landing-config.php` в `08_КОД/wp-theme/mu-plugins/landing-config/`, генерируется на stage-08 новым скиллом `wp-landing-config`, копируется деплоем в `/wp-content/mu-plugins/`.

---

## S2-E — SEO / Tech / Vitals Audit Skill

См. [полный спек](2026-05-15-s2e-seo-tech-audit-design.md).

**Что закрывает:**

- п.6 спеца 1 (автопроверка сайта) — становится **общим гейтом stage-11** для всех проектов.
- Дополнительно: каталогизированный набор из ~65 проверок, эквивалентный 80-метровому отчёту pr-cy (без платных backlinks/SERP-данных).

**Артефакт:** скилл `seo-tech-audit` + slash-команда `/landing-audit [<slug>|<url>] [--batch <file>]`. Выход — `11_QA/audit-report.{json,md,html}`.

**Гейт:** при `hard_gate fail` оркестратор предлагает auto-fix (добавить H1, заполнить OG, обновить SSL) и блокирует «approval» stage-11 до зелёного отчёта.

---

## S2-B — Block Editability Levels

**Что закрывает:** п.5 ПЛАН-ДОРАБОТОК.

**Идея:** расширить `block-spec.yaml` полем `editability: editable | semi | hardcoded` на уровне блока И на уровне отдельного control. Генератор `generate-lzb-templates.py`:

- `editable` — Lazy Blocks control видим в редакторе, value пишется в Гутенберг.
- `semi` — control видим, но с warning-баннером «Сложная композиция, осторожно».
- `hardcoded` — control скрыт от UI, значение зашито в template (берётся из `block-spec.yaml`).

**Lazy Blocks safety:** обязательный smoke-gate (см. выше) после каждого Task. Особое внимание на то, что `hardcoded` блок всё равно валидно рендерится в редакторе (placeholder с warning, не fatal).

---

## S2-CD — Multisite + Segment Cloning (объединённый, **СПЕК ГОТОВ**)

**Что закрывает:** п.6 (клонирование) + п.7 (поддомены/мультисайт).

**Спек:** [2026-05-18-s2cd-multisite-cloning-design.md](2026-05-18-s2cd-multisite-cloning-design.md) — POC-validated, готов к writing-plans.

**Архитектура (validated на боевом Beget shared 2026-05-18):**
- WordPress Multisite в subdomain mode на одном Beget-аккаунте
- Один корневой домен клиента (`liauto.dubai`) + поддомены сегментов
- Lazy Blocks через network-shared mu-plugin (один файл = блоки на всех subsites)
- SEO/AI через 5 mu-plugins (robots, schema, llms, gsc, blocks) — все per-site без cross-leak
- Клонирование через `wp site create` + content copy
- SSL — manual one-click через панель Beget (бесплатный wildcard Let's Encrypt, авто-renew). Скрейп — следующая итерация.

**POC results:** 10/11 GREEN (1 косметический). Все архитектурные риски закрыты. См. [tests/poc/RESULTS.md](../../../tests/poc/RESULTS.md) и [docs/beget-cookbook.md](../../beget-cookbook.md).

**Фазы имплементации (CD1-CD6):** см. §9 спека.

---

## Порядок реализации (обновлён 2026-05-15)

```
1. S2-CD (брейншторм → спек → план → имплементация по фазам)
       │
       ▼
2. Ревизия S2-A spec под multisite-aware (network-activated mu-plugin)
       │
       ├─► 3a. S2-A имплементация (по фазам, см. §«Фазы S2-A» ниже)
       │
       └─► 3b. S2-E имплементация (параллельно, с batch-mode по поддоменам)
                       │
                       ▼
                  4. S2-B имплементация
```

**Каждая фаза = отдельный план + отдельный PR в feature branch (worktree) + smoke-gate прогон на `dubai-avto-liza`.**

### Фазы S2-A (после revision)

| Фаза | Содержимое | Зачем сначала |
|---|---|---|
| A1 | Scaffolding + activation hook + `wp_landing_leads` + REST `/lead` + email-fallback | Заявки перестают теряться |
| A2 | Admin UI «Заявки» (список + экспорт CSV, multisite-aware фильтр) | Маркетолог видит лиды без SSH |
| A3 | CTA-пресеты + `cta_slot` в `block-spec.yaml` + helper | Закрывает п.4 ПЛАН-ДОРАБОТОК |
| A4 | Head & SEO админка + wp_kses фильтр | Закрывает п.2 ПЛАН-ДОРАБОТОК |
| A5 | 6 адаптеров + Test-connection + async-retry + шифрование ключей | Закрывает п.1 ПЛАН-ДОРАБОТОК |

### Фазы S2-E (после revision)

| Фаза | Содержимое |
|---|---|
| E1 | `run-audit.py` скелет + `html_checks.py` + `network_checks.py` + Markdown report |
| E2 | `vitals.py` (lighthouse) + `schema_checks.py` |
| E3 | `content_metrics.py` (тошнота/вода/Flesch RU) + `crawler.py` |
| E4 | `ai_readiness.py` + `external_apis.py` (opt-in) + multisite batch mode + интеграция в orchestrator stage-11 |

---

Каждый под-проект завершается merge в `main` + регрессионный прогон `test_lazy_blocks_smoke.sh` + `test_mu_plugin_smoke.sh` на `dubai-avto-liza` (требование CLAUDE.md).
