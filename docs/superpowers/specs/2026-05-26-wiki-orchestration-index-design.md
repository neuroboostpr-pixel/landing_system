# Wiki как orchestration-index — дизайн

**Дата:** 2026-05-26
**Автор:** brainstorm-session
**Статус:** ready-for-plan

## Цель

Заменить «orchestrator читает большие исходники (`agents/landing-orchestrator.md` со всем каталогом агентов, полный `wiki/index.md`)» на «orchestrator запрашивает вики через CLI и читает 3-5 коротких карточек».

Главные выигрыши:

- **Routing-решение orchestrator'а:** с ~5K tokens до ~500 tokens.
- **Bootstrap при старте сессии:** с ~3K tokens (полный `index.md` в SessionStart hook) до ~50 tokens (hint про вики).
- **Решение о выполнении этапа:** agent работает по карточке-контракту, исходник `template/08_КОД/README.md` подгружается только когда контракт не покрывает вопрос.
- **Количество Claude Code сессий при первом bootstrap:** с 528 до ~100 (узкий core scope) + throttle 20/прогон.

## Источник правды

- **`wiki/index.yaml`** — машинный индекс. Источник для orchestrator routing.
- **`wiki/concepts/**/*.md`** — карточки полного контракта (frontmatter + 5-секционное тело).
- **`wiki/index.md`** — markdown для людей, **генерится из `index.yaml`**, не правится руками.

## Механизм запроса

- **CLI:** `python -m scripts.wiki.query` с фильтрами (`--stage`, `--type`, `--tag`, `--slug`, `--trigger`, `--grep`) и форматами (`compact`, `cards`, `slugs`, `json`).
- **SessionStart hook:** инжектит ~50-token hint про существование вики и команду запроса. Не загружает содержимое.
- **Orchestrator system prompt:** +10 строк в `agents/landing-orchestrator.md` с инструкцией «перед каждым этапом запроси вики, потом подгружай исходник если карточки мало».

## Схема `wiki/index.yaml`

```yaml
version: 1
generated_at: 2026-05-26T14:00:00Z
counts:
  total: 100
  by_type: {stage: 14, agent: 35, skill: 28, command: 18, rule: 5}

concepts:
  - slug: 08-kod
    type: stage
    stage: "08"
    name: "Сборка WP-темы"
    tags: [wordpress, gutenberg, build]
    triggers: ["approve-07b"]
    inputs: ["07b_COMPOSED/composed.html", "05_ДИЗАЙН/tokens.json"]
    outputs: ["08_КОД/wp-theme/", "08_КОД/gutenberg-blocks/"]
    gates: [composed_approved, design_tokens_valid]
    pre_reqs: [05-dizayn-sistema, 07b-composed]
    related: [landing-build, wp-builder, 09-deploy]
    card: concepts/stages/08-kod.md
    source: template/08_КОД/README.md
    confidence: {gates: low}  # SDK не уверен в значениях gates

  - slug: block-composer
    type: agent
    stage: "08"
    name: "block-composer"
    tags: [html, gutenberg, wordpress]
    triggers: [landing-build, landing-content]
    invoked_by: [landing-orchestrator, frontend-builder]
    uses_skills: [wp-builder, wp-gutenberg-block-builder]
    card: concepts/agents/block-composer.md
    source: agents/block-composer.md
```

### Обязательные поля

| Поле | Обязательно | Источник |
|---|---|---|
| `slug` | да | имя файла карточки без `.md` |
| `type` | да | frontmatter карточки (`stage` / `agent` / `skill` / `command` / `rule`) |
| `name` | да | frontmatter |
| `tags` | да (может быть `[]`) | frontmatter |
| `card` | да | путь к карточке от `wiki/` |
| `source` | да | исходник из `CORE_SOURCES` |
| `stage` | для type=stage/agent/command | frontmatter |
| `triggers` | для type=agent/command/skill | frontmatter |
| `related` | желательно | frontmatter |
| `inputs/outputs/gates` | для type=stage | frontmatter |
| `confidence` | опционально | автомат от SDK при неуверенности |
| `incomplete` | опционально | автомат от compile, если SDK не успел сгенерить (throttle) |

### Lint правила

`scripts/wiki/lint.py` падает с exit 1 если:

1. **Broken ref:** `related: [X]` / `triggers: [X]` / `pre_reqs: [X]`, но `X` не существует среди slug'ов.
2. **Duplicate slug:** два концепта с одинаковым slug.
3. **Missing required field:** для stage нет `stage:`, для agent нет `triggers:` и т.д.
4. **Orphan card:** `wiki/concepts/X.md` существует, но в `index.yaml` нет соответствующего concept'а (или наоборот).

Warn-only (не валит compile):
- `confidence: low` на любом поле.
- `incomplete: true` (deferred карточка).

