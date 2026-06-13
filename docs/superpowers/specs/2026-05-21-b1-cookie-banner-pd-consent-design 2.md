# B1 — Cookie-баннер + 152-ФЗ согласие на обработку ПД

**Дата:** 2026-05-21
**Скоуп:** template-level юр-инфраструктура для каждого лендинга landing-system
**Зависимости:** brand-architect, wp-builder, landing-config mu-plugin (REST /lead, БД landing_leads)
**Будущая интеграция:** B2 (GTM с Google Consent Mode v2)
**Backlog:** [docs/BACKLOG.md#B1](../BACKLOG.md)

## 1. Контекст и проблема

Без баннера cookies и явного согласия на обработку ПД лендинг не может запускаться в РФ — нарушает Федеральный закон 152-ФЗ «О персональных данных» (статья 9 — требование явного и информированного согласия) и постановление №1119 (требования к Оператору ПД). Сейчас в template/ нет ни юр-страниц, ни баннера, ни checkbox'а в формах. Любая выкатка в продакшен — юр-риск (штрафы 60-300 тыс. руб. за отсутствие политики, до 6 млн за утечку без согласия).

Эта работа — template-level: артефакты создаются один раз в `template/` и копируются wp-builder'ом в каждый новый лендинг. Будущие лендинги получают compliance из коробки.

## 2. Дизайн в одной фразе

Категоризированный cookie-баннер (necessary/analytics/marketing) + обязательный checkbox согласия в формах + типовые юр-страницы /policy и /consent с реквизитами из brand-kit + интеграция с Google Consent Mode v2 + временная метка согласия в landing_leads.

## 3. Источник реквизитов

### 3.1 Расширение brand-kit

`template/04_БРЕНД/brand-kit.md` получает новую секцию `legal:`:

```yaml
legal:
  company_name: "Общество с ограниченной ответственностью «Ромашка»"  # полное юр-имя
  entity_type: "ООО"                                                   # ООО / АО / ИП
  inn: "7700123456"                                                    # ИНН (10 для ЮЛ, 12 для ИП)
  ogrn: "1234567890123"                                                # ОГРН (15 цифр для ЮЛ) или ОГРНИП (15 для ИП)
  legal_address: "123456, г. Москва, ул. Тверская, д. 1, оф. 100"      # юридический адрес
  contact_email: "info@romashka.ru"                                    # для запросов субъектов ПД
  dpo_email: "info@romashka.ru"                                        # представитель по ПД (часто = contact_email)
```

Все поля обязательны. dpo_email может совпадать с contact_email если у компании нет выделенного DPO (Data Protection Officer).

### 3.2 brand-architect agent — расширение

`agents/brand-architect.md` на этапе 04 после генерации цветов/типографики/логотипа спрашивает у пользователя legal-данные через структурированный prompt. Парсит ответ в YAML-секцию выше. Если пользователь не знает данных (например, IP-адрес ещё не получил status «не нужно для лендинга») — агент предупреждает что это блокирует деплой в РФ и записывает placeholders с явной пометкой `# TODO_LEGAL: заполнить до прод-деплоя`.

## 4. Cookie-баннер

### 4.1 Категории

Три блока:

- **Necessary (всегда ON, без toggle)** — серый текст «необходимы для работы сайта». Включает: WordPress session, lp_cookie_consent сам по себе, любые корзины/wishlist если есть.
- **Analytics (toggle, по умолчанию OFF)** — Яндекс.Метрика, Google Analytics 4, GTM analytics-tags.
- **Marketing (toggle, по умолчанию OFF)** — Facebook Pixel, ВКонтакте/MyTarget pixel, ремаркетинг.

### 4.2 UI

Position: fixed bottom, full-width, max-height 320px на мобильном (категории сворачиваются в аккордеон), 200px на десктопе.

Содержимое:
1. Заголовок «Мы используем cookies» + 1-2 строки описания
2. Три категории как раскрывающиеся блоки с тоггл-переключателями
3. Кнопки внизу:
   - **«Принять все»** (button-primary) — сразу analytics=true, marketing=true, save, hide
   - **«Сохранить настройки»** (button-secondary) — фиксирует текущее состояние тогглов
4. Ссылка на /policy справа внизу

Текст всех элементов — на русском, типовой по 152-ФЗ.

### 4.3 Логика появления

Баннер появляется при первом визите когда `lp_cookie_consent` в localStorage отсутствует. После любого выбора (Accept All или Save preferences) баннер скрывается и больше не появляется автоматически.

В footer темы добавляется мелкая ссылка/кнопка «Настройки cookies» (либо текстовая ссылка, либо иконка cookie 16x16). Клик переоткрывает баннер — пользователь может изменить решение в любой момент.

### 4.4 Хранение

localStorage key `lp_cookie_consent`, значение — JSON:

```json
{
  "analytics": true,
  "marketing": false,
  "ts": 1747834212,
  "version": 1
}
```

Поле `version` (int) — версия текста политики. При обновлении policy.html.template — bump version в JS-константе. Если localStorage `version < current` — баннер появляется снова (forced re-consent).

### 4.5 Google Consent Mode v2

В `<head>` темы, **до** загрузки gtag.js/Metrica.js/GTM, вставляется initialization:

```html
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
  'analytics_storage': 'denied',
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'wait_for_update': 500
});
</script>
```

После сохранения настроек cookie-banner.js вызывает:

```javascript
gtag('consent', 'update', {
  'analytics_storage': consent.analytics ? 'granted' : 'denied',
  'ad_storage': consent.marketing ? 'granted' : 'denied',
  'ad_user_data': consent.marketing ? 'granted' : 'denied',
  'ad_personalization': consent.marketing ? 'granted' : 'denied'
});
```

GA4/GTM видят флаги и не пишут persistent cookies до granted. В denied — собирают anonymized signals (cookieless pings для conversion modelling) — данные не теряются.

Яндекс.Метрика инициализируется условно: `ym(id, 'init', {...})` вызывается только если `consent.analytics === true`. Это интегрируется в analytics-engineer (B2) — здесь только прописываем contract.

## 5. Согласие на ПД в формах

### 5.1 legal-block.php

`template/08_КОД/template-parts/legal-block.php` — partial для вставки в каждую форму перед submit-кнопкой:

```html
<label class="lp-pd-consent">
    <input type="checkbox" name="pd_consent" value="1" required>
    <span>Я согласен на обработку моих персональных данных в соответствии с
    <a href="/policy" target="_blank">Политикой обработки персональных данных</a>
    и <a href="/consent" target="_blank">Согласием на обработку персональных данных</a>.</span>
</label>
```

`required` атрибут блокирует submit на уровне браузера — стандартная HTML5 валидация.

### 5.2 Бэкенд-валидация в landing-config

`skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` (POST `/wp-json/landing/v1/lead`):

- Добавить проверку: если `$_POST['pd_consent']` не равен `'1'` — вернуть 400 с message «Требуется согласие на обработку ПД».
- При успешном сохранении в БД — записать `pd_consent_granted_at = current_time('mysql')` (timestamp согласия).

### 5.3 БД-миграция

`skills/wp-landing-config/mu-plugin/landing-config/includes/db.php::install_schema()` — добавить колонку:

```sql
pd_consent_granted_at DATETIME NULL
```

в существующий `CREATE TABLE wp_<bid>_landing_leads`. dbDelta применит автоматически на следующей загрузке wp-admin (как было с lead_status_log в B19). Существующие строки получат NULL — это допустимо, означает что заявка создана до введения требования.

В list-page admin-leads.php — колонка не показывается (избегаем UI noise), доступна через export CSV.

## 6. Юридические страницы

### 6.1 Шаблоны

`template/08_КОД/legal-pages/policy.html.template` — типовая политика обработки ПД, ~15 секций:

1. Общие положения (определения, основания)
2. Кто Оператор ПД (подставляется `{{company_name}}`, `{{inn}}`, `{{legal_address}}`)
3. Категории субъектов ПД
4. Какие ПД обрабатываются (имя, телефон, email, IP-адрес, cookies, источник перехода, UTM-метки)
5. Цели обработки (обработка заявок, обратная связь, аналитика трафика)
6. Правовые основания (согласие субъекта по ст.6 ч.1 п.1, договорные обязательства по ст.6 ч.1 п.5)
7. Способы и сроки обработки (автоматизированный/неавтоматизированный, хранение 5 лет с даты последнего взаимодействия либо до отзыва согласия)
8. Передача ПД третьим лицам (CRM-системы, мессенджеры — список подставляется из landing-config integrations, если включён конкретный адаптер)
9. Трансграничная передача (нет / Telegram → Великобритания / etc — статически указывается «не осуществляется»)
10. Защита ПД (организационные/технические меры — стандартный пункт)
11. Права субъекта ПД (доступ, изменение, удаление, отзыв — обращение на `{{contact_email}}`)
12. Cookies (категории как в баннере, право отказаться)
13. Изменения политики
14. Контакты Оператора (`{{contact_email}}`, `{{dpo_email}}`, `{{legal_address}}`)
15. Дата последнего обновления

`template/08_КОД/legal-pages/consent.html.template` — типовое согласие по 152-ФЗ ст.9, более короткое (~5 секций):

1. Согласие предоставляется (`{{company_name}}`, `{{inn}}`, `{{legal_address}}`) — Оператор
2. Цели обработки (обработка заявок, обратная связь, маркетинговые коммуникации)
3. Перечень ПД (имя, телефон, email, сообщение, IP, cookies, UTM)
4. Перечень действий (сбор, запись, систематизация, накопление, хранение, уточнение, использование, передача согласно перечню в Политике, обезличивание, блокирование, удаление, уничтожение)
5. Срок действия согласия (5 лет с даты последнего взаимодействия) + способ отзыва (письменно на `{{contact_email}}` или через wp-admin форму)

### 6.2 Тексты — каноничные

Тексты основаны на типовых документах Роскомнадзора (rkn.gov.ru) и юр-практике lead-gen в РФ за 2023-2025. Они должны быть проверены юристом клиента перед прод-деплоем — но как стартовая точка работают.

### 6.3 README для маркетолога

`template/08_КОД/legal-pages/README.md` объясняет:
- что эти страницы делают и зачем
- что они генерируются из шаблонов с подстановкой реквизитов из brand-kit
- как редактировать после генерации (через wp-admin Pages, либо через изменение `.template` файлов и регенерацию через `landing-build`)
- предупреждение: проверить с юристом клиента, не нести юр-ответственность за template-тексты

### 6.4 Генерация в wp-builder

wp-builder на этапе 08_КОД:
1. Читает `04_БРЕНД/brand-kit.md`, парсит секцию `legal:`. Если пустая или `# TODO_LEGAL:` — пропускает с предупреждением (legal-pages не создаются, баннер ссылается на /policy которая 404).
2. Читает `template/08_КОД/legal-pages/policy.html.template`, заменяет `{{company_name}}`, `{{inn}}`, `{{ogrn}}`, `{{legal_address}}`, `{{contact_email}}`, `{{dpo_email}}` на значения из brand-kit.
3. То же для `consent.html.template`.
4. Через wp-cli создаёт две WordPress Pages: slug=policy, title=«Политика обработки персональных данных», content=обработанный HTML. То же для consent.
5. Pages помечаются meta-полем `_lp_legal_page=policy|consent` чтобы при regenerate их можно было обновить, а не создать дубль.

## 7. Файлы

### Создаются
- `template/08_КОД/template-parts/cookie-banner.php` — рендер HTML баннера
- `template/08_КОД/template-parts/cookie-banner.js` — toggle, save, gtag consent.update, footer-link reopener
- `template/08_КОД/template-parts/cookie-banner.css` — стили (использует CSS-переменные из tokens.json темы)
- `template/08_КОД/template-parts/legal-block.php` — checkbox для форм
- `template/08_КОД/template-parts/consent-init.php` — gtag('consent','default','denied') в head
- `template/08_КОД/legal-pages/policy.html.template` — типовая политика с placeholders
- `template/08_КОД/legal-pages/consent.html.template` — типовое согласие с placeholders
- `template/08_КОД/legal-pages/README.md` — пояснение

### Модифицируются
- `template/04_БРЕНД/brand-kit.md` — добавить секцию `legal:` (с примерами)
- `agents/brand-architect.md` — спрашивать legal-реквизиты на этапе 04
- `agents/wp-builder.md` — вставка cookie-banner в footer.php, вставка legal-block во все формы, генерация legal-pages с подстановкой
- `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` — добавить колонку pd_consent_granted_at в landing_leads
- `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` — валидация pd_consent=1, запись timestamp
- `config/stage-gates.yaml` — связать soft-check `legal_blocks_present` с реальной проверкой

## 8. Безопасность и compliance

- **pd_consent_granted_at — формальное доказательство.** Хранится в БД, не подлежит удалению через UI (UI смены статуса в B19 трогает только processed_status). Изъятие через wp-cli или phpmyadmin требует sudo на сервер.
- **Версионирование согласия (поле `version` в localStorage).** При изменении любого из шаблонов policy/consent — bump version. Пользователь увидит баннер снова.
- **Никаких third-party cookies до consent.update granted.** gtag('consent','default','denied') гарантирует это.
- **Cookie-баннер не пишет cookies сам по себе** (только localStorage). Поэтому не нужен парадоксальный «cookie для согласия на cookies».
- **CORS / nonce для REST /lead** — уже реализовано в landing-config (S2-A.1), не B1-specific.
- **Текст согласия — explicit, не pre-checked.** checkbox в форме всегда unchecked по умолчанию, без `checked` атрибута. Это требование 152-ФЗ ст.9 — Роскомнадзор считает pre-checked НЕ явным согласием.

## 9. Тестирование

### 9.1 Unit-тесты

**test_legal_block.php** (~5 ассертов):
- T1: render legal-block.php генерирует `<input type="checkbox" required>`
- T2: ссылки на /policy и /consent присутствуют и corrent
- T3: текст содержит «согласен на обработку моих персональных данных»

**test_rest_lead_pd_consent.php** (~6 ассертов, расширение существующего test_rest_lead.php):
- T1: POST /lead с pd_consent=1 → 200, в БД pd_consent_granted_at != NULL
- T2: POST /lead без pd_consent → 400
- T3: POST /lead с pd_consent='' → 400
- T4: POST /lead с pd_consent='0' → 400
- T5: timestamp pd_consent_granted_at в пределах текущей минуты

**test_db_schema_pd_consent.php** (~3 ассерта):
- T1: колонка pd_consent_granted_at добавлена в CREATE TABLE
- T2: тип DATETIME NULL
- T3: install_schema идемпотентна (повторный вызов не падает)

**test_legal_pages_render.php** (~8 ассертов):
- T1: policy.html.template содержит все placeholders {{company_name}}, {{inn}}, {{legal_address}}, {{contact_email}}
- T2: consent.html.template содержит все placeholders
- T3: после substitution policy.html не содержит {{...}}
- T4: после substitution consent.html не содержит {{...}}
- T5: если brand-kit.legal пустой — render возвращает null/error
- T6: если brand-kit.legal содержит TODO_LEGAL — render предупреждает

### 9.2 JS-тесты

cookie-banner.js — нужны минимальные unit-тесты на toggle/save logic. Можно через QUnit или просто bats со встроенным Node. **Defer** — JS-инфраструктуры тестирования в landing-system пока нет, добавление = отдельная фаза. На текущий момент покрываем ручной проверкой на ailexi.ru.

### 9.3 Live smoke

Расширение `tests/integration/test_s2a3_smoke.sh`:
- T9: POST /lead без pd_consent → 400
- T10: POST /lead с pd_consent=1 → 200 (с тестовыми данными)
- T11: страницы /policy и /consent отдают 200 на russian.ailexi.ru (если legal-pages засеяны)

### 9.4 UI-тесты

Отложены до боевого сайта (по решению пользователя 2026-05-20 не используем ailexi.ru для ручного UI-теста). На ailexi.ru проверяем livenes — баннер появляется, скрывается, localStorage пишется.

## 10. Скоуп: что НЕ делаем

- **Согласие на маркетинговую рассылку** отдельным чекбоксом (другое юр-основание, для lead-gen не нужно).
- **UI отзыва согласия в wp-admin** (для маркетолога). Редкий кейс, делается через wp-cli/phpmyadmin вручную.
- **Auto-detect геолокации** для GDPR vs 152-ФЗ vs CCPA вариантов баннера. Lead-gen РФ — фиксированный 152-ФЗ.
- **Custom-стили баннера через wp-admin**. Стили из tokens.json (наследуются от brand-kit).
- **A/B-тестирование текстов баннера**. YAGNI.
- **Cookie scanner** (автоопределение какие cookies пишет сайт). YAGNI — заранее знаем что Метрика/GTM.
- **JS-тесты cookie-banner.js**. Defer до появления JS-test инфраструктуры в landing-system.

## 11. Зависимости и интеграция

- **brand-architect** (этап 04) — собирает legal-реквизиты.
- **wp-builder** (этап 08) — вставляет artefacts в тему, генерирует legal-pages.
- **landing-config mu-plugin** (S2-A) — валидация pd_consent в REST, миграция БД.
- **B2 analytics-engineer (будущее)** — будет читать consent state и условно инициализировать Метрику/GTM.

## 12. План фаз

1. **B1.1** — расширение brand-kit.md секцией `legal:` + brand-architect prompt + парсер-helper + тест
2. **B1.2** — типовые policy.html.template и consent.html.template + README + render-helper с подстановкой + тест
3. **B1.3** — cookie-banner.{php,js,css} + consent-init.php + footer-link reopener
4. **B1.4** — legal-block.php для форм
5. **B1.5** — миграция БД (pd_consent_granted_at) + валидация в rest-lead.php + тесты
6. **B1.6** — расширение wp-builder agent (insert banner/legal-block, generate legal-pages)
7. **B1.7** — связать stage-gate soft-check `legal_blocks_present` с grep'ом
8. **B1.8** — расширение smoke, обновление CLAUDE.md, deploy/smoke на ailexi.ru

~8 фаз, каждая 2-4 коммита. Сопоставимо с B19.

## 13. Ссылки

- Backlog: [docs/BACKLOG.md#B1](../BACKLOG.md)
- 152-ФЗ: http://www.consultant.ru/document/cons_doc_LAW_61801/
- Google Consent Mode v2: https://developers.google.com/tag-platform/security/guides/consent
- Зависимость: [landing-config mu-plugin spec](2026-05-19-s2a-landing-config-revised.md)
- Будущая интеграция: B2 GTM ([backlog](../BACKLOG.md#B2))
