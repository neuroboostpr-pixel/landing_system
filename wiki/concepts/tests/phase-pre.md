---
type: unknown
name: phase-pre-tests
sources: ["tests/phase-pre/README.md", "tests/phase-pre/test-landing-start.bats", "tests/phase-pre/test-wizard-agent.bats", "tests/phase-pre/test-migrate-readmes.bats", "tests/phase-pre/test-template-readmes.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-onboarding-wizard", "landing-start", "landing-project-init", "landing-go"]
tags: ["tests", "bats", "pytest", "onboarding", "phase-pre"]
---

# phase-pre — тест-группа онбординг-визарда

## Что делает
Проверяет корректность всех артефактов, связанных с PR-E (Onboarding Wizard): структуру команды `/landing-start`, агента `landing-onboarding-wizard`, шаблон проекта и скрипт миграции `migrate-template-readmes.sh`.

## Когда вызывать / в каком этапе
Запускается перед мержем любого изменения, затрагивающего команду `/landing-start`, агента `landing-onboarding-wizard`, содержимое `template/` или скрипт `scripts/migrate-template-readmes.sh`. В CI должен проходить как precondition для этапов 00–01.

```bash
bats tests/phase-pre/
pytest tests/phase-pre/
```

## Что на вход / на выход

**Вход:**
- `commands/landing-start.md` — файл slash-команды
- `agents/landing-onboarding-wizard.md` — агент визарда
- `template/` — канонический шаблон проекта
- `scripts/migrate-template-readmes.sh` — скрипт миграции

**Выход:**
- exit 0 / exit 1 (bats/pytest стандартные результаты)
- Никаких артефактов не создаёт — только верификация

## Покрытие по файлам

| Файл | Что проверяется |
|---|---|
| `test-landing-start.bats` | frontmatter команды, ссылка на `landing-onboarding-wizard`, 4 шага материалов, упоминание `/landing-go` |
| `test-wizard-agent.bats` | frontmatter агента, 3-абзацный welcome, 4 шага (ШАГ 1–4), обязательность прототипа, ссылки на `wizard-check-materials.py` и `landing-project-init`, финальная подсказка `/landing-go` |
| `test-template-readmes.bats` | каждая папка template содержит `README.md`, наличие `04_БРЕНД/logos/README.md` и `07_ПРОТОТИП/source/README.md`, содержимое README (упоминание `logo.svg/png`, `favicon`, `prototype.pdf`) |
| `test-migrate-readmes.bats` | скрипт создаёт недостающие READMEs, идемпотентность (двойной запуск), не перезаписывает существующие READMEs, создаёт `logos/` если отсутствует |
| `test-wizard-check-materials.py` | pytest-тесты Python-скрипта проверки материалов визарда |

## Связанные концепты
- [[landing-onboarding-wizard]] — агент, чьё поведение покрывает `test-wizard-agent.bats`
- [[landing-start]] — команда, проверяемая в `test-landing-start.bats`
- [[landing-project-init]] — скилл, на который должен ссылаться визард
- [[landing-go]] — следующий шаг после визарда, его наличие в тестах обязательно
- [[landing-onboarding]] — скилл онбординга, смежный контекст

## Источник
- `tests/phase-pre/README.md`
- `tests/phase-pre/test-landing-start.bats`
- `tests/phase-pre/test-wizard-agent.bats`
- `tests/phase-pre/test-migrate-readmes.bats`
- `tests/phase-pre/test-template-readmes.bats`