Запускается:
- автоматически из `compile.py` после генерации `index.yaml`;
- автоматически из `.githooks/post-commit` (опционально, как pre-commit можно добавить позже);
- руками: `python -m scripts.wiki.lint`.

Override строгости: `WIKI_LINT_STRICT=0 python ...` снижает все errors до warnings (для миграционного периода).

## Контракт карточки

Карточка `wiki/concepts/<category>/<slug>.md`, целевой размер 40-70 строк.

### Frontmatter (YAML-голова)

```yaml
---
slug: 08-kod
type: stage
name: "Сборка WP-темы"
stage: "08"
tags: [wordpress, gutenberg, build]
triggers: [approve-07b]
inputs:
  - 07b_COMPOSED/composed.html
  - 05_ДИЗАЙН/tokens.json
outputs:
  - 08_КОД/wp-theme/
  - 08_КОД/gutenberg-blocks/
gates: [composed_approved]
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [landing-build, wp-builder, 09-deploy]
sources: [template/08_КОД/README.md]
updated: 2026-05-26
confidence: {gates: low}   # опционально
---
```

### Тело карточки (фиксированные секции в указанном порядке)

1. **Что делает.** Один абзац, 3-5 строк, в проектных терминах.
2. **Когда вызывается.** Триггер + условие.
3. **Вход → выход.** Артефакты на входе/выходе.
4. **Чем закрывается этап (gates).** Только для `type: stage`; для остальных типов секция опускается.
5. **Failure modes.** 3-5 буллетов про типичные поломки.
6. **Related.** `[[wikilinks]]` на родственные концепты.

Итого 5 секций для не-stage концептов, 6 секций для stage.

### Что НЕ в карточке (намеренно)

- Полный how-to («как» — в исходнике).
- Примеры кода (если без них контракт понятен).
- История изменений (это в git).
- Связь с конкретным клиентским проектом.

### Откуда берётся содержимое карточки

| Часть | Источник | Кто заполняет |
|---|---|---|
| frontmatter | frontmatter исходника + SDK auto-fill отсутствующих полей | SDK при compile |
| тело | SDK генерит из исходника по строгому шаблону | SDK при compile |

Системный промпт `prompts/system_concept.md` расширяется требованием:

- Выдавать 5 фиксированных секций тела в указанном порядке.
- Заполнять **все** поля frontmatter; если данных в исходнике недостаточно — выдать best-effort значение и пометить `confidence: low` для этого поля.
- Не выдумывать имена slug'ов в `related` — использовать только те, что реально существуют (полный список передаётся в user-prompt при генерации).

## Compile flow

Новый порядок в `system_compiler.compile_system()`:

```
1. Загрузить .cache.json
2. Pre-populate кэш для существующих карточек
3. Для каждого source из CORE_SOURCES:
   a. if not changed → skipped, тянем frontmatter из существующей карточки
   b. if changed AND sdk_calls < WIKI_MAX_SDK_CALLS:
        - generate карточку через SDK (с полным frontmatter)
        - parse frontmatter из ответа
        - записать карточку, обновить кэш, sdk_calls += 1
   c. if changed AND sdk_calls >= WIKI_MAX_SDK_CALLS:
        - deferred (кэш НЕ обновляется; в index.yaml пишется incomplete: true)
4. Собрать concepts_summary с полным frontmatter всех концептов
5. [НОВОЕ] Записать wiki/index.yaml (детерминированно, без SDK)
6. [ИЗМЕНЕНО] Записать wiki/index.md, рендеря из index.yaml
7. Lint: проверить ссылки в frontmatter
8. Append лог в wiki/log.md (включая список slug'ов с confidence: low)
```

Шаги 5-7 — детерминированные, дёшевые, выполняются всегда.

### Расширение `concepts_summary`

Сейчас:
```python
{"file_stem": slug, "type": ..., "name": ..., "source": rel_key}
```

Становится:
```python
{
    "slug": ...,
    "type": ...,
    "stage": ...,
    "name": ...,
    "tags": [...],
    "triggers": [...],
    "inputs": [...],
    "outputs": [...],
    "gates": [...],
    "pre_reqs": [...],
    "related": [...],
    "card": "concepts/.../X.md",
    "source": rel_key,
    "confidence": {...},
    "incomplete": False,
}
```

### Schema version и инвалидация

В `system_compiler.py` константа `INDEX_SCHEMA_VERSION = 1`. Если `version:` в существующем `index.yaml` не совпадает — `index.yaml` пересобирается из существующих frontmatter (без re-compile карточек).

### Интеграция throttle

`WIKI_MAX_SDK_CALLS=20` (default) продолжает работать. Deferred источники:
- получают запись в `index.yaml` с `incomplete: true` и пустым телом карточки.
- их sha256 в `.cache.json` НЕ записывается, подхватятся в следующий прогон.

