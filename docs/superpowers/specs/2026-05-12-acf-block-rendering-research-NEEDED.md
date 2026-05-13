# Research Task: ACF Block Frontend Rendering — ROOT CAUSE FOUND

**Date:** 2026-05-12
**Status:** ✅ Root cause identified. Decision made. Implementation pending.
**Priority:** Blocks "manager edits via Gutenberg" goal on existing landings

---

## 🎯 Root Cause (proven on prod 2026-05-12)

**На проде установлен ACF Free 6.8.0, а ACF Blocks API — Pro-only фича.**

Доказательства (via `wp eval` on neuroupgrade-v2 prod):
- `function_exists('acf_register_block_type')` → **NO**
- `class_exists('ACF_Blocks')` → **NO**
- `defined('ACF_PRO') && ACF_PRO` → **NO**
- `grep -r 'renderTemplate\|block_type_metadata' wp-content/plugins/advanced-custom-fields/` → пусто (нет кода блоков)

Что происходило:
1. `register_block_type($dir_with_block_json)` → WP-ядро читает `block.json`, создаёт `WP_Block_Type`
2. Секция `"acf": { "renderTemplate": ... }` **игнорируется ядром** (не стандартное свойство)
3. ACF Free **не подключает** фильтр `block_type_metadata`, который превратил бы `acf.renderTemplate` в `render_callback`
4. Блок попадает в registry без рендера → `do_blocks()` для `<!-- wp:acf/lp-... -->` возвращает пусто

Никакая комбинация namespace/путей/хуков **в принципе** не починит это с ACF Free.

**Почему мы это раньше не поймали:** `deploy.sh:48` ставит ACF командой `wp plugin install advanced-custom-fields --activate` — это Free версия с wp.org. Pro распространяется только через платный канал WP Engine. Stage-08 spec предполагал Pro, но не проверял это в preflight.

---

## ✅ Решение: миграция на Lazy Blocks

**Выбор пользователя (2026-05-12):** бесплатно, полное управление конструктором, без архитектурного риска.

