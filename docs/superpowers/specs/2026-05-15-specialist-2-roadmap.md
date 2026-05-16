# Roadmap — Специалист 2 (WordPress / админка / интеграции / аудит)

**Дата:** 2026-05-15
**Источник:** [docs/planning/2026-05-15-plan-dorabotok.md](../../planning/2026-05-15-plan-dorabotok.md) (Кирилл + Валерия)
**Owner:** Спец 2

Документ-каркас: разделяет всю часть Спеца 2 из ПЛАН-ДОРАБОТОК.md на 5 под-проектов. Каждый под-проект получает свой spec → plan → implementation цикл.

---

## Сводка под-проектов

| ID | Название | Покрывает пункты ПЛАН-ДОРАБОТОК | Приоритет | Зависимости |
|---|---|---|---|---|
| **S2-A** | Pre-deploy & Admin Config (mu-plugin `landing-config`) | п.1 Интеграции, п.2 Head/SEO, п.3 Маршрутизация заявок, п.4 CTA-routing | **P0 — сейчас** | Stage-08 Lazy Blocks миграция должна работать |
| **S2-E** | SEO / Tech / Vitals Audit Skill (`/landing-audit`) | п.6 спеца 1 «финальная авто-проверка» + новое (вне исходного плана) | **P0 — сейчас, параллельно с S2-A** | Только задеплоенный URL |
| **S2-B** | Block Editability Levels (editable / semi-editable / hardcoded) | п.5 | P1 | После S2-A (использует `landing-config.yaml` схему) |
| **S2-C** | Segment Cloning v2 | п.6 | P1 | После S2-A (нужны конфиги для копирования) |
| **S2-D** | WordPress Multisite + Subdomains | п.7 | P1 | После S2-C |

**Out of scope текущей итерации (P2):** п.8 SEO для многостраничных, п.9 маркетинговые сценарии.

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

## S2-C — Segment Cloning v2

**Что закрывает:** п.6 ПЛАН-ДОРАБОТОК.

**Идея:** доработать существующий `/landing-clone` (`skills/landing-versioning-and-cloning`):

- При клонировании копируется не только wp-theme и контент, но и `landing-config.yaml` (из S2-A).
- Появляется wizard «Какой сегмент?» — меняет текст / фото / цены / WhatsApp-номер.
- Дизайн, структура, технические блоки (`hardcoded` из S2-B) — НЕ меняются.

**Требует:** готовые S2-A (для копирования настроек) и S2-B (для понимания что трогать нельзя).

---

## S2-D — WordPress Multisite + Subdomains

**Что закрывает:** п.7 ПЛАН-ДОРАБОТОК.

**Идея:** один главный домен (`liauto.dubai`) + поддомены (`russian.liauto.dubai`, ...) на WP Multisite. Деплой переключается с single-site режима на multisite-aware. Один wp-admin для всех. mu-plugin `landing-config` из S2-A работает как **network-activated** — настройки шарятся между сайтами с возможностью override на уровне поддомена.

**Требует:** S2-C (без клонирования multisite не нужен).

---

## Порядок реализации

```
Сейчас (параллельно):
  ├─ S2-A (полный спек готов)
  └─ S2-E (полный спек готов)

После approval S2-A:
  └─ S2-B (требует landing-config.yaml схему из S2-A)

После approval S2-B:
  └─ S2-C

После approval S2-C:
  └─ S2-D
```

Каждый под-проект завершается merge в `main` + регрессионный прогон `test_lazy_blocks_smoke.sh` + `test_mu_plugin_smoke.sh` на `dubai-avto-liza` (требование CLAUDE.md).