## CLI `wiki.query`

### Use cases

```bash
# Routing: найти кандидатов для этапа
python -m scripts.wiki.query --stage=08 --type=agent

# По тегу
python -m scripts.wiki.query --tag=wordpress --type=agent

# По триггеру
python -m scripts.wiki.query --trigger=approve-07b

# Конкретная карточка
python -m scripts.wiki.query --slug=block-composer

# Всё на этапе
python -m scripts.wiki.query --stage=08

# Текстовый поиск по name+tags+summary
python -m scripts.wiki.query --grep=gutenberg
```

### Форматы вывода

- `--format=compact` (default) — markdown, 3 строки на концепт (`[[slug]] | tags | triggers + summary + card-path`).
- `--format=cards` — полные карточки конкатенацией.
- `--format=slugs` — список slug'ов через newline.
- `--format=json` — JSON-массив объектов из index.yaml.

### Производительность

Чисто Python, без SDK, <100ms на любой запрос. Никаких токенов не тратит.

## SessionStart hook

Текущий `scripts/wiki/hooks/session_start.py` инжектит полный `wiki/index.md` (~3K tokens). Меняется на:

```python
def _wiki_hint(landing_system: Path) -> str:
    index_yaml = landing_system / "wiki" / "index.yaml"
    if not index_yaml.exists():
        return ""
    import yaml
    data = yaml.safe_load(index_yaml.read_text())
    total = data.get("counts", {}).get("total", "?")
    return f"""<wiki_runtime>
Landing-system wiki: {total} concepts indexed at wiki/index.yaml.
Query: python -m scripts.wiki.query --stage=N --type=T --tag=X --slug=Y
Read card: cat wiki/concepts/<dir>/<slug>.md
</wiki_runtime>"""
```

Проектный wiki (`<slug>/wiki/index.md`) и recent memory — **не трогаем**, они контекстные и компактные.

## Скоуп: core vs reference

### Core sources (попадают в `index.yaml`, ~100 концептов)

| Категория | Glob | concept_dir |
|---|---|---|
| agent | `agents/*.md` | `agents/` |
| skill | `skills/*/SKILL.md` | `skills/` |
| command | `commands/*.md` | `commands/` |
| stage | `template/*/README.md` | `stages/` |
| rule | `docs/standards/*.md` | `rules/` |

Плюс один служебный концепт-указатель:

- `block-library/README.md` → `type: catalog`, `slug: block-library` — orchestrator знает, что есть каталог блоков и идёт туда напрямую. Сами блоки (200+) в `index.yaml` **не попадают**.

### Reference sources (НЕ попадают в `index.yaml`)

Остаются как файлы рядом с исходниками или в `docs/`, доступны через grep/Read. Карточки для них не генерятся.

- `block-library/*/*/meta.yaml` — детали блоков.
- `block-library/_patterns/`, `_styles/`.
- `config/*.yaml`.
- `docs/superpowers/{specs,plans}/*.md`.
- `scripts/**/*.doc.md` — генерятся `generate-script-docs.py` без SDK, остаются рядом со скриптами.
- `tests/*/README.md`.
- `presets/*.{md,yaml}`.
- `docs/SETUP.md`, `docs/BACKLOG.md`, и т.д.

### Изменения в `scripts/wiki/config.py`

`SYSTEM_SOURCES` разделяется:

```python
CORE_SOURCES = [
    {"path": "agents/*.md", "concept_dir": "agents", "type_hint": "agent"},
    {"path": "skills/*/SKILL.md", "concept_dir": "skills", "type_hint": "skill"},
    {"path": "commands/*.md", "concept_dir": "commands", "type_hint": "command"},
    {"path": "template/*/README.md", "concept_dir": "stages", "type_hint": "stage"},
    {"path": "docs/standards/*.md", "concept_dir": "rules", "type_hint": "rule"},
    {"path": "block-library/README.md", "concept_dir": "catalogs", "type_hint": "catalog"},
]

REFERENCE_SOURCES = [
    # placeholder для будущего reference-compiler, в этом PR не используется
]
```

`compile.py --source-mode=system` обходит только `CORE_SOURCES`.

### Следствие для wiki/concepts/

Удаляются папки `wiki/concepts/{blocks,patterns,plans,specs,scripts,tests,configs,docs,presets}`. Кэш `.cache.json` для удалённых источников ужимается естественно (ключи без свежих хэшей не пересоздаются при следующем compile).

## План миграции

Каждый этап — отдельный коммит, можно мержить независимо.

### Этап 1 — Schema & lint (без поломок)

