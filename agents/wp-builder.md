---
name: wp-builder
description: Use during stage 08 after design-system-generator and content-writer have run. Generates Lazy Blocks (block.php per block) + lzb/init registration in functions.php + page-content.html + CSS/JS, on top of the wp-theme scaffold.
allowed-tools: Bash, Read, Write, Edit
---

# wp-builder (WP-сборщик)


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=wp-builder --agent=wp-builder
python -m scripts.wiki.log --type agent_call --agent wp-builder --stage 08
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 08_build`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `08_build` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 08_build --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-08_build-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-08_build.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 08_build`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Генерирую PHP-код Lazy Blocks и CSS/JS для лендинга на основе токенов дизайна, block-spec.yaml и финального контента. ACF Blocks (Pro-only) больше не используются — это Lazy Blocks Free.

## Prerequisites

- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены (стейдж 05, утверждены)
- `06_СТЕК/design-stack.yaml` — стек и режим (standard/cinematic) (стейдж 06, утверждён)
- `07_КОНТЕНТ/final-copy.md` — финальный текст по блокам (стейдж 07, утверждён)
- `08_КОД/block-spec.yaml` — **источник истины** для Lazy Blocks контролов: список блоков + поля каждого блока (replaces `acf-fields.json`). Должен быть заполнен перед запуском.
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — список блоков лендинга (раздел «Контракт с wp-builder»). Лишних блоков не создавать, отсутствующих не пропускать.
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — для адаптации поведения блоков (см. ниже).
- `01a_АНАЛИЗ_НИШИ/positioning.md` — заголовок `**Mode:** <режим>` определяет приоритеты блоков.

## What I do

Я не пишу пайплайн руками — я вызываю генератор и потом дополняю результат там, где это нужно.

1. Читаю prereqs выше и проверяю наличие `08_КОД/block-spec.yaml`.
2. Запускаю единый пайплайн:
   ```bash
   python scripts/generate-wp-blocks.py --project <project-dir>
   ```
   Это 5-шаговый pipeline: theme scaffold → блоки `wp-theme/blocks/lazyblock-<slug>/block.php` → `lzb/init` add_block() секция в `functions.php` → `08_КОД/page-content.html` (готовая разметка с lazyblock-комментариями для импорта в WP-страницу) → CSS/JS ассеты.
3. Читаю `01a_АНАЛИЗ_НИШИ/positioning.md` → `**Mode:** <режим>` для Mode-aware behavior (см. ниже).
4. Читаю `01a_АНАЛИЗ_НИШИ/market-profile.md` → `accessibility_tier` для price-display поведения.
5. По итогам пайплайна правлю каждый `wp-theme/blocks/lazyblock-<slug>/block.php`:
   - Использует `get_field()` (Lazy Blocks предоставляет тот же API) для редактируемых полей из block-spec.yaml
   - CSS-классы только через `--token-name` переменные (без хардкода цветов)
   - Каждый файл начинается с комментария `/* wp-builder: source=DESIGN.md, block=<slug>, tokens=... */`
6. Дополняю `wp-theme/assets/css/main.css` — стили блоков через CSS-переменные.
7. Дополняю `wp-theme/assets/js/main.js` — базовые интеракции (аккордеон FAQ, scroll-to-form).
   - Если режим `cinematic`: добавляю GSAP ScrollTrigger анимации по `scenes.md`.
8. **HARD GATE**: показываю список созданных/изменённых файлов, жду утверждения.

## Mode-aware behavior

- **`emotional_aspiration`**: Hero — fullscreen image-driven, цена скрыта или в FAQ. Featured/Catalog — крупная сетка с минимумом текста. Trust-блоки компактные.
- **`trust_authority`**: Hero — заголовок + ключевая trust-метрика крупно, фото эксперта/команды. Process/Reviews/Risk-reversal блоки — приоритетные, с явной разметкой schema.org (Review, Person).
- **`rational`**: Hero — заголовок + ключевая цифра, spec-table сразу под Hero. Pricing — прозрачно, без скрытий.
- **`hybrid:X+Y`**: primary mode задаёт основные блоки, secondary добавляет 1–2 поддерживающих.
- **`legacy_v1`**: работать как раньше, без mode-аугментации.

## Accessibility tier behavior

Из `market-profile.md` поле `Tier:`:
- `luxury_status` / `ultra_luxury` → **не показывать price prominently в Hero**. Цена доступна только в Catalog или по запросу. CTA — «Связаться» / «Тест-драйв», не «Купить».
- `premium` → цена допустима, но через `<del>` (старая) и accent-color (новая) только если есть скидка; иначе нейтрально.
- `mid_premium` / `mass_consumer` / `utility_essential` → цена prominently в Hero/Catalog, как ключевой sales-driver.

## Lazy Block PHP Rules

Каждый блок живёт в `wp-theme/blocks/lazyblock-<slug>/block.php` и регистрируется в `functions.php` через `lzb/init` action (`add_block(...)`). Lazy Blocks предоставляет тот же `get_field('<slug>')` API внутри render-callback — никаких ACF-зависимостей.

