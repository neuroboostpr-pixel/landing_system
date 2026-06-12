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

## 🟢 RESOLVED — Content Extraction from Prototype (2026-06-01)

### BUG-001: Agent 07_content не парсит реальный прототип ✅ FIXED
**Статус:** ✅ RESOLVED (2026-06-01)  
**Дата открытия:** 2026-06-01  
**Дата закрытия:** 2026-06-01  

**Проблема (была):**
Этап 07_content заполнял content.md шаблонными текстами вместо того, чтобы извлечь реальные тексты из 07_ПРОТОТИП/source/prototype.{docx,pdf,md}.

**Решение:**
- ✅ **Spec:** [`specs/2026-06-01-content-extraction-spec.md`](superpowers/specs/2026-06-01-content-extraction-spec.md)
- ✅ **Plan:** текстовый план выше (фазы 1–6)
- ✅ **Implementation:**
  - Обновлен агент `agents/content-writer.md` — новый Algorithm для extraction из prototype.yaml
  - Добавлены hard-checks в `config/stage-gates.yaml::07_content`:
    - `content_md_exists` — проверка что content.md создан
    - `content_no_lorem` — валидация что нет Lorem ipsum
    - `content_sections_match` — кол-во секций совпадает
    - `extraction_log_exists` и `extraction_log_passed` — лог с статусом
  - Создан валидационный скрипт `skills/landing-system/scripts/validate-content-extraction.py` (72 SLOC)
  - Создан extraction-движок `scripts/extract-content-from-prototype.py` (220 SLOC) с поддержкой fallback на markdown
  - Написаны unit-тесты в `tests/phase-stage-07/test-content-extraction.bats` (9 тестов)
  - Обновлен `CLAUDE.md` с новым workflow `/landing-content`

**Что изменилось:**
```
07_ПРОТОТИП/source/prototype.docx (исходный клиентский файл)
  ↓ prototype-importer (парсинг)
07_ПРОТОТИП/prototype.yaml + prototype.md (структура) ✅
  ↓ content-writer (NOW: EXTRACTION из YAML!)
07_КОНТЕНТ/content.md (заполнено РЕАЛЬНЫМИ текстами) ✅
07_КОНТЕНТ/extraction-log.md (лог с ✅ SUCCESS маркером) ✅
  ↓ wireframe selector
07a_WIREFRAME/wireframe.html (показывает реальный контент, не template) ✅
```

**Проверка на neurokreator:**
- Запустить: `python3 scripts/extract-content-from-prototype.py d:\AI_TEAMS\Lendings\neurokreator\07_ПРОТОТИП\prototype.yaml --output d:\AI_TEAMS\Lendings\neurokreator\07_КОНТЕНТ\content.md --log-output d:\AI_TEAMS\Lendings\neurokreator\07_КОНТЕНТ\extraction-log.md`
- Проверить: `cat 07_КОНТЕНТ/content.md` должен содержать реальные тексты (курсы, цены, описания)
- Проверить: `grep -i lorem 07_КОНТЕНТ/content.md` должен возвращать nothing
- Проверить: `grep "✅ SUCCESS" 07_КОНТЕНТ/extraction-log.md` должен вернуть match
- Проверить: `bash scripts/gate-check.sh --stage 07_content --project neurokreator` должен вернуть exit 0

**На что это влияет:**
- ✅ wireframe.html теперь показывает РЕАЛЬНЫЙ контент из прототипа
- ✅ Маркетолог выбирает макет на основе реальных текстов, не template
- ✅ Дальнейшие этапы (07c_composed, 07d_photos, 07e_visuals) работают с корректным контентом
- ✅ neurokreator проект может успешно пройти stage 07 → 07a → 07b и дальше

**Дополнительное открытие:**
Проблема была ТАКЖЕ в агенте `prototype-importer` (stage 07a) — он парсил prototype.docx и заменял реальные тексты на Lorem ipsum. Для neurokreator это исправлено вручную в prototype.yaml, но для будущих проектов нужно улучшить `prototype-importer` чтобы он:
- ✅ Правильно парсил DOCX/PDF и не теряет реальный контент
- ✅ Не подменял реальные тексты Lorem ipsum по умолчанию
- Задача: создать BUG-002 для улучшения prototype-importer

---

## Приоритет 1 — функциональные дыры (блокирует прод-запуск)

### B1. Cookie-баннер + 152-ФЗ блок согласия на обработку ПД ✅ [spec](superpowers/specs/2026-05-21-b1-cookie-banner-pd-consent-design.md) [plan](superpowers/plans/2026-05-21-b1-cookie-banner-pd-consent-plan.md)
- **Реализовано:** legal-block.php, REST pd_consent validation, юр-страницы policy/consent.html.template + install_legal_pages.sh, Google Consent Mode v2 (через B2 mu-plugin), stage-gate soft-check `legal_blocks_present`.

### B2. Cookie-banner Library (5 layouts + admin) ✅ [spec](superpowers/specs/2026-05-22-b2-cookie-banner-library-design.md) [plan](superpowers/plans/2026-05-22-b2-cookie-banner-library-plan.md)
- **Реализовано:** 5 layouts в mu-plugin, Network admin с сегмент-селектором, token-driven CSS vars, Google Consent Mode v2, migration marker. wp-builder.md обновлён (устаревшие B1-инструкции убраны).

### ✅ B2b. GTM-вставка в `analytics-engineer`
- **Зачем:** `GTM_CONTAINER_ID` уже в `.env.example`, но никто его не использует.
- **Что добавить:** в `agents/analytics-engineer.md` — PHP-сниппет вставки GTM в `functions.php` рядом с Метрикой (читать `getenv('GTM_CONTAINER_ID')`, без `<noscript>` если cookie-баннер не дал согласия).
- **Размер:** ~30 SLOC. 2–3 часа.
- **Реализовано:** `lp_gtm_head` (wp_head, priority 2) + `lp_gtm_body` (wp_body_open, noscript только при analytics consent). 6 bats-тестов.