**Lazy Blocks** (https://wordpress.org/plugins/lazy-blocks/) — бесплатный аналог ACF Pro Blocks:
- v4.3.0 (2026-05-04), 20k+ active, 4.9★, active maintenance
- Inline-редактирование в Гутенберге работает из коробки
- Поддержка PHP-render шаблонов и theme-template файлов
- Export/Import блоков
- PHP-фильтр `lzb/register_blocks` (v4.1.0+) — позволяет регистрировать блоки кодом, не UI/DB (CI-совместимо)
- Pro-версия добавляет фишки (доп. controls, conditions, scripts), но НЕ нужна для базового UX

---

## Что keep / throw away в текущей реализации

### Keep (работает корректно):
- `scripts/lib/content_parser.py` — парсинг `final-copy.md` корректен
- `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` — генерация `template-parts/block-*.php` корректна по PHP
- Все bats-тесты пайплайна — структура pipeline корректна
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — деплой темы корректен

### Rewrite (для миграции на Lazy Blocks):
- `skills/wp-gutenberg-block-builder/scripts/generate-acf.py` — заменить генерацию `acf-fields.json` на генерацию JSON в формате Lazy Blocks (или PHP-массивы для `lzb/register_blocks`). Поля контента блока теперь живут в Lazy Block controls, не в ACF field-groups.
- `skills/wp-gutenberg-block-builder/scripts/generate-block-json.py` — либо удалить (если идём через `lzb/register_blocks`), либо адаптировать под формат block.json который Lazy Blocks понимает (нужно выяснить локально).
- `skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py` — переписать: вместо `register_block_type($path)` использовать `lzb/register_blocks` фильтр с массивом блоков.
- `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` (часть про template-parts) — рендер-файлы переехать в формат Lazy Blocks theme-templates (название папки/файла нужно выяснить локально). Сам PHP-контент `block-*.php` почти не меняется — Lazy Blocks даёт `$attributes` так же, как ACF давал `get_field()`.

### Throw away:
- Зависимость от ACF для блочного рендера (поля страницы — ACF Free всё ещё может использоваться)
- Логика `acf.renderTemplate` в block.json
- `wp acf import` для блок-полей (остаётся для page-level ACF полей если они нужны)

### Add:
- В preflight: проверка установлен ли Lazy Blocks на проде, и установка через `wp plugin install lazy-blocks --activate` если нет
- Удалить `wp plugin install advanced-custom-fields` (или оставить только для page-level meta)

---

## ✅ End-to-end API verified on prod (2026-05-12)

Локальная репро на neuroupgrade-v2 (Lazy Blocks 4.3.0 + WP 6.9.4) подтвердила работающую схему. `do_blocks()` отрендерил тестовый блок в 236 байт корректного HTML, `render_callback` привязан Lazy Blocks автоматически.

### Подтверждённый API регистрации (PHP в functions.php темы)

```php
add_action('lzb/init', function() {   // ← lzb/init, НЕ init и НЕ plugins_loaded
    if (!function_exists('lazyblocks')) return;
    lazyblocks()->add_block(array(
        'slug'     => 'lazyblock/<name>',    // namespace ДОЛЖЕН быть 'lazyblock/'
        'title'    => 'Human title',
        'icon'     => 'star-filled',          // dashicons имя
        'category' => 'common',               // или кастомная категория
        'keywords' => array('foo','bar'),
        'controls' => array(
            'c1' => array('name'=>'heading','type'=>'text','label'=>'Heading','default'=>'...'),
            'c2' => array('name'=>'subtitle','type'=>'rich-text','label'=>'Subtitle','default'=>''),
        ),
        'code' => array('output_method' => 'template'),
    ));
});
```

Доступные `type` для controls (Free): `text`, `textarea`, `rich-text`, `classic-editor`, `code-editor`, `number`, `range`, `url`, `email`, `password`, `image`, `gallery`, `file`, `inner-blocks`, `select`, `radio`, `checkbox`, `toggle`, `color`, `date-time`, `repeater`.

### Подтверждённый template-lookup

- Frontend: `<active_theme>/blocks/lazyblock-<name>/block.php` (обязателен)
- Editor preview: `<active_theme>/blocks/lazyblock-<name>/editor.php` (опционально)
- Slash в slug → dash: `lazyblock/test-hero` → папка `lazyblock-test-hero/`
- В шаблоне доступны: `$attributes` (с применёнными default'ами), `$block`, `$render_location`, `$context`
- Lazy Blocks автоматически оборачивает в `<div class="wp-block-lazyblock-<name>">` (можно отключить через `useBlockProps`)

### Ключевые тайминги (важно для генераторов)

- Lazy Blocks вызывает `do_action('lzb/init')` внутри `init` priority **5**
- Сами блоки регистрируются в `WP_Block_Type_Registry` на `init` priority **20**
- → регистрация через `add_block()` ДОЛЖНА происходить между этими точками — `lzb/init` это единственный правильный хук

### Критические нюансы API (выявлены extended-репро 2026-05-12)

#### 1. `controls` — это **flat array**, не nested
Дети repeater'ов идут в тот же top-level массив с `'child_of' => '<parent_control_id>'`. **`child_of` ссылается на КЛЮЧ массива (control ID), не на `name`** — это `class-controls.php` filter_control_value на строке 132.

```php
'controls' => array(
    'c_tiers'   => array('name'=>'pricing_tiers','type'=>'repeater','child_of'=>''),
    'c_t_name'  => array('name'=>'name','type'=>'text','child_of'=>'c_tiers'),  // ← child_of = 'c_tiers' (ID), не 'pricing_tiers'
    'c_t_feats' => array('name'=>'features','type'=>'repeater','child_of'=>'c_tiers'),
    'c_t_f_txt' => array('name'=>'text','type'=>'text','child_of'=>'c_t_feats'),  // nested repeater works
),
```

#### 2. Repeater value хранится как `rawurlencode(json_encode($array))`
В block markup значение repeater'а — это **строка** с urlencoded JSON, не массив. Lazy Blocks автоматически декодирует в `$attributes['<name>']` через `filter_control_value`. Внутри `block.php` ты работаешь с массивом как обычно.

**Следствие для генератора:** не пытайтесь вручную писать `<!-- wp:lazyblock/...` markup для seeding. Всегда либо через UI, либо через `wp post create` с правильной сериализацией.

#### 3. Зарезервированные имена атрибутов
Эти имена не использовать для controls — они автоматически прописываются Lazy Blocks:
- `anchor` (HTML id из supports.anchor)
- `lazyblock`, `className`, `blockId`, `blockUniqueClass`
- `ghostkitSpacings`, `ghostkitSR` (Ghost Kit integration)

Если такие имена нужны в контенте — переименовывать (например `anchor` → `lead`).

#### 4. Хук регистрации = `lzb/init`
- `init` priority 5: Lazy Blocks делает `do_action('lzb/init')` → твоя регистрация
- `init` priority 20: Lazy Blocks регистрирует все user_blocks в `WP_Block_Type_Registry`
- → Только `lzb/init` гарантирует попадание в реестр. `plugins_loaded` (слишком рано — plugin не загружен), `init` без приоритета (поздно — registry уже заполнен).

### Не проверено, но важно для следующего шага

- ❌ UX в реальном Гутенберге: inspector controls, drag-drop repeater rows, image picker, inline rich-text edit
- ❌ Сохранение страницы → повторное открытие в редакторе (round-trip)
- ❌ Кастомная категория `lp-blocks` через `block_categories_all` filter совместима с Lazy Blocks
- ❌ Inner-blocks control (если он понадобится для секций с вложенными блоками)

### ✅ Browser UX-проверка пройдена (2026-05-13)

На test-сервере проверены три архетипа блоков с реальным контентом NeuroUpgrade 3.0:

**Single-block (Hero):** post 77, [http://esper21.beget.tech/neuroupgrade-v2/?page_id=77]
- 6 text/textarea/url controls работают через UI
- **Image control с WP Media Library picker** — пользователь загрузил картинку, сохранилась, отрендерилась
- Top-level repeater (bullets) — 4 строки, drag-drop работает
- Round-trip ввёл → сохранил → фронт — все данные в HTML

**Section + InnerBlocks (Тарифы):** post 69
- Section с 3 текстовыми полями + InnerBlocks slot
- 3 prefilled tarify-card через `template`
- `allowedBlocks="['lazyblock/tarify-card']"` — в `+` показывает только разрешённый
- В каждом tarify-card: 7 scalar controls + popular toggle + repeater features (19 фич в "Продвинутом", 23 в "ВИП")
- На фронте рендер с реальными ценами, классами `nu-tier--popular`, SVG иконками `lp_render_icon('check')` темы

**Простой Section + InnerBlocks (Кейсы):** post 78
- 5 placeholder-карточек с реалистичными именами/контекстами
- `nu-student-case` стили темы применились

### Архитектурные нюансы для генератора

**1. Сложные блоки разбиваются на пару section+card** (паттерн InnerBlocks):
- Тарифы (с features) → `tarify-section` + `tarify-card`
- Кейсы/отзывы (с repeater из карточек) → `cases-section` + `case-card`
- Программа модулей → `program-section` + `program-module`
- FAQ → `faq-section` + `faq-item`

**Критерий разбиения:** если на верхнем уровне нужен repeater + у его строк нужны вложенные данные (особенно ещё один repeater или сложная структура) — разбиваем на section+card.

**2. Простые блоки остаются одним:** Hero, Final CTA, Footer, Promise, Author bio, Audience — у них только flat controls + 1 optional repeater на простых строках.

**3. CSS-патч для InnerBlocks-вложенности** (`display: contents`):
```css
.<section-grid-class> .lazyblock-inner-blocks,
.<section-grid-class> > .wp-block-lazyblock-<card-slug>,
.lazyblock-inner-blocks > .wp-block-lazyblock-<card-slug> { display: contents; }
```
Нужен потому что Gutenberg оборачивает каждый child в `<div class="wp-block-...">` + Lazy Blocks добавляет свой `<div class="lazyblock-inner-blocks">` — эти 2 wrapper'а ломают CSS Grid/Flex родителя. `display: contents` делает их прозрачными для layout.

Альтернатива на будущее: `useBlockProps` (Lazy Blocks 4.0+) — позволяет не оборачивать в `wp-block-*` wrapper, но `lazyblock-inner-blocks` всё равно останется. CSS-патч проще.

### Какие генераторы пишем

| Файл | Действие | Источник для генерации |
|---|---|---|
| `generate-block-json.py` | **удалить** (block.json не нужен — Lazy Blocks читает из `add_block()`) | — |
| `generate-block-registration.py` | **переписать**: вместо `register_block_type($path)` → `lazyblocks()->add_block($data)` на хуке `lzb/init` | `final-copy.md` + новый `block-spec.yaml` (как определить какие блоки section+card vs single) |
| `generate-acf.py` для блок-полей | **удалить** | — |
| `generate-theme.py --blocks-only` | **переписать**: пишет в `theme/blocks/lazyblock-<slug>/block.php` (НЕ в `theme/template-parts/block-<slug>.php`) | существующие production `template-parts/block-*.php` (с `nu-*` классами) как образец |
| `generate-theme.py --css-patches` | **новый**: дописывает в `assets/css/main.css` `display: contents` правила для каждой section+card пары | block-spec.yaml |
| `deploy-wordpress.sh` | **изменить**: убрать `wp plugin install advanced-custom-fields`, добавить `wp plugin install lazy-blocks --activate` | — |
| `preflight.sh` | **изменить**: проверять Lazy Blocks вместо ACF Pro | — |
| `front-page.php` (генерится темой) | **больше не нужен как rigid template** — манагерская страница из Гутенберга становится главной (page_on_front), front-page.php fallback или удаляется | — |

### Решённые в этом цикле open questions

- ~~Формат `lzb/register_blocks`~~ — используем `lazyblocks()->add_block($data)` (см. примеры в research-doc)
- ~~Theme templates folder convention~~ — `theme/blocks/lazyblock-<slug>/block.php`
- ~~Export/Import JSON~~ — не нужно, регистрируем кодом из functions.php
- ~~`include_within()` метод~~ — не нужно, Lazy Blocks ставится как plugin через wp-cli

### Готово к `writing-plans`

Все architectural decisions приняты, end-to-end проверка пройдена на test-сервере. Следующий шаг — формальный план миграции stage-08 generators через `superpowers:writing-plans`.

---

## Current state of neuroupgrade-v2 on prod (unchanged)

- Site renders correctly via `front-page.php` (PHP-template flow) — НЕ Gutenberg.
- WordPress DB — fresh init, admin `esper21`.
- ACF Free 6.8.0 active, 15 field-groups synced (но они для блоков, не используются).
- 15 block.json лежат в `wp-content/gutenberg-blocks/<slug>/`, регистрируются через `register_block_type()` на `init`, но без render_callback (см. root cause выше).
- Manager Gutenberg flow: **не работает** и не заработает на ACF Free.

---

## Next steps

1. Локальная мини-репро среда: чистый WP + Lazy Blocks Free + один тестовый блок (через UI), экспорт → разбор JSON формата, разбор theme-template папки.
2. Написать минимальный пример `lzb/register_blocks` для одного блока с одним RichText control и рендер-файлом — проверить что работает на фронте.
3. После working repro — обновить `writing-plans` план миграции stage-08 generators, согласовать с пользователем, далее TDD-имплементация.
