# Wiki Routing Observability — Design Spec

**Goal:** Доказать (или опровергнуть) что оркестратор реально использует wiki routing перед каждым этапом, и измерить экономию токенов по сравнению с прямым чтением исходников.

**Architecture:** Гибридный подход — `query.py` активно логирует каждый wiki query, `flush.py` пассивно парсит транскрипт сессии и детектит прямые чтения исходников (bypass). `stats.py` агрегирует оба потока. Preflight check в `session_start.py` блокирует запуск при проблемах окружения.

**Tech Stack:** Python 3.10+, stdlib only (`json`, `pathlib`, `datetime`, `os`), `pytest` для тестов.

---

## 1. Новые файлы

### `scripts/wiki/routing_log.py`

Единственная точка записи и чтения `logs/wiki-usage.jsonl`.

**Публичный API:**

```python
def log_query(
    session_id: str,
    filters: dict[str, str | None],
    hits: list[str],
    est_tokens_saved: int,
) -> None:
    """Пишет запись type=wiki_query в logs/wiki-usage.jsonl."""

def log_direct_read(
    session_id: str,
    path: str,
    est_tokens: int,
    had_prior_query: bool,
) -> None:
    """Пишет запись type=direct_read в logs/wiki-usage.jsonl."""

def read_events(since_days: int = 7) -> list[dict]:
    """Читает все события за последние since_days дней."""

def estimate_tokens_saved(wiki_dir: Path, hits: list[dict]) -> int:
    """est_tokens_saved = sum(source sizes)/4 - sum(card sizes)/4 для хитов."""

def estimate_tokens_file(path: Path) -> int:
    """Размер файла в байтах / 4. Возвращает 0 если файл не существует."""
```

**Формат записей в `logs/wiki-usage.jsonl`:**

```json
{"ts": "2026-05-27T14:23:11", "type": "wiki_query", "session_id": "abc123", "filters": {"stage": "08", "type": "agent"}, "hits": ["wp-builder", "integrations-engineer"], "hits_count": 2, "est_tokens_saved": 4200}
{"ts": "2026-05-27T14:25:03", "type": "direct_read", "session_id": "abc123", "path": "agents/wp-builder.md", "est_tokens": 3200, "had_prior_query": true}
```

**Обработка ошибок:** если запись в лог упала с `OSError` или `PermissionError` — логируем в `sys.stderr` и продолжаем. Основной flow (`query.py`) не прерывается.

**Подсчёт токенов:**
- Для `log_query`: `est_tokens_saved = sum(source_file_sizes_bytes) / 4 - sum(card_sizes_bytes) / 4`
- Для `log_direct_read`: `est_tokens = file_size_bytes / 4`
- Делитель 4 — приближение (1 токен ≈ 4 байта), стабильный и воспроизводимый.

---

### `scripts/wiki/transcript_parser.py`

Парсит JSONL транскрипт Claude Code, извлекает tool calls. **Самый хрупкий модуль** — при изменении формата транскрипта тесты сигнализируют первыми.

**Публичный API:**

```python
@dataclass
class ToolCall:
    ts: str
    tool_name: str
    input_params: dict

def extract_tool_calls(transcript_path: Path) -> list[ToolCall]:
    """Читает JSONL, возвращает все tool calls. При неизвестном формате — пропускает строку."""

def is_source_read(tc: ToolCall) -> bool:
    """True если Read tool с путём agents/*.md | skills/*/SKILL.md | commands/*.md"""

def is_wiki_query(tc: ToolCall) -> bool:
    """True если Bash tool с 'scripts.wiki.query' в команде."""

def get_session_id(transcript_path: Path) -> str:
    """Имя файла транскрипта без расширения как session_id."""

def extract_query_slugs(tc: ToolCall) -> list[str]:
    """Из Bash wiki query извлекает --slug= значения если есть."""

def extract_query_stage(tc: ToolCall) -> str | None:
    """Из Bash wiki query извлекает --stage= значение если есть."""
```

