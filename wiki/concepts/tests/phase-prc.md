---
type: rule
name: phase-prc-tests
sources: ["tests/phase-prc/README.md"]
updated: 2026-05-18
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation", "landing-visuals", "icon-generator", "infographic-builder"]
tags: ["tests", "bats", "pytest", "pr-c", "visual-generation", "07d"]
---

# Тесты Phase PR-C (Visual Generation)

## Что делает
Набор автоматических тестов, проверяющих корректность работы компонентов этапа PR-C — AI-генерации иконок и инфографики через codex. Убеждается, что агенты, обёртки codex и gate-проверки работают по спецификации.

## Когда вызывать / в каком этапе
Запускаются на этапе **07d** (Visual Generation) — после появления `07b_COMPOSED/composed.html` и до финального approve визуалов. Также выполняются в CI при любом коммите, затрагивающем агентов, скиллы или template/07d_VISUALS.

## Что на вход / на выход

**Вход:**
- Исходники агентов (`agents/*.md`) с валидным YAML-frontmatter
- Обёртки codex CLI (`scripts/codex-*.sh` или аналоги)
- Конфиг gate-проверок для этапа 07d
- Папка шаблона `template/07d_VISUALS/`
- Блоки из `block-library/`, связанные с визуальными слотами

**Выход:**
- Отчёт bats/pytest (pass / fail по каждому тест-кейсу)
- Нет файловых артефактов — только статус выхода (exit 0 = все тесты прошли)

**Файлы тест-группы:**
| Файл | Что проверяет |
|---|---|
| `test-agents-frontmatter.bats` | YAML-frontmatter всех агентов валиден и содержит обязательные поля |
| `test-codex-wrappers.bats` | Обёртки codex CLI отвечают корректно, hash-кэш работает |
| `test-landing-visuals-gate.bats` | Gate `/landing-visuals` не пропускает этап при отсутствии `composed.html` |
| `test-new-blocks.bats` | Новые блоки из PR-C прошли lint и имеют `meta.yaml` |
| `test-template-07d.bats` | Структура `template/07d_VISUALS/` соответствует канону |

## Запуск

```bash
# Bats-тесты
bats tests/phase-prc/

# Pytest (если есть test_*.py)
pytest tests/phase-prc/
```

## Связанные концепты
- [[visual-curator]] — оркестратор этапа 07d, чья логика покрывается тестами gate и template
- [[visual-generation]] — скилл генерации визуалов; тесты проверяют его codex-обёртки
- [[landing-visuals]] — команда запуска этапа; тест `test-landing-visuals-gate.bats` проверяет её gate
- [[icon-generator]] — агент генерации иконок, frontmatter которого проверяет `test-agents-frontmatter.bats`
- [[infographic-builder]] — агент инфографики, аналогично

## Источник
- `tests/phase-prc/README.md`