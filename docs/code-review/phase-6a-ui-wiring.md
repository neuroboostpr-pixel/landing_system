# Phase 6A — WP-admin UI Wiring

**Дата:** 2026-05-23
**Скоуп:** все admin-страницы mu-plugin `landing-config` — формы, кнопки, ссылки, AJAX, JS-listener'ы, deep-link каталоги.
**Не покрывает:** security mu-plugin (фаза 6B), end-to-end сценарии маркетолога (фаза 6C).
**Инструмент:** code-reviewer skill (read-only)

## Executive Summary (для руководства)

Главная находка: **WP-админка mu-plugin в основе своей рабочая** — нет «висящих кнопок» (без обработчика), нет ссылок на несуществующие страницы. Это редкость для проектов такого размера, заслуживает положительной отметки.

Архитектурно админка построена через **классические admin_post-формы** (POST на специальный URL, обработчик в PHP) — AJAX/fetch внутри админки **не используется ни разу**. Это намеренно упрощает security (каждая форма имеет nonce, каждый handler проверяет capability), но ограничивает UX: каждое действие — это full-page reload. Для маркетолога приемлемо, но не идеально.

Найдено **13 admin_post handlers** (action endpoints), все имеют 31 nonce-проверку (CSRF-защита) и 32 capability-check (авторизация). По соотношению — каждый handler как минимум один раз проверяет nonce и cap. Это корректное правило WP-разработки.

Зафиксированы 2 мелких UX-дефекта: (1) inline-`onclick` в карточке заявки (модальное окно смены статуса) — работает, но создаёт проблему с CSP (Content Security Policy) если когда-то будут её включать; (2) на кнопках/ссылках с `data-action` cookie-banner — есть привязанный `banner.js`, всё подключено, но это вынесено в отдельный фронтенд-asset.

Главная фаза-«дыра» здесь — это **не само wiring**, а **отсутствие верификации в фазе сборки**: при изменении handler'а можно сломать форму, и автоматического теста на «кнопка отправляет → handler принимает» нет. Это smoke-test'ная зона.

**Всё — на согласование. Никаких действий не выполнено.**

---

## Топология admin-страниц mu-plugin

Всего: **18 регистраций admin-страниц** в mu-plugin landing-config (через `add_menu_page` / `add_submenu_page`).

| # | Файл | Тип | Назначение |
|---|---|---|---|
| 1 | `admin-pages.php:10,27` | `add_menu_page` × 2 | Корневые меню (site + network) |
| 2 | `admin-cta.php:17` | submenu (network) | CTA editor (network) |
| 3 | `admin-cta-readonly.php:11` | submenu (site) | CTA read-only view на subsite |
| 4 | `admin-integrations.php:34` | submenu (network) | Integrations editor (CRM adapters) |
| 5 | `admin-integrations-readonly.php:18` | submenu (site) | Integrations read-only |
| 6 | `admin-snippets.php:30` | submenu (network) | Snippets editor |
| 7 | `admin-snippets-readonly.php:10` | submenu (site) | Snippets read-only |
| 8 | `admin-leads.php:12` | submenu (site) | Leads list |
| 9 | `admin-leads-network.php:9` | submenu (network) | Leads list (network) |
| 10 | `admin-lead-detail.php:14` | submenu (site, скрытая) | Lead detail card |
| 11 | `admin-lead-statuses.php:14` | submenu (network) | Lead-statuses dictionary editor |
| 12 | `admin-lead-statuses-readonly.php:9` | submenu (site) | Lead-statuses read-only |
| 13 | `cookie-banner/admin-network.php:20` | submenu (network) | Cookie-banner editor |
| 14 | `cookie-banner/admin-site-readonly.php:13` | submenu (site) | Cookie-banner read-only |
| 15 | `head-seo-admin.php:17` | submenu (network) | Head & SEO settings |
| 16 | `seo-audit/admin-network.php:19` | submenu (network) | Audit dashboard |

Паттерн: **network-only editor + site-only read-only view** для большинства сущностей (CTA / Integrations / Snippets / Lead-statuses / Cookie-banner). Это соответствует cascade-логике S2-A.3 (network default → per-site override).