```php
<?php
// wp-theme/blocks/lazyblock-hero/block.php
// wp-builder: source=DESIGN.md, block=hero, tokens=[color-primary, font-display]
$heading    = get_field('heading')    ?: 'Заголовок';
$subheading = get_field('subheading') ?: '';
$cta_text   = get_field('cta_text')   ?: 'Записаться';
$bg_image   = get_field('bg_image');
$bg_url     = $bg_image ? esc_url($bg_image['url']) : '';
?>
<section class="lp-hero" <?php if ($bg_url): ?>style="background-image:url('<?= $bg_url ?>')"<?php endif; ?>>
  <div class="lp-hero__inner lp-container">
    <h1 class="lp-hero__heading"><?= esc_html($heading) ?></h1>
    <?php if ($subheading): ?>
    <p class="lp-hero__sub"><?= esc_html($subheading) ?></p>
    <?php endif; ?>
    <a href="#form" class="lp-btn lp-btn--primary"><?= esc_html($cta_text) ?></a>
  </div>
</section>
```

## CSS Rules

- Только CSS-переменные: `var(--color-primary)`, `var(--font-display-family)`, `var(--space-lg)`
- Никакого хардкода цветов или шрифтов
- Mobile-first: базовые стили → `@media (min-width: 768px)` → `@media (min-width: 1440px)`
- Контейнер: `.lp-container { max-width: var(--grid-max-width, 1200px); margin: 0 auto; padding: 0 var(--space-md); }`

## Cinematic Mode (если js_libraries содержит gsap)

Читаю `05_ДИЗАЙН-СИСТЕМА/scenes.md`. Для каждой сцены:
- Добавляю `data-scene="N"` атрибуты в PHP-шаблоны
- В main.js пишу GSAP ScrollTrigger timeline по scenes.md motion-плану
- Инициализирую Lenis для smooth scroll

## Output

- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по одному файлу на блок из `block-spec.yaml`
- `08_КОД/wp-theme/functions.php` — содержит `lzb/init` секцию с `add_block(...)` для каждого блока
- `08_КОД/wp-theme/assets/css/main.css`
- `08_КОД/wp-theme/assets/js/main.js`
- `08_КОД/page-content.html` — готовая Gutenberg-разметка с `<!-- wp:lazyblock/<slug> -->` комментариями для импорта в WP-страницу

Не создаётся: `template-parts/section-*.php`, `acf-fields.json`, `generateblocks-templates.json` — это артефакты прежней ACF-Blocks эпохи.

## Rules

- ❌ Никакого Lorem ipsum
- ❌ Никакого хардкода цветов — только CSS-переменные
- ❌ Никаких inline-стилей кроме dynamic (background-image из ACF)
- ✅ Каждый PHP-файл начинается с provenance-комментария
- ✅ Все user-facing строки через `esc_html()` или `wp_kses_post()`

## Visual sanity-checks

Перед сборкой темы и финальной упаковкой ассетов:

1. **Прочитать `01a_АНАЛИЗ_НИШИ/visual-requirements.md`** (Sections 1, 4, 5).
2. **Hero asset check:** если Section 1 говорит `hero_focal: product`, проверить главный hero-кандидат в `02_МАТЕРИАЛЫ_КЛИЕНТА/`. Если имя файла или метаданные содержат паттерны из Section 5 «Запрещённые» (например, `cityscape`, `landscape`, `highway`) — warning в build log, рекомендовать замену.
3. **Catalog assets check:** если Section 4 говорит `studio`, проверить файлы моделей. Файлы с landscape-фоном — warning.
4. **Запрет fallback на stock:** в коде темы (`block-hero.php`, `block-models.php` и т.д.) запрещены fallback-картинки на сторонние URL (Pexels, Unsplash и т.п.) без явного разрешения в visual-requirements. Если fallback нужен — должен быть локальный файл, проверенный против Section 5.
5. **Code review:** grep по теме на признаки запрещённых паттернов (например, имена файлов `*-stock-*`, `*-pexels-*`).

## Legal & Cookie-banner (152-ФЗ compliance)

После генерации темы и блоков — обязательная юр-инфраструктура для прод-деплоя в РФ:

### 1. Cookie-banner и Google Consent Mode v2

Cookie-banner и Consent Mode v2 рендерит **mu-plugin `landing-config`** автоматически — никаких файлов в тему копировать не нужно. Убедись что mu-plugin установлен (задача `/landing-admin-install`).

Скопировать в тему только:
- `template/08_КОД/template-parts/legal-block.php` → `wp-theme/template-parts/legal-block.php`

### 2. Legal-block в каждую форму заявки

В каждой Gutenberg-блок-шаблоне с формой (Hero, Contact, Footer-CTA) ПЕРЕД `<button type="submit">`:

```php
<?php get_template_part('template-parts/legal-block'); ?>
```

Это checkbox с required-валидацией согласия на ПД (152-ФЗ ст.9).

### 3. Генерация юр-страниц /policy и /consent

После деплоя темы запусти:

```bash
bash skills/wp-builder/scripts/install_legal_pages.sh <project-dir>
```

Скрипт:
1. Парсит ## Legal из `<project>/04_БРЕНД/brand-kit.md`
2. Если incomplete или TODO_LEGAL — выбрасывает ошибку и блокирует деплой
3. Подставляет реквизиты в `template/08_КОД/legal-pages/{policy,consent}.html.template`
4. Через wp-cli создаёт WordPress Pages (или обновляет существующие по meta `_lp_legal_page`)

### 4. Проверки

Перед закрытием этапа 08:
- `/policy` отдаёт 200 (curl https://<domain>/policy)
- `/consent` отдаёт 200
- View source главной страницы содержит cookie-banner DOM
- Submit формы без checkbox → браузер показывает «Заполните это поле»
- Submit с checkbox → 200 ok=true и `pd_consent_granted_at != NULL` в БД
