# Wiki Stage/Agent/Skill Tracking — Design Spec

**Goal:** Логировать факт запуска каждого этапа, агента и скила с автоматической корреляцией `via_wiki: true/false` — для выявления утечек токенов и узких мест, которые можно перенести на wiki.

**Architecture:** Три новых типа событий (`stage_start`, `agent_call`, `skill_call`) в существующем `logs/wiki-usage.jsonl`. `gate-check.sh` пишет `stage_start`, агенты/скилы пишут свои события через новый CLI `python -m scripts.wiki.log`. Корреляция `via_wiki` — автоматическая: `routing_log.py` проверяет наличие `wiki_query` с тем же `session_id` и `stage` в логе до данного события. Отчёт расширяется новой секцией "Запуски vs вики".

**Tech Stack:** Python 3.10+, stdlib only; bash для gate-check.sh интеграции; pytest.

---

## 1. Новые типы событий

### `stage_start` — пишет `gate-check.sh`

```json
{
  "ts": "2026-05-27T16:39:00",
  "type": "stage_start",
  "session_id": "abc123",
  "stage": "04_brand",
  "project": "lixiang-dubai3",
  "via_wiki": true
}
```

`via_wiki: true` если в `logs/wiki-usage.jsonl` есть `wiki_query` с тем же `session_id` и `filters.stage` содержащим номер этапа (например `"04"` для `"04_brand"`).

### `agent_call` — пишет агент в pre-flight блоке

```json
{
  "ts": "2026-05-27T16:39:10",
  "type": "agent_call",
  "session_id": "abc123",
  "agent": "brand-architect",
  "stage": "04",
  "via_wiki": true
}
```

### `skill_call` — пишет скил в pre-flight блоке

```json
{
  "ts": "2026-05-27T16:38:55",
  "type": "skill_call",
  "session_id": "abc123",
  "skill": "landing-brand",
  "stage": "04",
  "via_wiki": false
}
```

---

## 2. Автоматическая корреляция `via_wiki`

В `routing_log.py` новая функция:

```python
def was_wiki_queried(session_id: str, stage: str) -> bool:
    """True если в логе есть wiki_query с тем же session_id и stage до текущего момента."""
```

Логика:
- Читает `LOG_PATH` (только события текущей сессии по `session_id`)
- Ищет `type == "wiki_query"` где `filters.stage` начинается с нормализованного номера этапа
  - `"04_brand"` → ищем `stage` начинающийся с `"04"` или равный `"04_brand"`
- Возвращает `True` если хотя бы одно такое событие найдено
- При `OSError` или пустом логе — возвращает `False` (не блокирует)

---

## 3. Новый CLI: `python -m scripts.wiki.log`

Новый файл `scripts/wiki/log.py` — тонкий CLI-враппер над `routing_log.py`:

```bash
python -m scripts.wiki.log \
  --type agent_call \
  --agent brand-architect \
  --stage 04 \
  --session-id $CLAUDE_SESSION_ID
```

```bash
python -m scripts.wiki.log \
  --type skill_call \
  --skill landing-brand \
  --stage 04
```

`--session-id` необязателен — если не передан, берётся из `$CLAUDE_SESSION_ID`. Если и env нет — `"unknown"`.

**Новые функции в `routing_log.py`:**

```python
def log_stage_start(session_id: str, stage: str, project: str) -> None:
    via_wiki = was_wiki_queried(session_id, stage)
    _write({"ts": ..., "type": "stage_start", "session_id": session_id,
            "stage": stage, "project": project, "via_wiki": via_wiki})

def log_agent_call(session_id: str, agent: str, stage: str) -> None:
    via_wiki = was_wiki_queried(session_id, stage)
    _write({"ts": ..., "type": "agent_call", "session_id": session_id,
            "agent": agent, "stage": stage, "via_wiki": via_wiki})

def log_skill_call(session_id: str, skill: str, stage: str) -> None:
    via_wiki = was_wiki_queried(session_id, stage)
    _write({"ts": ..., "type": "skill_call", "session_id": session_id,
            "skill": skill, "stage": stage, "via_wiki": via_wiki})
```

---

## 4. Интеграция в `gate-check.sh`

После определения `session_id` (из env `$CLAUDE_SESSION_ID`), перед основными проверками — добавить вызов:

