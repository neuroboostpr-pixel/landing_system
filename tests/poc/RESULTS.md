# POC Gauntlet — Final Results

**Date:** 2026-05-18
**Test domain:** ailexi.ru (Beget shared, plan "Blog")
**Run by:** Claude Code
**Architecture validated:** WP Multisite (subdomain mode) + Lazy Blocks + RankMath + SEO/AI mu-plugins

## Summary

| # | Test | Result | Note |
|---|------|--------|------|
| 00 | setup-multisite | 🟢 GREEN | wildcard DNS + WP install + 2 subsites + plugins + theme |
| 01 | lazy-blocks-network | 🟢 GREEN | Lazy Block via mu-plugin registers on all 3 subsites |
| 02 | lazy-blocks-render | 🟢 GREEN | Frontend HTML per-subsite, correct headline per host |
| 03 | sitemap-per-site | 🟢 GREEN | /wp-sitemap.xml independent per subsite |
| 04 | robots-per-site | 🟢 GREEN | AI bot allow-list + correct host identification (no leak) |
| 05 | rank-math-network | 🟢 GREEN | Per-site titles + no cache leak |
| 06 | schema-org-faq | 🟢 GREEN | Organization + FAQPage JSON-LD per-host |
| 07 | llms-txt-rewrite | 🟡 RED (cosmetic) | Body+host correct; Content-Type is text/html instead of text/plain |
| 08 | search-console-meta | 🟢 GREEN | GSC verification per-blog (no cross-leak) |
| 09 | ai-bot-fetches | 🔴 RED (BEGET WAF) | **Beget blocks GPTBot/ClaudeBot with 503; PerplexityBot passes** |
| 10 | clone-subsite | 🟢 GREEN | `wp site create` + content copy works end-to-end |

**9 GREEN / 2 RED / 11 total**

Both REDs have known root causes (not architectural):
- **07:** WP template loader overrides Content-Type. Fix via `.htaccess` direct rewrite or sending headers earlier in the request lifecycle.
- **09:** Beget's WAF/DDoS-Guard blocks OpenAI/Anthropic crawlers at the edge. **This is a hosting-level issue, not WP-side.** Mitigation options for prod:
  - Open Beget support ticket to whitelist GPTBot/ClaudeBot UAs
  - Use Cloudflare as proxy (allows fine-grained bot management)
  - Document that AI-search visibility requires hosting tier upgrade or proxy

## Critical findings (architectural)

### ✅ WP Multisite на Beget shared РАБОТАЕТ полностью

1. Beget API позволяет создать wildcard DNS (`*.<root>`) одним вызовом `domain/addSubdomainVirtual` с `subdomain="*"`.
2. Любой поддомен резолвится автоматически через wildcard.
3. Beget НЕ создаёт отдельных public_html для subdomains — все запросы идут в один WP install.
4. После `site/linkDomain` для каждого FQDN nginx роутит правильно.
5. PHP 8.3 ставится через `domain/changePhpVersion` (full_fqdn).
6. WP `core multisite-install` отрабатывает на Beget shared без проблем.

### ✅ Lazy Blocks через mu-plugin РАБОТАЕТ на multisite

**Главный риск S2-CD закрыт.** Один файл `wp-content/mu-plugins/landing-blocks.php` регистрирует блок на ВСЕХ subsites одновременно. Frontend рендер работает корректно с per-page параметрами (headline).

Жёсткие требования (без них тихо НЕ работает):
1. Slug `lazyblock/<name>` (Lazy Blocks хардкодит namespace).
2. `add_action('init', ..., 5)` — priority < 20.
3. Render через `code.frontend_callback` в массиве блока.
4. `code.output_method = 'php'`.

### ✅ SEO и AI-готовность с дня 1

Per-site sitemaps, robots.txt с AI bot allow-list, Schema.org JSON-LD, GSC verification — всё работает без cross-site leak. RankMath SEO 1.0.270 поддерживает multisite из коробки.

### ⚠️ SSL — не покрывается Beget API

Wildcard SSL через Beget API недоступен. Решение для прода: ручной выпуск Let's Encrypt per-subsite через панель Бегета, либо Cloudflare как DNS+SSL прокси.

### 🔴 Beget блокирует GPTBot/ClaudeBot UAs

**Это серьёзная проблема для AI-видимости.** Без её решения сайт **невидим для ChatGPT и Claude**. Решения:
1. Запрос на whitelist в Beget support (1-2 дня).
2. Cloudflare proxy + bot management.
3. Документирование как known limitation.

## Что POC закрыл для S2-CD

| Question | Answered? | How |
|---|---|---|
| Можно ли поднять WP Multisite на Beget shared? | ✅ YES | Test 00 + 01 |
| Работает ли Lazy Blocks с network-shared definitions? | ✅ YES | Test 01 + 02 |
| Можно ли через mu-plugin делать SEO/AI customizations? | ✅ YES | Tests 04, 06, 08 |
| Не утекает ли контент между subsites (cache leak)? | ✅ NO LEAKS | Tests 03, 04, 05, 06, 08 |
| Работает ли клонирование? | ✅ YES | Test 10 |
| Видят ли AI боты SSR контент? | 🟡 PARTIAL | Test 09 (Beget WAF blocks 2/3 bots) |
| Wildcard SSL автоматизирован? | ❌ NO | Manual workaround required |

## Что артефакты остались на Beget после POC

- WP Multisite installation на `ailexi.ru` + subsites `alpha.ailexi.ru`, `bravo.ailexi.ru`, `clone.ailexi.ru`
- DB `esper21_poc` (~5 MB)
- 5 mu-plugins в `wp-content/mu-plugins/`: poc-block.php, poc-robots.php, poc-schema.php, poc-llms.php, poc-gsc.php
- Backup старого ailexi.ru WP в `~/poc-backup/` (1.6 MB SQL + 96 MB uploads tar.gz)

Очистка: запуск `tests/poc/teardown.sh` (TODO написать) или ручной снос через панель Бегета + `wp db reset`.

## Recommended next steps

1. **Принять S2-CD spec** (готов на 2026-05-18) — главные риски закрыты.
2. **Решить вопрос с GPTBot/ClaudeBot** до начала разработки (S2-CD.5 SSL фаза может быть совмещена с Cloudflare proxy).
3. **Запустить writing-plans** для фазы CD1 (migrate-to-multisite + landing-segment команда).
