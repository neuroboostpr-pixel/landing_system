# Asset Pipeline (Stage-08)

Контракт по работе с любыми ассетами лендинга: фото, иконки (SVG inline и
файловые), фоны, фавиконы, логотипы. Этот документ — единственный источник
правды для генераторов, шаблонов блоков и деплой-скрипта.

> Кто это читает: `frontend-builder`, `landing-orchestrator`, любой
> разработчик, который правит `08_КОД/` или скрипты Stage-08.

## TL;DR

| Тип ассета | Откуда берётся | Где лежит в проекте | Как попадает в page-content | Как доходит до браузера |
|---|---|---|---|---|
| **Фото клиента** | `07c_PHOTOS/inbox/` → подбор → `selections.yaml` | `08_КОД/assets/photos/<slug>.<ext>` | `wp media import` → attachment_id → URL-encoded `{id,url}` | `wp_get_attachment_image()` в block.php |
| **Сгенерированные иконки (PNG)** | `07d_VISUALS` (codex) | `08_КОД/assets/icons/<slug>.png` | Тот же путь, что фото | То же |
| **Inline SVG-иконки** | composed-source (вручную или из icon-pack) | inline в `page-content.html` как `icon_svg` attr | URL-encode raw `<svg>` → строка в textarea-attr | `wp_kses(rawurldecode(...), $svg_allowed)` |
| **CSS-фоны** | composed-source | `08_КОД/assets/photos/` (или `assets/decorations/`) | НЕ через page-content. URL прямо в `assets/css/main.css` | браузер тянет `url('../photos/X.jpg')` |
| **Фавикон / site icon** | бренд-кит (`04_БРЕНД/`) | `08_КОД/assets/icons/favicon.{ico,png,svg}` | `wp media import` → ID → атрибут `favicon` / `site_icon` | `wp_get_attachment_image_url()` в `<link rel="icon">` (functions.php) |
| **Логотип (raster)** | `04_БРЕНД/logos/` | `08_КОД/assets/logos/<slug>.{png,svg}` | `wp media import` → ID → атрибут `logo` / `logo_image` | `wp_get_attachment_image()` |
| **Логотип SVG inline** | `04_БРЕНД/logos/*.svg` | inline в page-content как `logo_svg` attr | URL-encode | `wp_kses` |

## Принципы

1. **Один скрипт — один контракт.** Преобразование «что в HTML → что в БД WP»
   живёт **только** в `skills/wp-cli-deployer/scripts/fix-page-content-images.py`.
   Никаких `sed`-loops, никаких inline-замен в `deploy-wordpress.sh`.

2. **Шаблон блока знает только свой формат.** `block.php` либо ждёт массив
   (Gutenberg-parsed), либо строку (URL-encoded), но **не угадывает** —
   нормализует через `is_string($x) ? json_decode(rawurldecode($x), true) : $x`.

3. **Idempotency.** Повторный прогон `fix-page-content-images.py` на уже
   обработанном HTML — **no-op** (нулевая статистика по всем счётчикам).
   Тест: `tests/phase-stage-08/test-fix-page-content-images.py::test_idempotent_full_run`.

4. **Allow-list по именам атрибутов, а не по типу контрола.** Если контрол
   `textarea` называется `icon_svg` — он SVG. Если `description` — обычный
   текст. Имена закреплены в двух константах:
   - `IMAGE_ATTR_KEYS` (объекты `{id,url}`, URL-encoded)
   - `SVG_ATTR_KEYS` (raw HTML, URL-encoded)

## Поток данных (детально)

### A. Фото / raster-изображение

```
07c_PHOTOS/inbox/photo.jpg
        ↓ selections.yaml + compose
08_КОД/assets/photos/hero.jpg            ← файл на диске
08_КОД/page-content.html:
        "hero_bg": __IMAGE_ATTACHMENT_ID__assets/photos/hero.jpg__
                            ↓ wp media import → photo-map.txt: hero.jpg|10
                            ↓ fix-page-content-images.py
        "hero_bg": "%7B%22id%22%3A10%2C%22url%22%3A%22%22%7D"
                            ↓ wp post update
LZB image control сохраняет как-есть.
                            ↓ render
block.php: $img = rawurldecode → json_decode → ['id'=>10, 'url'=>'']
           → wp_get_attachment_image(10, 'large')
```

**Контракт:** `IMAGE_ATTR_KEYS` (см. скрипт) — единственный список, который
триггерит URL-encode. Если block-spec.yaml добавляет новый image-контрол —
дополни константу в обоих местах:
- `skills/wp-cli-deployer/scripts/fix-page-content-images.py::IMAGE_ATTR_KEYS`
- (если нужен особый рендер) `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py`

### B. Inline SVG (icon_svg, logo_svg, …)

```
composed.html: <span class="icon"><svg>…</svg></span>
        ↓ generate-page-content.py
page-content.html: "icon_svg":"<svg viewBox=\"0 0 24 24\">…</svg>"
        ↓ fix-page-content-images.py (raw `<` → URL-encode)
"icon_svg":"%3Csvg%20viewBox%3D%220%200%2024%2024%22%3E…%3C%2Fsvg%3E"
        ↓ wp post update
                            ↓ render
block.php: wp_kses(rawurldecode($attributes['icon_svg']), $svg_allowed)
```

**Зачем URL-encode?** Gutenberg парсит block-attribute JSON между
`<!-- wp:lazyblock/X { ... } /-->`. Сырая `<` или `>` ломает парсер
(он принимает `}` внутри SVG за закрытие attrs). URL-encoded строка
безопасна, идентична после `rawurldecode`.