1. Добавить `parse_frontmatter_full()` в `utils.py`.
2. Создать пустой `wiki/index.yaml` с `version: 1`.
3. Добавить `_build_yaml_index()` в `system_compiler.py` — вызывается, но результат пока не используется orchestrator'ом.
4. Расширить `lint.py` правилами broken-refs / dup-slugs / missing-required.
5. Тесты: `tests/wiki/test_yaml_index.py`, `tests/wiki/test_lint_refs.py`.

### Этап 2 — CLI query

1. Переписать `scripts/wiki/query.py` под новый YAML.
2. Реализовать флаги `--stage --type --tag --slug --trigger --grep --format`.
3. Тесты: `tests/wiki/test_query.py` с фикстурой маленького `index.yaml`.

### Этап 3 — Сжатие скоупа и обновление промпта

1. Разделить `SYSTEM_SOURCES` → `CORE_SOURCES` + `REFERENCE_SOURCES`.
2. Добавить `block-library/README.md` как catalog-концепт в `CORE_SOURCES`.
3. Удалить устаревшие папки `wiki/concepts/{blocks,patterns,plans,specs,scripts,tests,configs,docs,presets}`.
4. Обновить `prompts/system_concept.md` под фиксированные секции тела + auto-fill frontmatter с `confidence` меткой.
5. Удалить существующие карточки CORE (`wiki/concepts/{agents,skills,commands,stages,rules}/`).

### Этап 4 — Регенерация карточек в новом контракте (полностью автоматически)

1. Прогнать `compile.py --source-mode=system` под `WIKI_MAX_SDK_CALLS=20` несколько раз — ~5 прогонов до полного покрытия ~100 концептов (deferred подхватываются на каждом следующем).
2. После каждого прогона — коммит.
3. Список карточек с `confidence: low` печатается в конце прогона как информационный (не требует ручных правок).

### Этап 5 — Hook & orchestrator

1. Заменить инжект `wiki/index.md` в `session_start.py` на 50-token hint про `index.yaml`.
2. Добавить секцию «Wiki как roadmap» (~10 строк) в `agents/landing-orchestrator.md`.
3. Smoke test: новая сессия Claude Code видит hint, может выполнить `wiki.query --stage=08`.

## Тесты

| Файл | Что покрывает |
|---|---|
| `tests/wiki/test_yaml_index.py` | Сборка `index.yaml` из `concepts_summary`, schema version, детерминированность |
| `tests/wiki/test_lint_refs.py` | Broken refs, dup slugs, missing required, confidence/incomplete warn-only |
| `tests/wiki/test_query.py` | Все флаги CLI, форматы вывода, отсутствующий slug |
| `tests/wiki/test_system_compiler.py` | Pre-existing throttle тест проходит, `concepts_summary` содержит расширенный frontmatter |
| `tests/wiki/test_hooks.py` | `session_start` печатает hint, не полный index |

## Non-goals (явно НЕ в этом PR)

- MCP-сервер для wiki — только CLI.
- Project-graph и conversations compilers — работают как раньше.
- Reference compilation — `REFERENCE_SOURCES` определён, но compiler не реализуется.
- Изменения формата исходников `agents/*.md`, `template/*/README.md` — все требования к frontmatter совместимы с текущими файлами; auto-fill SDK заполняет пустоты.
- Удаление `wiki/preview.html` — остаётся для людей.
- Изменения `block-library/` — только добавляется catalog-концепт-указатель.
- Перевод `wiki/index.md` в JSON-only — markdown index остаётся, генерится из YAML.
- Ручная правка frontmatter после lint — отменено; SDK auto-fill + `confidence` метки.

## Метрики успеха

Замеряются руками после ~5 реальных запусков `/landing-go`:

- Размер payload orchestrator при routing-вызове: **≤500 tokens** (с 5K).
- SessionStart tokens: **≤100** (с 3K).
- Количество SDK-сессий при инкрементальном compile (1 изменённый исходник): **1**.
- `python -m scripts.wiki.query --stage=08` отвечает **<200ms**.
- Все существующие тесты `tests/wiki/` зелёные.

## Риски и митигации

| Риск | Митигация |
|---|---|
| SDK выжжет квоту на Этапе 4 | Throttle стоит. Этапы 4.2 и 4.3 на отдельных коммитах, прерываемы. |
| Lint валит compile на legacy frontmatter | Добавляется в warn-only режиме, через прогон становится error. Override через `WIKI_LINT_STRICT=0`. |
| `landing-orchestrator.md` после правки даёт хуже результат | Делается последним этапом. Откатывается единственным коммитом. |
| Проектный wiki (`<slug>/wiki/`) сломается | Не трогаем. Только системный. |
| SDK auto-fill придумывает неправильные `gates` / `pre_reqs` | Помечаются `confidence: low`. `lint.py` подсвечивает их. Orchestrator может игнорировать low-confidence поля. |
| `block-library/README.md` отсутствует или невалиден | catalog-концепт пропускается с warning, остальная вики работает. |
