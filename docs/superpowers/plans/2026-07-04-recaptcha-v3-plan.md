# reCAPTCHA v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить защиту форм через Google reCAPTCHA v3 — настройка ключей в WP Admin (Общие настройки), серверная проверка score в REST endpoint, логирование score в таблице заявок и отображение в списке заявок.

**Architecture:** Site Key хранится открыто в `wp_options`, Secret Key шифруется через существующий `encryption.php` (AES-256-GCM). JS читает Site Key из `window.lpRecaptchaSiteKey`, добавляет токен к форме перед отправкой. PHP в `rest-lead.php` проверяет токен через `siteverify`, при score ниже порога возвращает 400. Score пишется в новую колонку `recaptcha_score` таблицы `landing_leads`.

**Tech Stack:** PHP 8.1, WordPress mu-plugin, Google reCAPTCHA v3 API, существующий `encryption.php`, `db.php` (dbDelta pattern), `admin-general-settings.php`, `rest-lead.php`, `lead-form.js`.

---

## Затрагиваемые файлы

| Файл | Действие |
|---|---|
| `includes/db.php` | Добавить колонку `recaptcha_score`, migration function |
| `includes/rest-lead.php` | Читать `g-recaptcha-response`, вызывать siteverify, писать score |
| `includes/admin-general-settings.php` | Секция reCAPTCHA: site key, secret key (encrypt), score threshold, enable/disable |
| `includes/admin-leads.php` | Колонка Score в таблице заявок |
| `landing-config.php` | Вызов новой migration function |
| `assets/js/lead-form.js` (hibridcars-uae) | Получать токен от grecaptcha перед fetch |

---

### Task 1: Миграция БД — добавить колонку `recaptcha_score`

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`

- [ ] **Step 1: Добавить колонку в схему таблицы**

В функции `create_tables_for_current_blog()` добавить строку после `roistat_visit`:

```php
roistat_visit VARCHAR(64) NOT NULL DEFAULT '',
recaptcha_score DECIMAL(3,2) NULL,
ip VARCHAR(45) NOT NULL DEFAULT '',
```

- [ ] **Step 2: Добавить migration function**

После `maybe_migrate_roistat_visit()` добавить:

```php
/**
 * One-time migration: add recaptcha_score column to existing installs.
 * Marker: landing_config_migration_recaptcha_score
 */
function maybe_migrate_recaptcha_score(): void {
    if (get_site_option('landing_config_migration_recaptcha_score')) {
        return;
    }

    $ok = true;
    if (is_multisite()) {
        $sites = get_sites(['number' => 0]);
        foreach ($sites as $site) {
            switch_to_blog((int)$site->blog_id);
            try {
                create_tables_for_current_blog();
            } catch (\Throwable $e) {
                $ok = false;
            } finally {
                restore_current_blog();
            }
        }
    } else {
        try {
            create_tables_for_current_blog();
        } catch (\Throwable $e) {
            $ok = false;
        }
    }

    if ($ok) {
        update_site_option('landing_config_migration_recaptcha_score', true);
    }
}
```

- [ ] **Step 3: Подключить migration в `landing-config.php`**

В `landing-config.php` после вызова `maybe_migrate_roistat_visit()` добавить:

```php
\LandingConfig\DB\maybe_migrate_recaptcha_score();
```

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/db.php
git add skills/wp-landing-config/mu-plugin/landing-config/landing-config.php
git commit -m "feat(recaptcha): add recaptcha_score column migration"
```

---

### Task 2: Настройки reCAPTCHA в General Settings

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-general-settings.php`

- [ ] **Step 1: Добавить save-логику для recaptcha полей**

В блоке `if (isset($_POST['lp_general_nonce']) && wp_verify_nonce(...))` добавить после сохранения rate_limit:

```php
// reCAPTCHA settings
$rc_enabled    = !empty($_POST['lp_recaptcha_enabled']);
$rc_site_key   = sanitize_text_field($_POST['lp_recaptcha_site_key'] ?? '');
$rc_secret_raw = sanitize_text_field($_POST['lp_recaptcha_secret_key'] ?? '');
$rc_threshold  = min(1.0, max(0.0, (float)($_POST['lp_recaptcha_threshold'] ?? 0.5)));