**Контракт:** `SVG_ATTR_KEYS` — единственный список. Шаблон `block.php`
автогенерится с `wp_kses + rawurldecode`, allowlist описан в
`generate-lzb-templates.py::_SVG_KSES_PHP`. Расширять allowlist — там же.

### C. CSS background-image

```
composed.html: <section style="background:url(assets/photos/X.jpg)">
        ↓ bundle-assets.py + generate-css
wp-theme/assets/css/main.css: .hero { background: url('../photos/X.jpg') }
```

**Контракт:** CSS-фоны **не идут через page-content**. Они вкомпиливаются в
`assets/css/main.css` с relative-path **относительно css-файла** (`../photos/X.jpg`).
Файлы копируются в `wp-content/themes/<slug>/assets/photos/`.

Если background-фото должно быть редактируемым из WP-админки — заведи
image-контрол на блоке (`bg_image`), и блок отрендерит `<div style="...">`
с URL из `wp_get_attachment_image_url()`.

### D. Фавикон

```
04_БРЕНД/favicon.{ico,png,svg} (или 04_БРЕНД/logos/favicon-32.png)
        ↓ bundle-assets.py
08_КОД/assets/icons/favicon.<ext>
        ↓ wp media import
photo-map.txt: favicon.png|12
        ↓ wp option set landing_favicon_id 12
        ↓ functions.php:
add_action('wp_head', function() {
  if ($id = get_option('landing_favicon_id')) {
    printf('<link rel="icon" href="%s">', esc_url(wp_get_attachment_image_url($id, 'full')));
  }
});
```

**Контракт:** favicon — это **site-level** ассет, а не атрибут блока. Он не
лежит в page-content. Импортируется отдельным шагом и сохраняется в
`wp_options`. Раздел кода — в скилле `wp-theme-assembler` (TBD: добавить
helper-функцию `landing_register_favicon($attachment_id)`).

### E. Логотип

Если логотип в шапке/футере — это контрол блока (`logo` / `logo_image`),
работает по схеме (A) для raster или (B) для inline-SVG.

## Чек-лист при добавлении нового типа ассета

1. **В каком формате он попадает в browsable HTML?**
   - `{id,url}` object → добавить ключ в `IMAGE_ATTR_KEYS`
   - raw `<svg>`/`<picture>` → добавить ключ в `SVG_ATTR_KEYS`
   - файл, на который ссылается CSS → ничего в page-content, только в `bundle-assets.py`
   - site-level настройка → отдельный `wp option`

2. **Какой control в block-spec.yaml?**
   - `image` → автогенерится с json_decode-нормализацией
   - `textarea` + имя из `SVG_ATTR_KEYS` → автогенерится с `wp_kses + rawurldecode`
   - другое → проверь, что генератор шаблона знает, что делать

3. **Тест.** В `tests/phase-stage-08/test-fix-page-content-images.py`
   добавь кейс: input → expected output. Idempotency проверяется одним
   общим тестом, новый ключ туда не надо.

4. **Doc.** Если новый класс ассетов — добавь строку в таблицу TL;DR
   и (если нужно) раздел в «Поток данных».

## Стартовые значения IMAGE_ATTR_KEYS / SVG_ATTR_KEYS

Актуальный список — в самом скрипте
(`skills/wp-cli-deployer/scripts/fix-page-content-images.py`). На момент
написания этого документа:

- **IMAGE_ATTR_KEYS:** `hero_bg`, `section_image`, `model_image`,
  `background`, `side_image`, `bg_image`, `card_image`, `thumbnail`,
  `gallery_image`, `logo`, `logo_image`, `favicon`, `site_icon`.

- **SVG_ATTR_KEYS:** `icon_svg`, `svg`, `background_svg`,
  `decoration_svg`, `logo_svg`.

- **ASSET_FILE_EXTS:** `jpg`, `jpeg`, `png`, `webp`, `svg`, `ico`, `gif`, `avif`.

## Известные грабли

- **Двойной encode.** Если запустить `fix-page-content-images.py` дважды
  без `idempotency`-проверки, `{` превратится в `%257B`. Проверка в скрипте
  опирается на наличие литерального `<` (для SVG) и `{` (для image-объектов
  регулярка не матчит уже encoded строку, т.к. ищет `{...}`).

- **LZB image control принимает строку, но НЕ массив на input.** В
  page-content.html всегда сериализуй как URL-encoded JSON-строку, не как
  raw object. Блок-шаблон умеет нормализовать обратно.

- **`esc_html` режет SVG.** Никогда не оборачивай SVG-атрибут в `esc_html`
  на выходе — используй `wp_kses` с явным allowlist'ом (см. `_SVG_KSES_PHP`
  в `generate-lzb-templates.py`).

- **CSS-фоны после rsync.** Если в CSS `url('assets/...')` без `../` —
  браузер ищет относительно `style.css` и не находит. Всегда `../photos/...`.

## Связанные файлы

- `skills/wp-cli-deployer/scripts/fix-page-content-images.py` — трансформер
- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py` — шаблоны
- `skills/wp-theme-assembler/scripts/bundle-assets.py` — копирование файлов
- `tests/phase-stage-08/test-fix-page-content-images.py` — контракт-тесты

## C2: наш CSS — источник истины вида элемента

Общее правило из 16 болячек сборки (спека reference-driven §4.2): геометрию
(размер, пропорции, форму) элементов задаёт НАШ CSS, а не размеры/стили,
которые навешивает WordPress (width/height-атрибуты у `<img>`, дефолты
`wp-block-styles`, content-width обёрток). Гейт: `lint-theme-php.py` (08_build).
