---
type: rule
name: phase-4-tests
sources: ["tests/phase-4/README.md", "tests/phase-4/test-agents-phase4.bats", "tests/phase-4/test-commands-phase4.bats"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-builder", "integrations-engineer", "analytics-engineer", "seo-optimizer", "landing-build", "wp-gutenberg-block-builder", "wp-theme-assembler"]
tags: ["tests", "bats", "phase-4", "stage-08", "ci"]
---

# Phase-4 Tests — тесты этапа сборки WordPress-темы

## Что делает

Автоматически проверяет, что все агенты и команды, отвечающие за этап 08 (сборка WordPress-темы и интеграции), присутствуют в системе и содержат обязательные поля. Это CI-барьер: если агент или скрипт исчезнет из репозитория — тесты упадут.

## Когда вызывать / в каком этапе

Тесты принадлежат этапу 08 (генерация кода). Запускаются:
- автоматически в CI при каждом коммите, затрагивающем `agents/`, `skills/`, `.claude/commands/`;
- вручную разработчиком перед мержем PR, связанного с любым агентом или скиллом этапа 08.

```bash
# Bats-тесты
bats tests/phase-4/

# Python-тесты (если есть test_*.py)
pytest tests/phase-4/
```

## Что на вход / на выход

**Вход:**
- Файловая система репозитория: `agents/*.md`, `skills/*/SKILL.md`, `.claude/commands/*.md`, скрипты (`generate-theme.py`, `bundle-assets.py`, `render-build-preview.py`), шаблон `build-preview.html.j2`.

**Выход:**
- BATS-отчёт (pass/fail по каждому тесту).
- Exit-код: `0` — все проверки прошли, `1` — есть падения.

**Что именно проверяется:**

| Файл | Проверки |
|---|---|
| `agents/wp-builder.md` | существует, name/description frontmatter, упоминание stage 08, HARD GATE |
| `agents/integrations-engineer.md` | существует, frontmatter, упоминание Telegram и Fluent Forms |
| `agents/analytics-engineer.md` | существует, frontmatter, Yandex Metrika, `YM_COUNTER_ID` |
| `agents/seo-optimizer.md` | существует |
| `.claude/commands/landing-build.md` | существует, frontmatter, ссылки на 3 скрипта, HARD GATE |
| `skills/wp-gutenberg-block-builder/SKILL.md` | существует |
| `skills/wp-theme-assembler/SKILL.md` | существует |
| Скрипты `generate-theme.py`, `bundle-assets.py`, `render-build-preview.py` | файлы на месте |
| `tools/html/templates/build-preview.html.j2` | шаблон присутствует |

## Связанные концепты

- [[wp-builder]] — агент генерации Lazy Blocks и WordPress-темы; основная проверяемая единица
- [[integrations-engineer]] — агент подключения Telegram-вебхука и Fluent Forms; проверяется наличие и содержимое
- [[analytics-engineer]] — агент настройки Яндекс Метрики; проверяется счётчик `YM_COUNTER_ID`
- [[seo-optimizer]] — агент SEO-мета и Schema.org; проверяется существование файла
- [[landing-build]] — команда `/landing-build`, которую эти агенты обслуживают
- [[wp-gutenberg-block-builder]] — скилл генерации PHP-блоков; проверяется `SKILL.md` и `generate-theme.py`
- [[wp-theme-assembler]] — скилл сборки темы; проверяется `SKILL.md`, `bundle-assets.py`, `render-build-preview.py`

## Источник

- `tests/phase-4/README.md`
- `tests/phase-4/test-agents-phase4.bats`
- `tests/phase-4/test-commands-phase4.bats`