Теперь у меня достаточно данных. Составляю wiki-страницу:

---
type: unknown
name: phase-3
sources: ["tests/phase-3/README.md", "tests/phase-3/test-agents-phase3.bats", "tests/phase-3/test-commands-phase3.bats"]
updated: 2026-05-18
stage: "05-07"
uses: ["design-system-generator", "scene-director", "stack-planner", "content-writer", "landing-design", "landing-stack", "landing-content"]
tags: ["tests", "bats", "phase-3", "design", "stack", "content"]
---

# phase-3 — Тест-группа: дизайн, стек, контент

## Что делает

Автоматически проверяет целостность агентов и команд этапов 05–07: дизайн-система, подбор стека и написание контента. Гарантирует, что файлы существуют, содержат корректный frontmatter и ключевые артефакты.

## Когда вызывать / в каком этапе

Запускается в CI после коммитов, затрагивающих агенты `design-system-generator`, `scene-director`, `stack-planner`, `content-writer` или команды `landing-design`, `landing-stack`, `landing-content`. Соответствует стадиям 05 (дизайн-токены), 06 (стек) и 07 (контент).

```bash
# Bats-тесты
bats tests/phase-3/

# Pytest (если есть test_*.py)
pytest tests/phase-3/
```

## Что на вход / на выход

**Вход:**
- Файлы агентов `agents/design-system-generator.md`, `agents/scene-director.md`, `agents/stack-planner.md`, `agents/content-writer.md`
- Файлы команд `.claude/commands/landing-design.md`, `.claude/commands/landing-stack.md`, `.claude/commands/landing-content.md`

**Выход:**
- Результат `bats` / `pytest` — pass/fail по каждому assertion
- Проверяется наличие ключевых слов: `DESIGN.md`, `design-preview.html`, `design-stack.yaml`, `final-copy.md`, `cinematic`

**Покрытые кейсы:**
| Файл | Что проверяет |
|---|---|
| `test-agents-phase3.bats` | Существование, frontmatter `name:`, ключевые артефакты 4 агентов |
| `test-commands-phase3.bats` | Существование, `description:`, упоминание агента и артефакта 3 команд |

## Связанные концепты

- [[design-system-generator]] — агент этапа 05, генерирует `DESIGN.md` и `tokens.json`
- [[scene-director]] — агент этапа 05 для cinematic-режима, создаёт `scenes.md`
- [[stack-planner]] — агент этапа 06, формирует `design-stack.yaml`
- [[content-writer]] — агент этапа 07, пишет `final-copy.md` и `seo-copy.md`
- [[landing-design]] — команда запуска этапа 05
- [[landing-stack]] — команда запуска этапа 06
- [[landing-content]] — команда запуска этапа 07

## Источник

- `tests/phase-3/README.md`
- `tests/phase-3/test-agents-phase3.bats`
- `tests/phase-3/test-commands-phase3.bats`