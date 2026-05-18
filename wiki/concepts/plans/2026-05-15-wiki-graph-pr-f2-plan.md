---
type: rule
name: pr-f2-wiki-compilation-plan
sources: ["docs/superpowers/plans/2026-05-15-wiki-graph-pr-f2-plan.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses: ["compile-py", "hash-cache", "sdk-client", "system-compiler", "wiki-graph-pr-f1-plan"]
tags: ["wiki", "pr-f2", "compilation", "sdk", "plan"]
---

# PR-F.2 — Реализация системной компиляции wiki

## Что делает
Реализует режим `compile.py --source-mode=system`: читает исходники системы (агенты, скиллы, команды, этапы шаблона, правила, блоки) и через Claude Agent SDK генерирует структурированные wiki-страницы в папке `landing-system/wiki/` с концептами, главным индексом и журналом прогонов.

## Когда вызывать / в каком этапе
Это план реализации PR-F.2 — выполняется разработчиком после завершения PR-F.1 (скелет `compile.py`, модули `config.py`, `utils.py`). Результат плана — рабочий `compile --source-mode=system`, который впоследствии вызывается автоматически git-хуком (PR-F.4) после каждого коммита, затрагивающего исходники системы.

## Что на вход / на выход

**Вход:**
- `requirements.txt` — добавить `claude-agent-sdk>=0.1.0` и `pytest-mock>=3.12`
- Исходники системы: `agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`, `template/*/README.md`, `docs/standards/*.md`, `block-library/**/meta.yaml`
- Скелет `scripts/wiki/compile.py` из PR-F.1

**Выход (создаются новые файлы):**
- `scripts/wiki/hash_cache.py` — SHA256-кэш для пропуска неизменённых файлов
- `scripts/wiki/sdk_client.py` — изолированная обёртка над `claude-agent-sdk`
- `scripts/wiki/system_compiler.py` — главная логика компиляции
- `scripts/wiki/prompts/system_concept.md` — системный промпт для генерации концепта
- `scripts/wiki/prompts/system_index.md` — системный промпт для генерации `index.md`
- `scripts/wiki/bootstrap-system.sh` — скрипт первого запуска
- `wiki/concepts/**/*.md` — сгенерированные концепты (после bootstrap)
- `wiki/index.md`, `wiki/log.md`, `wiki/.cache.json`
- Тесты: `tests/wiki/test_hash_cache.py`, `test_sdk_client.py`, `test_system_compiler.py`

## Связанные концепты
- [[wiki]] — целевая папка, куда пишется результат компиляции
- [[pr-f1-wiki-skeleton-plan]] — предыдущий PR, создал скелет CLI и конфиг
- [[compile-py]] — CLI, в котором реализуется ветка `--source-mode=system`
- [[stage-gates]] — правила hard gate, на соответствие которым wiki должна быть синхронной с исходниками

## Источник
- `docs/superpowers/plans/2026-05-15-wiki-graph-pr-f2-plan.md`