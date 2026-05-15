# scripts/wiki — wiki compiler

Адаптация [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) под нашу систему.

## Три режима

| Mode | Источник | Назначение |
|---|---|---|
| `system` | `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/`, `block-library/` | `landing-system/wiki/` — карта архитектуры |
| `project-graph` | артефакты проекта (`composed.html`, `selections.yaml`, …) | `~/Lendings/<slug>/wiki/` — граф структуры лендинга |
| `conversations` | транскрипты сессий | `~/Lendings/<slug>/memory/compiled/` — память разговоров |

## Использование

```bash
# Системный wiki (после изменений в системе)
python -m scripts.wiki.compile --source-mode=system

# Граф конкретного проекта
python -m scripts.wiki.compile --source-mode=project-graph --project=dubai-avto-liza

# Память разговоров (обычно вызывается хуком, не вручную)
python -m scripts.wiki.compile --source-mode=conversations --project=dubai-avto-liza
```

## Статус по PR

- **PR-F.1** (текущий): инфраструктура + CLI-скелет. Логика не реализована.
- **PR-F.2**: реализация `--source-mode=system`.
- **PR-F.3**: реализация `--source-mode=project-graph` + интеграция в `template/`.
- **PR-F.4**: хуки SessionStart/End/PreCompact + реализация `--source-mode=conversations`.
- **PR-F.5**: `lint.py` + `preview.html` рендерер.

Полный spec: [docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md](../../docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md)
