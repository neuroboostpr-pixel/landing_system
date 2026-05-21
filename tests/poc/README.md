# POC Gauntlet: WordPress Multisite + Lazy Blocks + SEO/AI on Beget

**Цель:** до начала любой имплементации S2-CD доказать, что выбранная архитектура
(WP Multisite в subdomain mode + Lazy Blocks + SEO/AI готовность) реально работает
на боевом окружении (Beget shared hosting).

**Тестовый домен:** `ailexi.online` (предоставлен пользователем, на нём ничего
важного нет, можно «топтать»).

**Принцип:** каждый из 10 тестов отвечает на один конкретный вопрос. Если ответ ✅ —
тест зелёный. Если ❌ — гонщик останавливается, мы либо чиним архитектуру,
либо ищем обходной путь, либо меняем выбор.

## Запуск

```bash
# Все переменные окружения уже зашиты в lib/env.sh
cd tests/poc
bash run-all.sh        # последовательно все 10 тестов
bash teardown.sh       # снести всё созданное (WP, БД, DNS, SSL)
```

Каждый отдельный тест можно гонять изолированно:

```bash
bash scripts/01-lazy-blocks-network.sh
```

## Структура

| Файл | Что проверяет | Hard gate? |
|------|---------------|------------|
| `00-setup-multisite.sh` | WP установлен, multisite (subdomain) активирован, 2 subsite созданы | ✅ блокирующий — без этого тесты 01-10 не запускаются |
| `01-lazy-blocks-network.sh` | Lazy Blocks Free активирован network-wide, тестовый блок зарегистрирован через `functions.php`, виден в Gutenberg на обоих subsite | ✅ |
| `02-lazy-blocks-render.sh` | На каждом subsite страница с блоком рендерится на фронте, HTML содержит `lazyblock-*` маркер | ✅ |
| `03-sitemap-per-site.sh` | `/wp-sitemap.xml` на каждом subsite — валидный XML, содержит свои URL и не содержит URL других subsite | ✅ |
| `04-robots-per-site.sh` | `/robots.txt` per-subsite, AI-боты (GPTBot, ClaudeBot, PerplexityBot) явно разрешены через mu-plugin | ✅ |
| `05-rank-math-network.sh` | RankMath Free network-активирован, per-site настройки независимы | ✅ |
| `06-schema-org-faq.sh` | FAQPage Schema.org через RankMath на subsite → JSON-LD виден в HTML | ✅ |
| `07-llms-txt-rewrite.sh` | Свой mu-plugin отдаёт `/llms.txt` per-subsite с правильным контентом | ✅ |
| `08-search-console-meta.sh` | mu-plugin отдаёт разные verification meta-tags на разных subsite (нет кросс-сайт-утечки) | ✅ |
| `09-ai-bot-fetches.sh` | `curl --user-agent "GPTBot" /` отдаёт server-rendered HTML с контентом блока | ✅ |
| `10-clone-subsite.sh` | `wp site create` создаёт новый subsite + копирование контента работает | ✅ |

## Lib

- `lib/env.sh` — все переменные (логины, домен, пути)
- `lib/beget-api.sh` — обёртка для https://api.beget.com (DNS, subdomain, SSL, MySQL)
- `lib/ssh.sh` — обёртка для SSH/SCP на esper21.beget.tech
- `lib/assert.sh` — общие assertion-функции (assert_status_2xx, assert_contains и т.д.)

## Артефакты

После прогона:
- `tests/poc/results.md` — отчёт human-readable
- `tests/poc/results.json` — машино-читаемый
- `tests/poc/logs/<NN-test-name>.log` — полный вывод каждого теста
