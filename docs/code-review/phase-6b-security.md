# Phase 6B — WP-admin Security (deep)

**Дата:** 2026-05-23
**Скоуп:** все PHP и JS-файлы mu-plugin `landing-config` + публичный REST endpoint `/wp-json/landing/v1/lead` + 6 CRM-адаптеров.
**Главная зона риска во всём проекте.**
**Инструмент:** code-reviewer skill (read-only)

## Executive Summary (для руководства)

Главная находка: **REST endpoint для приёма заявок (`/wp-json/landing/v1/lead`) защищён только honeypot-полем + rate-limit per-IP (10 req/час)**. Этого **недостаточно** против целевой атаки. Honeypot блокирует только примитивных ботов, которые заполняют все поля; продвинутый бот легко обходит. Rate-limit per-IP обходится через прокси/VPN/Tor. Никакой проверки Origin/Referer нет. Атакующий может бесконтрольно слать поддельные заявки в базу клиентов → засорить CRM, обрушить email-уведомления, ввести в заблуждение маркетолога.

Вторая критическая находка: **множественные XSS-векторы** через `<?php echo $var ?>` без `esc_*` обёрток. Самые опасные точки: (1) `llms-txt-rewrite.php:24` — `echo $content` напрямую из wp_option (super-admin контроль, но **любой XSS в админке = catastrophic** если cookie-сессия украдена); (2) admin-snippets.php — `<?php echo $segment ?>` в hidden input (segment приходит из `$_GET`, контролируем атакующим); (3) admin-cta.php — `<?php echo $t ?>` где `$t` — тип CTA (приходит из effective config). По строгому правилу WP «escape on output» — это нарушения, но severity зависит от того, может ли атакующий контролировать значение.

Третья: **сырые SQL-запросы без `$wpdb->prepare()`** в `admin-leads.php:48,197`: `"SELECT * FROM \`$table\` ORDER BY ..."`. Имя таблицы собирается через `get_leads_table_name()` (helper, не user-input), поэтому SQL-injection в строгом смысле здесь нет. Но **отсутствие `prepare()` — это нарушение паттерна**, и при будущем рефакторинге легко вставить user-input в этот же запрос.

Четвёртая (опасная **в logs**): **Telegram bot-токен передаётся в URL** (`https://api.telegram.org/bot{$token}/sendMessage`). Этот URL **попадает в access-log хостинга** (Бегет логирует все исходящие запросы). Любой кто получит доступ к access-log (другой сайт на том же IP, утечка backup) — получит токен. Telegram API поддерживает токен в теле запроса — стандартная практика для конфиденциальных токенов.

Положительные находки: **encryption module реализован корректно** (AES-256-GCM с auth tag, random IV per encryption, ключ из wp-config). **Snippets sanitized через `wp_kses`** с whitelist. **`switch_to_blog` корректно парен с `restore_current_blog`** в большинстве мест, и `cascade.php` использует try/finally — это правильный паттерн. **152-ФЗ согласие реально проверяется** на REST endpoint (`pd_consent !== '1'` → 400). **CRM-вызовы все имеют timeout=10** (нет DoS-вектора через зависший CRM).

**Всё — на согласование. Никаких действий не выполнено.**

---

## 🔴 Критичные

### #1 🔴 КРИТИЧНО — REST endpoint /lead защищён только honeypot+rate-limit; продвинутый бот обойдёт, можно засорить базу заявок

**Что это значит простыми словами:**
Главный публичный endpoint системы — `POST /wp-json/landing/v1/lead` — принимает заявки от посетителей лендинга. Чтобы любой посетитель мог отправить (это его задача), endpoint открыт всем: `permission_callback => '__return_true'`. Защита от ботов реализована минимально:

1. **Honeypot**: скрытое поле `website` должно быть пустым (бот, заполняющий все поля, поймёт что попался).
2. **Rate-limit**: не более 10 заявок в час с одного IP.
3. **152-ФЗ согласие**: проверка `pd_consent === '1'`.

