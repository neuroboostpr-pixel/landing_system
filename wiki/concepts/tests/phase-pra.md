---
type: unknown
name: phase-pra-tests
sources: ["tests/phase-pra/README.md"]
updated: 2026-05-18
triggers: []
stage: "07a-07b"
uses: ["prototype-import", "block-composition", "wireframe-rendering", "block-library-management", "design-tokens-generation", "prototype-importer"]
tags: ["tests", "bats", "phase-pra", "qa"]
---

# Тесты Phase PR-A

## Что делает

Набор автоматических bats-тестов, которые проверяют работоспособность всех скриптов и агентов этапа PR-A: импорт прототипа, рендер wireframe, compose-блоки, библиотека блоков. Запускается через `bats` или `pytest` и даёт быструю проверку перед коммитом.

## Когда вызывать / в каком этапе

Запускаются на этапах 07a (wireframe) и 07b (compose) — после любых изменений в скиллах `prototype-import`, `wireframe-rendering`, `block-composition` или `block-library-management`. Рекомендуется запускать перед коммитом через pre-commit хук или вручную.

```bash
# Все bats-тесты группы
bats tests/phase-pra/

# Конкретный файл
bats tests/phase-pra/test-render-wireframe.bats
```

## Что на вход / на выход

**Вход:** исходники скиллов и скриптов в `skills/`, агенты в `agents/`, блоки в `block-library/`, фикстуры в `tests/phase-pra/fixtures/`.

**Выход:** результат `bats` — `ok` / `not ok` по каждому кейсу. При провале — диагностика с названием упавшего теста.

**Покрытые области (18 файлов):**

| Файл | Что проверяет |
|---|---|
| `test-agents-exist.bats` | Наличие файлов агентов (prototype-importer и др.) |
| `test-compose-blocks.bats` | `compose-blocks.py` — сборка блоков из prototype.yaml + selections |
| `test-design-md-sections.bats` | SKILL.md `design-tokens-generation` содержит ≥9 секций |
| `test-enrich-quiz-funnel.bats` | `enrich-quiz-funnel.py` — обогащение quiz-блоков |
| `test-extract-pdf-text.bats` | `extract-pdf-text.py` — извлечение текста из PDF |
| `test-gallery.bats` | `render-gallery.py` — генерация HTML-галереи блоков |
| `test-inject-content.bats` | `inject-content.py` — подстановка текстов в data-slot |
| `test-inject-tokens.bats` | `inject-tokens.py` — подстановка CSS-переменных из tokens.json |
| `test-match-candidates.bats` | `match-candidates.py` — подбор блоков-кандидатов по типу |
| `test-md-to-yaml.bats` | `md-to-yaml.py` — конвертация prototype.md → prototype.yaml |
| `test-patterns-library.bats` | 15 паттернов, 6 style-moods, 8 visual-skills существуют |
| `test-render-wireframe.bats` | `render-wireframe.py` — генерация wireframe.html |
| `test-scaffold-block.bats` | `scaffold-block.py` — создание нового блока с нужными файлами |
| `test-seed-blocks.bats` | Валидность catalog.yaml библиотеки блоков |
| `test-validate-catalog.bats` | `validate-catalog.py` — схема каталога |
| `test-validate-meta.bats` | `validate-meta.py` — схема meta.yaml блоков |
| `test-validate-prototype.bats` | `validate-prototype.py` — схема prototype.yaml |
| `test-validate-selections.bats` | `validate-selections.py` — схема selections.yaml |

## Связанные концепты

- [[prototype-import]] — скрипты extract-pdf-text, md-to-yaml, validate-prototype
- [[block-composition]] — скрипты compose-blocks, inject-content, inject-tokens, validate-selections
- [[wireframe-rendering]] — скрипты render-wireframe, match-candidates, enrich-quiz-funnel
- [[block-library-management]] — скрипты scaffold-block, validate-catalog, validate-meta, render-gallery
- [[design-tokens-generation]] — проверяется структура SKILL.md
- [[prototype-importer]] — проверяется наличие файла агента

## Источник

- `tests/phase-pra/README.md`