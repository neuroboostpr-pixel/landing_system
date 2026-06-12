# Reference-Driven Flow — Phase 4 (Zone C: сборка в WordPress)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans.

**Goal:** Зона C спеки: всё для сборки выводится из composed.html, цвета только через токены, деплой не забывает .htaccess/плагины/favicon, болячки сборщика чинятся по приоритету.

### Task C3: Токенизация цветов (verify-tokens)
- `scripts/verify_tokens.py`: прямые цвета (#hex/rgb()/hsl()) допустимы ТОЛЬКО внутри
  определения `:root {}`; исключения — whitelist (бренд-цвета мессенджеров
  #25D366/#0088cc/#2AABEE, зелёная точка «онлайн»), `meta name="theme-color"`,
  маркер `/* token-exempt */` на строке.
- Проверяет и composed.html (<style>), и CSS-файлы темы (`08_КОД/wp-theme/**/*.css`)
  — «токенизировать макет и тему синхронно» (спека §4.3).
- Tests: tests/phase-stage-07/test_verify_tokens.py (TDD).
- Гейт: hard_check `tokens_only_colors` в 07c_composed (+ упоминание в 08).

### Task C4: Деплой — .htaccess, плагины, favicon
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh`:
  1. после rsync темы — rsync `08_КОД/plugins/` → `wp-content/plugins/` + `wp plugin activate`;
  2. `wp rewrite flush --hard` + проверка наличия `.htaccess` (создать дефолтный WP если нет);
  3. favicon: если есть `04_БРЕНД/favicon/favicon.png` — `wp media import` + `wp option update site_icon`.
- Идемпотентно; каждый шаг с явным логом.

### Task C1: Конвертер composed.html → файлы сборки
- `skills/wp-gutenberg-block-builder/scripts/composed-to-build.py`:
  composed.html → (a) `05_ДИЗАЙН-СИСТЕМА/tokens.from-composed.json` (из :root),
  (b) `08_КОД/block-spec.yaml` (секции → блоки: slug, поля-тексты, repeater для
  повторяющихся карточек), (c) `08_КОД/fonts-deps.yaml` (из <head>),
  (d) манифест фото (src из <img>).
- Acceptance: `lint-composed-vs-spec.py` проходит на сгенерированном spec.
- Tests: fixture composed.html → проверка структуры выходов.

### Task C2: Болячки сборщика (приоритет — ломающие вёрстку)
По таблице спеки §4.2, чинится в `scripts/generate-wp-blocks.py` (+ helpers), TDD:
1. контент дублируется → не дописывать поля, если вёрстка их содержит;
2. внутренние карточки теряются → вставлять вложенные блоки;
3. картинки: имя файла → путь в теме;
4. масштаб: CSS-правила покрывают верхние обёртки блока;
5. дефолты WP перебивают кнопки → тема отключает дефолты;
6. перенос CSS точный, без «улучшений» (никаких добавленных min-height);
7. повторное объявление функции в block.php → оборачивать function_exists;
8. `<script>` в блоке → только в файлы темы;
9. фото растягивает формы → CSS-геометрия приоритетнее размеров WP.
Общее правило: **наш CSS — источник истины вида элемента** (фиксируется в asset-pipeline.md).

**Допущение:** часть болячек проверяема только живым прогоном на Beget — для них код+тест на генераторе, прогон отметить в STATUS.
