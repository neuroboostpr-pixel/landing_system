---
type: script
name: migrate-to-preview-panel
sources: ["scripts/migrate-to-preview-panel.sh"]
updated: 2026-05-18
triggers: []
stage: ""
uses: []
tags: ["migration", "preview-panel", "palette", "css", "bash"]
---

# migrate-to-preview-panel.sh — миграция на плагин предпросмотра

## Что делает
Одноразовый скрипт миграции: заменяет устаревший хардкодный компонент `nu-theme-bar` на плагин `lp-preview-panel` и автоматически заполняет файлы палитры проекта и библиотеки на основе существующего CSS.

## Когда вызывать / в каком этапе
Запускается вручную один раз при переводе существующего проекта или библиотеки блоков на новую архитектуру preview-panel. Актуально при обновлении landing-system, когда в проекте ещё используется старый `nu-theme-bar`. Не привязан к конкретному этапу pipeline — это утилита разовой миграции.

Вызов:
```bash
bash scripts/migrate-to-preview-panel.sh <project-path> <library-path>
```

## Что на вход / на выход

**Вход:**
- `<project-path>` — путь к папке проекта-лендинга (например `~/Lendings/my-project`)
- `<library-path>` — путь к папке общей библиотеки блоков (например `block-library/`)
- Существующие CSS-файлы проекта — из них скрипт извлекает переменные палитры

**Выход:**
- Файлы проекта обновлены: `nu-theme-bar` заменён на `lp-preview-panel`
- Файлы палитры (`palette.yaml` или аналог) заполнены значениями, извлечёнными из CSS
- Аналогичные файлы палитры обновлены в папке библиотеки

## Связанные концепты
- [[design-tokens-generation]] — генерация токенов дизайна; после миграции палитра должна быть совместима с tokens.json
- [[block-library-management]] — управление библиотекой блоков; скрипт затрагивает структуру library-path
- [[design-system-generator]] — агент, который работает с палитрой и preview-компонентами после миграции

## Источник
- `scripts/migrate-to-preview-panel.sh`