# B29 — Wiki Run ID Корреляция

**Goal:** Устранить ложные утечки в routing-report: все запуски агентов и скилов через субагентов показывают `via_wiki = false` даже если вики запрашивалась, потому что субагент работает в отдельной сессии с другим `session_id`.

**Architecture:** Ввести `run_id` — идентификатор одного рабочего запуска (одна команда `/landing-go` или ручной запуск агента). Контроллер генерирует `run_id` и записывает в `.wiki-run-id`. `log.py` читает его автоматически как fallback для `--session-id`. `was_wiki_queried()` ищет `wiki_query` по `run_id`, а не по `session_id` Claude. Отчёт группируется по `run_id`.

**Tech Stack:** Python 3.10+, pytest, Markdown.

**Зависимости:** нет. Независимая доработка wiki-инфраструктуры.

---

## Контекст и проблема

### Что сейчас

`was_wiki_queried(session_id, stage)` ищет `wiki_query`-запись с совпадающим `session_id` в `logs/wiki-usage.jsonl`. Claude Code присваивает каждому субагенту свой `session_id`. В итоге:

1. Контроллер делает `wiki_query` → пишет запись с `session_id = A`
2. Субагент запускает агент → `log_agent_call` вызывается с `session_id = B`
3. `was_wiki_queried(B, stage)` → совпадений нет → `via_wiki = false`

Результат: routing-report показывает 100% утечек при работе через субагентов — данные бесполезны.

### Что нужно

Привязать все события одного рабочего запуска к единому `run_id`, независимо от `session_id` Claude Code. Один `/landing-go` = один `run_id`. Новый день = новый `run_id`.

---

## Дизайн

### `run_id` — формат и жизненный цикл

Формат: `landing-YYYYMMDD-HHMM` (например `landing-20260528-1721`).

**Создание:** при старте любого агента/оркестратора — если `.wiki-run-id` не существует, создать с новым id.

**Использование:** `log.py` читает `.wiki-run-id` автоматически если `--session-id` не передан.

**Очистка:** не удаляется автоматически. Новый запуск на следующий день создаёт новый файл (перезаписывает).

**Формат файла:** одна строка — сам `run_id`.

### Новый модуль `scripts/wiki/run_id.py`

```python
RUN_ID_PATH = config.REPO_ROOT / ".wiki-run-id"

def get_or_create() -> str:
    """Читает run_id из файла. Если нет — генерирует новый и записывает."""

def get() -> str | None:
    """Только читает. None если файла нет."""

def reset() -> str:
    """Генерирует новый run_id, перезаписывает файл. Возвращает новый id."""
```

`get_or_create()` генерирует id в формате `landing-YYYYMMDD-HHMM`.

### Изменения в `log.py`

Текущий fallback: `session_id = args.session_id or os.environ.get("CLAUDE_SESSION_ID", "unknown")`

Новый fallback (приоритет):
1. `--session-id` (явный аргумент)
2. `.wiki-run-id` файл через `run_id.get_or_create()`
3. `CLAUDE_SESSION_ID` env (legacy fallback)
4. `"unknown"`

Таким образом агентам ничего менять не нужно — `log.py` сам подхватывает `run_id`.

### Изменения в `routing_log.py`

`was_wiki_queried()` логика не меняется — она уже ищет по `session_id`. Теперь `session_id` во всех записях будет одинаковым (`run_id`) для одного запуска → корреляция работает.

Дополнительно: добавить поле `run_id` в каждую запись лога (дублирует `session_id` для явности):

```json
{"ts": "...", "type": "agent_call", "session_id": "landing-20260528-1721", "run_id": "landing-20260528-1721", ...}
```

### `.wiki-run-id` в `.gitignore`

Файл временный, не должен попадать в коммиты. Добавить в корневой `.gitignore`.

---

## Изменения в отчёте (`stats.py`)

### Сводка по запускам (новая секция)

Добавить секцию **"Запуски (сводка)"** перед детализацией:

```markdown
## Запуски (сводка)

| run_id | Дата | Агентов/этапов | Через вики | Утечки |
|---|---|---|---|---|
| landing-20260528-1721 | 28 мая 17:21 | 15 | 12 | 3 |
| landing-20260527-1103 | 27 мая 11:03 | 8 | 8 | 0 |
```

Агрегация: группировать `stage_start` + `agent_call` + `skill_call` по `run_id`, считать total / via_wiki=true / via_wiki=false.

### Детализация (существующая секция)

Добавить колонку `run_id` в таблицу "Запуски vs вики":

```markdown
| Время | run_id | Тип | Имя | Stage | via_wiki | Утечка? |
```

`run_id` показывается сокращённо: только дата+время (`20260528-1721`), без префикса `landing-`.

---

## Затронутые файлы

**Создать:**
- `scripts/wiki/run_id.py` — утилита для чтения/записи `.wiki-run-id`
- `tests/wiki/test_run_id.py` — тесты

**Изменить:**
- `scripts/wiki/log.py` — fallback на `run_id.get_or_create()`
- `scripts/wiki/stats.py` — сводка по run_id + колонка в детализации
- `.gitignore` (корневой) — добавить `.wiki-run-id`

**Не меняются:**
- `scripts/wiki/routing_log.py` — логика `was_wiki_queried()` не трогается
- Все агенты и скилы — `log.py` сам подхватывает `run_id`

---

## Что НЕ входит в этот спек

- Принудительный сброс `run_id` через команду (можно удалить файл вручную)
- Группировка по проекту внутри run_id
- Хранение истории run_id (только текущий в файле)
- Изменение формата `logs/wiki-usage.jsonl` (обратная совместимость сохраняется)

---

## Self-review

1. **Placeholders:** нет TBD/TODO
2. **Consistency:** `run_id` совпадает с `session_id` в записях — `was_wiki_queried()` не нужно переписывать
3. **Scope:** один новый модуль + два изменённых файла + отчёт — scope чёткий
4. **Ambiguity:** "новый день = новый run_id" — `reset()` вызывается явно оркестратором при старте, не по времени