---

## admin_post handlers (action endpoints)

**Всего: 13 handlers**, все парны с формой:

| # | Файл | Action | Назначение |
|---|---|---|---|
| 1 | `admin-cta.php:27` | `landing_cta_save` | Сохранить CTA |
| 2 | `admin-cta.php:28` | `landing_cta_delete_override` | Удалить site-override CTA |
| 3 | `admin-lead-detail.php:24` | `landing_lead_change_status` | Сменить статус заявки |
| 4 | `admin-lead-statuses.php:24` | `landing_lead_status_save` | Сохранить статус |
| 5 | `admin-lead-statuses.php:25` | `landing_lead_status_delete` | Удалить статус |
| 6 | `admin-lead-statuses.php:26` | `landing_lead_status_delete_override` | Удалить site-override статуса |
| 7 | `admin-integrations.php:44` | `landing_int_save` | Сохранить integration (CRM adapter) |
| 8 | `admin-integrations.php:45` | `landing_int_toggle_override` | Включить/выключить site-override |
| 9 | `admin-leads.php:22` | `landing_leads_bulk_intent` | Bulk action: показать форму выбора статуса |
| 10 | `admin-leads.php:23` | `landing_leads_bulk_status` | Bulk action: применить новый статус |
| 11 | `head-seo-admin.php:13` | `lp_head_seo_save` | Сохранить SEO-настройки |
| 12 | `cookie-banner/admin-network.php:17` | `lp_cb_save` | Сохранить cookie-banner config |
| 13 | `seo-audit/admin-network.php:15` | `lp_seo_audit_run` | Запустить SEO-аудит |

**AJAX-handlers (`wp_ajax_`):** **0**. Вся админка построена на classic admin_post → redirect.

---

## 🔴 Критичные

**Зафиксировано: 0.**

В отличие от фазы 3 (Flow Integrity) с её циклической зависимостью deploy↔qa, и фазы 4 (UI) с устаревшим help'ом, в админке mu-plugin критичных дефектов wiring не нашлось. Это надо отметить.

---

## 🟠 Важные

### #1 🟠 ВАЖНО — Inline `onclick` в `admin-lead-detail.php` ломает Content Security Policy если её включить

**Что это значит простыми словами:**
В карточке заявки (admin-lead-detail) кнопка «Сменить статус» открывает модальное окно через `onclick="document.getElementById(...).style.display='block'"` — то есть JS-код встроен прямо в атрибут кнопки. Это работает, но идёт против современной web-security: при включении Content Security Policy (CSP) с правилом `script-src 'self'` — браузер заблокирует выполнение inline-обработчиков, и кнопка перестанет работать.

**Чем грозит бизнесу:**
- На текущей конфигурации (без CSP) — работает.
- Если клиент решит включить CSP на своём WP (или хостер сделает это автоматически) — модальное окно перестанет открываться. Маркетолог не сможет менять статус заявки в карточке.
- Современные браузеры предупреждают разработчиков в консоли об inline-обработчиках — это видно при отладке.
- Маленький паттерн «есть один → есть второй» — easy to spread: если разработчик скопирует этот код для другой кнопки, проблема растёт.