Это **достаточно** против примитивных скриптов-спамеров. Это **не защита** против:
- продвинутого бота, который прочитал HTML и пропускает honeypot;
- атакующего, использующего пул прокси/VPN/Tor — каждый IP делает по 1-2 запроса в час;
- вредоносного скрипта с лендинга-конкурента, который инджектится в форму и шлёт заявки в фон;
- атакующего, который знает API и шлёт прямые POST'ы с разными User-Agent.

**Чем грозит бизнесу:**
- **Засорение базы клиента**: 1000 поддельных заявок за ночь — маркетолог не разберёт, real CRM-leads теряются среди мусора.
- **DDoS email-уведомлений**: каждая заявка триггерит `wp_mail($admin_email, ...)`. Если хостинг ограничит отправку — реальные заявки перестанут приходить.
- **DoS базы**: 1М заявок займут storage. Бегет может отрубить базу.
- **Финансовый ущерб клиента**: если клиент платит за CRM по числу записей (AmoCRM, Bitrix24) — атакующий может умножить счёт.
- **Юридический риск**: атакующий может включить в `message` оскорбления, незаконный контент — а маркетолог увидит это уже после того как уведомление ушло на email.

**Оценка срочности (мнение ревьюера, на согласование):** **БЛОКИРУЕТ запуск в прод для клиентов с известной целевой аудиторией** (юристы, медицина, недвижимость — там целевые атаки реальны).

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`
- Строка 14: `'permission_callback' => '__return_true'` — открыт всем (это by design для публичной формы).
- Строки 22-24: honeypot — `$params['website']` должно быть пустым.
- Строки 27-33: rate-limit per IP через transient (`landing_lead_rl_<md5(ip)>`, 10/час).
- Строки 36-42: pd_consent check.
- **Что отсутствует:**
  - Нет проверки `$_SERVER['HTTP_ORIGIN']` или `HTTP_REFERER` (anti-direct-API-call).
  - Нет CAPTCHA (reCAPTCHA / hCaptcha / Cloudflare Turnstile).
  - Нет ML/heuristic spam-detection (например, проверка наличия URL в message — типичный спам-паттерн).
  - Нет per-fingerprint rate-limit (только per-IP — обходится прокси).

**Воспроизведение атаки (PoC):**
```bash
# 100 поддельных заявок за минуту с разных IP через прокси-пул:
for i in $(seq 1 100); do
  curl -X POST https://landing.example.com/wp-json/landing/v1/lead \
    -x "http://proxy${i}.example.com:8080" \
    -d "name=Test${i}" -d "phone=+79000000${i}" \
    -d "pd_consent=1" -d "message=spam${i}"
done
```

**Возможные пути решения (на согласование, приоритет от дешёвого к дорогому):**
1. **Origin/Referer check**: «принимать только если Origin начинается с домена клиента». 5 минут работы. Останавливает 80% direct-API атак.
2. **Cloudflare Turnstile** (бесплатная CAPTCHA): добавить frontend widget + backend verify. ~1 час работы. Останавливает 95% ботов.
3. **Spam-фильтр на content**: запретить >1 URL в message, >3 emoji подряд, кириллицу+латиницу одновременно в имени.
4. **Email-уведомление throttle**: не более 1 email в 5 минут даже если заявок много.
5. **Опциональный per-domain (а не per-IP) rate-limit** через cookie или browser fingerprint.

---

### #2 🔴 КРИТИЧНО — Множественные unescaped XSS-векторы через `<?php echo $var ?>` без `esc_html/esc_attr`

**Что это значит простыми словами:**
WordPress правило безопасности: **«любая динамическая переменная при выводе в HTML обязана быть обёрнута в `esc_html()` / `esc_attr()` / `esc_url()`»**. Это защищает от XSS — внедрения JS-кода в HTML. Если переменная не обёрнута и атакующий может её контролировать → атакующий может выполнить JS в браузере жертвы (украсть cookie, сменить пароль, угнать сессию).

В коде mu-plugin **20+ мест с unescaped echo**. Не все одинаково опасны: часть переменных — серверные константы (тип CTA из effective config, скорее всего безопасно), часть — user-input через `$_GET` (опасно). Точная classification по каждому требует разбора.

**Самые опасные места:**

1. **`llms-txt-rewrite.php:24` — `echo $content;`** — содержимое llms.txt из option, контролируется super-admin. Угроза: если super-admin аккаунт взломан или есть инсайдер → атакующий пишет JS в llms.txt. Каждый посетитель страницы `/llms.txt` получает XSS.

2. **`admin-snippets.php:553` — `<input type="hidden" name="segment" value="<?php echo $segment; ?>">`** — `$segment` приходит из `$_GET['segment']`. Атакующий заводит ссылку `?segment="><script>alert(1)</script>` → super-admin кликает → XSS в админке.

