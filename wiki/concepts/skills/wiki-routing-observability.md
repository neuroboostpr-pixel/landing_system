---
slug: wiki-routing-observability
type: skill
name: "Wiki Routing Observability"
tags: [wiki, observability, logging, analytics, routing]
triggers: []
inputs: [wiki/index.yaml, logs/wiki-usage.jsonl]
outputs: [logs/wiki-usage.jsonl, wiki/routing-report.md]
pre_reqs: [wiki]
related: [wiki, wiki-audit-checklist]
sources: ["skills/wiki-routing-observability/SKILL.md"]
updated: 2026-05-27
confidence: {triggers: low}
---

# Wiki Routing Observability

## Что делает

Переиспользуемый скилл для измерения эффективности wiki-роутинга. Логирует каждый вызов `query.py` в `logs/wiki-usage.jsonl`, а по окончании сессии парсит транскрипт и находит прямые чтения исходников (bypass — когда агент читает `agents/*.md` или `skills/*/SKILL.md` напрямую вместо wiki). На старте сессии выводит строку статистики: сколько запросов прошло через wiki, сколько обошли её, сколько токенов сэкономлено и каков процент bypass. Команда `--report` генерирует полный Markdown-отчёт в `wiki/routing-report.md`.

## Когда вызывается

Активируется автоматически через хук `session_start` при каждом запуске сессии в проекте, где скилл установлен. Может вызываться вручную через CLI (`python -m scripts.wiki.stats`) для получения сводки или отчёта за период. Прямых пользовательских триггеров нет — это фоновая инфраструктура.

## Вход → выход

**Вход:** `wiki/index.yaml` (должен существовать), директория `logs/` (создаётся автоматически), опционально — файл транскрипта текущей сессии для парсинга bypass.

**Выход:** `logs/wiki-usage.jsonl` с записями о каждом запросе; строка статистики в консоли на старте сессии; `wiki/routing-report.md` при запуске `--report`.

## Failure modes

- `wiki/index.yaml` не существует — preflight падает, статистика не показывается.
- `logs/` не доступна для записи — лог-записи теряются беззвучно.
- `SOURCE_READ_PATTERNS` в `config.py` не настроен под проект — bypass-файлы не детектируются, bypass rate занижен.
- Транскрипт не передан или недоступен — прямые чтения не обнаруживаются, статистика неполная.
- `--exact-tokens` без `ANTHROPIC_API_KEY` — команда падает с ошибкой авторизации.

## Related

- [[wiki]] — основная wiki-система, эффективность которой измеряет этот скилл
- [[wiki-audit-checklist]] — ручной аудит wiki; дополняет автоматическую observability