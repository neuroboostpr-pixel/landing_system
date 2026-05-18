---
type: unknown
name: phase-preview-panel
sources: ["tests/phase-preview-panel/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: []
tags: ["tests", "bats", "pytest", "palette", "preview-panel"]
---

# Тесты: Phase Preview Panel

## Что делает
Набор автоматических тестов для функциональности preview-панели палитр. Проверяет экспорт палитр, генерацию CSS, фильтрацию по осям и корректность схемы данных палитры.

## Когда вызывать / в каком этапе
Запускается при разработке или изменении компонентов preview-панели — до коммита в ветку. Актуален при работе с палитрами дизайн-системы (этап 05).

## Что на вход / на выход

**Вход:**
- Исходные скрипты и конфиги системы, связанные с палитрами и preview-панелью
- Bats-тесты в `tests/phase-preview-panel/*.bats`

**Выход:**
- Отчёт о прохождении/падении тестов в stdout
- Exit code 0 при успехе, ненулевой — при ошибке

## Состав тестов

| Файл | Что проверяет |
|---|---|
| `test-export-palettes.bats` | Корректный экспорт палитр |
| `test-generate-axes-filter.bats` | Фильтрация палитр по осям (тип/настроение) |
| `test-generate-palette-css.bats` | Генерация CSS-переменных из палитры |
| `test-migrate-to-preview-panel.bats` | Миграция данных в формат preview-panel |
| `test-palette-schema.bats` | Валидация схемы YAML-файла палитры |

## Запуск

```bash
# Bats-тесты
bats tests/phase-preview-panel/

# Pytest (если есть test_*.py)
pytest tests/phase-preview-panel/
```

## Связанные концепты
- [[design-tokens-generation]] — генерация токенов, с которыми работают палитры
- [[design-system-generator]] — этап 05, где используется preview-панель

## Источник
- `tests/phase-preview-panel/README.md`