3. **`admin-snippets.php:423,550` — `echo $domain`** — domain берётся из site row, формально из БД, но если БД заражена (через другой вектор) → XSS.

4. **`admin-cta.php:80` — `<option value="<?php echo $t; ?>"`** — `$t` тип CTA, итерируется по массиву конфига; меньшее зло, но тот же паттерн.

5. **`segment-selector.php:25` — `<option value="<?php echo $bid; ?>"`** — `$bid` blog_id из БД, обычно integer; но `intval` нет — формально может быть user input.

**Чем грозит бизнесу:**
- **Угон сессии super-admin** через XSS в админке → атакующий получает полный контроль над сайтом → крадёт лиды/CRM-ключи/деплоит шеллы.
- **XSS в публичном `/llms.txt`** → каждый посетитель страницы заражён.
- **XSS в hidden input segment** → классический stored-XSS через query parameter.

**Оценка срочности (мнение ревьюера, на согласование):** **БЛОКИРУЕТ прод**. Это базовое правило WP-разработки. WP Security Audit Tools (Wordfence, Sucuri) при сканировании сразу фалбят такой код.

**Статус решения:** ☐ на согласовании

---

**Технические детали (полный список):**

Найдено через `grep -rnE 'echo \$|<\?= \$' --exclude-dir=esc_html`:

| Файл:строка | Код | Источник переменной | Severity |
|---|---|---|---|
| `llms-txt-rewrite.php:24` | `echo $content;` | wp_option (super-admin) | 🔴 |
| `admin-snippets.php:553` | `value="<?php echo $segment; ?>"` | $_GET | 🔴 |
| `admin-snippets.php:550` | `echo $snippet ? ... : ...; }` (with `$domain` interpolation) | DB row | 🟠 |
| `admin-snippets.php:423` | `Снипеты — <?php echo $domain; ?>` | DB row | 🟠 |
| `admin-snippets.php:297` | `<h1><?php echo $snippet ? 'Edit ...' : ...` | static literal | 🟢 |
| `admin-snippets.php:253,326,327,458,575,576,586,587` | echo $pos/$sc/$s['enabled'] | constants | 🟡 |
| `admin-cta.php:80` | `value="<?php echo $t; ?>"` | array key | 🟡 |
| `admin-leads.php:83` | `<strong><?php echo $bu; ?></strong>` | integer count | 🟢 (всё равно нужно `(int)`) |
| `cookie-banner/admin-network.php:244,245` | `name="categories[<?php echo $i; ?>]..."` | loop index | 🟢 |
| `segment-selector.php:25` | `<option value="<?php echo $bid; ?>"` | DB/loop | 🟡 |
| `seo-audit/admin-network.php:199` | `<?php echo $segment === 'all' ? ... : ...` | static literals | 🟢 |
| `seo-audit/tabs/ai_readiness.php:54` | `<?php echo $is_hard ? '🔴 hard' : '🟡 soft'; ?>` | bool ternary | 🟢 |

