# Composed ↔ block-spec Linter — Design

**Status:** approved (interactive brainstorm 2026-05-21).
**Owner:** landing-system / stage-08 quality gate.
**Related:** [docs/asset-pipeline.md](../../asset-pipeline.md), [docs/standards/stage-execution-protocol.md](../../standards/stage-execution-protocol.md), [skills/wp-gutenberg-block-builder/scripts/generate-page-content.py](../../../skills/wp-gutenberg-block-builder/scripts/generate-page-content.py)

## Problem

Stage-08 строит WordPress-тему из `08_КОД/block-spec.yaml`. Spec — единственный
источник правды для `generate-page-content.py` (никто не парсит composed.html
во время сборки). Если spec неполный относительно эталонного
`07b_COMPOSED/composed*.html` — лендинг рендерится с пропущенным контентом, и
это видно только глазами после деплоя.

Конкретный случай (dubai-avto-liza, 2026-05-21):
- В composed feature-statement-карточка содержит **4 `<p>`**, в spec —
  однострочный text → live показал только 1 абзац.
- В composed `model-card` содержит **4 spec-bullets**, **5 color-swatches**,
  длинное описание → в spec было 3 bullets, нет colors, пустое description.
- Слайдер моделей содержит 5 `<img>` → в spec photo1..5 присутствуют, но
  template-значения пустые.

Все три фикса пришлось делать руками через `fix-*.py`-скрипты. Следующий
лендинг с похожим composed столкнётся с теми же дырами.

## Goal

Автоматически выявлять расхождения «composed.html ↔ block-spec.yaml» **до**
stage-08-сборки, блокировать gate если расхождения есть, и опционально
авто-исправлять spec.

## Non-goals

- **Не** парсим composed целиком в spec автоматически. Создание spec'а — задача
  агента `frontend-builder` (LLM), линтер только проверяет результат.
- **Не** проверяем CSS / визуальное соответствие. Это работа Visual QA
  (`/landing-qa`).
- **Не** трогаем уже-задеплоенные сайты. Линтер работает на исходниках в
  `08_КОД/`.

## Architecture

Три модуля + один gate-hook:

```
skills/wp-gutenberg-block-builder/scripts/
├── lib/
│   ├── composed_inspector.py     # NEW: parse composed.html → tree of facts
│   ├── spec_inspector.py         # NEW: parse block-spec.yaml → tree of facts
│   └── lint_heuristics.py        # NEW: rule definitions (bullets, swatches, ...)
├── lint-composed-vs-spec.py      # NEW: CLI entry point (verify, --fix)
└── ... (existing generators)

scripts/
└── gate-check.sh                 # MODIFIED: stage-08 invokes lint script
```

### Module: composed_inspector.py

Парсит composed-html через BeautifulSoup. Возвращает дерево:

```python
@dataclass
class InspectedBlock:
    probe_selector: str           # from spec
    matches: list[InspectedMatch] # one per DOM element matched

@dataclass
class InspectedMatch:
    tag: str
    attrs: dict
    children: list[InspectedChild]

@dataclass
class InspectedChild:
    heuristic: str   # "bullets", "color-swatches", "multi-paragraph", ...
    count: int       # how many items of this kind found
    values: list[str]  # extracted text/data for auto-fix
```

API:
```python
def inspect(composed_path: Path, probes: list[str]) -> list[InspectedBlock]
```

### Module: spec_inspector.py

Читает `block-spec.yaml` через существующий `block_spec.load()`. Возвращает:

```python
@dataclass
class InspectedSpec:
    blocks: list[InspectedSpecBlock]

@dataclass
class InspectedSpecBlock:
    slug: str
    probe_selector: str | None       # NEW field on Block
    probe_kind: str                  # "single" | "card-collection" (default: "single")
    controls: list[InspectedControl]
    template: list[dict]             # for section-card

@dataclass
class InspectedControl:
    name: str
    type: str
    has_default: bool
    default_value: object | None
```

### Module: lint_heuristics.py

Фиксированный реестр правил. Каждое правило — функция:

```python
def check_bullets(spec_block: InspectedSpecBlock, dom_match: InspectedMatch) -> list[LintIssue]
def check_color_swatches(...) -> list[LintIssue]
def check_multi_paragraph(...) -> list[LintIssue]
def check_slider_images(...) -> list[LintIssue]
def check_inline_svg_icon(...) -> list[LintIssue]
```

```python
@dataclass
class LintIssue:
    severity: Literal["error", "warning"]
    block_slug: str
    heuristic: str
    message: str
    suggested_fragment: str | None  # YAML snippet for --fix
```

### Heuristic catalog

| Heuristic | DOM probe (within parent match) | Spec expectation | Severity if mismatch |
|---|---|---|---|
| `bullets` | `ul[class$="-specs"] > li`, `ul.specs > li` | controls с `text` или один `repeater`; count of fields ≥ count of `<li>` | error |
| `color-swatches` | `[style*="--c"]`, `.color-swatch` | text-control `colors` (CSV) или repeater `colors` | error |
| `multi-paragraph` | `<p>` count > 1 в одном `.feature-card` / `.model-card` | textarea-control с `\n\n`-разделителями; nl2br на рендере | error |
| `slider-images` | `.slider-track > img`, `[data-slider] img` | controls `photo1..photoN`; template должен содержать все N | error |
| `inline-svg-icon` | `.feature-icon > svg`, `.icon > svg` | имя control в `SVG_ATTR_KEYS` (см. asset-pipeline) | error |
| `bg-image-css` | `style*="background"` или `::after { url(...) }` в `<style>` | informational only — это site-asset | warning |

