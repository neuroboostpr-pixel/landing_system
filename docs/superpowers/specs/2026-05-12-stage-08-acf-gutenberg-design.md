# Stage 08 — Verifiable WP Build (ACF Blocks + Gutenberg + Hard Gate)

**Date:** 2026-05-12
**Status:** Approved (pending user review of written spec), ready for implementation plan
**Author:** brainstorming session with user

## Problem

Spec `landing-system-design.md` обещает на stage 08:
- генерацию Gutenberg-блоков (`08_КОД/gutenberg-blocks/`),
- генерацию ACF-полей (`08_КОД/acf-fields.json`),
- сценарий: «клиент логинится в WP-админку, видит ACF-поля, правит текст и цену».

В реальности **3 существующих лендинга не имеют ни ACF, ни Gutenberg-блоков.** Корневые причины:

1. **Skill `wp-gutenberg-block-builder` лживо назван** — генерирует только PHP template-parts (`section-hero.php` через `get_template_part`), не Gutenberg-блоки. Ни в одном из 6 скриптов skill'а нет `register_block_type` или `block.json`.
2. **`generate-acf.py` хардкодит 6 секций** (`hero/about/services/proof/form/faq`) через aliases-словарь, не соответствующих реальной структуре проектов (где 10-14 нестандартных секций).
3. **Stage-gate на 08 пуст** — переход на stage 09 (deploy) не требует наличия ни ACF JSON, ни блоков, ни регистрации. Битый артефакт не блокирует деплой.
4. **`wp acf import` в `deploy-wordpress.sh`** глотает ошибки (`2>/dev/null || true`), поэтому если ACF-плагин не активен или JSON битый — никто не узнаёт.
5. **Spec не проверяется автоматически** — bats-тестов на этап 08 не существует.

В результате клиент не может редактировать тексты через WP-админку, требуется ручная правка PHP-файлов и редеплой.

## Goals

1. Каждый новый лендинг, прошедший `/landing-build`, имеет:
   - `acf-fields.json` с группой полей на каждый H2-блок из `final-copy.md`.
   - `gutenberg-blocks/<slug>/block.json` для каждого блока.
   - `acf_register_block_type(...)` или эквивалентную регистрацию в `functions.php`.
2. Менеджер заходит в WP-админку, открывает страницу, видит блоки в инсертере + ACF-форму со всеми полями в сайдбаре, редактирует тексты, сохраняет — без правки PHP.
3. Stage-08 hard-gate блокирует переход на deploy, если артефакты отсутствуют.
4. Существующие 3 лендинга помечаются `legacy: true`, gate их не блокирует. Backport-скрипт переводит их в новую архитектуру по требованию.

## Out of scope (YAGNI)

- **Native Gutenberg + JSX/React.** Отказались в пользу ACF Blocks (UX менеджера идентичен, время разработки в 3-5 раз меньше).
- **Frontend editor** (inline-editing на live-сайте). Менеджер работает через wp-admin.
- **Изменение формата `final-copy.md`** (frontmatter, YAML-content). Парсер адаптируется к существующему свободному markdown.
- **ACF Pro.** Free версии достаточно (text, textarea, wysiwyg, url, image, repeater).
- **Visual block thumbnails.** Иконка из dashicons + заголовок.
- **CI/CD автоматизация.** Гейты локально через `npm run test:*`.
- **Backwards-compatibility между версиями ACF.** Пишем под current ACF Free v6+.
- **UI для списка legacy-проектов.** `grep -l "legacy: true" Lendings/*/.landing-state.yaml`.
- **Авто-перевод field labels на русский.** ContentParser использует заголовок поля или fallback на `name.replace('-', ' ').capitalize()`. Ручная правка в JSON всегда возможна.
- **Backport `neuroupgrade-v2` и других существующих лендингов** в рамках этой фичи. Делается отдельно после merge'а.

## Architecture

Три связанных слоя.

### Layer A — Content parser

Модуль `scripts/lib/content_parser.py`. Один класс `ContentParser` с двумя статическими методами: `parse(md_path) -> list[Block]` и `validate(blocks) -> None`.