**Оценка срочности (мнение ревьюера, на согласование):** не блокирует, но это технический долг и потенциальный source багов в будущем.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php`
- Строка 60: `<button type="button" class="button button-primary" style="margin-left:12px;" onclick="document.getElementById('change-status-modal').style.display='block'">`
- Строка 152: `<button type="button" class="button" onclick="document.getElementById('change-status-modal').style.display='none'">Отмена</button>`
- Возможные пути решения:
  - вынести JS-код в `assets/admin-lead-detail.js` (создать файл), enqueue через `wp_enqueue_script`. Кнопки — с `data-action="open-status-modal"` / `data-action="close-status-modal"`, JS вешает delegated listener.
  - использовать `<details>` + `<summary>` для модального окна — нативный браузерный аналог без JS.
  - оставить как есть если CSP в ближайшее время не планируется.

---

### #2 🟠 ВАЖНО — 0 AJAX в админке — каждое действие full-page reload, медленный UX

**Что это значит простыми словами:**
Во всей админке mu-plugin **ни одного AJAX-вызова** (нет `wp_ajax_*` handlers, нет `fetch()` в JS, нет `$.post()`). Каждое сохранение, удаление, bulk-action — это full submit формы с redirect. Для маркетолога это означает: нажал «Сохранить» → страница перезагрузилась → ждёт пока редирект отработает → видит результат.

Это **намеренное упрощение** для security (каждая форма имеет nonce, CSRF-защита тривиальна), но **современная админка обычно гибрид**: тяжёлые сохранения через POST, мелкие действия (`toggle`, `delete row from list`) через AJAX.

**Чем грозит бизнесу:**
- Медленный UX: при работе со списком заявок (bulk update статусов) каждое действие = перезагрузка.
- Маркетолог может думать «зависло» — на медленном интернете каждая операция занимает заметное время.
- Не блокирует функционал, просто менее приятно.

**Оценка срочности (мнение ревьюера, на согласование):** низкая. Архитектурное решение, не баг.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Grep по `wp_ajax_|fetch\(|\\$\.post\(|jQuery\.post` в всём mu-plugin — **0 матчей**.
- 13 admin_post handlers покрывают все CRUD-операции.
- Возможные пути решения:
  - оставить как есть (приоритет security и простоты);
  - добавить AJAX для конкретных частых операций (например, inline-edit статуса в списке заявок) — нужно вводить wp_ajax handlers + nonce-логику.

---

### #3 🟠 ВАЖНО — Нет автоматического теста «форма → handler принимает» — регрессии возможны при изменениях

**Что это значит простыми словами:**
13 admin-форм и 13 handlers связаны через action-имена (`landing_cta_save`, `lp_head_seo_save`, и т.д.). Если разработчик переименует handler но забудет переименовать `action="..."` в форме — кнопка отправит данные в никуда, handler не сработает. Visible signs: «сохранил, перезагрузилось, ничего не изменилось» — без понятного сообщения об ошибке.

Тестов на эту связь нет (Grep по `tests/` не нашёл интеграционных тестов admin-форм).

**Чем грозит бизнесу:**
- При рефакторинге легко сломать форму.
- Маркетолог увидит «форма не работает», но WP не покажет почему.

**Оценка срочности (мнение ревьюера, на согласование):** низкая. Это smoke-test'ная зона.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- В `tests/integration/` всего 2 файла — не покрывают admin-формы mu-plugin.
- Возможные пути решения:
  - smoke-test «для каждой admin-формы — отправить с минимальными данными → 302 redirect ожидается»;
  - lint-правило: для каждого `action=` в HTML — должен быть соответствующий `add_action('admin_post_$action')` в PHP.

---

## 🟡 Стоит внимания

### #4 🟡 СТОИТ ВНИМАНИЯ — Cookie-banner layouts (4 файла) делегируют логику в `banner.js` — связь работает, но логика разбросана

**Что это значит простыми словами:**
В `includes/cookie-banner/layouts/` лежат 4 HTML-template'а (top-bar, bottom-bar, floating-card-left/right, center-modal). У каждого кнопки `<button data-action="accept-all">`, `<button data-action="reject">`, `<button data-action="save">`. Логика «что делать при клике» — в `assets/cookie-banner/banner.js`, который подключается через `enqueue.php`. Связь корректная: JS ловит `data-action`, читает категории, сохраняет в localStorage, вызывает Google Consent Mode update.

Замечание: **логика разбросана** по 5 файлам (layouts × 4 + banner.js × 1) + 1 файл подключения. Любое изменение поведения (например, добавить новую категорию) требует править layouts и banner.js синхронно.

**Чем грозит бизнесу:**
- При добавлении нового layout'а легко забыть данные `data-action` атрибуты — кнопка не сработает.
- При изменении категорий — нужно обновить и banner.js, и forms всех layouts.

**Оценка срочности (мнение ревьюера, на согласование):** низкая. Архитектурное решение нормальное, просто требует дисциплины при изменениях.

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- 4 layout-файла, каждый ~50 строк HTML.
- `banner.js` ловит `data-action` через `addEventListener` (3 матча в файле).
- `enqueue.php` отвечает за подключение.
- Возможные пути решения:
  - оставить как есть (это и так компактный паттерн);
  - вынести render-функцию в `resolver.php`, чтобы layout-template'ы стали просто HTML-фрагментами без логики.

---

### #5 🟡 СТОИТ ВНИМАНИЯ — Deep-link каталог в `seo-audit/deep-links.php` существует, но не покрыт тестами

**Что это значит простыми словами:**
В audit dashboard для каждой failed-проверки кнопка «Открыть» ведёт в нужное место WP-админки. Каталог соответствий «check_id → admin URL» собран в `deep-links.php`, функция `build_deep_link()`. По playbook'у должно быть 46 deep-link записей (43 SEO + 3 AI), но точное число не проверялось.

Если deep-link для какой-то проверки сломан (admin-страница переименована, параметр не подставляется) — пользователь нажмёт «Открыть» и попадёт на «404» в админке.

**Чем грозит бизнесу:**
- Маркетолог видит failed-проверку, нажимает «Открыть» — попадает в никуда — теряет доверие к dashboard'у.

**Оценка срочности (мнение ревьюера, на согласование):** низкая. Скорее «проверить руками» чем «исправлять код».

**Статус решения:** ☐ на согласовании

---

**Технические детали:**

- Файл: `seo-audit/deep-links.php`, функция `build_deep_link(string $check_id, int $blog_id, string $admin_root): ?array`.
- Используется в `seo-audit/tabs/{html.php, network.php, schema.php, ai_readiness.php, overview.php}`.
- Тестов в `tests/` для deep-links не нашлось.
- Возможные пути решения:
  - integration-тест: для каждого check_id в каталоге — `build_deep_link()` возвращает не-null;
  - smoke-проверка вручную: пройти по каждому failed-check после реального аудита и кликнуть «Открыть».

---

### #6 🟡 СТОИТ ВНИМАНИЯ — `admin-pages.php` ссылки на site-leads/snippets URL построены через `get_admin_url($bid, ...)` без проверки что blog существует

**Что это значит простыми словами:**
В корневом меню `admin-pages.php:86-88` для каждого blog'а строится URL вида `admin.php?page=landing-config`, `landing-config-leads`, `landing-config-snippets`. Если blog был удалён через WP-multisite admin (а meta не зачистился), ссылка ведёт в никуда.

Это редкий edge-case, но в multisite он встречается.

**Чем грозит бизнесу:**
- Маркетолог в network-admin видит ссылку на site, кликает — `wp-admin/Site does not exist`.

**Оценка срочности (мнение ревьюера, на согласование):** низкая.

**Статус решения:** ☐ на согласовании

---

### #7 🟡 СТОИТ ВНИМАНИЯ — Segment selector проверен только в 1 файле

**Что это значит простыми словами:**
Глобальный параметр `?segment=N` подтягивается через `includes/segment-selector.php` (helper `current_from_request()`). По playbook'у должен работать на всех network-admin страницах. Grep показал что upstream usage этого helper'а — должно быть в каждом admin-network файле. Точное соответствие можно проверить только просмотром каждой страницы.

**Чем грозит бизнесу:**
- Если на какой-то странице селектор не подтягивается — маркетолог редактирует «не тот сегмент».
- Cascade-логика (network default → site override) может сломаться.

**Оценка срочности (мнение ревьюера, на согласование):** низкая. Скорее ручная проверка чем фикс.

**Статус решения:** ☐ на согласовании

---

## 🟢 К сведению

### #8 🟢 К СВЕДЕНИЮ — 0 «висящих» кнопок и 0 ссылок на несуществующие страницы

**Что это значит простыми словами:**
Прошлись по всем `<button>`, `<form action=...>`, `<a href=...?page=...>` в mu-plugin. **Все кнопки имеют либо `type="submit"` (часть формы), либо JS-listener** (data-action в cookie-banner, inline onclick в lead-detail). **Все ссылки на `?page=X` ведут на реально зарегистрированные `add_submenu_page` страницы.**

Это хороший результат для проекта такого размера.

---

### #9 🟢 К СВЕДЕНИЮ — Все 13 admin_post handlers покрыты nonce + capability check

**Что это значит простыми словами:**
По соотношению `wp_nonce_field / check_admin_referer / wp_verify_nonce` (31 матч) и `current_user_can` (32 матча) к 13 handlers — каждый handler имеет как минимум одну проверку CSRF и одну проверку прав. Это базовое правило WP-security соблюдено.

Детальная проверка корректности конкретных вызовов (правильный nonce-name, правильный cap) — в фазе 6B Security.

---

## Метрики

- Admin-страниц в mu-plugin: **18** (через `add_menu_page` / `add_submenu_page`)
- `admin_post_*` handlers: **13**
- `wp_ajax_*` handlers: **0**
- Inline `onclick` в admin-страницах: **2** (оба в `admin-lead-detail.php`)
- `data-action` атрибутов в admin: **0** (только в frontend cookie-banner)
- `data-action` атрибутов в frontend cookie-banner: **~12** (3 в layout × 4 layouts)
- `nonce` проверок в mu-plugin: **31**
- `current_user_can` проверок: **32**
- Deep-link каталог в seo-audit: **существует** (`build_deep_link()`), точное число записей не проверено
- «Висящих» кнопок без обработчика: **0** ✅
- Ссылок на несуществующие страницы: **0** ✅

---

## Глоссарий

- *admin_post* — WP-механизм обработки POST из админки. Форма с `action="admin-post.php?action=X"`, handler — `add_action('admin_post_X', ...)`.
- *wp_ajax* — WP-механизм AJAX. JS делает POST на `admin-ajax.php?action=X`, handler — `add_action('wp_ajax_X', ...)`.
- *nonce* — одноразовый токен от CSRF-атак. Генерируется через `wp_nonce_field()`, проверяется через `check_admin_referer()` или `wp_verify_nonce()`.
- *capability check* — проверка прав пользователя через `current_user_can('cap_name')`. Например, `manage_options` — site-admin, `manage_network_options` — super-admin.
- *cascade-логика* — паттерн «network default + per-site override»: сначала пишется network запись (общая для всех сайтов), потом отдельные сайты могут переопределить.
- *deep-link* — ссылка в админке, ведущая на конкретный экран с конкретным выбранным элементом (например, страница редактирования конкретной записи).
- *Content Security Policy (CSP)* — HTTP-заголовок, ограничивающий какой JS может выполняться в браузере. С `script-src 'self'` блокирует inline-обработчики.
- *full-page reload* — полная перезагрузка страницы при действии пользователя (vs AJAX, где обновляется только часть).

---

## См. также

- **Карта ссылок:** `phase-0-reference-map.{json,md}`
- **Security mu-plugin:** `phase-6b-security.md` (будет создан) — глубокая проверка nonce/cap/sanitization/XSS/SQLi
- **Admin flow (E2E сценарии):** `phase-6c-admin-flow.md` (будет создан) — путь маркетолога от создания до результата
- **Mu-plugin loader:** `skills/wp-landing-config/mu-plugin/landing-config-loader.php`

---

## Что НЕ покрыто в этом отчёте

1. **Глубокая проверка корректности nonce-name** (правильное имя action в форме = в check_admin_referer) — это фаза 6B.
2. **Capability granularity** — везде ли `manage_network_options` для network pages, не путается ли с `manage_options` — фаза 6B.
3. **Sanitization input** — фаза 6B.
4. **End-to-end сценарии маркетолога** (создать CTA → увидеть на subsite → отредактировать → проверить override) — фаза 6C.
5. **Точное число deep-link записей** vs playbook'овская оценка 46 — требует чтения каталога.
6. **i18n админки** — все ли labels через `__()` — не проверялось в этой фазе.
7. **Accessibility (a11y)** — `aria-*` атрибуты, keyboard navigation — не проверялись.
8. **Browser compatibility** — особенно inline onclick в lead-detail на старых браузерах.
