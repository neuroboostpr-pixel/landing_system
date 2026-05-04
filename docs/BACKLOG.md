# Landing System — Backlog

Отложенные задачи поверх MVP (stage-gates + onboarding). Каждый пункт — отдельный spec → plan → реализация.

**Контекст:** базовый MVP описан в [`specs/2026-05-04-stage-gates-onboarding-mcp-design.md`](superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md), реализован в коммитах `444b40d..0746ef4`.

---

## Как взять задачу в работу

Внутри Claude Code в этом репо:

```
/brainstorming Уточни scope задачи "<название из списка ниже>"
```

После brainstorm Claude напишет spec в `docs/superpowers/specs/`, затем:
```
/writing-plans
/executing-plans   # или /subagent-driven-development
```

Пример: `/brainstorming Добавить GTM-вставку в analytics-engineer + поддержать DENY/ALLOW режим cookie-баннера`.

---

## Приоритет 1 — функциональные дыры (блокирует прод-запуск)

### B1. Cookie-баннер + 152-ФЗ блок согласия на обработку ПД
- **Зачем:** обязательно для запуска в РФ. Без этого сайт нарушает закон.
- **Что добавить:**
  - `template/08_КОД/template-parts/legal-block.php` — компонент под формами
  - `template/08_КОД/template-parts/cookie-banner.php` + JS (без плагина)
  - `template/08_КОД/legal-pages/policy.html` + `consent.html` — страницы политики и согласия
  - Расширить `agents/wp-builder.md` — вставлять legal-block во все формы
  - Soft-check `legal_blocks_present` в `config/stage-gates.yaml` уже есть — связать с реальной проверкой
- **Размер:** ~200 SLOC. 1–2 дня.

### B2. GTM-вставка в `analytics-engineer`
- **Зачем:** `GTM_CONTAINER_ID` уже в `.env.example`, но никто его не использует.
- **Что добавить:** в `agents/analytics-engineer.md` — PHP-сниппет вставки GTM в `functions.php` рядом с Метрикой (читать `getenv('GTM_CONTAINER_ID')`, без `<noscript>` если cookie-баннер не дал согласия).
- **Размер:** ~30 SLOC. 2–3 часа.