**Формат tool call в транскрипте Claude Code (текущий):**

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "name": "Read",
      "input": {"file_path": "/path/to/agents/wp-builder.md"}
    }
  ]
}
```

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "name": "Bash",
      "input": {"command": "python -m scripts.wiki.query --stage=08 --type=agent"}
    }
  ]
}
```

**Защитное поведение:**
- `content` может быть строкой или списком блоков — оба варианта обрабатываются
- Отсутствующие поля (`name`, `input`) → пропуск записи, не исключение
- Битый JSON в строке JSONL → пропуск строки
- Пустой файл → пустой список

**Тесты на формат (критичные):**

| Тест | Что проверяет |
|---|---|
| `test_extracts_read_tool_call` | Нормальный Read с file_path |
| `test_extracts_bash_tool_call` | Нормальный Bash с command |
| `test_content_as_string_ignored` | content=строка не крашится |
| `test_missing_name_field_skipped` | Нет поля name → пропуск |
| `test_missing_input_field_skipped` | Нет поля input → пропуск |
| `test_broken_json_line_skipped` | Битая строка → пропуск |
| `test_empty_transcript` | Пустой файл → [] |
| `test_is_source_read_agents` | agents/X.md → True |
| `test_is_source_read_skills` | skills/X/SKILL.md → True |
| `test_is_source_read_commands` | commands/X.md → True |
| `test_is_source_read_wiki_card` | wiki/concepts/X.md → False (карточка не считается bypass) |
| `test_is_wiki_query_bash` | Bash с scripts.wiki.query → True |
| `test_is_wiki_query_other_bash` | Bash с другой командой → False |

---

### `scripts/wiki/stats.py`

Агрегация событий из лога и генерация отчёта.

**Публичный API:**

```python
@dataclass
class StatsResult:
    queries: int
    direct_reads: int
    est_tokens_saved: int
    est_tokens_spent_bypass: int
    bypass_rate: float  # direct_reads / (queries + direct_reads)
    top_bypass: list[dict]  # [{path, count, had_prior_query_count}]
    by_date: list[dict]  # [{date, queries, direct_reads, est_saved}]

def compute_stats(events: list[dict], since_days: int = 7) -> StatsResult:
    """Агрегирует события за период."""

def generate_report(stats: StatsResult, since_days: int = 7) -> str:
    """Возвращает Markdown строку."""

def one_line_summary(stats: StatsResult) -> str:
    """Одна строка для session_start хинта."""
    # → "Wiki routing (7d): 23 queries · 8 direct reads · ~18 400 tokens saved · bypass rate 26%"
```

**CLI:**
```bash
python -m scripts.wiki.stats              # summary в терминал
python -m scripts.wiki.stats --report     # пишет wiki/routing-report.md
python -m scripts.wiki.stats --days=30    # за месяц
```

**Пример `wiki/routing-report.md`:**

```markdown
# Wiki Routing Report (2026-05-21 — 2026-05-27)

| Дата       | Queries | Direct reads | Est. saved | Bypass rate |
|------------|---------|--------------|------------|-------------|
| 2026-05-27 |       8 |            3 |   6 400 t  |        27%  |
| 2026-05-26 |      15 |            5 |  12 000 t  |        25%  |

**Итого за 7 дней:** 23 queries · 8 direct reads · ~18 400 tokens saved
**Bypass rate:** 26%

## Топ bypass файлов

| Файл | Всего | had_prior_query=true | had_prior_query=false |
|------|-------|----------------------|-----------------------|
| agents/wp-builder.md | 3 | 1 | 2 |
| skills/wp-gutenberg-block-builder/SKILL.md | 2 | 0 | 2 |
```

---

### `scripts/wiki/preflight.py`

Проверка окружения перед запуском логирования.

**Публичный API:**

```python
@dataclass
class CheckResult:
    ok: bool
    name: str
    message: str
    fix_hint: str

def check_disk_space(min_mb: int = 50) -> CheckResult
def check_logs_dir_writable() -> CheckResult
def check_index_yaml_exists() -> CheckResult
def check_index_yaml_parseable() -> CheckResult

def run_preflight() -> list[CheckResult]:
    """Возвращает все результаты. Не бросает исключений."""
```