**Возможные пути решения:**
- 🔴/🟠 точки — **обязательно** обернуть в `esc_html()` / `esc_attr()` для атрибутов / `wp_kses()` для llms.txt (если HTML-теги нужны).
- 🟡/🟢 точки — обернуть для согласованности паттерна (даже если переменная безопасна сейчас, при будущем рефакторинге кто-то добавит user-input).
- Включить статический анализатор (PHPCS с WordPress-Extra ruleset) в pre-commit hook.

---

### #3 🔴 КРИТИЧНО — Telegram bot-токен в URL → попадает в access-log хостинга

**Что это значит простыми словами:**
Telegram API позволяет отправлять токен бота двумя способами: (1) в URL `https://api.telegram.org/bot{TOKEN}/sendMessage`, (2) в HTTP-заголовке `Authorization`. Mu-plugin использует первый способ. **Каждый исходящий запрос с токеном в URL попадает в access-log хостинга**:

- Бегет логирует все исходящие HTTPS-запросы (URL без body) для биллинга и безопасности.
- Backup-файлы access-log часто хранятся месяцами.
- Если backup утечёт (взломан хостер, ошибка сотрудника) — токен любого Telegram-бота клиента в открытом виде.

С Telegram bot-токеном атакующий: пишет в группу клиента под видом бота, удаляет сообщения, читает входящие callback'и.

**Чем грозит бизнесу:**
- Утечка bot-токенов всех клиентов системы при компрометации хостера.
- Сложно ротировать: чтобы заменить токен, нужно вручную пересоздать бота, обновить настройки в админке каждого клиента.
- Регуляторные риски: если бот использовался для работы с PД (например, отправка ОТП-кодов) — это утечка middleware-credentials.

**Оценка срочности (мнение ревьюера, на согласование):** стоит решить до сдачи клиенту. Не блокирует функционал, но в случае инцидента — масштабный compromise.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php`
- Строка 64: `\wp_remote_post("https://api.telegram.org/bot{$token}/sendMessage", ...)`
- Строка 76: `\wp_remote_get("https://api.telegram.org/bot{$token}/getMe", ...)`
- Telegram API support обоих способов (см. https://core.telegram.org/bots/api#authentication).
- Возможные пути решения:
  - Перейти на header-based auth: `wp_remote_post('https://api.telegram.org/bot/sendMessage', ['headers' => ['Authorization' => 'Bot ' . $token], ...])`. ❌ Это **не работает** для Telegram (он требует токен в URL по дизайну API).
  - Альтернатива: **не логировать токен в /logs/** на стороне Beget — настроить access-log mask для api.telegram.org. Требует Beget support.
  - Третий вариант: проксировать через свой backend, который имеет токен в env, и наружу не светит. Сложно, дорого.
  - **Реалистичный путь:** ротировать токен раз в месяц (через `BotFather`), документировать процедуру.

(Telegram API дизайн исторический — это известная проблема всей экосистемы Telegram-ботов.)

---

## 🟠 Важные

### #4 🟠 ВАЖНО — Сырые SQL в `admin-leads.php` без `$wpdb->prepare()` — нарушение паттерна, риск регрессии

**Что это значит простыми словами:**
Стандартный паттерн WP-разработки: **все SQL-запросы обёрнуты в `$wpdb->prepare()`**. Это автоматически escape'ит user-input. В `admin-leads.php` найдено 2 случая прямой строки:

```php
$count_rows = $wpdb->get_results(
    "SELECT processed_status AS s, COUNT(*) AS n FROM `$table` GROUP BY processed_status",
    ARRAY_A
);
$rows = $wpdb->get_results("SELECT * FROM `$table` ORDER BY created_at DESC", ARRAY_A);
```

**Сейчас это не SQL-injection**, потому что `$table` берётся из helper'а (не user-input). Но:
- **Нарушает паттерн** — кто-то при будущем рефакторинге может добавить `WHERE status='$user_input'` без prepare.
- WP Security Audit Tools пометят как warning.
- При code review «не prepare» — это всегда red flag.

**Чем грозит бизнесу:**
- Регрессия SQL-injection при будущем изменении.
- WP-аудитор клиента (если будет ревьюить плагин) обозначит как замечание.

**Оценка срочности (мнение ревьюера, на согласование):** не блокирует, но это базовая гигиена.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `admin-leads.php:48` — count query
- Файл: `admin-leads.php:197` — full SELECT
- Файл: `admin-leads-network.php:32` — есть get_results (полнее не проверял в этой выгрузке)
- Файл: `lead-status-log.php:45` — есть get_results
- Возможные пути решения:
  - Завернуть в `prepare()`: `$wpdb->prepare("SELECT * FROM %i ORDER BY created_at DESC", $table)` (WP 6.2+ поддерживает `%i` для identifier).
  - Для совместимости со старыми WP: `esc_sql($table)` хотя бы.

---

### #5 🟠 ВАЖНО — Bitrix24 webhook URL берётся из user-config — потенциальный SSRF

**Что это значит простыми словами:**
В `Bitrix24Adapter.php:63,76` запрос идёт на `$endpoint` — переменную, которая собирается из настроек CRM (вводит маркетолог в админке). Если валидации URL нет — маркетолог-аккаунт под угрозой может прописать `http://localhost:6379/INFO\r\n` (Redis), `http://169.254.169.254/latest/meta-data/` (AWS metadata service) и т.п. — это SSRF (Server-Side Request Forgery): сервер делает запрос куда атакующий укажет.