### B3. Бэкап `wp db export` до деплоя в prod
- **Зачем:** сейчас деплой rsync'ит без отката.
- **Что добавить:** в `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — перед `rsync` запустить `ssh ... "wp db export /tmp/backup-<ts>.sql"`, скачать локально в `09_ДЕПЛОЙ/backups/`.
- **Размер:** ~20 SLOC. 1 час.

### B4. Sitemap.xml в `seo-optimizer`
- **Зачем:** без sitemap.xml поисковики хуже индексируют.
- **Что добавить:** в `agents/seo-optimizer.md` — генерация статичного `sitemap.xml` (главная + legal-страницы), либо подключение Rank Math плагина.
- **Размер:** ~40 SLOC. 2 часа.

---

## Приоритет 2 — расширение и удобство

### B5. Автоустановка WP-плагинов при деплое
- **Зачем:** сейчас плагины ставятся вручную.
- **Что добавить:** в `deploy-wordpress.sh` — после rsync читать `06_СТЕК/design-stack.yaml`, выполнить `wp plugin install <list> --activate`. Дефолтный список: WP Rocket / LiteSpeed Cache, ShortPixel, Wordfence, UpdraftPlus, Limit Login Attempts, Redirection, Really Simple SSL.
- **Размер:** ~50 SLOC. 3 часа.

### B6. fallback photo-stylist (промпты для ChatGPT)
- **Зачем:** если у пользователя нет `HUGGINGFACE_TOKEN`, photo-stylist должен выдавать готовые промпты для ручной обработки клиентских фото в ChatGPT/Шедеврум.
- **Что добавить:** в `agents/photo-stylist.md` — если HF API не настроен, генерировать `02_МАТЕРИАЛЫ_КЛИЕНТА/photo-prompts.md` с одним промптом на каждую нужную картинку (привязка к brand-style из `04_БРЕНД/brand-kit.md`).
- **Размер:** ~80 SLOC. 1 день.

### B7. Soft-check фото-стиля в `client-assets-collector`
- **Зачем:** soft_check `photo_style_consistency` в gate-check.yaml уже есть как prompt, но агент пока спрашивает «вручную». Добавить автоматическую оценку.
- **Что добавить:** в `agents/client-assets-collector.md` — анализ фото из `02_МАТЕРИАЛЫ_КЛИЕНТА/` через Pillow (палитра, контраст, ориентация), вывод в `02_МАТЕРИАЛЫ_КЛИЕНТА/style-report.md` с рекомендацией «однородный / нужна обработка / каких не хватает».
- **Размер:** ~120 SLOC. 1 день.

### B8. migration-engineer (301-редиректы при переносе сайта)
- **Зачем:** при переносе со старого сайта нужны 301 со старых URL.
- **Что добавить:**
  - `agents/migration-engineer.md` — собирает старые URL у пользователя, генерирует `09_ДЕПЛОЙ/redirects.csv`
  - Активация плагина Redirection при деплое + импорт CSV через wp-cli
- **Размер:** ~150 SLOC. 1–2 дня.

---

## Приоритет 3 — большие фичи (своё подплечо)

### B9. Multilang (i18n-engineer + Polylang)
- **Зачем:** для клиентов с международной аудиторией.
- **Что добавить:**
  - `agents/i18n-engineer.md` — активируется флагом `multilang: true` в `00_БРИФ/brief.md`
  - Установка Polylang (free) при деплое
  - Языковые версии каждого блока в `07_КОНТЕНТ/`
  - Переключатель языка в шапке темы
- **Размер:** ~300 SLOC. 3–4 дня.

### B10. Staging-окружение
- **Зачем:** деплой сразу в prod рискованно.
- **Что добавить:**
  - `scripts/deploy.sh --env staging|prod` (флаг с дефолтом `staging`)
  - `template/09_ДЕПЛОЙ/deploy-targets.yaml` — параметры staging-домена и prod-домена
  - Для prod: обязательное подтверждение `--confirm` + бэкап БД
- **Размер:** ~100 SLOC. 1 день.

### B11. WP-CLI MCP-сервер
- **Зачем:** удалённое управление WP без ручного `ssh+wp` в каждой команде. Облегчает работу другим агентам.
- **Что добавить:**
  - `mcp/wp-cli-mcp/` (Node.js) с инструментами: `wp_plugin_install`, `wp_plugin_list`, `wp_theme_activate`, `wp_acf_import`, `wp_db_export`, `wp_cache_flush`
  - Регистрация в `.claude/settings.json`
  - Замена ручных `ssh+wp` в `wp-cli-deployer` на MCP-вызовы
- **Размер:** ~400 SLOC + тесты. 3–5 дней.

### B12. DNS MCP-серверы (Beget / Cloudflare / Reg.ru)
- **Зачем:** автоматическая привязка домена при деплое.
- **Что добавить:**
  - `mcp/beget-dns-mcp/`, `mcp/cloudflare-dns-mcp/`, `mcp/regru-dns-mcp/`
  - Каждый: `dns_list_records`, `dns_create_a_record`, `dns_create_cname`, `dns_delete_record`
  - Интеграция в `wp-deployer` — при деплое создавать A-запись на IP сервера
- **Размер:** 3 × ~250 SLOC. 1 неделя.

---

## Приоритет 4 — техдолг и устойчивость

### B13. Concurrency-safe `gate-state.sh` через `flock`
- **Проблема:** если две команды одновременно пишут в `.landing-state.yaml`, одно изменение теряется.
- **Что добавить:** обернуть `yq -i` в `flock "$state_file.lock"` + валидация YAML до записи.
- **Размер:** ~20 SLOC. 1 час.

### B14. Single-registry в `aggregate.py`
- **Проблема:** есть `ALL` и `_MODULES` параллельно — добавление 16-го валидатора требует правки в двух местах.
- **Что добавить:** убрать `ALL`, использовать только `_MODULES[name].validate()`.
- **Размер:** ~10 SLOC. 30 минут.

### B15. `pyproject.toml` с `pythonpath = .`
- **Проблема:** надо запускать `PYTHONPATH=. pytest`, а не просто `pytest`.
- **Что добавить:** `pyproject.toml` с `[tool.pytest.ini_options] pythonpath = ["."]`.
- **Размер:** 5 строк. 10 минут.

### B16. Кеш результатов validate-all в wizard.sh
- **Проблема:** `wizard.sh` вызывает `validate-all.sh` дважды, бьёт API дважды.
- **Что добавить:** сохранять результат первого вызова в переменную, выводить и переиспользовать.
- **Размер:** ~10 SLOC. 30 минут.

---

## Прогресс

- ✅ MVP (stage-gates + onboarding) — реализован
- ⏳ B1–B4 — рекомендую брать в первую очередь
- 🔮 B5–B16 — по мере роста системы

Если вопросы по конкретной задаче — спроси через `/brainstorming <id>` (например `/brainstorming B6`).
