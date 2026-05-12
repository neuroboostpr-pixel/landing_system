# Preview Panel + Global Palette Library — Design Spec

**Date:** 2026-05-12
**Status:** Approved (pending user review of v2), ready for implementation plan
**Author:** brainstorming session with user

## Problem

В `neuroupgrade-v2` уже есть «панель превью палитры» — `<select>` в шапке сайта, который переключает `body.theme-*` и сохраняет выбор в `localStorage`. Нужно решить три связанные задачи:

1. **Расширить runtime-панель** — добавить вторую ось «тип hero-блока» (`Static` / `Parallax`, расширяется в будущем).
2. **Вынести панель в общий компонент мастер-системы**, чтобы любой новый лендинг получал её автоматически. С возможностью **скрывать на проде** и **фиксировать дефолт для всех** через WP-админку.
3. **Создать глобальную библиотеку палитр** в мастер-системе. Каждая новая палитра, спроектированная на `/landing-design`, после апрува попадает в библиотеку и становится доступной для будущих проектов. На старте нового проекта палитры выбираются из библиотеки в одном из трёх режимов (точечно / несколько / весь каталог).

Эти задачи связаны: панель показывает в селекте то, что было выбрано из библиотеки и заснапшочено в проект на `/landing-build`.

## Out of scope (YAGNI)

- Пресеты «комбо-наборов» (палитра + hero как одно целое). Hero и палитра — независимые оси.
- Глобальная библиотека hero-вариантов. Hero регистрируется темой проекта.
- Экспорт/импорт настроек WP.
- Кастомные WP-роли — используем встроенные capabilities.
- Visual regression — это работа `/landing-qa`.
- Multi-site, WPML.
- Публикация плагина в WordPress.org.
- Автообновление плагина на проде. Обновление = новый `/landing-build`.
- Версионирование палитр (`source_version`, diff). Если палитра в библиотеке поменялась — старые проекты не подтягивают изменение автоматически.
- Автодобавление палитр в библиотеку до апрува дизайн-системы (защищает от черновиков).
- Удаление палитр из библиотеки автоматическими средствами. Только ручная правка YAML.

## Lifecycle (как одна палитра живёт от идеи до прода)

```
/landing-design
    │
    ├─ создаёшь палитру с нуля → пишется в <project>/05_ДИЗАЙН-СИСТЕМА/palettes.yaml
    │                            (id + говорящее имя + токены)
    │
    │  [палитра пока ТОЛЬКО в проекте]
    │
    ▼
ты апрувишь дизайн-систему (HARD GATE)
    │
    ├─ скрипт-экспортёр читает <project>/05_ДИЗАЙН-СИСТЕМА/palettes.yaml
    └─ добавляет новые id в landing_system/presets/palettes.yaml
       (дедупликация по id; если id есть — пропускает с notice)
    ▼
/landing-build
    │
    ├─ снапшотит выбранные палитры (из 04_БРЕНД/palettes.yaml проекта)
    │  в тему: CSS-классы body.theme-<id> + регистрация фильтра
    │  lp_preview_panel_axes
    ▼
Runtime-панель на сайте показывает их в селекте

──────────────────────────────────────────────────────────────────────
Следующий проект:
/landing-brand
    │
    ├─ агент спрашивает режим:
    │     [1] точечно (1-3)
    │     [2] несколько (4-6, рекомендуется)
    │     [3] весь каталог
    ├─ агент предлагает кандидатов из landing_system/presets/palettes.yaml
    │  на основе niche-analysis + brand-input
    ├─ ты подтверждаешь/правишь набор
    └─ выбранные палитры снапшотятся в <project>/04_БРЕНД/palettes.yaml

(затем — /landing-design, и палитры могут уйти обратно в библиотеку,
если ты создашь там новые)
```

## Architecture

Три отдельных слоя:

| Слой | Что | Где живёт |
|---|---|---|
| **Global palette library** | YAML-файл с накопленной коллекцией палитр | `landing_system/presets/palettes.yaml` |
| **Project snapshot** | Поднабор палитр, заснапшоченных в проект | `<project>/04_БРЕНД/palettes.yaml` |
| **WP-плагин `lp-preview-panel`** | Runtime-панель, админка, capability-gate, фиксация дефолтов | `<project>/08_КОД/plugins/lp-preview-panel/` (копируется из `template/08_КОД/plugins/`) |

### Разделение ответственности плагина и темы