В случае mu-plugin маркетолог-роль обычно доверенная (super-admin), но **если атакующий получит maintain-level доступ** (фишинг → маркетолог) — он может скрапить внутреннюю сеть Бегета.

**Чем грозит бизнесу:**
- Атакующий с доступом к маркетолог-аккаунту → SSRF → может прочитать локальные redis/memcached/PHP-FPM статусы.
- На некоторых конфигурациях Beget — доступ к metadata-сервисам облака.

**Оценка срочности (мнение ревьюера, на согласование):** низкая (требует уже скомпрометированного админ-аккаунта), но базовая защита нужна.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `adapters/Bitrix24Adapter.php:63,76`.
- Endpoint берётся из конфига integration: `$endpoint = $settings['endpoint']`.
- Валидации схемы (только `https://*.bitrix24.ru` или `https://*.bitrix24.com`) **не зафиксировано** в коде (требует более глубокого Read адаптера).
- Возможные пути решения:
  - whitelist схем: `if (!preg_match('#^https://[a-z0-9-]+\.bitrix24\.(ru|com|de|fr)/#', $endpoint)) return error;`
  - `wp_http_validate_url($endpoint)` — встроенный WP-валидатор.
  - блок `file://`, `gopher://`, `php://` через preg_match.

То же замечание применимо к `AmoCRMAdapter` (URL составной: `{$sub}.amocrm.ru`, где `$sub` — поддомен из конфига).

---

### #6 🟠 ВАЖНО — REST endpoint пишет `$_SERVER['REMOTE_ADDR']` и `User-Agent` напрямую в БД без анонимизации (152-ФЗ ст.7)

**Что это значит простыми словами:**
По 152-ФЗ статья 7 (принципы обработки ПД) — оператор обязан **минимизировать** обрабатываемые ПД. IP-адрес и User-Agent посетителя — это ПД (по позиции Роскомнадзора). Они пишутся в `landing_leads.ip` и `landing_leads.user_agent` **в полном виде**. Никакой анонимизации (например, обнуление последнего октета IPv4 — стандарт GDPR) нет.

Это **не безопасность в строгом смысле**, но **юридический риск**: при проверке Роскомнадзора оператор должен обосновать почему хранит полный IP. Стандартный ответ «для anti-fraud» работает первые 30 дней; долгосрочное хранение в clear требует обоснования.

