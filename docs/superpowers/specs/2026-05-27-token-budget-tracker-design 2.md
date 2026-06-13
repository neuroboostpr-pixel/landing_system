# Token Budget Tracker — Design Spec

**Date:** 2026-05-27
**Status:** draft
**PR:** token-budget-tracker

## Проблема

`wiki/routing-report.md` отслеживает только вики-запросы и прямые обходы вики.
Остальные источники токенов — framework loads (Skill/Command), bash stdout,
session_start инжекты — невидимы. Нет возможности понять: где утечка, что можно
переложить на вики, а что нельзя.

## Цель

Расширить `routing-report.md` полным token budget по всем категориям источников
за 7 дней. Формат: одна таблица по категориям + секция утечек (direct_read с
`can_be_wiki: true`).

---

## Архитектура

### Новый event type: `context_inject`

Добавляется в `scripts/wiki/routing_log.py` рядом с `wiki_query` и `direct_read`.

```jsonc
{
  "ts": "2026-05-27T13:00:00",
  "type": "context_inject",
  "session_id": "...",
  "model": "claude-sonnet-4-6",
  "source_category": "session_start",   // кто/где произошло
  "source_label": "project_wiki",        // что именно
  "path": "lixiang-dubai3/wiki/index.md", // опционально
  "est_tokens": 314,
  "can_be_wiki": false                   // true = утечка, можно переложить на вики
}
```

**Правило `can_be_wiki`:**
- `direct_read` — всегда `true` (агент читал исходник вместо вики-карточки)
- `framework_load`, `session_start`, `bash_stdout` — всегда `false` (нельзя переложить)

---

## Категории источников

| `source_category` | `source_label` примеры | Кто пишет | `can_be_wiki` |
|---|---|---|---|
| `session_start` | `project_wiki`, `project_memory` | `session_start.py` | false |
| `framework_load` | `skill:<name>`, `command:<name>` | `flush.py` (synthetic) | false |
| `bash_stdout` | `gate-check.sh`, `render-pipeline-map.sh` | `flush.py` (из транскрипта) | false |
| `direct_read` | `agents/niche-analyst.md` | `flush.py` (уже есть) | **true** |

**Fixed overhead (константа, не пишется в лог):**
- `CLAUDE.md` — ~10 231 токенов каждую сессию (35 809 bytes / 3.5).
  Фреймворк грузит автоматически, не через tool call, не детектируется.
  Отображается в отчёте как строка `CLAUDE.md (fixed)`.

---

## Изменения по файлам

### 1. `scripts/wiki/routing_log.py`

Добавить функцию:

```python
def log_context_inject(
    session_id: str,
    source_category: str,   # session_start | framework_load | bash_stdout | direct_read
    source_label: str,
    est_tokens: int,
    can_be_wiki: bool = False,
    path: str = "",
    model: str = "",
) -> None
```

Пишет запись `type: context_inject` в `logs/wiki-usage.jsonl`.

Существующий `log_direct_read()` остаётся как есть (для обратной совместимости).
`flush.py` начнёт также писать `context_inject` с `can_be_wiki=True` для тех же
событий. Дублирования в отчёте не будет — `compute_stats()` читает либо
`direct_read`, либо `context_inject / direct_read`, не оба.

> **Решение о миграции:** `direct_read` events остаются в логе навсегда (обратная
> совместимость). `compute_stats()` объединяет их с `context_inject` при агрегации.

### 2. `scripts/wiki/hooks/session_start.py`

В `_system_wiki_hint()` после инжекта project_wiki и project_memory добавить
вызовы `log_context_inject()`:

```python
# после чтения proj_index
routing_log.log_context_inject(
    session_id, "session_start", "project_wiki",
    est_tokens=int(len(proj_index) / 3.5), path=str(proj_index_path)
)
# после чтения memory_recent  
routing_log.log_context_inject(
    session_id, "session_start", "project_memory",
    est_tokens=int(len(memory_recent) / 3.5), path=str(memory_path)
)
```

`session_id` берётся из `os.environ.get("CLAUDE_CODE_SESSION_ID", "")`.

### 3. `scripts/wiki/flush.py`

После парсинга tool_calls добавить два новых блока:

**Блок A — framework_load (synthetic):**
```python
for tc in tool_calls:
    if tc.tool_name == "mcp__claude_ai__skill":          # Skill tool invocation
        skill_name = tc.input_params.get("skill", "")
        skill_file = LANDING_SYSTEM / "skills" / skill_name / "SKILL.md"
        if skill_file.exists():
            routing_log.log_context_inject(
                session_id, "framework_load", f"skill:{skill_name}",
                est_tokens=routing_log.estimate_tokens_file(skill_file),
                path=str(skill_file)
            )
    # аналогично для Command tool
```