update_option('lp_recaptcha_enabled',   (int) $rc_enabled);
update_option('lp_recaptcha_site_key',  $rc_site_key);
update_option('lp_recaptcha_threshold', $rc_threshold);

// Encrypt secret key only if non-empty and changed (placeholder не перезаписывает)
if ($rc_secret_raw !== '' && $rc_secret_raw !== '***') {
    $encrypted = \LandingConfig\Encryption\encrypt($rc_secret_raw);
    update_option('lp_recaptcha_secret_key_enc', $encrypted);
}
```

- [ ] **Step 2: Добавить чтение текущих значений**

После блока чтения rate_limit добавить:

```php
$rc_enabled   = (bool) get_option('lp_recaptcha_enabled', false);
$rc_site_key  = (string) get_option('lp_recaptcha_site_key', '');
$rc_threshold = (float) get_option('lp_recaptcha_threshold', 0.5);
$rc_has_secret = (string) get_option('lp_recaptcha_secret_key_enc', '') !== '';
```

- [ ] **Step 3: Добавить HTML-секцию в форму**

После закрывающего `</table>` секции «Защита от спама» добавить:

```php
<h2>reCAPTCHA v3</h2>
<p class="description" style="margin-bottom:1em;">
    Получить ключи: <a href="https://www.google.com/recaptcha/admin/create" target="_blank">google.com/recaptcha/admin/create</a> → тип «Score based (v3)».
</p>
<table class="form-table" role="presentation">
    <tr>
        <th scope="row">Включить reCAPTCHA</th>
        <td>
            <label>
                <input type="checkbox" name="lp_recaptcha_enabled" value="1" <?php checked($rc_enabled); ?>>
                Проверять токен при отправке форм
            </label>
        </td>
    </tr>
    <tr>
        <th scope="row"><label for="lp_recaptcha_site_key">Site Key (публичный)</label></th>
        <td>
            <input type="text" id="lp_recaptcha_site_key" name="lp_recaptcha_site_key"
                   value="<?php echo esc_attr($rc_site_key); ?>"
                   class="regular-text" placeholder="6Lc...">
            <p class="description">Вставляется в JS на странице.</p>
        </td>
    </tr>
    <tr>
        <th scope="row"><label for="lp_recaptcha_secret_key">Secret Key (секретный)</label></th>
        <td>
            <input type="text" id="lp_recaptcha_secret_key" name="lp_recaptcha_secret_key"
                   value="<?php echo $rc_has_secret ? '***' : ''; ?>"
                   class="regular-text" placeholder="6Lc...">
            <p class="description">
                <?php if ($rc_has_secret): ?>
                    Ключ сохранён (зашифрован). Введите новый, чтобы заменить.
                <?php else: ?>
                    Хранится в зашифрованном виде. Никогда не передаётся в JS.
                <?php endif; ?>
            </p>
        </td>
    </tr>
    <tr>
        <th scope="row"><label for="lp_recaptcha_threshold">Минимальный score</label></th>
        <td>
            <input type="number" id="lp_recaptcha_threshold" name="lp_recaptcha_threshold"
                   value="<?php echo esc_attr($rc_threshold); ?>"
                   min="0" max="1" step="0.1" style="width:80px;">
            <p class="description">От 0.0 (бот) до 1.0 (человек). Рекомендуется 0.5. Заявки с score ниже порога отклоняются.</p>
        </td>
    </tr>
</table>
```

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-general-settings.php
git commit -m "feat(recaptcha): add reCAPTCHA v3 settings UI in General Settings"
```

---

### Task 3: Серверная проверка в REST endpoint

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`

- [ ] **Step 1: Добавить helper-функцию verify_recaptcha()**

После функции `get_rate_limit()` добавить:

```php
/**
 * Verify reCAPTCHA v3 token. Returns score (0.0–1.0) or null on failure/disabled.
 * Returns false if score is below threshold (bot detected).
 */