| Слой | Знает | НЕ знает |
|---|---|---|
| **Плагин** | как нарисовать панель, как читать/писать WP-опции, capability-check, JS-движок переключения, localStorage, query-params, страница в админке | какие именно палитры/hero существуют |
| **Тема** | свой список палитр (читает из `<project>/04_БРЕНД/palettes.yaml`) и hero-типов, CSS под каждый класс (`body.theme-k`, `body.hero--parallax`), assets для hero | как устроена панель, где хранится дефолт |

### Контракт между плагином и темой

Тема регистрирует оси через фильтр `lp_preview_panel_axes`:

```php
add_filter( 'lp_preview_panel_axes', function ( $axes ) {
    // Палитры — генерируются wp-theme-assembler из 04_БРЕНД/palettes.yaml
    // при /landing-build. Тут — пример того, как это выглядит после генерации.
    $axes['palette'] = [
        'label'             => 'Палитра',
        'default'           => 'paper-minimal',
        'body_class_prefix' => 'theme-',
        'options' => [
            'paper-minimal'   => 'Paper Minimal',
            'quiet-dark'      => 'Quiet Dark',
            'beige-editorial' => 'Beige Editorial',
            'iqido-guideline' => 'IQIDO Guideline',
        ],
    ];
    // Hero — тема регистрирует сама, без библиотеки.
    $axes['hero'] = [
        'label'             => 'Hero',
        'default'           => 'static',
        'body_class_prefix' => 'hero--',
        'options' => [
            'static'   => 'Static',
            'parallax' => 'Parallax',
        ],
    ];
    return $axes;
} );
```

### Структура плагина

```
template/08_КОД/plugins/lp-preview-panel/
├── lp-preview-panel.php          (plugin header, bootstrap)
├── includes/
│   ├── class-axes.php            (читает фильтр lp_preview_panel_axes)
│   ├── class-panel.php           (рендер фронт-панели через wp_body_open)
│   └── class-settings.php        (страница админки Settings → Превью-панель)
├── assets/
│   ├── panel.css                 (стили панели, портированы из nu-theme-bar)
│   ├── panel.js                  (init + change handlers, все оси)
│   └── admin.js                  (только для страницы настроек)
├── tests/
│   ├── php/                      (PHPUnit)
│   ├── js/                       (Vitest + jsdom)
│   └── bats/                     (миграционный скрипт)
└── readme.txt
```

## Global Palette Library

### Файл

`landing_system/presets/palettes.yaml`. Один файл, все палитры. Читается глазом, diff'ится в git.

### Схема записи

```yaml
palettes:
  - id: paper-minimal
    name: "Paper Minimal"
    description: "Светлый бумажный минимализм. Подходит editorial-нишам."
    created_at: "2026-05-12"
    created_in_project: "neuroupgrade-v2"
    tokens:
      bg_base: "#FAFAF7"
      bg_alt:  "#F0EFE9"
      text_primary: "#1A1A1A"
      text_muted:   "#525252"
      accent:       "#C44E2A"
      accent_alt:   "#0E2B30"
      border:       "#D6D5CE"
      # точный список токенов — берётся из текущей схемы
      # skill design-tokens-generation на момент реализации

  - id: quiet-dark
    name: "Quiet Dark"
    ...
```

**Поля:**
- `id` — kebab-case, уникальный в библиотеке. Используется как `body.theme-<id>` и ключ опции.
- `name` — человекочитаемое имя, отображается в селекте панели и в `/landing-brand`-выборе.
- `description` — одна строка, помогает агенту/тебе на этапе выбора кандидатов.
- `created_at`, `created_in_project` — для трассировки. Не обязательны функционально, но полезны.
- `tokens` — словарь токенов. Структура должна совпадать со структурой токенов проекта в `05_ДИЗАЙН-СИСТЕМА`.

### Правила добавления

1. Палитра создаётся **только** на `/landing-design`, в `<project>/05_ДИЗАЙН-СИСТЕМА/palettes.yaml`.
2. При **апруве дизайн-системы** (HARD GATE проходит) скрипт-экспортёр копирует новые палитры в `landing_system/presets/palettes.yaml`.
3. **Дедупликация по `id`.** Если `id` уже есть в библиотеке — пропускается с notice «id collision, library entry preserved». Так защищаемся от случайных перезаписей чужой работой.
4. Никакого автодобавления до апрува. Никакого автоудаления.
5. Ручная правка YAML — всегда валидный путь (для именования, описаний, чистки).

### Snapshot в проект

На `/landing-build` (или `/landing-brand`, если палитры выбираются из библиотеки):