### CLI

```
lint-composed-vs-spec.py --project <path> [--composed <file>] [--fix] [--json]
```

Defaults:
- `--composed`: auto-detect — `composed-brutalist.html` если есть, иначе `composed.html`.
- `--fix`: применяет auto-fix модификации в `block-spec.yaml`, с комментариями
  `# AUTO-LINT 2026-05-21: added from composed.html` рядом с каждой добавленной
  строкой. Бэкап сохраняется в `08_КОД/block-spec.yaml.bak.<timestamp>`.
- `--json`: машинно-читаемый вывод (для интеграции с другими гейтами).

Exit code: `1` если есть errors, `0` если только warnings, `2` для system
errors (composed.html не найден когда --strict).

### Gate integration

`scripts/gate-check.sh` для stage-08:

```bash
# Add after existing checks:
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project "$PROJECT_DIR" \
    || { echo "ERROR: composed↔spec lint failed. Run with --fix or update spec manually."; exit 1; }
```

Stage 08 не закрывается без зелёного линта (strict mode из brainstorm).

## Data flow (example: features-section)

1. **composed_inspector** видит `<section class="features-section">` с
   `<div class="features-grid">` внутри. Внутри 6 `.feature-card`. Первая
   имеет класс `feature-statement` и 4 `<p>`. Остальные 5 — обычные с
   `<svg>`, `<h3>`, `<p>`.

2. Linter ищет в spec блок где `probe_selector: ".features-section"` →
   находит `features` (section-card). `probe_kind: "card-collection"` →
   ожидает совпадение `len(spec.blocks[features].card.template) ==
   5` (без statement, который статичен в block.php).

3. Дополнительно линтер заходит в первую `.feature-statement` карточку,
   обнаруживает 4 `<p>`. Ищет в spec.features.controls control
   `feat_statement` (textarea). Проверяет default — `\n\n.count` < 3 →
   **error**: "feat_statement composed has 4 paragraphs, spec default has 1".

4. Заходит в каждую `.feature-card:not(.feature-statement)`, обнаруживает
   `<svg>`. Проверяет card.controls на `icon_svg` (имя в `SVG_ATTR_KEYS`) и
   что в template[i] значение присутствует (не пустая строка) → если пусто,
   **error**.

5. `--fix` пишет в spec:
   ```yaml
   feat_statement:
     type: textarea
     default: |
       LiXiang — smart, quiet, and luxurious. Exactly as it should be...

       Li vehicles are built for people who no longer see...

       Every detail is designed to elevate everyday life...

       Li is a statement on the outside and a better way of living.
     # AUTO-LINT 2026-05-21: extracted 4 paragraphs from composed.html
   ```

## Error handling

| Условие | Поведение |
|---|---|
| `composed.html` отсутствует | warning, exit 0 (некоторые проекты собираются без composed) |
| `block-spec.yaml` отсутствует | error, exit 2 (это критическая ошибка stage-08) |
| `probe_selector` не задан на блоке | warning «no probe configured», блок пропускается |
| `probe_selector` некорректный CSS | error, сообщение с конкретной ошибкой парсера |
| `--fix` без `--composed` и нечего исправлять | exit 0, печатает "no issues found" |
| `--fix` хочет переписать существующее ненулевое значение | НЕ переписывает, пишет warning «would overwrite existing default; skip — fix manually» |

## Testing

Tests live in `tests/phase-stage-08/`:

- `test-composed-inspector.py` — фикстуры (минимальная composed.html, brutalist
  features-section, model-card со слайдером) → проверяем извлекаются правильные
  факты.
- `test-spec-inspector.py` — фикстуры мини-spec → проверяем парсинг
  controls/template/probe_selector.
- `test-lint-rules.py` — для каждого heuristic: pass case, fail case, auto-fix
  fragment корректный.
- `test-lint-integration.py` — end-to-end: запуск CLI на готовом проекте, exit
  code корректный, `--fix` записывает spec правильно (с бэкапом).

Все тесты на pytest, идиоматика как в [tests/phase-stage-08/test-fix-page-content-images.py](../../../tests/phase-stage-08/test-fix-page-content-images.py).

## Migration

Существующие проекты (dubai-avto-liza, lixiang-dubai, и пр.):
1. Запустить линтер без `--fix` → отчёт о расхождениях.
2. Запустить с `--fix` → spec обновлён, ручной review diff'а.
3. Пересобрать stage-08 (`/landing-go` или `landing-build`).
4. Зафиксировать в commit.

Для новых проектов: линтер срабатывает автоматически на stage-08 gate, ошибка
блокирует pipeline. Агент `frontend-builder` должен заполнить spec корректно
с первой попытки (auto-fix как safety net).

## Out of scope (future work)

- **Bidirectional sync** (composed → spec изменения, spec → composed обновления).
  Сейчас composed считается immutable source-of-truth, spec — derived.
- **Custom heuristics** через plugin-API. Список фиксирован.
- **Visual diff** между rendered live и composed. Это работа Visual QA.

## Acceptance criteria

- [ ] `lint-composed-vs-spec.py --project dubai-avto-liza` показывает не менее
  3 errors (statement multi-p, model-card bullets count, model-card colors).
- [ ] `--fix` исправляет spec так, что повторный запуск возвращает exit 0.
- [ ] Все тесты в `tests/phase-stage-08/test-*-inspector*.py` зелёные.
- [ ] `gate-check.sh` блокирует stage-08 при failing lint.
- [ ] Документация в `docs/standards/stage-08-spec-lint.md` (новый файл).