Используется **всеми** генераторами и backport-скриптом — single source of truth для структуры блоков.

```python
@dataclass
class Field:
    name: str
    label: str
    type: str  # text | textarea | wysiwyg | url | image | repeater
    default: str | None = None
    subfields: list[Field] | None = None
    defaults: list[dict] | None = None

@dataclass
class Block:
    slug: str
    title: str
    fields: list[Field]
    source_line: int
```

### Layer B — Generators

Четыре скрипта в `skills/wp-gutenberg-block-builder/scripts/`:

| Скрипт | Что пишет |
|---|---|
| `generate-acf.py` (рефакторинг) | `08_КОД/acf-fields.json` — одна ACF group на блок, привязка к `acf/lp-<slug>` |
| `generate-block-json.py` (новый) | `08_КОД/gutenberg-blocks/<slug>/block.json` для каждого блока |
| `generate-block-registration.py` (новый) | AUTO-GENERATED секция в `08_КОД/wp-theme/functions.php` с `register_block_type()` циклом |
| `generate-theme.py` (расширение) | Создаёт недостающие `template-parts/block-<slug>.php`, не перезаписывает существующие |

Оркестратор: `scripts/generate-wp-blocks.py` → npm-команда `npm run generate-wp-blocks`. Используется из `wp-theme-assembler` и из `backport-acf-to-legacy.sh`.

### Layer C — Hard gate + legacy