> Точное имя tool для Skill-tool нужно уточнить при реализации через
> `transcript_parser` — проверить реальный транскрипт.

**Блок B — bash_stdout:**
```python
for tc in tool_calls:
    if tc.tool_name == "Bash":
        output = tc.output or ""            # output поле ToolCall если есть
        est = int(len(output) / 3.5)
        if est > 100:                        # порог: игнорировать пустые/мелкие
            cmd = tc.input_params.get("command", "")
            label = _extract_script_label(cmd)   # "gate-check.sh" из команды
            routing_log.log_context_inject(
                session_id, "bash_stdout", label,
                est_tokens=est
            )
```

> `ToolCall.output` — нужно добавить поле в `transcript_parser.py`.
> Bash output хранится в транскрипте в `toolResult` записях (не в `toolUse`).
> `transcript_parser` должен матчить `toolResult` по `toolUseId` к соответствующему
> `toolUse`, чтобы получить output.

### 4. `scripts/wiki/transcript_parser.py`

Расширить:
1. `ToolCall` dataclass — добавить поле `output: str = ""`
2. `extract_tool_calls()` — после парсинга `toolUse` блоков матчить
   соответствующие `toolResult` по `toolUseId`, заполнять `output`.
3. `SOURCE_READ_PATTERNS` — расширить в `config.py` (см. ниже).

### 5. `scripts/wiki/config.py`

Расширить `SOURCE_READ_PATTERNS`:

```python
SOURCE_READ_PATTERNS: list[str] = [
    "agents/*.md",
    "skills/*/SKILL.md",
    "commands/*.md",
    "docs/standards/*.md",
    # новые:
    "docs/**/*.md",
    "template/**/*.md",
    "CLAUDE.md",
    "wiki/**/*.md",
    "memory/**/*.md",
    "skills/*/*.md",
]
```

### 6. `scripts/wiki/stats.py`

**`compute_stats()`** — читать оба типа: `direct_read` + `context_inject`.
Агрегировать в `by_category` dict.

**`generate_report()`** — добавить две новые секции:

```markdown
## Token Budget по категориям (7д)

| Категория      | Событий | ~Токенов | Можно на вики? |
|----------------|---------|----------|----------------|
| wiki_query     | 5       | −4 564   | —              |
| direct_read    | 2       | +1 200   | ⚠️ да          |
| session_start  | 3       | +940     | нет            |
| framework_load | 8       | +14 300  | нет            |
| bash_stdout    | 12      | +3 100   | нет            |
| CLAUDE.md      | —       | ~10 231  | нет (fixed)    |

## Утечки — читается напрямую вместо вики

| Файл | ~Токенов | Агент знал про вики |
|------|----------|---------------------|
| agents/niche-analyst.md | 800 | нет |
| skills/landing-build/SKILL.md | 400 | да ⚠️ |
```

**`one_line_summary()`** — расширить:
```
Вики-граф (7д): 5 запросов · 2 обхода · ~4 564 сэкономлено · ⚠️ 1 200 токенов в обход
```
(добавить `⚠️ N токенов в обход` если `direct_reads > 0`)

---

## Что НЕ входит в скоуп

- Exact token counting через Anthropic API — уже есть `--exact-tokens` флаг, не трогаем
- Auto-fix: отчёт только информирует, не предлагает действий
- Page-level breakdown внутри bash_stdout (только label скрипта)
- История за >7 дней (уже есть `--days=N` флаг)

---

## Тесты

Новые тест-файлы в `tests/wiki/`:

- `test_routing_log_context_inject.py` — `log_context_inject()` пишет правильную запись
- `test_stats_budget.py` — `compute_stats()` агрегирует `context_inject` события
- `test_report_budget_section.py` — `generate_report()` рендерит секцию Token Budget
- `test_transcript_parser_output.py` — `extract_tool_calls()` матчит toolResult к toolUse

Существующие тесты wiki не ломаются: `direct_read` events читаются как раньше.

---

## Риски

**R1: Имя Skill tool в транскрипте неизвестно.**
Нужно проверить реальный транскрипт — как называется tool_name когда агент
вызывает `Skill` tool. Возможные варианты: `mcp__claude_ai__skill`, `Skill`,
`skill`. При реализации — первым делом распарсить живой транскрипт.

**R2: toolResult матчинг в транскрипте.**
Claude Code JSONL может хранить tool output не в той же строке что tool call.
Структура: `toolUse` → `toolResult` по `toolUseId`. Если формат отличается —
fallback: `output = ""`, bash_stdout не логируется (не блокирует остальное).

**R3: session_id в session_start.**
`CLAUDE_CODE_SESSION_ID` env var может не быть выставлен в момент session_start
hook. Fallback: пустая строка — запись всё равно пишется, просто без session_id.
