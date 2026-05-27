---
name: wiki-routing-observability
description: Hybrid logging for wiki routing systems — tracks wiki queries vs direct source reads, estimates token savings, preflight checks. Reusable across any project with a wiki/index.yaml.
---

# wiki-routing-observability

Переиспользуемый скилл для измерения эффективности wiki routing.

## Что делает

- Логирует каждый `query.py` вызов → `logs/wiki-usage.jsonl`
- На session end парсит транскрипт → детектит прямые чтения исходников (bypass)
- `session_start` показывает stats строку: queries / direct reads / tokens saved / bypass rate
- `python -m scripts.wiki.stats --report` → `wiki/routing-report.md`

## Компоненты

| Файл | Назначение |
|---|---|
| `scripts/wiki/routing_log.py` | Запись/чтение JSONL лога |
| `scripts/wiki/transcript_parser.py` | Парсинг tool calls из транскрипта |
| `scripts/wiki/stats.py` | Агрегация и Markdown отчёт |
| `scripts/wiki/preflight.py` | Проверка окружения |

## Развёртывание на новом проекте

1. Скопировать этот скилл в новый проект
2. В `config.py` задать `SOURCE_READ_PATTERNS`:
   ```python
   SOURCE_READ_PATTERNS = ["agents/*.md", "skills/*/SKILL.md"]
   ```
3. В `session_start.py` добавить вызов preflight + stats (3 строки — см. пример)
4. В `query.py` добавить вызов `routing_log.log_query()` после filter

## Требования

- Python 3.10+, stdlib only
- `wiki/index.yaml` должен существовать
- `logs/` должна быть writable (создаётся автоматически)

## CLI

```bash
python -m scripts.wiki.stats                # summary строка
python -m scripts.wiki.stats --report       # Markdown отчёт
python -m scripts.wiki.stats --days=30      # за месяц
python -m scripts.wiki.stats --exact-tokens # точный подсчёт (требует ANTHROPIC_API_KEY)
```

## Bypass rate интерпретация

- **0-10%** — wiki routing работает отлично
- **10-25%** — небольшой bypass, нормально
- **25-50%** — агент часто обходит wiki, стоит изучить топ bypass файлов
- **>50%** — wiki routing не работает, проверить SOURCE_READ_PATTERNS