| Скрипт | Что делает |
|---|---|
| `scripts/lib/gate-checks/stage-08.sh` (новый, вызывается из `gate-check.sh`) | 8 hard + 2 warning проверок. Skip если `legacy: true` в state.yaml |
| `scripts/lib/gate-checks/stage_08_helper.py` (новый) | Python-helper для проверок 5-9 (валидация JSON, сравнение со структурой блоков) |
| `scripts/mark-legacy-projects.sh` (новый, одноразовый) | Помечает `legacy: true` все Lendings/* проекты не проходящие gate |
| `scripts/backport-acf-to-legacy.sh` (новый) | Применяет генераторы B на проект. Опции `--dry-run`, `--force`. Бэкап в `.backport-backup-<ts>/`. Снимает `legacy: true` после успеха |
| `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` (правка) | `wp acf import` без `2>/dev/null || true` — fail loudly если импорт битый |

### Зависимости

```
ContentParser (A)
    ├──── used by ─→ generate-acf.py (B)
    ├──── used by ─→ generate-block-json.py (B)
    ├──── used by ─→ generate-block-registration.py (B)
    ├──── used by ─→ generate-theme.py (B)
    ├──── used by ─→ stage_08_helper.py (C)
    └──── used by ─→ backport-acf-to-legacy.sh (через генераторы B)

gate-check.sh (C) проверяет файлы которые создают B
```

## Content Parser (Layer A) — details

### Алгоритм

1. **Прочитать** `07_КОНТЕНТ/final-copy.md` (или альтернативный путь из `.landing-state.yaml`).
2. **Разбить по `^## `** — каждый H2 = один Block. Любой preamble до первого H2 игнорируется.
3. **Для каждого сегмента:**
   - **Slug:** заголовок → lowercase → стрип эмодзи/символов → lookup в `scripts/lib/slug-aliases.yaml` → если нет alias, транслитерация кириллица→латиница → kebab-case.
   - **Title:** оригинальный H2 текст.
   - **Source line:** номер строки.
   - **Fields:** ordered rule application (см. таблицу).

### Field type heuristics

| Pattern в markdown | ACF field name | Type |
|---|---|---|
| `*курсив*` в начале блока, или blockquote `> ...` | `eyebrow` | text |
| Первая prose-строка (не курсив/quote/list) | `title` | text |
| Параграф `**bold link:**` или `[label](url)` CTA-стиль | `cta-label` + `cta-url` | text + url |
| `![alt](path)` | `image-<alt-slug или counter>` | image |
| Плоский список `- item\n- item` | `bullets` | repeater (subfield `text: text`) |
| Серия `### Heading` ≥2 с одинаковой структурой под ними | имя группы по эвристике | repeater (subfields из общих pattern'ов) |
| Параграф ≥80 символов | `body` | textarea |
| Параграф ≤80 символов | `lede` | text |

Если эвристика не уверена в типе — `textarea` (безопасный дефолт). Никакого ML, просто ordered regex.

### Slug aliases

`scripts/lib/slug-aliases.yaml` — расширяемый словарь:

```yaml
"тарифы": pricing
"цены": pricing
"hero": hero
"главный экран": hero
"программа": program
"модули": program
"аудитория": audience
"для кого": audience
"автор": author
"кейсы": cases
"вопросы": faq
"faq": faq
"контакты": contacts
"футер": footer
"подвал": footer
"cta": cta
"призыв": cta
```

Редактируется по мере встречи новых кейсов. На старте — алиасы из существующих лендингов.

### Block icons

`scripts/lib/block-icons.yaml` — таблица slug → dashicon name:

```yaml
hero: cover-image
pricing: tag
program: portfolio
audience: groups
author: businessperson
cases: awards
faq: format-aside
footer: editor-alignleft
cta: megaphone
# fallback: block-default
```

### Validation

`ContentParser.validate(blocks)` raises `ContentParseError`, если:

- 0 H2 в файле.
- Slug collision (`## Цены` и `## Тарифы` оба алиасятся в `pricing` → ошибка с указанием line numbers, предложение переименовать или убрать alias).
- Любой блок имеет 0 полей.

### Manual review flag

Если эвристика обнаруживает «неуверенный» случай (блок имеет необычную структуру, нестандартные элементы), парсер добавляет slug в список `manual_field_review_needed` в `.landing-state.yaml`. Gate показывает warning (не блокирует), просит ручного ревью.

### Edge cases

| Случай | Поведение |
|---|---|
| H2 на английском | Транслитерация no-op, slug = lowercase kebab |
| Эмодзи в заголовке | Стрипаются |
| Inline HTML | Сохраняется в `body` (wysiwyg) |
| Таблицы markdown | Пытаемся в repeater с колонками = subfields, fallback в textarea |
| Изображение в первом параграфе | `featured-image`, не `image-1` |

## Generators (Layer B) — details

### B1. `generate-acf.py` (рефакторинг)

**Input:** `--project <path>`
**Reads:** `07_КОНТЕНТ/final-copy.md` через ContentParser
**Writes:** `08_КОД/acf-fields.json`

**Format** — стандартный ACF Local JSON export (импортируется через `wp acf import`):

```json
[
  {
    "key": "group_lp_hero",
    "title": "Hero",
    "fields": [
      {"key": "field_lp_hero_eyebrow", "label": "Eyebrow", "name": "eyebrow", "type": "text"},
      {"key": "field_lp_hero_title", "label": "Title", "name": "title", "type": "text"},
      {"key": "field_lp_hero_bullets", "label": "Bullets", "name": "bullets", "type": "repeater",
       "sub_fields": [
         {"key": "field_lp_hero_bullets_text", "label": "Text", "name": "text", "type": "text"}
       ]}
    ],
    "location": [[{"param": "block", "operator": "==", "value": "acf/lp-hero"}]]
  }
]
```

- Каждый блок — одна ACF group.
- `location` всегда привязан к ACF block (`acf/lp-<slug>`).
- Ключи детерминированы (`group_lp_<slug>`, `field_lp_<slug>_<fieldname>`). Идемпотентно.

**Behaviour:**
- Если `acf-fields.json` существует — бэкап `acf-fields.json.bak` + перезапись.
- ContentParseError → exit 1, понятное сообщение со ссылкой на строку.

### B2. `generate-block-json.py`

**Writes:** `08_КОД/gutenberg-blocks/<slug>/block.json` per block.

Template:

```json
{
  "apiVersion": 3,
  "name": "acf/lp-hero",
  "title": "Hero",
  "description": "Hero section (auto-generated from 07_КОНТЕНТ/final-copy.md)",
  "category": "lp-blocks",
  "icon": "cover-image",
  "keywords": ["hero", "lp"],
  "acf": {
    "mode": "preview",
    "renderTemplate": "template-parts/block-hero.php"
  },
  "supports": {
    "align": false,
    "anchor": true,
    "html": false
  }
}
```

- `name: "acf/lp-<slug>"` — `acf` namespace обязателен для ACF Blocks.
- `category: "lp-blocks"` — собственная категория в инсертере (регистрируется в functions.php).
- `icon` через `block-icons.yaml`, fallback `block-default`.
- `mode: "preview"` — в редакторе сразу показывает PHP-превью с дефолтными значениями.

### B3. `generate-block-registration.py`

**Modifies:** `08_КОД/wp-theme/functions.php`

Добавляет/обновляет AUTO-GENERATED секцию:

```php
// AUTO-GENERATED START: lp-block-registration — DO NOT EDIT MANUALLY
//                      Regenerated by generate-block-registration.py
add_action( 'init', 'lp_register_block_category' );
function lp_register_block_category() {
    add_filter( 'block_categories_all', function ( $categories ) {
        return array_merge(
            $categories,
            [ [ 'slug' => 'lp-blocks', 'title' => 'Landing-page blocks', 'icon' => null ] ]
        );
    } );
}

add_action( 'init', 'lp_register_acf_blocks' );
function lp_register_acf_blocks() {
    $blocks = [ 'hero', 'audience', 'program', /* ... */ ];
    foreach ( $blocks as $slug ) {
        register_block_type( get_template_directory() . '/../../gutenberg-blocks/' . $slug );
    }
}
// AUTO-GENERATED END
```

- Маркеры `AUTO-GENERATED START` / `END` ограничивают регенерируемую секцию.
- Код вне маркеров (кастомные хелперы `nu_field()`, `nu_body_class`, фильтры `lp_preview_panel_axes`) не трогается.
- Если маркеры удалены ручной правкой — скрипт отказывается работать с сообщением «add markers back or use --force».
- Бэкап `functions.php.bak` перед изменением.

### B4. `generate-theme.py` (расширение)

- Берёт `list[Block]` через ContentParser.
- Если `template-parts/block-<slug>.php` **не существует** — создаёт заглушку с актуальными `nu_field('field-name', 'default-value')` вызовами.
- Если файл **существует** — не перезаписывает (сохраняет ручную работу).

### Orchestrator: `scripts/generate-wp-blocks.py`

Последовательно вызывает B1 → B2 → B3 → B4 на указанном проекте. Поддерживает `--dry-run` (печатает что будет сделано без записи).

В `package.json`:

```json
"scripts": {
  "generate-wp-blocks": "python scripts/generate-wp-blocks.py"
}
```

Используется из `wp-theme-assembler` (новый этап в pipeline) и из `backport-acf-to-legacy.sh`.

## Hard Gate (Layer C) — details

### `scripts/lib/gate-checks/stage-08.sh`

Вызывается из основного `gate-check.sh` когда проверяется stage 08.

**Legacy bypass:** первая команда модуля:

```bash
if grep -q "^[[:space:]]*legacy:[[:space:]]*true" "$PROJECT/.landing-state.yaml" 2>/dev/null; then
    echo "⚠ stage-08: skipping hard-checks (project marked legacy)"
    exit 0