function verify_recaptcha(string $token): float|false|null {
    if (!(bool) get_option('lp_recaptcha_enabled', false)) {
        return null; // disabled — skip
    }

    $secret_enc = (string) get_option('lp_recaptcha_secret_key_enc', '');
    if ($secret_enc === '') {
        return null; // not configured — skip
    }

    $secret = \LandingConfig\Encryption\decrypt($secret_enc);
    if ($secret === '') {
        return null;
    }

    if ($token === '') {
        return false; // enabled but no token provided
    }

    $response = wp_remote_post('https://www.google.com/recaptcha/api/siteverify', [
        'body'    => ['secret' => $secret, 'response' => $token],
        'timeout' => 5,
    ]);

    if (is_wp_error($response)) {
        return null; // network error — fail open (don't block legit users)
    }

    $data = json_decode(wp_remote_retrieve_body($response), true);
    if (empty($data['success'])) {
        return false;
    }

    $score     = (float) ($data['score'] ?? 0.0);
    $threshold = (float) get_option('lp_recaptcha_threshold', 0.5);

    return $score >= $threshold ? $score : false;
}
```

- [ ] **Step 2: Вызвать проверку в handle_lead() и сохранить score**

В `handle_lead()` после honeypot-проверки добавить:

```php
// reCAPTCHA v3
$recaptcha_token = sanitize_text_field(wp_unslash($params['g-recaptcha-response'] ?? ''));
$recaptcha_result = verify_recaptcha($recaptcha_token);
if ($recaptcha_result === false) {
    return new \WP_REST_Response(['ok' => false, 'error' => 'captcha_failed'], 400);
}
$recaptcha_score = is_float($recaptcha_result) ? $recaptcha_result : null;
```

- [ ] **Step 3: Добавить recaptcha_score в $data и INSERT**

В массиве `$data` добавить поле:

```php
'recaptcha_score' => $recaptcha_score,
```

В SQL INSERT добавить колонку (найти существующий INSERT и расширить):

Найти строку с `roistat_visit` в INSERT и добавить после неё:

```php
// в список колонок:
`recaptcha_score`,
// в список значений:
$recaptcha_score !== null ? $recaptcha_score : 'NULL',
```

Используя `$wpdb->prepare` это выглядит так — добавить `%f` или `NULL`:

```php
$score_sql = $recaptcha_score !== null
    ? $wpdb->prepare('%f', $recaptcha_score)
    : 'NULL';
// и вставить $score_sql напрямую в SQL (не через prepare placeholder — NULL нельзя через %f)
```

- [ ] **Step 4: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php
git commit -m "feat(recaptcha): server-side token verification + score logging"
```

---

### Task 4: Score в списке заявок (admin-leads.php)

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`

- [ ] **Step 1: Найти заголовки таблицы и добавить колонку Score**

Найти строку с `<th>` заголовками таблицы заявок (обычно: Имя, Телефон, Источник, Дата, Статус) и добавить:

```html
<th>Score</th>
```

- [ ] **Step 2: В строке заявки вывести score**

В цикле по заявкам найти `<td>` поля и добавить:

```php
$score = isset($lead->recaptcha_score) && $lead->recaptcha_score !== null
    ? number_format((float)$lead->recaptcha_score, 2)
    : '—';
$score_color = '';
if ($lead->recaptcha_score !== null) {
    if ($lead->recaptcha_score >= 0.7) $score_color = 'color:#2ec463;font-weight:600;';
    elseif ($lead->recaptcha_score >= 0.4) $score_color = 'color:#f0b849;font-weight:600;';
    else $score_color = 'color:#d63638;font-weight:600;';
}
echo '<td><span style="' . $score_color . '">' . esc_html($score) . '</span></td>';
```

- [ ] **Step 3: Commit**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php
git commit -m "feat(recaptcha): show score in leads list with color coding"
```

---

### Task 5: Фронтенд — получить токен перед отправкой формы

**Files:**
- Modify: `d:/AI_TEAMS/Lendings/hibridcars-uae/08_КОД/wp-theme/assets/js/lead-form.js`
- Modify: `d:/AI_TEAMS/Lendings/hibridcars-uae/08_КОД/wp-theme/functions.php` — инжектировать `window.lpRecaptchaSiteKey` и скрипт api.js

- [ ] **Step 1: Инжектировать Site Key и скрипт reCAPTCHA в functions.php**

В `lp_render_subpage()` после инжекции `lpRestBase` добавить:

```php
// Inject reCAPTCHA site key if configured
$rc_site_key = (string) get_option('lp_recaptcha_site_key', '');
$rc_enabled  = (bool)   get_option('lp_recaptcha_enabled', false);
if ($rc_enabled && $rc_site_key !== '') {
    $rc_script = '<script>window.lpRecaptchaSiteKey=' . json_encode($rc_site_key) . ';</script>' . "\n"
        . '<script src="https://www.google.com/recaptcha/api.js?render=' . esc_attr($rc_site_key) . '" async defer></script>';
    $html = str_replace('</head>', $rc_script . "\n</head>", $html);
}
```

Для главной страницы (WP-шаблон) добавить `wp_head` hook в `functions.php`:

```php
add_action('wp_head', function () {
    $rc_site_key = (string) get_option('lp_recaptcha_site_key', '');
    $rc_enabled  = (bool)   get_option('lp_recaptcha_enabled', false);
    if (!$rc_enabled || $rc_site_key === '') return;
    echo '<script>window.lpRecaptchaSiteKey=' . json_encode($rc_site_key) . ';</script>' . "\n";
    echo '<script src="https://www.google.com/recaptcha/api.js?render=' . esc_attr($rc_site_key) . '" async defer></script>' . "\n";
});
```

- [ ] **Step 2: Обернуть fetch в grecaptcha.execute в lead-form.js**

Найти блок начала fetch (строка ~219) и обернуть:

```js
var restBase = window.lpRestBase || '/wp-json';

function doSubmit() {
  fetch(restBase + '/landing/v1/lead', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  })
  .then(function (r) {
    if (!r.ok) {
      return r.json().then(function (data) {
        throw new Error(data.error || ('HTTP ' + r.status));
      });
    }
    return r.json();
  })
  .then(function (data) {
    console.log('[lead-form] ok, lead_id:', data.lead_id);
    window.location.href = '/thank-you/';
  })
  .catch(function (err) {
    console.error('[lead-form] error:', err.message);
    window.location.href = '/thank-you/';
  });
}

if (window.lpRecaptchaSiteKey && window.grecaptcha) {
  grecaptcha.ready(function () {
    grecaptcha.execute(window.lpRecaptchaSiteKey, { action: 'submit' }).then(function (token) {
      body.append('g-recaptcha-response', token);
      doSubmit();
    });
  });
} else {
  doSubmit();
}
```

- [ ] **Step 3: Commit**

```bash
git add "d:/AI_TEAMS/Lendings/hibridcars-uae/08_КОД/wp-theme/assets/js/lead-form.js"
git add "d:/AI_TEAMS/Lendings/hibridcars-uae/08_КОД/wp-theme/functions.php"
git commit -m "feat(recaptcha): inject site key + api.js, get token before form submit"
```

---

### Task 6: Deploy + проверка

- [ ] **Step 1: Deploy на тест**

```bash
cd d:/AI_TEAMS/Lendings/hibridcars-uae && echo "y" | bash deploy/deploy.sh test
```

- [ ] **Step 2: Настроить в WP Admin теста**

Зайти: **Лендинг → Общие настройки → reCAPTCHA v3**
- Вставить тестовые ключи (из Google reCAPTCHA Admin Console)
- Включить чекбокс
- Порог: 0.5
- Нажать «Сохранить»

- [ ] **Step 3: Проверить рендер**

```bash
curl -s "https://esper21.ru/" | grep "recaptcha\|lpRecaptchaSiteKey"
```

Ожидаемый результат: строки с `lpRecaptchaSiteKey` и `api.js?render=`.

- [ ] **Step 4: Отправить форму и проверить score в заявках**

Открыть **WP Admin → Лендинг → Заявки** — новая заявка должна иметь score в колонке (зелёный ≥0.7, жёлтый 0.4–0.7, красный <0.4).

- [ ] **Step 5: Deploy на прод после успешного теста**

```bash
echo "y" | bash deploy/deploy.sh prod
```

---

## Зависимости между задачами

```
Task 1 (DB migration) → Task 3 (REST, пишет score)
Task 2 (Admin UI)     → Task 3 (REST, читает настройки)
Task 3                → Task 4 (Admin leads, читает score из БД)
Task 5 (Frontend)     → Task 3 (отправляет токен)
Tasks 1–5             → Task 6 (Deploy)
```
