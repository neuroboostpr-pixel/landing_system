---
type: rule
name: phase-stage-08
sources: ["tests/phase-stage-08/README.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-builder", "frontend-builder", "stage-gates"]
tags: ["tests", "bats", "stage-08", "wp-blocks", "legacy"]
---

# Тесты этапа 08 (Сборка WordPress-темы)

## Что делает
Группа автоматических тестов (bats + pytest) для проверки корректности работы этапа 08 — генерации WordPress-темы, Lazy Blocks и gate-чека перед переходом к деплою.

## Когда вызывать / в каком этапе
Запускается при разработке и проверке этапа **08 (Код)**. Следует запускать:
- перед коммитом изменений в `wp-builder`, `frontend-builder` или скрипты gate-check;
- в CI/CD после любого изменения в `scripts/` или `skills/wp-*`.

## Что на вход / на выход

**Вход:**
- Готовый проект с утверждёнными этапами 05–07 (design-system, composed.html, content).
- Bash-среда с установленным `bats-core`.

**Выход:**
- Отчёт bats: прошли / упали тесты по четырём группам.
- Exit code `0` — можно коммитить; `1` — нужно чинить.

## Состав тест-файлов

| Файл | Что проверяет |
|------|---------------|
| `test-gate-check-stage-08.bats` | Gate-check скрипт корректно блокирует переход на этап 09 при неполном этапе 08 |
| `test-generate-wp-blocks.bats` | Генерация `block.php` (Lazy Blocks) для каждого блока из composed.html |
| `test-backport-legacy.bats` | Команда backport корректно адаптирует старые проекты к новой структуре |
| `test-mark-legacy-projects.bats` | Скрипт правильно помечает legacy-проекты в `.landing-state.yaml` |

## Запуск

```bash
# Все bats-тесты группы
bats tests/phase-stage-08/

# Если есть Python-тесты
pytest tests/phase-stage-08/
```

## Связанные концепты
- [[wp-builder]] — агент, чью работу проверяют тесты generate-wp-blocks
- [[frontend-builder]] — агент этапа 08b, блоки которого валидируются
- [[stage-gates]] — механизм gate-check, тестируемый в test-gate-check-stage-08
- [[08-kod]] — этап, к которому относится данная тест-группа

## Источник
- `tests/phase-stage-08/README.md`