1. Выбранные палитры копируются из `landing_system/presets/palettes.yaml` в `<project>/04_БРЕНД/palettes.yaml` целиком (id + name + tokens).
2. Скрипт темы (`wp-theme-assembler`) генерирует CSS-классы `body.theme-<id> { --bg-base: ...; --text-primary: ...; }` в `assets/css/palettes.css`.
3. Скрипт темы генерирует блок `add_filter('lp_preview_panel_axes', ...)` в `functions.php` с актуальным списком.

После этого прод-сайт самодостаточен — глобальная библиотека для него не нужна.

## Palette Selection Flow (`/landing-brand`)

Агент `/landing-brand` после анализа brand-input спрашивает:

```
Сколько палитр показать клиенту на согласовании?

  [1] Точечно (1-3)        — клиент знает что хочет
  [2] Несколько (4-6)      — есть направление, выбираем из вариаций (рекомендуется)
  [3] Весь каталог         — клиент в полном поиске
```

**Режим [1] и [2]:**
- Агент предлагает кандидатов из библиотеки на основе niche-analysis (тон ниши, целевая аудитория) + brand-input (если уже есть направление).
- Показывает: `id`, `name`, `description`, мини-превью токенов в терминале.
- Ты подтверждаешь/правишь набор.

**Режим [3]:**
- Снапшотится вся библиотека.

**Edge-case.** Клиент посмотрел набор и говорит «ни одна не подходит, ещё». Решение для MVP: перезапустить `/landing-brand` с новым набором или докинуть в `04_БРЕНД/palettes.yaml` руками. Никакой `--extend-palettes` команды на старте не делаем (YAGNI).

**Дефолт.** В `lp_preview_panel.defaults.palette` пишется первая палитра из снапшота. Можно поменять в WP-админке.

## UI Runtime Panel

### Front-end панель

Рендерится плагином в хук `wp_body_open`. Класс контейнера — `.lp-preview-panel`. Каждая ось — отдельная строка с `<label>` и `<select data-lp-axis="<key>">`.

```
┌──────────────────────────────────────────────────────────────────────┐
│ Превью палитры:        [ Quiet Dark ▾ ]               выбор сохр-ся │
│ Превью hero:           [ Parallax ▾ ]                                │
└──────────────────────────────────────────────────────────────────────┘
```

Mobile (≤640px): подписи `.label/.hint` скрываются, селекты во всю ширину, по одному на строке.

A11y: `role="region"`, `aria-label="Панель превью"`, `<label>` к каждому select, `screen-reader-text` для подписи.

### JS-движок (panel.js)

Единый обработчик на все оси:

1. **Init.** Для каждой зарегистрированной оси значение читается в приоритете:
   `URL ?<axis>=<value>` → `localStorage['lp-axis-<axis>']` → серверный дефолт (`wp_options`) → `default` из фильтра темы.
   Применяется как класс на `<body>`: `theme-<id>`, `hero--<id>`. `select.value` синхронизируется.
2. **Change.** При смене селекта: снять старый класс по префиксу оси, добавить новый, записать в `localStorage['lp-axis-<axis>']`.
3. **Per-axis isolation.** Оси независимы — смена палитры не трогает hero и наоборот.

Серверный дефолт прокидывается на фронт через `wp_localize_script` (или inline `<script>`).

### Применение hero-варианта в теме

Оба варианта hero одновременно в DOM, видимость через body-класс:

```css
.lp-hero__parallax-stage { display: none; }
body.hero--parallax .lp-hero__parallax-stage { display: block; }
body.hero--parallax .lp-hero__static-bg     { display: none; }
```

Тема обязана:
- Скрыть/показать DOM-узлы под `body.hero--*`.
- Использовать `loading="lazy"` для не-активных hero-ассетов.
- Опционально: JS-lazy-инициализация parallax только при `body.hero--parallax`.

## Видимость панели

| Кто | Условие | Видна? |
|---|---|---|
| Залогинен и имеет `edit_theme_options` | всегда | да |
| Аноним | `lp_preview_panel.visible_to_anon === true` | да |
| Аноним | иначе | нет (вообще не рендерится в HTML) |

«Не в HTML» — буквально: плагин возвращает раньше, чем рендерит. Не `display:none`.

## Админка WP

**Путь:** `Settings → Превью-панель` (`options-general.php?page=lp-preview-panel`).
**Capability:** `manage_options`.

### Содержимое страницы

```
Превью-панель
─────────────────────────────────────────────────────────

[✓] Показывать панель превью анонимным посетителям
    Если выключено — панель видят только админы.

─────────────────────────────────────────────────────────
Текущие дефолты для всех посетителей

  Палитра:  [ Quiet Dark               ▾ ]
  Hero:     [ Static                   ▾ ]

  [ Сохранить дефолты ]

  ─ или ─

  [ Зафиксировать мой текущий выбор как дефолт ]
  (берёт значения из твоего localStorage в этом браузере)

─────────────────────────────────────────────────────────
[ Сбросить настройки ]
```