```bash
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
$PYTHON_CMD -m scripts.wiki.log \
    --type stage_start \
    --stage "$stage" \
    --project "$(basename "$project")" \
    --session-id "$SESSION_ID" \
    >/dev/null 2>&1 || true
```

Падение логирования не прерывает gate-check (`|| true`).

---

## 5. Интеграция в агенты и скилы

**Правило:** каждый агент и скил системы обязан логировать свой запуск в pre-flight блоке. Не список конкретных файлов — а принцип для всех без исключения.

**Агенты** (`agents/*.md`) — в pre-flight блок, после `wiki.query`:

```bash
python -m scripts.wiki.log --type agent_call --agent <slug> --stage <N>
```

`<slug>` — имя файла агента без `.md`. `<N>` — номер этапа к которому привязан агент (например `04` для `brand-architect`). Если агент не привязан к конкретному этапу (оркестратор) — передавать текущий этап из контекста вызова.

**Скилы** (`skills/*/SKILL.md`) — в pre-flight блок:

```bash
python -m scripts.wiki.log --type skill_call --skill <slug> --stage <N>
```

`<slug>` — имя папки скила. `<N>` — этап из контекста вызова.

**Реализация:** при добавлении нового агента или скила — строка логирования обязательна. Модель должна добавлять её автоматически при создании/редактировании любого `agents/*.md` или `skills/*/SKILL.md`.

---

## 6. Расширение отчёта `routing-report.md`

Новая секция после "Детали wiki_query":

```markdown
## Запуски vs вики (7д)

| Время | Тип    | Имя               | Stage  | via_wiki | Утечка? |
|-------|--------|-------------------|--------|----------|---------|
| HH:MM | skill  | <skill-slug>      | <N>    | ❌       | ⚠️      |
| HH:MM | stage  | <NN_stage-name>   | <N>    | ✅       |         |
| HH:MM | agent  | <agent-slug>      | <N>    | ✅       |         |
```

Секция содержит **все** события `stage_start`, `agent_call`, `skill_call` из лога за период — не фильтруя по конкретным именам.

`Утечка? = ⚠️` если `via_wiki == false` — агент/скил/этап запустился без предварительного wiki-запроса.

В `StatsResult` добавить:
```python
launches: list[dict] = field(default_factory=list)  # stage_start/agent_call/skill_call events
```

---

## 7. Изменения в существующих файлах

| Файл | Изменение |
|------|-----------|
| `scripts/wiki/routing_log.py` | `was_wiki_queried()`, `log_stage_start()`, `log_agent_call()`, `log_skill_call()` |
| `scripts/wiki/stats.py` | `StatsResult.launches`, секция "Запуски vs вики" в `generate_report()` |
| `scripts/gate-check.sh` | вызов `python -m scripts.wiki.log --type stage_start` |
| `agents/*.md` — **все** | `python -m scripts.wiki.log --type agent_call` в pre-flight каждого агента |
| `skills/*/SKILL.md` — **все** | `python -m scripts.wiki.log --type skill_call` в pre-flight каждого скила |

### Новые файлы

| Файл | Назначение |
|------|-----------|
| `scripts/wiki/log.py` | CLI-враппер для логирования из bash |
| `tests/wiki/test_launch_tracking.py` | тесты новой функциональности |

---

## 8. Тестовая стратегия

**`tests/wiki/test_launch_tracking.py`:**

- `test_was_wiki_queried_true` — лог содержит wiki_query с нужным stage → True
- `test_was_wiki_queried_false_no_query` — нет wiki_query в сессии → False
- `test_was_wiki_queried_false_wrong_stage` — wiki_query есть, но другой stage → False
- `test_was_wiki_queried_false_wrong_session` — wiki_query есть, но другой session_id → False
- `test_log_stage_start_writes_via_wiki_true` — пишет запись с via_wiki=True при наличии prior query
- `test_log_stage_start_writes_via_wiki_false` — пишет via_wiki=False без prior query
- `test_log_agent_call_writes_record` — запись agent_call в лог
- `test_log_skill_call_writes_record` — запись skill_call в лог
- `test_stats_launches_section_in_report` — generate_report() содержит "Запуски vs вики"
- `test_stats_leak_marker_for_no_wiki` — ⚠️ появляется для via_wiki=False

---

## 9. Out of scope

- `bash_call` логирование (кроме gate-check.sh через `stage_start`)
- Ретроспективный анализ старых логов
- UI в wp-admin
- Автоматический `via_wiki` для скилов вызываемых через Claude UI (не через bash)
