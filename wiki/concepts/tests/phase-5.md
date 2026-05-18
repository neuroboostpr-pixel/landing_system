---
type: rule
name: phase-5-tests
sources: ["tests/phase-5/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: []
tags: ["testing", "bats", "pytest", "phase-5"]
---

# Тесты Phase-5

## Что делает

Группа автотестов для PR пятой фазы landing-system. Проверяет агентов и команды, добавленные в этом PR, через bats (bash-тесты) и pytest (Python-тесты).

## Когда вызывать / в каком этапе

Запускается вручную разработчиком при работе с кодом phase-5 — до коммита или в CI. Не является частью основного pipeline для маркетолога.

## Что на вход / на выход

**Вход:**
- Установленный `bats-core` (для `.bats`-тестов)
- Установленный `pytest` (для `test_*.py`-тестов, если они появятся)

**Выход:**
- Результат прогона: pass / fail по каждому тест-кейсу
- Ненулевой exit-код при любой ошибке (блокирует коммит в CI)

**Команды запуска:**
```bash
# Bash-тесты
bats tests/phase-5/

# Python-тесты
pytest tests/phase-5/
```

**Тест-файлы:**
- `tests/phase-5/test-agents-phase5.bats` — тесты агентов
- `tests/phase-5/test-commands-phase5.bats` — тесты команд

## Связанные концепты

- [[stage-gates]] — гейты этапов, которые тесты помогают проверять
- [[landing-orchestrator]] — оркестратор, чьи команды тестируются

## Источник

- `tests/phase-5/README.md`