### Хранение

Одна WP-опция `lp_preview_panel`, массивом:

```php
[
    'visible_to_anon' => true,
    'defaults' => [
        'palette' => 'quiet-dark',
        'hero'    => 'static',
    ],
]
```

### «Зафиксировать мой текущий выбор»

`admin.js` читает все `localStorage['lp-axis-*']`, подставляет значения в селекты дефолтов перед сабмитом формы. Без серверной магии.

### Sanitize

На сохранении:
- Ключ оси должен присутствовать в `lp_preview_panel_axes`.
- Значение должно быть в `options` этой оси.
- Невалидные значения отбрасываются молча с admin notice.

## Интеграция в landing-system

### Где живёт плагин

`landing_system/template/08_КОД/plugins/lp-preview-panel/` — канонический источник.

### `/landing-design` — экспорт палитр в библиотеку

При апруве дизайн-системы (HARD GATE проходит):

1. Скрипт `scripts/export-palettes-to-library.sh <project-path>` (или эквивалент в `skill design-tokens-generation`) читает `<project>/05_ДИЗАЙН-СИСТЕМА/palettes.yaml`.
2. Для каждой записи проверяет наличие `id` в `landing_system/presets/palettes.yaml`.
3. Если нет — добавляет с заполнением `created_at`, `created_in_project`.
4. Если есть — пропускает с notice (не перезаписывает).

### `/landing-brand` — выбор палитр из библиотеки

Skill `brand-kit-build` обновляется:
- Добавляется шаг «выбор режима» (1/2/3).
- Для [1]/[2] агент читает `landing_system/presets/palettes.yaml`, предлагает кандидатов на основе niche-analysis.
- Для [3] копирует всю библиотеку.
- Результат пишется в `<project>/04_БРЕНД/palettes.yaml`.

### `/landing-build` — снапшот в тему

Skill `wp-theme-assembler` обновляется:

1. Копировать `template/08_КОД/plugins/lp-preview-panel/` в `<project>/08_КОД/plugins/`.
2. Читать `<project>/04_БРЕНД/palettes.yaml`.
3. Сгенерировать `assets/css/palettes.css` с блоками `body.theme-<id> { --token: value; ... }`.
4. В `functions.php` добавить `add_filter('lp_preview_panel_axes', …)` с актуальным списком палитр + hero-вариантами темы.

### `/landing-deploy`

Skill `wp-cli-deployer` обновляется:
- Активировать плагин через `wp plugin activate lp-preview-panel`.
- В чек-лист деплоя добавлен пункт: «убедись, что `visible_to_anon` снят на проде» (или принудительно сбрасывать в `false` при первой активации).

### Миграция `neuroupgrade-v2`

Одноразовый скрипт `scripts/migrate-to-preview-panel.sh <project-path>`:

1. Парсит `08_КОД/wp-theme/header.php`, удаляет блок `<div class="nu-theme-bar">…</div>`.
2. Парсит `08_КОД/wp-theme/assets/js/main.js`, удаляет функцию `initThemeSwitcher` и её вызов.
3. Достаёт текущие палитры (`H/I/J/K`) из CSS темы и записывает их в `04_БРЕНД/palettes.yaml` с временными именами (потом ты переименуешь). Параллельно экспортирует в библиотеку.
4. Копирует плагин из `template/08_КОД/plugins/lp-preview-panel/`.
5. Генерирует фильтр `lp_preview_panel_axes` в `functions.php` темы.

Для будущих проектов миграция не нужна — всё через `/landing-build`.

### Что НЕ трогаем

- `lixiang-dubai`, старый `neuroupgrade` (без `-v2`) — у них нет панели, и она им не нужна.

## Edge-cases

| Случай | Поведение |
|---|---|
| Тема не зарегистрировала ни одной оси | Плагин просто не рендерит панель |
| `defaults.palette` в WP указывает на удалённый id | Fallback на `default` из фильтра, admin notice |
| Плагин активен, но тема не подключила фильтр | Панель не рендерится. Без warning. |
| localStorage недоступен | `try/catch`, fallback на серверный дефолт |
| Два hero одновременно в DOM, тема забыла CSS | Намеренный visible-failure — заметишь в превью, починишь стилем |
| Невалидное значение в URL | Игнорируется, fallback по цепочке |
| ID collision при экспорте палитры в библиотеку | Пропуск с notice, библиотечная запись сохраняется |
| Палитра в библиотеке поменялась после снапшота в проект | Не подтягивается. Чтобы обновить — перезапустить `/landing-build`. |
| `landing_system/presets/palettes.yaml` отсутствует | Скрипт-экспортёр создаёт его пустым с шапкой. `/landing-brand` показывает «библиотека пуста, создавай палитру в /landing-design». |
| Невалидный YAML в библиотеке | Хард-ошибка с указанием строки. Не fallback — мы не хотим терять данные. |