**Чем грозит бизнесу:**
- Штраф РКН при проверке: до 75К ₽ за «избыточный сбор ПД» (КоАП 13.11 ч.1).
- При утечке БД — больший масштаб публичной катастрофы (IP+phone+email = identifiable user).

**Оценка срочности (мнение ревьюера, на согласование):** не блокирует MVP, но риск растёт с числом клиентов.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `rest-lead.php:66-67`.
- Возможные пути решения:
  - анонимизация IP: `$ip_anon = preg_replace('/\.\d+$/', '.0', $ip);` (для IPv4).
  - удаление IP через 30 дней (cron job).
  - не писать User-Agent если он не нужен для анализа.
  - явно в Privacy Policy указать «храним IP для anti-fraud 30 дней» (если решение оставить как есть).

---

### #7 🟠 ВАЖНО — Encryption module: ключ зависит от `SECURE_AUTH_KEY/SALT` wp-config — ротация ломает все зашифрованные данные

**Что это значит простыми словами:**
В `encryption.php` ключ выводится из `SECURE_AUTH_KEY` и `SECURE_AUTH_SALT` из wp-config через sha256. WP-документация рекомендует периодически ротировать эти ключи (для invalidation сессий). **Если админ ротирует SECURE_AUTH_KEY — все ранее зашифрованные CRM-credentials становятся нечитаемыми**, потому что ключ изменился. Восстановить — невозможно, нужно вручную ввести все credentials заново.

В коде это **задокументировано**: `error_log('[landing-config] decrypt: openssl_decrypt returned false (wrong key, tampered ct, or rotated salt)');` (строка 73). Но: маркетолог об этом не предупреждается, и при обновлении WP админ может не понять что ротация ломает плагин.

**Чем грозит бизнесу:**
- После ротации wp-config keys — все CRM-интеграции перестают работать молча.
- Маркетолог видит «не отправляются заявки в CRM» через несколько часов — может не связать с ротацией.
- При recovery нужно перенастраивать AmoCRM/Bitrix/Telegram credentials — это потеря рабочего дня.

**Оценка срочности (мнение ревьюера, на согласование):** низкая. Edge case, но реальный.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `encryption.php`, функция `_key()` (строка ~19).
- Возможные пути решения:
  - использовать **отдельную константу** в wp-config (`LANDING_CONFIG_KEY`) которую админ явно не ротирует.
  - при decrypt-failure: log + admin notice «зашифрованные данные не читаются, проверьте конфиг».
  - re-encrypt-on-key-change хелпер.

---

## 🟡 Стоит внимания

### #8 🟡 СТОИТ ВНИМАНИЯ — `switch_to_blog` используется в loop в `admin-pages.php:64` — N+1 паттерн

**Что это значит простыми словами:**
В `admin-pages.php` для рендера корневого меню в loop'е по всем сайтам вызывается `switch_to_blog($bid)` → читает option → `restore_current_blog()`. На multisite с 50 сайтами это 100 BLOG_SWITCH'ей + 50 option-read'ов. Каждый switch — это переинициализация WP global state.

**Чем грозит:** медленная загрузка корневого меню для multisite с большим числом сайтов.

**Оценка срочности:** низкая. Связано с фазой 2 #5 (heavy operations).

**Статус решения:** ☐ на согласовании

---

### #9 🟡 СТОИТ ВНИМАНИЯ — Email-уведомления не throttle'ятся — DoS-вектор

При каждой заявке `wp_mail($admin_email, ...)`. Если злоумышленник прорвал rate-limit — каждая заявка генерирует email. Бегет/SMTP-провайдер ограничит отправку, реальные уведомления потеряются.

**Возможное решение:** batch'ить email — «1 email с N заявками раз в 5 минут».

---

### #10 🟡 СТОИТ ВНИМАНИЯ — `error_log()` в encryption-failure может содержать sensitive context