fi
```

### 10 проверок

| # | Проверка | Level | Hard-fail message |
|---|---|---|---|
| 1 | `08_КОД/wp-theme/` exists | hard | `08_КОД/wp-theme/ not found — run /landing-build first` |
| 2 | ≥1 `register_block_type` в functions.php | hard | `No Gutenberg block registration found in functions.php — run npm run generate-wp-blocks` |
| 3 | `acf-fields.json` exists | hard | `08_КОД/acf-fields.json missing — run scripts/generate-acf.py` |
| 4 | `acf-fields.json` is valid JSON | hard | `acf-fields.json is not valid JSON: <error>` |
| 5 | ACF group for each H2 in final-copy.md | hard | `ACF group missing for block 'foo' (H2 at line 47). Run npm run generate-wp-blocks` |
| 6 | Each ACF group has ≥1 field | hard | `ACF group 'foo' has no fields` |
| 7 | Each registered block has `template-parts/block-<slug>.php` | hard | `block-foo.php template part missing for registered block 'acf/lp-foo'` |
| 8 | `block.json` exists for each block | hard | `gutenberg-blocks/foo/block.json missing` |
| 9 | `block.json` has title/description/category/icon | warning | `block.json for 'foo' missing recommended fields: <list>` |
| 10 | `manual_field_review_needed` пуст в state.yaml | warning | `ContentParser flagged blocks for manual review: <list>` |

### Python helper `stage_08_helper.py`

Содержит логику проверок 5-9 (JSON parsing, comparison с ContentParser output, glob проверки). Возвращает exit 0/1, печатает errors/warnings в stderr.

### `scripts/mark-legacy-projects.sh`

Одноразовый, идемпотентный. При первой раскатке фичи помечает `legacy: true` все Lendings-проекты не проходящие gate:

```bash
for project in "$LANDINGS_ROOT"/*/; do
    [ -f "$project/.landing-state.yaml" ] || continue
    if bash scripts/lib/gate-checks/stage-08.sh "$project" >/dev/null 2>&1; then
        echo "✓ $(basename "$project") — passes stage-08, no marking needed"
    else
        if grep -q "^legacy:" "$project/.landing-state.yaml"; then
            echo "  $(basename "$project") — already marked"
        else
            echo "⚠ $(basename "$project") — marking legacy:true"
            echo "legacy: true  # auto-marked $(date -u +%Y-%m-%d) — pre-stage-08-hardening" >> "$project/.landing-state.yaml"
        fi
    fi
done
```

### `scripts/backport-acf-to-legacy.sh`

Usage: `backport-acf-to-legacy.sh <project-path> [--dry-run] [--force]`.

**Шаги:**
1. Бэкап текущих `functions.php`, `acf-fields.json` в `.backport-backup-<timestamp>/`.
2. ContentParser.validate на `07_КОНТЕНТ/final-copy.md` — если падает, exit с сообщением.
3. `--dry-run`: `generate-wp-blocks.py --dry-run`, печатает diff, не пишет.
4. Без `--force`: если `acf-fields.json` уже существует, refuses с сообщением.
5. `python scripts/generate-wp-blocks.py --project <path>`.
6. `bash scripts/lib/gate-checks/stage-08.sh <path>` — должен пройти.
7. Снимает `legacy: true` из state.yaml.

### `wp-cli-deployer/scripts/deploy-wordpress.sh` (правка)

Меняем:

```bash
ssh ... "echo '${ACF_CONTENT}' | wp acf import --json - --path=... --allow-root" 2>/dev/null || true
```

На:

```bash
if [ -f "$ACF_JSON" ]; then
    if ! ssh ... "wp plugin is-active advanced-custom-fields --path=... --allow-root"; then
        echo "❌ ACF plugin not active on remote. Install/activate first:"
        echo "   wp plugin install advanced-custom-fields --activate"
        exit 1
    fi
    ssh ... "wp acf import --json - --path=... --allow-root" < "$ACF_JSON" || {
        echo "❌ wp acf import failed (see stderr above)"
        exit 1
    }
fi
```

Деплой падает явно, если ACF не активен или JSON битый. Никаких silent fails.

## Edge cases

| Случай | Поведение |
|---|---|
| Слабый markdown — генерит «generic-блок» с body+title | `manual_field_review_needed` warning |
| Маркеры AUTO-GENERATED удалены | Скрипт отказывается, требует `--force` или восстановления маркеров |
| `legacy: true` забыли убрать после backport | Backport автоматически снимает после успешного gate-check'а |
| ACF-плагин не активен на live | deploy-wordpress.sh падает с actionable message |
| Slug collision (две H2 → один alias) | ContentParseError с line numbers, предлагает переименовать |
| ACF-ключи зависят от hash/timestamp | Не зависят (детерминированные: `field_lp_<slug>_<name>`) |
| Backport перетирает ручные правки в block.php | `generate-theme.py` не перезаписывает существующие `block-*.php` |
| 60 тестов проходят, но реальный WP не работает | Manual E2E checklist обязателен перед merge |

## Testing

### Layer A — pytest

`tests/phase-stage-08/test-content-parser.py` (~25-30 кейсов):

| Группа | Что |
|---|---|
| Slug generation | транслитерация, kebab-case, эмодзи, aliases |
| Field types | каждая эвристика (italic→eyebrow, list→bullets, ### series→repeater) |
| Defaults | дефолты вытаскиваются из текста |
| Validation | 0 H2, slug collision, empty block |
| Roundtrip | parse(fixture) → expected JSON exact match |
| Edge cases | таблицы, HTML, эмодзи, non-latin |

### Layer B — bats

| Файл | Тесты |
|---|---|
| `test-generate-acf.bats` | 5-6 |
| `test-generate-block-json.bats` | 4-5 |
| `test-generate-block-registration.bats` | 4-5 |
| `test-generate-wp-blocks.bats` | 3-4 |

Каждый bats-файл: фикстуры из `fixtures/content/*.md`, ожидаемые результаты в `fixtures/expected/*.json`, тесты идемпотентности, бэкапа, error handling.

### Layer C — bats

| Файл | Тесты |
|---|---|
| `test-gate-check-stage-08.bats` | 12-14 (по одному на каждую проверку + legacy bypass + happy path) |
| `test-backport-legacy.bats` | 5-6 (dry-run, force, autobackup, legacy unmark) |
| `test-mark-legacy-projects.bats` | 3-4 (идемпотентность) |

### Тестовая инфраструктура

```
tests/phase-stage-08/
├── fixtures/
│   ├── content/
│   │   ├── minimal.md
│   │   ├── all-field-types.md
│   │   ├── repeater-blocks.md
│   │   ├── slug-collision.md
│   │   ├── empty.md
│   │   ├── empty-block.md
│   │   └── neuroupgrade-snapshot.md
│   ├── expected/
│   │   ├── minimal.acf.json
│   │   ├── minimal.functions.php
│   │   ├── minimal.block-hero.json
│   │   └── ...
│   └── projects/
│       ├── valid-project/
│       ├── missing-acf/
│       ├── orphan-block/
│       └── legacy-project/
├── test-content-parser.py
├── test-generate-acf.bats
├── test-generate-block-json.bats
├── test-generate-block-registration.bats
├── test-generate-wp-blocks.bats
├── test-gate-check-stage-08.bats
├── test-backport-legacy.bats
└── test-mark-legacy-projects.bats
```

### npm script

```json
"test:phase-stage-08": "bats tests/phase-stage-08/*.bats && python -m pytest tests/phase-stage-08/test-content-parser.py -v"
```

**Итого:** ~30 pytest + ~30 bats = ~60 тестов.

### Manual E2E checklist (после реализации)

1. `/landing-new test-stage08` → пройти этапы 01-07 с минимальным контентом.
2. `/landing-build` → проверить наличие `acf-fields.json`, `gutenberg-blocks/*/block.json`, AUTO-GENERATED секции.
3. `bash scripts/gate-check.sh path/to/test-stage08 08` → должен пройти.
4. Деплой на staging → WP-админка → создать страницу → проверить инсертер → категория `Landing-page blocks` + зарегистрированные блоки.
5. Добавить блок Hero → ACF-форма в сайдбаре с подписями → редактировать → preview обновляется.
6. На существующем legacy-проекте: `backport-acf-to-legacy.sh --dry-run` → проверить diff → запустить без флага → проверить артефакты и снятие legacy.

## Acceptance Criteria

1. `scripts/lib/content_parser.py` экспортирует `ContentParser.parse()` и `validate()`, проходит pytest (≥25 кейсов).
2. `scripts/generate-acf.py` генерирует валидный ACF Local JSON по `final-copy.md`. `wp acf import` импортирует без ошибок.
3. `scripts/generate-block-json.py` создаёт `block.json` per block с `apiVersion:3`, `name:acf/lp-<slug>`, `renderTemplate` указывающим на PHP-блок.
4. `scripts/generate-block-registration.py` добавляет AUTO-GENERATED секцию в `functions.php` с категорией `lp-blocks` и циклом `register_block_type`. Идемпотентно. Код вне маркеров не трогает.
5. `scripts/generate-wp-blocks.py` — оркестратор B1→B2→B3→B4, идемпотентный, поддерживает `--dry-run`.
6. `scripts/lib/gate-checks/stage-08.sh` — 8 hard + 2 warning. Hard-fail на каждом broken-fixture.
7. `scripts/mark-legacy-projects.sh` — одноразовый, идемпотентный, помечает legacy всё что не проходит gate.
8. `scripts/backport-acf-to-legacy.sh` — `--dry-run`, `--force`, автобэкап, снятие legacy после успеха.
9. `skills/wp-gutenberg-block-builder/SKILL.md` обновлён под реальное поведение (B1-B4 + ContentParser).
10. `wp-cli-deployer/scripts/deploy-wordpress.sh` — `wp acf import` без silent fail.
11. `/landing-deploy` блокируется gate-check'ом на проекте без `legacy: true` если артефактов нет.
12. `npm run test:phase-stage-08` зелёный (~60 кейсов).
13. Документация: раздел в `docs/SETUP.md` про ACF/Gutenberg, что менеджер видит в админке.

## Risks

| Риск | Mitigation |
|---|---|
| ContentParser слабый на сложных markdown | `manual_field_review_needed` warning + slug-aliases/block-icons расширяются; парсер падает явно при невозможности |
| AUTO-GENERATED маркеры стерты | Скрипт отказывается работать, бэкап существует |
| `legacy: true` забыли убрать после backport | Backport снимает автоматически; mark-legacy идемпотентен |
| ACF-плагин не активен на live | deploy-wordpress.sh выводит actionable message |
| Slug-collision на двух H2 | Validate падает с line numbers и предложением fix |
| Идемпотентность ломается | Все ключи детерминированы, никаких UUID/timestamp |
| Backport перетирает ручные правки | `generate-theme.py` не перезаписывает существующие block.php; functions.php бэкапится |
| 60 тестов проходят, integration не работает | Manual E2E checklist обязателен перед merge |

## Files summary

### New files

```
landing_system/
├── scripts/
│   ├── lib/
│   │   ├── content_parser.py            (Layer A)
│   │   ├── slug-aliases.yaml            (Layer A — aliases table)
│   │   ├── block-icons.yaml             (Layer B — icon table)
│   │   └── gate-checks/
│   │       ├── stage-08.sh              (Layer C)
│   │       └── stage_08_helper.py       (Layer C)
│   ├── generate-wp-blocks.py            (Layer B — orchestrator)
│   ├── mark-legacy-projects.sh          (Layer C — one-shot)
│   └── backport-acf-to-legacy.sh        (Layer C)
│
├── skills/wp-gutenberg-block-builder/scripts/
│   ├── generate-block-json.py           (new, Layer B)
│   └── generate-block-registration.py   (new, Layer B)
│
└── tests/phase-stage-08/                (full suite, see Testing section)
```

### Modified files

```
landing_system/
├── skills/wp-gutenberg-block-builder/
│   ├── SKILL.md                         (honest description of what it does)
│   └── scripts/
│       ├── generate-acf.py              (rewrite to use ContentParser)
│       └── generate-theme.py            (extend to create block-*.php from blocks)
├── skills/wp-cli-deployer/scripts/
│   └── deploy-wordpress.sh              (remove silent fail on wp acf import)
├── scripts/gate-check.sh                (call stage-08.sh module)
├── config/stage-gates.yaml              (stage 08 documents hard-checks)
├── package.json                         (test:phase-stage-08 + generate-wp-blocks scripts)
├── docs/SETUP.md                        (manager-facing ACF/Gutenberg section)
└── docs/superpowers/specs/2026-05-03-landing-system-design.md (note: stage 08 implementation specified by this spec)
```