**Поведение при failures в `session_start.py`:**

```
⚠️  Wiki preflight failed:
  - logs/ not writable: C:\AI_TEAMS\landing_system\logs\ (PermissionError)
    Fix: mkdir logs
  - index.yaml missing
    Fix: python -m scripts.wiki.compile --source-mode=system

Wiki routing disabled until fixed.
Set WIKI_PREFLIGHT_SKIP=1 to bypass checks and continue without logging.
```

Если `WIKI_PREFLIGHT_SKIP=1` — preflight пропускается, routing_log не вызывается, но хинт добавляет `[logging disabled]`.

---

## 2. Изменения в существующих файлах

### `scripts/wiki/query.py`

После `filter_concepts()`, перед возвратом результатов:

```python
try:
    from scripts.wiki import routing_log
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    est_saved = routing_log.estimate_tokens_saved(wiki_dir, hits)
    routing_log.log_query(session_id, filters_dict, [c["slug"] for c in hits], est_saved)
except Exception as e:
    print(f"[wiki routing_log] failed to log: {e}", file=sys.stderr)
```

### `scripts/wiki/flush.py`

После записи уроков, добавляем блок анализа routing:

```python
from scripts.wiki import transcript_parser, routing_log

tool_calls = transcript_parser.extract_tool_calls(transcript_path)
session_id = transcript_parser.get_session_id(transcript_path)

# Собираем wiki queries этой сессии для had_prior_query
queried_slugs: set[str] = set()
queried_stages: set[str] = set()
for tc in tool_calls:
    if transcript_parser.is_wiki_query(tc):
        queried_slugs.update(transcript_parser.extract_query_slugs(tc))
        stage = transcript_parser.extract_query_stage(tc)
        if stage:
            queried_stages.add(stage)

for tc in tool_calls:
    if transcript_parser.is_source_read(tc):
        path = tc.input_params.get("file_path", "")
        slug = Path(path).stem
        # had_prior_query = True если: slug явно запрашивался через --slug=
        # ИЛИ через --stage= query, и этот файл относится к тому этапу
        # (приближение: stage query считается prior для любого source read после него)
        had_prior = (
            slug in queried_slugs
            or bool(queried_stages)  # был хотя бы один stage query в сессии
        )
        est = routing_log.estimate_tokens_file(Path(path))
        routing_log.log_direct_read(session_id, path, est, had_prior)
```

### `scripts/wiki/hooks/session_start.py`

В `_system_wiki_hint()`, после подсчёта `total`:

```python
# Preflight
from scripts.wiki.preflight import run_preflight
import os
failures = []
if not os.environ.get("WIKI_PREFLIGHT_SKIP"):
    failures = [r for r in run_preflight() if not r.ok]

if failures:
    lines = ["⚠️  Wiki preflight failed:"]
    for f in failures:
        lines.append(f"  - {f.message}\n    Fix: {f.fix_hint}")
    lines.append("Set WIKI_PREFLIGHT_SKIP=1 to bypass.")
    return "<wiki_runtime>\n" + "\n".join(lines) + "\n</wiki_runtime>"

# Stats line
from scripts.wiki import routing_log, stats
events = routing_log.read_events(since_days=7)
if events:
    s = stats.compute_stats(events)
    stats_line = stats.one_line_summary(s)
else:
    stats_line = "Wiki routing (7d): no data yet"

return (
    "<wiki_runtime>\n"
    f"Landing-system wiki: {total} concepts indexed at wiki/index.yaml.\n"
    "Query: python -m scripts.wiki.query --stage=N --type=T --tag=X --slug=Y\n"
    "Read card: cat wiki/concepts/<dir>/<slug>.md\n"
    f"{stats_line}\n"
    "</wiki_runtime>"
)
```

---

## 3. Файлы которые не трогаем

- `wiki/index.yaml` — не меняется
- `scripts/wiki/compile.py`, `system_compiler.py` — не меняются
- `scripts/wiki/lint.py` — не меняется
- `.githooks/post-commit` — не меняется