```php
error_log('[landing-config] decrypt: openssl_decrypt returned false (wrong key, tampered ct, or rotated salt)');
```

Сам по себе безопасно. Но проверить **все** `error_log()` вызовы (грep не сделан в этой фазе) — не пишутся ли там phone/email/CRM-credentials.

---

## 🟢 К сведению (положительные)

### #11 🟢 К СВЕДЕНИЮ — Encryption module реализован корректно (AES-256-GCM, random IV, auth tag)

```php
$iv = random_bytes(openssl_cipher_iv_length(CIPHER));
$ct = openssl_encrypt($plaintext, CIPHER, _key(), OPENSSL_RAW_DATA, $iv, $tag);
```

Random IV per encryption ✅, OPENSSL_RAW_DATA ✅, authenticated encryption (GCM с `$tag`) ✅. Это правильный паттерн. Зафиксировано.

---

### #12 🟢 К СВЕДЕНИЮ — Snippets защищены через `wp_kses` с whitelist

`snippets.php:64-66` — `wp_kses($code, ALLOWED_HTML)`. Whitelist пользовательских HTML-тегов. Это правильный подход (хотя стоит проверить что в ALLOWED_HTML нет `<script>` без capability-check super-admin).

---

### #13 🟢 К СВЕДЕНИЮ — REST endpoint sanitizes input через `sanitize_text_field` + `wp_unslash`

```php
$name = sanitize_text_field(wp_unslash($params['name'] ?? ''));
$email = sanitize_email(wp_unslash($params['email'] ?? ''));
```

Правильный паттерн ✅.

---

### #14 🟢 К СВЕДЕНИЮ — CRM-вызовы все имеют `timeout=10` (нет DoS через зависший CRM)

В каждом адаптере найден `'timeout' => 10` — это защита от ситуации «CRM завис, наш обработчик зависает на 60 секунд, PHP-FPM worker занят». ✅.

---

### #15 🟢 К СВЕДЕНИЮ — `switch_to_blog` корректно парен с `restore_current_blog`; `cascade.php` использует try/finally

```php
\switch_to_blog($blog_id);
try { ... }
finally { \restore_current_blog(); }
```

Это правильный exception-safe паттерн. Большинство мест в коде также парные (хоть и без try/finally). ✅

---

### #16 🟢 К СВЕДЕНИЮ — `sslverify` не отключен ни в одном адаптере (WP default = true)

Grep по `sslverify` в `adapters/` — 0 матчей. WP по умолчанию проверяет SSL-сертификаты. ✅

---

### #17 🟢 К СВЕДЕНИЮ — 152-ФЗ согласие реально enforce'нится на REST endpoint

`rest-lead.php:37-42` — `pd_consent !== '1'` → 400. Timestamp `pd_consent_granted_at` пишется в БД (строка 70). Это **реально соответствует** заявлению CLAUDE.md о соблюдении 152-ФЗ ст.9. ✅

---

## Метрики

- PHP-файлов в mu-plugin landing-config: **~55**
- REST endpoints зарегистрировано: **1** (`/wp-json/landing/v1/lead`)
  - С `permission_callback` НЕ `__return_true`: **0** (этот публичный — единственный)