### ✅ B3. Бэкап `wp db export` до деплоя в prod
- **Зачем:** сейчас деплой rsync'ит без отката.
- **Что добавить:** в `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — перед `rsync` запустить `ssh ... "wp db export /tmp/backup-<ts>.sql"`, скачать локально в `09_ДЕПЛОЙ/backups/`.
- **Размер:** ~20 SLOC. 1 час.
- **Реализовано:** `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` + 5 bats-тестов. Commit: `feat(deploy): add wp db backup before rsync (B3)`.

### ✅ B4. Sitemap.xml в `seo-optimizer`
- **Зачем:** без sitemap.xml поисковики хуже индексируют.
- **Что добавить:** в `agents/seo-optimizer.md` — генерация статичного `sitemap.xml` (главная + legal-страницы), либо подключение Rank Math плагина.
- **Размер:** ~40 SLOC. 2 часа.
- **Реализовано:** `skills/seo-optimizer/scripts/generate-sitemap.py` (51 строка) + 5 pytest-тестов + шаг 8 в `agents/seo-optimizer.md`.

---

## Приоритет 2 — расширение и удобство

### ✅ B5. Автоустановка WP-плагинов при деплое
- **Зачем:** сейчас плагины ставятся вручную.
- **Что добавить:** в `deploy-wordpress.sh` — после rsync читать `06_СТЕК/design-stack.yaml`, выполнить `wp plugin install <list> --activate`. Дефолтный список: WP Rocket / LiteSpeed Cache, ShortPixel, Wordfence, UpdraftPlus, Limit Login Attempts, Redirection, Really Simple SSL.
- **Размер:** ~50 SLOC. 3 часа.
- **Реализовано:** `skills/wp-cli-deployer/scripts/get-plugin-list.py` (merge stack+defaults, no dupes) + bash-блок в `deploy-wordpress.sh`. 5 pytest + 6 bats тестов.

### ✅ B6. fallback photo-stylist (промпты для ChatGPT)
- **Зачем:** если у пользователя нет `HUGGINGFACE_TOKEN`, photo-stylist должен выдавать готовые промпты для ручной обработки клиентских фото в ChatGPT/Шедеврум.
- **Что добавить:** в `agents/photo-stylist.md` — если HF API не настроен, генерировать `02_МАТЕРИАЛЫ_КЛИЕНТА/photo-prompts.md` с одним промптом на каждую нужную картинку (привязка к brand-style из `04_БРЕНД/brand-kit.md`).
- **Размер:** ~80 SLOC. 1 день.
- **Реализовано:** `skills/photo-styling/scripts/generate-photo-prompts.py` (шаблоны по типу фото: portrait/team/product/process/default, цвета из brand-kit.md) + step 0 в `photo-stylist.md` с fallback-веткой. 5 pytest-тестов.

### ✅ B7. Soft-check фото-стиля в `client-assets-collector`
- **Зачем:** soft_check `photo_style_consistency` в gate-check.yaml уже есть как prompt, но агент пока спрашивает «вручную». Добавить автоматическую оценку.
- **Что добавить:** в `agents/client-assets-collector.md` — анализ фото из `02_МАТЕРИАЛЫ_КЛИЕНТА/` через Pillow (палитра, контраст, ориентация), вывод в `02_МАТЕРИАЛЫ_КЛИЕНТА/style-report.md` с рекомендацией «однородный / нужна обработка / каких не хватает».
- **Размер:** ~120 SLOC. 1 день.
- **Реализовано:** `skills/client-assets-collection/scripts/analyze-photo-style.py` (orientation, dominant_color, RMS contrast, verdict) + шаг 6 в `client-assets-collector.md`. 5 pytest-тестов.

### ✅ B8. migration-engineer (301-редиректы при переносе сайта)
- **Зачем:** при переносе со старого сайта нужны 301 со старых URL.
- **Что добавить:**
  - `agents/migration-engineer.md` — собирает старые URL у пользователя, генерирует `09_ДЕПЛОЙ/redirects.csv`
  - Активация плагина Redirection при деплое + импорт CSV через wp-cli
- **Размер:** ~150 SLOC. 1–2 дня.
- **Реализовано:** `agents/migration-engineer.md` (5 шагов: сбор → CSV → валидация → импорт → curl-check) + `skills/wp-cli-deployer/scripts/import-redirects.py` (parse/validate/generate_wp_commands). 6 pytest + 6 bats тестов.

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

### ✅ B10. Staging-окружение
- **Зачем:** деплой сразу в prod рискованно.
- **Что добавить:**
  - `scripts/deploy.sh --env staging|prod` (флаг с дефолтом `staging`)
  - `template/09_ДЕПЛОЙ/deploy-targets.yaml` — параметры staging-домена и prod-домена
  - Для prod: обязательное подтверждение `--confirm` + бэкап БД
- **Размер:** ~100 SLOC. 1 день.
- **Реализовано:** `deploy-wordpress.sh` получил `--env staging|prod` (дефолт staging) + `--confirm` guard для prod + загрузку параметров из `09_ДЕПЛОЙ/deploy-targets.yaml`. Новый скрипт `get-deploy-target.py`. Шаблон `template/09_ДЕПЛОЙ/deploy-targets.yaml`. 5 pytest + 7 bats тестов.

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

### B17. CTA Library + Lazy Blocks integration (S2-A.1)
- **Проблема:** текущая модель CTA в `landing-config` (S2-A) — только 5 фиксированных
  пресетов в `wp_options::landing_cta_presets` (primary/whatsapp/phone/form_modal/learn_more).
  Каждый пресет = только канал связи (тип+URL+label), без визуала и без превью.
  Маркетолог сохраняет настройки и **не видит** где эти кнопки используются,
  как выглядят, и сколько их на сайте. На multisite (N сегментов × N кнопок на странице)
  навигация невозможна.
- **Что нужно (по словам пользователя):**
  1. **Библиотека произвольных CTA-кнопок** (CPT `lp_cta` или аналог) —
     любое кол-во кнопок с лейблами/типами/визуалами, не привязано к 5 жёстким именам.
  2. **Связывание с Lazy Blocks** — каждый блок, использующий CTA, имеет dropdown
     «выбрать кнопку из библиотеки». Когда библиотека меняется — кнопка обновляется
     везде.
  3. **Usage map в админке** — для каждого сайта (и сводно по всей multisite-сети):
     список «кнопка X используется в N блоках на страницах Y/Z» + превью кнопки.
- **Размер:** большой PR (новый CPT, миграция со старых 5 пресетов, Lazy Blocks meta,
  REST endpoint для usage-scan, новая admin-CTA с list table + preview, network
  aggregate). Требует отдельный spec + plan + worktree.
- **Зависимости:** S2-A (готов), требует rescan блоков на каждом сайте при изменении.
- **Обратная совместимость:** `landing_get_cta('primary'/...)` должен продолжать работать
  — миграция превращает 5 пресетов в 5 первых записей CPT.

### B18. Snippet-input для счётчиков/пикселей/верификаций (S2-A.2)
- **Проблема:** текущие поля Head & SEO ожидают **только ID** (например `93902743`),
  а пользователи Яндекс.Метрики / GA4 / FB Pixel / GSC копируют с сервиса **готовый
  HTML-snippet** (`<script>...</script>`, `<meta name="...">`). Сейчас если вставить
  весь snippet — он сохранится как «ID», и сгенерированная разметка в `wp_head` будет
  битая. Маркетолог не знает «надо вырезать только цифры».
- **Что нужно:**
  1. **Auto-detect:** поле принимает либо ID, либо snippet. Если snippet — извлечь ID
     регулярками (`ym\((\d+),`, `G-[A-Z0-9]+`, `fbq\('init','(\d+)'\)`, `content="([a-zA-Z0-9_-]+)"`
     для verification и т.д.). Если ID — сохранить как было.
  2. **Превью «как будет в `<head>`»** под полем — показать сгенерированный snippet
     (тот же что `landing_render_head_extras` выдаёт), чтобы пользователь увидел
     что код корректный.
  3. **Альтернатива:** разрешить «raw snippet override» режим — если пользователь
     хочет вставить именно свой код (например custom Tag Manager wrapper), он
     выбирает «raw» и его snippet идёт в `<head>` как есть (через `wp_kses_post`
     или с расширенным allow-list — `raw_html_head` уже это умеет).
  4. **Help-текст** «Можете вставить как ID, так и весь скрипт — мы распарсим».
- **Применимо ко всем полям Head & SEO** (GA4, Y.Metrika, FB Pixel, TikTok Pixel,
  GSC, Y.Webmaster). Скорее всего такое же поведение нужно и для **integrations**
  (Telegram webhook URL, AmoCRM token и т.д. — пользователи копируют URL целиком
  с querystring или с лишними пробелами).
- **Размер:** средний — добавить parser-функции в `sanitize_callback` для каждого
  поля + JS-превью в admin-head-seo.php. Можно сделать в той же ветке что B17 или
  отдельно.
- **Зависимости:** S2-A (готов).

### B19. Lead status workflow (S2-A.3)

- **Проблема:** в таблице `wp_<bid>_landing_leads` есть колонка `processed_status`
  (default `'pending'`), но в админке «Заявки» **нет UI для смены статуса**.
  Маркетолог видит список — но не может пометить заявку как «обработана» / «в работе» /
  «закрыта». На multisite с десятками заявок в неделю это критично.
- **Что нужно:**
  1. **Vocabulary статусов** — минимум: `pending` (новая), `in_progress` (в работе),
     `won` (закрыта успешно), `lost` (отказ), `spam`. Обсудить custom-статусы.
  2. **UI:** dropdown в строке таблицы для смены статуса inline (AJAX),
     или bulk-actions «отметить выбранные как X».
  3. **Фильтр по статусу** сверху списка (вкладки `Все | Новые | В работе | Закрыто | Спам`,
     как в WP Posts).
  4. **Двусторонняя синхронизация с CRM:** когда CRM меняет статус заявки (через webhook),
     обновлять `processed_status` в БД. Когда маркетолог меняет в админке — пушить в CRM.
     (Каждый адаптер должен расширить interface методом `update_status($lead_id, $status)`,
     если CRM это поддерживает.)
  5. **История изменений:** writes в `wp_<bid>_landing_lead_log` с adapter='admin' +
     status='manual_update' + error_text=old→new.
- **Размер:** средний. Если без CRM-sync — мелкий (admin UI + AJAX endpoint + миграция
  допустимых значений). CRM-sync — отдельная фаза, требует расширения AdapterInterface.
- **Зависимости:** S2-A (готов).

### B20. Live testing для adapters (Telegram/WhatsApp/AmoCRM/Bitrix24/HubSpot)

- **Не тестировались** в Live E2E smoke S2-A (на ailexi.ru): только Email-adapter
  имеет проверенную реализацию через `wp_mail`. Остальные 5 адаптеров (Telegram Bot API,
  WhatsApp Cloud API, AmoCRM v4, Bitrix24 webhook, HubSpot v3) написаны по docs API,
  но **не запускались с реальными credentials**.
- **Что нужно для каждого:**
  1. Получить test-credentials (test bot / sandbox account).
  2. Заполнить в админке «Интеграции», нажать «Test connection» — убедиться что 200 OK.
  3. POST в `/wp-json/landing/v1/lead` — убедиться что lead доставлен в CRM (контакт/сделка
     создан, в Telegram пришло сообщение, и т.д.).
  4. Проверить `wp_<bid>_landing_lead_log` — должна быть запись `status=success`.
  5. Принудительно сломать (неверный token) — убедиться что retry планируется (60s/5min/30min)
     и логируется как `failed`.
- **Особенно проверить:**
  - **AmoCRM:** payload v4/leads/complex (lead+contact в одном вызове) — может потребовать
    custom_fields_values корректировку под реальный аккаунт.
  - **Bitrix24:** webhook URL — реальный формат `https://*.bitrix24.ru/rest/N/TOKEN/`.
  - **HubSpot:** lifecyclestage = 'lead' может конфликтовать с pipeline-config аккаунта.
  - **WhatsApp Cloud:** требует verified business account + approved template для
    proactive messages. Если только tests — может работать только в test-mode.
  - **Encryption round-trip:** убедиться что AES-256-GCM шифрование при save и decrypt
    при send работают корректно (на ailexi.ru не проверялось — все adapter fields пусты).
- **Размер:** N×30мин на adapter с обновлением spec'а под реальные API quirks.
- **Зависимости:** S2-A (готов), test-credentials от пользователя.

---

---

## Приоритет 1 — UX флоу: референсы и визуальные решения

### B23. Этап 03: агент не сообщает о недоступных референсах ✅ [spec](superpowers/specs/2026-05-28-b23-b24-reference-validation-visual-strategist-design.md) [plan](superpowers/plans/2026-05-28-b23-b24-b26-reference-validation-visual-strategist-mockup-plan.md)

**Что сейчас происходит:**
`references-curator` получает URL от пользователя, пытается (или не пытается) его открыть, и молча продолжает работу. Если URL недоступен (Behance, Tilda, Instagram — все требуют браузер или авторизацию), агент либо игнорирует референс, либо записывает его в `index.yaml` с `status: approved` без реального чтения визуала. При этом агент пишет notes — описание стиля — на основе догадок или названия проекта, а не реального содержимого.

**Почему некорректно:**
Менеджер думает, что референс был обработан. На этапе 04 brand-architect читает `index.yaml` с ложными notes и принимает дизайн-решения на их основе. В итоге менеджер согласовал один визуальный стиль в голове, а получил другой — потому что агент описал референс неверно.

**Конкретный пример (lixiang-dubai3):**
Референс OFFtrail (Behance) был описан как `"dark premium"` — агент не смог открыть страницу и сочинил описание. Реальный референс: ярко-синий фон `#2B72B8`, editorial layout, Archivo Black. В итоге brand-architect сделал чёрный дизайн `#0A0A0A`.

**Что нужно:** агент обязан явно сообщить какие URL недоступны и запросить альтернативу (скриншот или текстовое описание) перед продолжением. Зафиксировано как правило в `docs/standards/stage-agent-preamble.md` (шаг 8), но нет реализации в агенте и нет проверки в gate-check.

---

### B24. Этап 03: агент самостоятельно добавляет референсы без согласования ✅ [spec](superpowers/specs/2026-05-28-b23-b24-reference-validation-visual-strategist-design.md) [plan](superpowers/plans/2026-05-28-b23-b24-b26-reference-validation-visual-strategist-mockup-plan.md)

**Что сейчас происходит:**
`references-curator` добавляет в `03_РЕФЕРЕНСЫ/index.yaml` референсы из собственных источников (конкуренты из `01a_АНАЛИЗ_НИШИ/competitors.yaml`, "эталонные" сайты ниши) без явного подтверждения пользователем. Для lixiang-dubai3 были добавлены BMW UAE, Mercedes-Benz UAE, Tesla UAE, Genesis UAE — пользователь давал только OFFtrail.

**Почему некорректно:**
Пользователь не видел и не утверждал эти референсы. Brand-architect берёт все `status: approved` записи как равнозначные источники. Нишевые дефолты (premium-auto = тёмный фон) усиливаются добавленными агентом референсами (BMW/Mercedes — все тёмные), перевешивая реальный референс пользователя.

**Что нужно:** агент может предложить дополнительные референсы, но обязан показать список пользователю и получить явное `approved` для каждого перед записью в index.yaml.

---

### B25. Этап 04: brand-architect выбирает палитру без показа альтернатив

**Что сейчас происходит:**
`brand-architect` генерирует `brand-kit.md` с одним вариантом палитры — тем, который сам счёл наиболее подходящим для ниши. Менеджер видит готовый brand-kit.html и либо утверждает, либо не понимает что можно было получить другое. Никакого выбора между вариантами нет.

**Почему некорректно:**
Визуальный стиль — ключевое дизайн-решение, которое должен принимать менеджер/клиент, а не агент. Агент не знает ни рынок, ни предпочтения аудитории, ни пожелания клиента, которые могли не попасть в бриф. Одно молчаливое решение на этапе 04 ломает весь последующий флоу вплоть до composed.html.

**Решается через B23+B24:** после внедрения `visual-strategist` (этап 03b) brand-architect получает готовый `visual-concept.yaml` от менеджера и только реализует его. Отдельная доработка 04 не нужна — проблема устраняется на уровне 03b.

**Статус:** закрывается реализацией B23+B24. Отдельного плана не требует.

---

### B26. Этап 04→05: нет точки проверки "это то, что вы имели в виду?" ✅ [spec](superpowers/specs/2026-05-28-b26-quick-mockup-stage05-design.md) [plan](superpowers/plans/2026-05-28-b23-b24-b26-reference-validation-visual-strategist-mockup-plan.md)

**Что сейчас происходит:**
После утверждения brand-kit.html пользователь нажимает `+` и агент сразу генерирует полную дизайн-систему (DESIGN.md + tokens.json + design-preview.html). К моменту когда пользователь видит composed.html — несколько этапов уже зафиксировано, переделка стоит дорого.

**Почему некорректно:**
Brand-kit.html показывает палитру свотчами и шрифтами — это абстракция. Пользователь не видит как эти токены выглядят на реальном лендинге пока не дойдёт до 07b. Разрыв между "одобрил brand-kit" и "увидел результат" — 3–4 этапа и много токенов.

**Что нужно:** между этапом 04 и 05 — быстрый mockup: 1–2 блока (hero + один контентный) с реальными токенами, чтобы пользователь увидел "как это будет выглядеть" до генерации полной дизайн-системы. Требует отдельного brainstorm — не охвачено спеком B23+B24.

### B28. Флоу 03→07b: отклонения агентов не фиксируются ✏️ [spec](superpowers/specs/2026-05-28-b27-b28-brand-architect-decisions-log-design.md)

**Что сейчас происходит:**
Менеджер выбирает концепт в 03b, но к этапу 07b уже не видит связи между своим выбором и результатом. Агенты принимают самостоятельные решения (типографика, отступы, иконки) молча — не сообщают об этом и нигде не фиксируют.

**Почему некорректно:**
К моменту composed.html менеджер смотрит на результат и не понимает: это реализация его концепта или агент добавил что-то от себя? Нет возможности отследить где флоу "свернул" от задуманного.

**Что нужно:**
- Каждый агент (brand-architect, design-system-generator, block-composer) при завершении этапа формирует список отклонений от `visual-concept.yaml` — только то что решил сам
- Если отклонений нет → молчит
- Если есть → пишет в чат явно: "Я принял следующие самостоятельные решения: ..."
- `landing-orchestrator` после каждого `--approve` дописывает отклонения в `<project>/decisions.log.md`

**Формат `decisions.log.md`:**
```
## Этап 04_brand — 2026-05-28
- Типографика: выбран Inter 700 (направление из концепта: "строгий гротеск") — подобрано агентом
- Иконки: Lucide set (не было в концепте) — подобрано агентом

## Этап 05_design — 2026-05-28
(нет отклонений)
```

**Зависит от:** B23+B24 (нужен `visual-concept.yaml` как эталон для сравнения).

---

### B27. Этап 04: нет разграничения типов правок при "не то" ✏️ [spec](superpowers/specs/2026-05-28-b27-b28-brand-architect-decisions-log-design.md)

**Что сейчас происходит:**
При любом "не то" на `brand-kit.html` агент либо переделывает всё сам по своему усмотрению, либо теряется что именно менять. Нет чёткого правила: какие правки решаются прямо в 04, а какие требуют возврата в 03b.

**Почему некорректно:**
Правки по цвету или mood — это концептуальные решения, которые должны идти через `visual-concept.yaml` (иначе 03b и 04 разойдутся). Правки по типографике и иконкам — локальные, не затрагивают концепт. Смешивание приводит к тому что агент либо меняет концепт без ведома менеджера, либо гоняет его через лишние этапы по мелочи.

**Что нужно:** в `agents/brand-architect.md` — явная логика routing правок:
- Цвет / mood → STOP, сообщи "это концептуальная правка — обнови `visual-concept.yaml` в 03b", перегенерируй brand-kit после
- Типографика / иконки → принять правку прямо в 04, перегенерировать brand-kit без возврата

**Зависит от:** B23+B24 (нужен `visual-concept.yaml`). Реализуется обновлением `agents/brand-architect.md`.

### B29. Wiki-корреляция всегда ложная при запуске через субагентов ✏️ [spec](superpowers/specs/2026-05-28-b29-wiki-run-id-correlation-design.md) [plan](superpowers/plans/2026-05-28-b29-wiki-run-id-correlation-plan.md)

**Что происходит сейчас:**
В отчёте "Запуски vs вики" (`wiki/routing-report.md`) все записи с `via_wiki = ✗` (утечка) — даже те агенты, которые содержат pre-flight строку `python -m scripts.wiki.query`. Это происходит при запуске через субагентов (subagent-driven-development, executing-plans).

**Почему некорректно:**
`was_wiki_queried()` в `scripts/wiki/routing_log.py` ищет `wiki_query`-запись с совпадающим `session_id` в `wiki/wiki-usage.jsonl`. Но субагент работает в **отдельной сессии** (`session_id` отличается от основной). В итоге:

1. Основная сессия делает wiki_query → пишет запись с `session_id = A`
2. Субагент запускает агент/скил → `log_agent_call` проверяет `session_id = B`
3. Совпадений нет → `via_wiki = false` — хотя вики действительно запрашивалась

Дополнительная проблема: `python -m scripts.wiki.query` в pre-flight агентов — это **инструкция для Claude**, не bash-скрипт. Если субагент получил задание напрямую (без pre-flight в промпте), он может вообще пропустить этот шаг.

**Что нужно:**
Вариант А (минимальный): в `was_wiki_queried()` добавить поддержку `parent_session_id` — при записи `agent_call` / `skill_call` из субагента передавать `parent_session_id` (основная сессия) и проверять оба id.

Вариант Б (правильный): отделить "запрос к вики выполнен в промпте" (инструкция агенту) от "вики-запись залогирована в этой же сессии". Субагент-диспетчер (controller) должен сам логировать `wiki_query` перед диспатчем, а `session_id` субагента — наследовать от контроллера через явный параметр `--parent-session`.

**Влияние:** все отчёты routing с субагентами показывают 100% утечек — данные бесполезны для анализа.

**Зависит от:** понимания архитектуры session_id в Claude Code (субагенты создают отдельные session).

### B35. Block Library + Wireframe: единая связанная система

**Концепция (утверждена 2026-05-29):**

Два инструмента с чёткими ролями:

```
Галерея (block-library/gallery.html)   →   Wireframe (07a_WIREFRAME/wireframe.html)
────────────────────────────────────       ─────────────────────────────────────────
SVG-схемы — чистая геометрия               Те же блоки-шаблоны
Типовые тексты (HEADLINE / BODY / CTA)     + реальные тексты из prototype.yaml
Без стилей проекта                         + стили дизайн-системы проекта (tokens.json эт.05)
Фильтрация по категории                    + чекбокс вкл/выкл каждого блока
Постоянная — не привязана к проекту        + стрелки ↑↓ для изменения порядка
                                           Сохраняет selections.yaml
                                                ↓
                                    compose-blocks.py → composed.html
```

**Галерея (B35a):**
- SVG-схема каждого блока генерируется программно из `meta.yaml` (`layout_pattern` + `slots`)
- Каждый слот → прямоугольник своей пропорции (image=широкий, headline=узкая полоса, cta=скруглённый)
- Layout-паттерн определяет расположение: split=2 колонки, grid-3=3 колонки, centered=центр, stacked=вертикально
- Под каждой схемой — структурное название: `Hero: фото справа + текст + CTA`
- Размер файла < 100KB
- Фильтрация по категории (CSS-only)

**Wireframe (B35b):**
- Берёт выбранные шаблоны из галереи (или предлагает кандидатов по типу блока из prototype.yaml)
- Рендерит template.html каждого блока **со стилями дизайн-системы проекта**:
  токены из `05_ДИЗАЙН-СИСТЕМА/tokens.json` инжектятся в `:root` каждого
  блока (через inject-tokens / bridge `--lp-*`), так что блоки показывают
  реальные цвета и шрифты клиента, а не нейтральную серую заглушку. Без
  tokens.json (до этапа 05) — fallback на нейтральные lo-fi дефолты.
- Подставляет реальные тексты из prototype.yaml в слоты (`{{slot:headline}}` → реальный headline)
- UI: для каждой позиции — чекбокс включить/отключить + стрелки ↑↓ + radio-выбор варианта
- Экспортирует selections.yaml со статусом каждого блока (enabled/disabled) и порядком

**Зависит от:** B34 (финальная таксономия должна быть готова до перестройки галереи).

---

### B30. Эталон-референс в агентах — ссылка на конкретный проект

**Что происходит сейчас:**
`agents/landing-orchestrator.md` содержал строку `Эталон-референс: ~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` — ссылку на конкретный клиентский проект как эталон качества. Это ломает систему: проект может быть удалён, переименован, или отсутствовать на другой машине.

**Исправлено:** строка заменена на ссылку на `docs/standards/premium-07b-checklist.md` + `scripts/verify-composed-premium.sh`.

**Общее правило (применить ко всем агентам):** никаких ссылок на конкретные проекты из `~/Lendings/` в агентских инструкциях. Эталоны качества — только в `docs/standards/`.

**Статус:** частично исправлено в `landing-orchestrator.md`. Проверить все остальные агенты на аналогичные ссылки.

---

### B31. Wireframe: плейсхолдеры вместо реальных текстов + несогласованные стили блоков

**Что происходит сейчас:**
`wireframe.html` показывает блоки с плейсхолдерами `[SLOT: headline]` вместо реальных текстов из `prototype.yaml`. Стили блоков из block-library разные — каждый блок выглядит из другой вселенной. Это делает wireframe бесполезным для оценки структуры.

**Что нужно (уточнено 2026-06-02):**
Wireframe рендерит блоки **со стилями дизайн-системы проекта** — токены из
`05_ДИЗАЙН-СИСТЕМА/tokens.json` накладываются на каждый блок (реальные цвета и
шрифты клиента), а не нейтральная серая заглушка. До этапа 05 (нет tokens.json)
— fallback на нейтральные lo-fi дефолты.

В любом случае: `inject-content.py` подставляет тексты из `prototype.yaml`, а
стили дизайн-системы инжектятся в `:root` каждого блока перед рендером.

> Ранее тут были два режима (lo-fi / styled нейтральный). Решение пересмотрено:
> дизайн-система проекта накладывается на wireframe сразу, нейтраль — только
> fallback до этапа 05.

**Зависит от:** `skills/wireframe-rendering/scripts/render-wireframe.py` + `inject-content.py`.

---

### BUG-003. render-wireframe.py сломана на Windows — Python синтаксис 3.9+ ⚠️ БЛОКИРУЕТ B31/B32

**Статус:** 🟡 IN BACKLOG (2026-06-01)  
**Приоритет:** HIGH — блокирует правильную генерацию wireframe.html для PR-A stage 07b  
**Блокирует:** B31 (lo-fi + styled wireframe режимы), B32 (UI для выбора типов блоков)

**Проблема:**
- `skills/wireframe-rendering/scripts/render-wireframe.py` использует `dict[str, str]` синтаксис (Python 3.9+)
- На Windows с PowerShell/WSL Python не работает (exit 49 без вывода)
- Как результат: wireframe.html генерируется вручную с ТОЛЬКО 2 вариантами на блок вместо всех из catalog
- Пример: Header имеет 3 реальных блока в block-library, но показываются 2 hardcoded варианта

**Что нужно исправить:**
1. Заменить `dict[str, str]` на `Dict[str, str]` (typing module для Python 3.8 совместимости)
2. Проверить Python version check в pre-flight
3. Создать fallback-версию `render-wireframe-compat.py` или добавить version-check в основной скрипт
4. Тестирование на Python 3.8+

**Что даст:**
- ✅ wireframe.html автоматически читает catalog.yaml
- ✅ Показывает ВСЕ подходящие блоки для каждого типа (header: 3, hero: 5, features: 6, cta: 7, pricing: 4, footer: 3 вместо hardcoded 2)
- ✅ Маркетолог выбирает из ПОЛНОГО списка, не из сокращённого

**Как взять:**
```
/brainstorming Зафиксить render-wireframe.py для Windows — Python 3.8+ совместимость
```

**Оценка:** 2–3 часа (syntax fix + testing).

---

### B32. Wireframe: нет UI для выбора типа блока и отключения лишних

**Что происходит сейчас:**
В `wireframe.html` нет возможности:
- Отключить блок (например, убрать quiz-блоки из автомобильного лендинга)
- Выбрать тип блока внутри категории (hero с фото слева / справа / full-screen — сейчас варианты смешаны)
- Видеть к какой категории относится каждый вариант

Как результат: quiz-блоки (онбординг-воронка) попали в selections.yaml лендинга автомобилей.

**Что нужно:**
- Чекбокс «Включить/отключить блок» рядом с каждой позицией
- Группировка вариантов по sub-type (hero-photo-left / hero-photo-right / hero-fullscreen)
- Фильтрация кандидатов по нише из `prototype.yaml::niche` — quiz-блоки не показываются для b2c-автомобилей если в нише нет quiz
- Блоки отсутствующие в `prototype.yaml` не предлагаются

**Зависит от:** BUG-003 (render-wireframe.py должна работать) + `block-library/` meta.yaml структура.

---

### B33. Стандарт премиальности: визуальное качество вместо JS-паттернов

**Что происходит сейчас:**
`scripts/verify-composed-premium.sh` проверяет наличие JS/CSS паттернов (parallax, lightbox, count-up, clip-path). Это технические маркеры, не визуальное качество. Можно пройти 18/18 и при этом получить дешёво выглядящую страницу — что и происходит.

**Что нужно:**
Заменить / дополнить чеклист на визуальный стандарт из 12 критериев:

1. **Воздух / spacing** — большие отступы между секциями, вертикальная ритмика, контент не прилипает
2. **Типографика** — max 2 шрифта, иерархия размеров через clamp(), хороший line-height, консистентный letter-spacing
3. **Сетка и alignment** — чёткая grid-система, одинаковые контейнеры, равномерные интервалы
4. **Ограниченная палитра** — 1 основной + 1 акцент + нейтральная база, без случайных градиентов
5. **Визуальная консистентность** — один стиль карточек, одинаковые радиусы/тени/бордеры, единый язык иконок
6. **Качество изображений** — единый color grading, нет generic stock
7. **Hero composition** — один dominant visual, чистая композиция, focal point
8. **Motion design** — subtle, smooth easing, ничего не дёргается, нет bounce
9. **Тени и depth** — мягкие shadows, консистентный blur, один уровень depth-системы
10. **Детализация UI** — hover states, focus states, tactile кнопки, иконки одинаковой толщины
11. **Mobile polish** — отступы адаптированы, hero не ломается, типографика остаётся дорогой
12. **Ритм страницы** — смена плотности, чередование масштаба, «визуальное дыхание»

**Реализация:** новый скрипт `scripts/verify-composed-visual.py` (Python, парсит CSS) проверяет:
- spacing токены ≥ 80px между секциями
- количество font-family ≤ 2
- количество цветов в :root ≤ 8
- единообразие border-radius (не более 3 разных значений)
- наличие `@media (max-width: ...)` адаптива
- наличие `transition` на интерактивных элементах

Оценка 0–100, порог прохождения 85 = premium visual.

**Зависит от:** нового скрипта + обновления `config/stage-gates.yaml`.

### B34. Двухуровневая семантическая таксономия блоков + умный импортёр

**Что происходит сейчас:**
- Таксономия одноуровневая и хаотичная: `hero, features, trust, social-proof, process, pricing, faq, cta, quiz, contacts, footer, header, gallery, team`. `trust` покрывает совершенно разные вещи (манифест, гарантии, цифры, партнёры).
- 183 блока в библиотеке, большинство — автоматически загруженный мусор с неинформативными `display_name_ru` типа `"Контактная полоса с крупным номером, подписью и маленькой оранжевой ссылкой"` (стиль вместо структуры).
- В галерее/варфрейме **два комбобокса = Категория → layout_pattern** (split/grid-3/centered). Но `layout_pattern` — это структура **вёрстки**, а пользователю при сборке лендинга нужна **семантика контента** («мне нужны отзывы», а не «мне нужен split»).
- Импортёр (`scripts/import-blocks/import-from-url.sh`) добавляет блоки без проверки дублей.

**Целевая модель: ДВА семантических уровня (категория → подкатегория)**

Комбобоксы в галерее и варфрейме работают так:
- **Комбобокс 1 — Категория** (уровень 2): крупная функция блока на странице.
- **Комбобокс 2 — Подкатегория** (уровень 3): семантический подтип по **роли на лендинге**, а не по вёрстке. Появляется ТОЛЬКО там, где блоки внутри категории играют **разную роль** (например пользователь ищет именно «отзывы» или именно «сравнительную таблицу тарифов»). Если внутри категории блоки отличаются только раскладкой — уровня 3 НЕТ.
- `layout_pattern` (split/grid-3/centered/stacked/...) **остаётся только в метаданных** блока (`meta.yaml` / `catalog.yaml`), в комбобоксы НЕ выводится. Это технический атрибут вёрстки для рендера и дедупликации, не выбор пользователя.

**Критерий уровня 3:** «разная роль на лендинге». Разная вёрстка одного и того же
контента (3 карточки vs 4 карточки vs split) — это `layout_pattern`, НЕ уровень 3.

**Часть 1 — Категории (уровень 2) и подкатегории (уровень 3):**

Если у категории нет подкатегорий — комбобокс 2 в галерее/варфрейме скрывается,
блоки фильтруются только по категории. В метаданных таких блоков `variant: null`.

**Шапка / Навигация**
- _(нет уровня 3)_

**Первый экран**
- _(нет уровня 3 — с формой / с видео и т.п. это функционал, а не тип)_

**Бегущая строка**
- _(нет уровня 3)_

**Преимущества**
- _(нет уровня 3 — карточки / сравнение это вёрстка, а не роль)_

**Контент**
- о продукте
- проблема → решение
- как это работает

**Соц. доказательства**
- отзывы
- наши клиенты
- рейтинги
- цифры
- кейсы
- упоминания в медиа

**Доверие**
- сертификаты
- гарантии
- безопасность

**Цены**
- карточки тарифов
- сравнительные таблицы

**Формы**
- сбор email
- многошаговая
- квиз
- бронирование

**FAQ**
- _(нет уровня 3)_

**Подвал**
- _(нет уровня 3)_

**Итого: 11 категорий.**
- С уровнем 3 (5): Контент, Соц. доказательства, Доверие, Цены, Формы.
- Без уровня 3 (6): Шапка/Навигация, Первый экран, Бегущая строка, Преимущества, FAQ, Подвал.

**Не входит в эту итерацию (за бортом MVP):** Призыв к действию (CTA — это
функционал, встраивается в другие блоки, не отдельный блок), Срочность,
Интеграции, Демонстрация продукта, нишевые блоки (SaaS / курсы / агентства /
e-commerce / локальный бизнес). Та же 2-уровневая механика, отдельная итерация B34.2.

**Миграция старых категорий (183 блока сейчас):**
- `header` → `Шапка / Навигация`.
- `hero` → `Первый экран`.
- `features` → `Преимущества`.
- `about`, `manifesto`, `process`, `problem-solution` → `Контент` (подкатегории: о продукте / проблема→решение / как это работает).
- `social-proof`, `stats`, `partners`, `team` (если кейсы/логотипы) → `Соц. доказательства` (подкатегории: отзывы / наши клиенты / рейтинги / цифры / кейсы / упоминания в медиа).
- `trust`, `guarantees` → `Доверие` (подкатегории: сертификаты / гарантии / безопасность).
- `pricing` → `Цены` (подкатегории: карточки тарифов / сравнительные таблицы).
- `quiz`, `lead-form` → `Формы` (подкатегории: сбор email / многошаговая / квиз / бронирование).
- `faq` → `FAQ`.
- `footer`, `contacts` → `Подвал`.
- `cta` → распределить: повторный CTA-блок убрать как отдельный (CTA встраивается в hero/формы/footer); если блок самостоятельный по контенту — пересмотреть поблочно.
- `gallery` → пересмотреть поблочно (фото-галереи могут уйти в `Соц. доказательства`/кейсы или в `Контент`).

**Часть 2 — Схема метаданных блока:**
```yaml
id: social-proof-001
category: social-proof        # уровень 2 (комбобокс 1)
variant: testimonials         # уровень 3 (комбобокс 2) — НОВОЕ поле
layout_pattern: grid-3        # только метаданные, НЕ в комбобоксах
display_name_ru: "Отзывы: 3 карточки с фото и цитатой"
slots: [...]                  # editable content schema
```
Будущий уровень «поведение блока» (spacing/theme/responsive/animations) — отдельная итерация (B34.3), сюда не входит, но поле задела не ломает.

**Часть 3 — Чистка библиотеки:**
Оставить эталонные блоки, покрывающие каждую пару (category × variant). Дубли по `(category, variant, layout_pattern)` схлопнуть. Критерий сохранения — уникальная комбинация семантики + структуры, а не цвет/стиль.

**Часть 4 — Умный импортёр (новый скил `/landing-import-blocks`):**
- Принимает скриншот или URL.
- Codex извлекает `category` (уровень 2), `variant` (уровень 3), `layout_pattern` (метаданные), слоты.
- Проверяет что в библиотеке нет блока с идентичной тройкой `(category, variant, layout_pattern)`.
- Если уникальный — добавляет с id формата `<category>-<NNN>` и `variant`, имя структурное.
- Если дубль — показывает похожий блок и спрашивает подтверждение.

**Часть 5 — Переименование display_name_ru:**
Формат: `"[Категория · подкатегория]: [структура элементов]"` (подкатегория опускается, если её нет):
- ❌ `"Контактная полоса с крупным номером, подписью и маленькой оранжевой ссылкой"`
- ✅ `"Подвал: телефон крупно + подпись + ссылка"`
- ❌ `"Сетка 4×2 карточек с принципами работы"`
- ✅ `"Преимущества: 4×2 карточки с нумерацией"`
- ✅ `"Соц. доказательства · отзывы: 3 карточки с фото и цитатой"`

**Часть 6 — Галерея + варфрейм:**
Оба комбобокса переключаются с `category → layout_pattern` на `category → variant`. `generate-gallery.py` и `render-wireframe.py`/`match-candidates.py` читают новое поле `variant`. Комбобокс 2 скрывается для категорий без подкатегорий. Карточка показывает бейдж категории, бейдж подкатегории (если есть) и мелкий технический тег `layout_pattern`.

**ЯЗЫК UI — обязательно русский.** В комбобоксах и на бейджах выводятся
**русские человекочитаемые названия** из таблицы ниже, НЕ технические слаги.
Слаги (`social-proof`, `testimonials`) живут только в данных/коде; пользователь
видит «Соц. доказательства» → «отзывы». Это требование, а не рекомендация.

Структура двух комбобоксов строго как согласовано:
- Комбобокс 1 «Категория» — 11 пунктов (русские названия).
- Комбобокс 2 «Подкатегория» — появляется только для 5 категорий с уровнем 3;
  для остальных 6 скрыт.

**Таблица меток (источник истины для UI-лейблов):**

| Категория (слаг) | Метка в UI | Подкатегории (слаг → метка) |
|---|---|---|
| `header` | Шапка / Навигация | — |
| `hero` | Первый экран | — |
| `marquee` | Бегущая строка | — |
| `features` | Преимущества | — |
| `content` | Контент | `about`→о продукте, `problem-solution`→проблема → решение, `process`→как это работает |
| `social-proof` | Соц. доказательства | `testimonials`→отзывы, `clients`→наши клиенты, `ratings`→рейтинги, `numbers`→цифры, `cases`→кейсы, `media`→упоминания в медиа |
| `trust` | Доверие | `certificates`→сертификаты, `guarantees`→гарантии, `security`→безопасность |
| `pricing` | Цены | `cards`→карточки тарифов, `comparison`→сравнительные таблицы |
| `forms` | Формы | `email`→сбор email, `multi-step`→многошаговая, `quiz`→квиз, `booking`→бронирование |
| `faq` | FAQ | — |
| `footer` | Подвал | — |

**Зависит от:** B31 (lo-fi wireframe), B32 (UI выбора блоков).
**Блокирует:** перестройку галереи (B30) — финальная таксономия должна быть готова до неё.

### PR-S. Style Moods System — интерактивный выбор mood'ов в wireframe

**Статус:** 🚀 PHASE 1-3 COMPLETE (2026-06-02) — Phase 4-5 PENDING

**Что это:**
Система стилевых mood'ов (brutalist, editorial-warm, swiss-modernist, retro-windows, coral-soft, monochrome-precision) уже полностью реализована в block-library (CSS palette, typography, motion, 38 patterns). Но пользователи не могут **выбирать** mood'ы и **видеть превью** разных mood-вариантов одного блока.

**Цель:**
Добавить mood как третье измерение в wireframe-selection (наряду с layout type + block variant):
1. **Wireframe UI** — mood tabs ниже layout tabs, preview разных моодов для одного блока
2. **Selections.yaml** — сохранять `style_mood` per block
3. **Compose pipeline** — применять mood CSS + patterns автоматически
4. **Для всех проектов** — не только neurokreator

**Фазы реализации:**
- **Phase 1:** Wireframe UI enhancement — mood tabs в `wireframe-shell.html`, mood previews в `render-wireframe.py`
- **Phase 2:** Selections.yaml extension — добавить `style_mood` поле
- **Phase 3:** Compose pipeline integration — читать mood, применять CSS + patterns в `compose-blocks.py`
- **Phase 4:** Validation & Testing — e2e тесты
- **Phase 5:** Docs & Onboarding — MOOD-SELECTION-GUIDE.md

**Размер:** ~800 SLOC в 3 файлах. Неделя work.

**Зависит от:** Ничего (mood infrastructure уже есть).

**Блокирует:** Future PR-S.2 (mood auto-detection по niche).

**Артефакты:**
- ✏️ Spec: [Design spec](superpowers/specs/2026-06-02-pr-s-style-moods-system-spec.md) (TBD)
- ✅ Plan: [Implementation plan](superpowers/plans/2026-06-02-pr-s-style-moods-system-plan.md) — готов, пошаговый (5 фаз, 800 SLOC, 5–7 дней)

---

## Прогресс

- ✅ MVP (stage-gates + onboarding) — реализован
- ✅ B1 — реализован (legal-block, consent REST, юр-страницы, Consent Mode v2 через B2)
- ✅ B2 — реализован (cookie-banner library 5 layouts, mu-plugin, admin UI)
- ✅ B2b (GTM), B3 (db backup), B4 (sitemap) — выполнено
- ✅ B21–B22 — реализованы (`/landing-delete`, `/landing-rename`)
- ✅ B23–B24 — реализованы (validate-url.py, extract-palette.py, refs-palette.html, visual-strategist агент, generate-concept.py, stage 03b_visual_concept)
- ✅ B25 — закрывается через B23+B24 (visual-strategist решает проблему на уровне 03b)
- ✅ B26 — реализован (generate-mockup.py, side-by-side A/B mockup в начале этапа 05)
- ✅ B27–B28 — реализованы (routing правок в brand-architect, decisions log)
- ✅ B29 — реализован (wiki run_id корреляция для субагентов)
- 🔮 B5–B20 — по мере роста системы

Если вопросы по конкретной задаче — спроси через `/brainstorming <id>` (например `/brainstorming B6`).