---

## 4. Gitignore

Добавить в `.gitignore`:
```
logs/wiki-usage.jsonl
wiki/routing-report.md
```

---

## 5. Тестовая стратегия

Все тесты — `pytest`, без SDK calls, без сети.

**`tests/wiki/test_transcript_parser.py`** — 13 тестов (перечислены выше). Используют fixture-файлы в `tests/wiki/fixtures/transcripts/` с синтетическими JSONL транскриптами. При изменении формата транскрипта — эти тесты падают первыми.

**`tests/wiki/test_routing_log.py`** — 5 тестов:
- `test_log_query_writes_jsonl`
- `test_log_direct_read_writes_jsonl`
- `test_read_events_filters_by_days`
- `test_oserror_does_not_raise`
- `test_estimate_tokens_file`

**`tests/wiki/test_stats.py`** — 5 тестов:
- `test_compute_stats_empty_events`
- `test_compute_stats_bypass_rate`
- `test_compute_stats_top_bypass`
- `test_one_line_summary_format`
- `test_generate_report_markdown`

**`tests/wiki/test_preflight.py`** — 4 теста:
- `test_check_disk_space_ok`
- `test_check_logs_dir_writable_missing_dir`
- `test_check_index_yaml_missing`
- `test_run_preflight_returns_all_results`

---

## 6. Out of scope

- Cron-запуск stats (ручной запуск достаточно)
- UI в wp-admin
- Хранение транскриптов (flush.py уже получает путь от Claude Code)
- Точный подсчёт токенов через tiktoken (приближение /4 достаточно для сравнения)

---

## 7. Задача: Скилл `wiki-routing-observability` для переиспользования

После реализации основного функционала — выделить универсальные компоненты в переносимый скилл.

### Что универсально (выносится в скилл)

- `routing_log.py` — чистая логика записи/чтения JSONL, не зависит от структуры проекта
- `stats.py` — агрегация и отчёт, не зависит от структуры проекта
- `transcript_parser.py` — формат транскрипта одинаков для любого Claude Code проекта; паттерны `is_source_read()` параметризуются через конфиг

### Что остаётся специфичным для landing-system

- Паттерны `is_source_read()` — пути `agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`
- Интеграция с `session_start.py` и `wiki/index.yaml`
- `query.py` вызов

### Механизм параметризации

Добавить в `scripts/wiki/config.py` (уже существует):

```python
# Паттерны путей которые считаются "source reads" (bypass wiki)
SOURCE_READ_PATTERNS: list[str] = [
    "agents/*.md",
    "skills/*/SKILL.md",
    "commands/*.md",
    "docs/standards/*.md",
]
```

`transcript_parser.is_source_read()` читает `SOURCE_READ_PATTERNS` из конфига вместо хардкода.

### Структура скилла

```
skills/wiki-routing-observability/
  SKILL.md                  # описание скилла
  scripts/
    routing_log.py          # копия (без изменений)
    stats.py                # копия (без изменений)
    transcript_parser.py    # копия с SOURCE_READ_PATTERNS из конфига
    preflight.py            # копия (без изменений)
  config.example.yaml       # пример конфига для нового проекта
  README.md                 # инструкция по развёртыванию
```

### Развёртывание на новом проекте

1. Скопировать `skills/wiki-routing-observability/` в новый проект
2. В `config.yaml` задать `source_read_patterns` под структуру нового проекта
3. Подключить `session_start.py` интеграцию (3 строки)
4. Готово — логирование работает

### Файлы для этой задачи

- Создать: `skills/wiki-routing-observability/SKILL.md`
- Создать: `skills/wiki-routing-observability/config.example.yaml`
- Изменить: `scripts/wiki/config.py` — добавить `SOURCE_READ_PATTERNS`
- Изменить: `scripts/wiki/transcript_parser.py` — читать паттерны из конфига
- Тест: `test_transcript_parser.py` — добавить `test_source_read_uses_config_patterns`