- `admin_post_*` handlers: 13 (см. фазу 6A) — все с nonce ✅ и capability ✅
- `wp_ajax_*` handlers: 0
- CRM-адаптеров: **6** (Email, Telegram, WhatsApp, AmoCRM, Bitrix24, HubSpot)
- Из них с `timeout`: **6** ✅
- Из них с явным `sslverify`: **0** (но default WP = true) ✅
- Из них с whitelist URL-схем: **0** ❌ (см. #5 SSRF)
- Encryption: **AES-256-GCM** ✅
- Sensitive-data в URL: **1** (Telegram bot-токен, см. #3)
- Unescaped XSS-векторов (echo без esc_*): **~20** мест, из них:
  - 🔴 critical (user-controlled или super-admin-controlled): **2-3** (см. #2)
  - 🟠 high (DB-controlled): **2-3**
  - 🟡 medium (constants, integers): **~15** (нарушение паттерна, но low impact)
- Сырых SQL без `prepare()`: **4 матча** в 3 файлах (admin-leads.php, admin-leads-network.php, lead-status-log.php) — все с safe table-name, но паттерн нарушен (см. #4)
- `switch_to_blog` пар: ~10, проверены — все имеют `restore_current_blog` в обозримой близости ✅

---

## Глоссарий

- *REST endpoint* — URL, на который браузер/сервер делает HTTP-запрос за данными. Здесь `/wp-json/landing/v1/lead` — публичный приём заявок с лендинга.
- *honeypot* — скрытое поле формы; если бот его заполнил — отбраковываем. Защита от примитивных ботов.
- *rate-limit* — ограничение числа запросов в единицу времени. Per-IP легко обходится прокси.
- *XSS (cross-site scripting)* — внедрение JS в страницу. Выполнится в браузере жертвы, украдёт сессию.
- *SQL injection* — внедрение SQL в запрос через user-input. Открывает БД атакующему.
- *SSRF (server-side request forgery)* — атакующий заставляет сервер обратиться по своему URL (например, на внутреннюю сеть).
- *AES-256-GCM* — современный алгоритм аутентифицированного шифрования. Лучшая практика.
- *random IV* — случайный «вектор инициализации» для каждого шифрования. Без него — повторные сообщения видны.
- *auth tag* — встроенный MAC у GCM-режима; ловит tampering ciphertext.
- *nonce* — одноразовый токен от CSRF.
- *capability check* — проверка прав пользователя в WP (например `manage_options`).
- *switch_to_blog / restore_current_blog* — WP-функции переключения контекста между сайтами в multisite. Парные.
- *wp_kses* — WP-функция для очистки HTML с whitelist разрешённых тегов.
- *esc_html / esc_attr / esc_url* — WP-функции для escape вывода (XSS-защита).
- *prepare* — `$wpdb->prepare()` — безопасное составление SQL с placeholder'ами.
- *sslverify* — параметр `wp_remote_*` для проверки SSL-сертификата у удалённого сервера.
- *152-ФЗ* — российский закон о ПД.
- *ОТП-код* — одноразовый пароль (one-time password).
- *PoC (proof of concept)* — минимальная демонстрация работы уязвимости.

---

## См. также

- **REST endpoint:** `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`
- **Encryption:** `skills/wp-landing-config/mu-plugin/landing-config/includes/encryption.php`
- **CRM adapters:** `skills/wp-landing-config/mu-plugin/landing-config/adapters/`
- **UI wiring (предыдущая фаза):** `phase-6a-ui-wiring.md`
- **Admin flow (следующая фаза):** `phase-6c-admin-flow.md`

---

## Что НЕ покрыто в этом отчёте

1. **Запуск `/security-review` встроенного скилла** для cross-проверки findings — не запущен (это требует отдельной фазы, плейбук рекомендует параллельный запуск).
2. **Глубокий анализ AmoCRMAdapter и HubSpotAdapter** (URL составление, OAuth flow, token storage) — Read целиком не делался.
3. **DB-schema analysis** — поля `wp_<bid>_landing_leads` и их размеры/индексы — для определения возможных DB-flood атак.
4. **JS-XSS в `banner.js`** — frontend cookie-banner — не анализировался на DOM-XSS.
5. **CSP (Content Security Policy) audit** — какие headers mu-plugin шлёт, могут ли быть усилены.
6. **i18n security** (translation-based XSS) — переводы не проверялись.
7. **Capability granularity audit** — каждый network-page реально требует `manage_network_options`? Не каждый по факту проверен глубоко.
8. **Adapter-specific OAuth/token-refresh logic** — не входило в quick-pass.
9. **PoC для каждого finding** — описаны concept, без рабочих exploit'ов (read-only режим, не пентестим).