## Тестирование

### Плагин

| Что | Как | Где |
|---|---|---|
| Sanitize WP-опции | PHPUnit | `tests/php/test-settings.php` |
| Capability gate | PHPUnit | `tests/php/test-panel-visibility.php` |
| Регистрация осей через фильтр | PHPUnit | `tests/php/test-axes.php` |
| JS init priority (URL > LS > server > theme) | Vitest + jsdom | `tests/js/init.test.js` |
| JS body-class swap | Vitest | `tests/js/swap.test.js` |
| Migration script (neuroupgrade-v2) | bats | `tests/bats/test-migrate.bats` |

### Библиотека палитр

| Что | Как | Где |
|---|---|---|
| Экспорт: новые id добавляются, дубликаты пропускаются | bats (или pytest для py-скрипта) | `tests/test-export-palettes.bats` |
| Невалидный YAML — хард-ошибка | то же | то же |
| Snapshot в проект: id/name/tokens переносятся 1:1 | bats | `tests/test-snapshot-palettes.bats` |
| CSS-генерация: на каждую палитру — `body.theme-<id>` блок | bats + diff против fixture | `tests/test-generate-palette-css.bats` |

### E2E (ручной чек-лист на neuroupgrade-v2 после миграции)

- Залогиниться как админ → панель видна → переключить hero на Parallax → parallax-секция появилась, static исчезла.
- Разлогиниться, `visible_to_anon=false` → перезагрузить → панель отсутствует в HTML (View Source).
- `visible_to_anon=true` → панель видна анонимно.
- «Зафиксировать мой выбор» в админке → подставилось → сохранить → инкогнито → дефолты применились.
- `?palette=quiet-dark&hero=parallax` в URL → применилось независимо от localStorage.
- На `/landing-design` создать новую палитру → апрувнуть → проверить, что `id` появился в `landing_system/presets/palettes.yaml`.
- Запустить `/landing-brand` на новом тестовом проекте в режиме [2] → агент предложил кандидатов, включая только что созданную.

## Риски

| Риск | Mitigation |
|---|---|
| Клиент случайно увидит панель на проде | Default `visible_to_anon=false`. Чек-лист `/landing-deploy`. |
| Hero-ассеты грузятся даже для неактивного hero | Тема использует `loading="lazy"`, опционально JS-lazy parallax. Документировано в `template/CLAUDE.md`. |
| Конфликт `body`-классов с темой | Префиксы `theme-` и `hero--` зарезервированы. Документируем. |
| WP-опция указывает на удалённый id | Sanitize при чтении: fallback на `default`. |
| Библиотека палитр загрязняется черновиками | Экспорт только после апрува дизайн-системы (не до). |
| Палитра в библиотеке стала «устаревшей» (поменялся вкус) | Ручная правка/удаление YAML. Не лечим автоматически — это редкая операция. |
| Конфликт id (две палитры с одинаковым id из разных проектов) | Дедупликация по id с сохранением первой, notice пользователю. |

## Acceptance Criteria

1. Плагин `lp-preview-panel` лежит в `template/08_КОД/plugins/`.
2. `landing_system/presets/palettes.yaml` существует и валиден (пустой или с данными).
3. Все PHPUnit/Vitest/bats тесты зелёные.
4. neuroupgrade-v2 мигрирован: панель отрендерилась плагином, обе оси (палитра + hero) работают, поведение по палитре идентично текущему.
5. На neuroupgrade-v2 hero-ось реально переключает между двумя визуальными состояниями (static / parallax-stub).
6. В админке neuroupgrade-v2 есть страница `Settings → Превью-панель` с обеими опциями.
7. По умолчанию `visible_to_anon=false`.
8. `/landing-deploy` чек-лист содержит шаг по видимости панели.
9. `/landing-design` после апрува экспортирует палитры в `landing_system/presets/palettes.yaml` (с дедупликацией по id).
10. `/landing-brand` поддерживает три режима выбора (1-3 / 4-6 / весь каталог) и снапшотит результат в `<project>/04_БРЕНД/palettes.yaml`.
11. `/landing-build` генерирует CSS-классы `body.theme-<id>` из снапшота и регистрирует фильтр.
