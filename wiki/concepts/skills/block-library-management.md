---
type: skill
name: block-library-management
sources: ["skills/block-library-management/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses:
  - ux-composer
  - block-library
tags:
  - block-library
  - validation
  - scaffolding
  - catalog
---

# Block Library Management — управление библиотекой блоков

## Что делает

Предоставляет три утилиты для работы с общей библиотекой wireframe-блоков (`block-library/`): создаёт новые блоки по шаблону, проверяет корректность каталога и метаданных каждого блока. Используется агентом `ux-composer` в момент внедрения блоков в проект.

## Когда вызывать / в каком этапе

Вызывается в двух ситуациях:

1. **При добавлении нового блока в библиотеку** — нужно создать структуру папки и заполнить `meta.yaml` через scaffolding-скрипт.
2. **При валидации перед деплоем или review** — убедиться, что `catalog.yaml` и все `meta.yaml` в библиотеке корректны по схеме.

Также автоматически подключается агентом `ux-composer` когда тот инжектирует блоки из библиотеки в `wireframe.html` или `composed.html` (этапы 07a–07b).

## Что на вход / на выход

**Вход:**
- `block-library/catalog.yaml` — общий каталог всех блоков
- `block-library/<category>/<block-id>/meta.yaml` — метаданные конкретного блока
- Параметры для scaffold: `--id <block-id>` и `--category <category>`

**Выход:**
- Отчёт валидации (stdout) с ошибками схемы или `OK`
- Новая папка блока со скелетом файлов (`meta.yaml`, шаблон разметки) при scaffolding

## Скрипты

| Скрипт | Назначение |
|---|---|
| `scripts/validate-catalog.py <path>` | Проверить `catalog.yaml` на соответствие схеме |
| `scripts/validate-meta.py <path>` | Проверить `meta.yaml` одного блока |
| `scripts/scaffold-block.py --id <id> --category <cat>` | Создать новый блок из шаблона |

## Связанные концепты

- [[ux-composer]] — использует этот скилл при инжекции блоков на этапах 07a/07b
- [[block-library]] — сама библиотека, которой управляет скилл (200+ блоков)
- [[landing-wireframe]] — этап 07a, где ux-composer подбирает блоки из каталога
- [[landing-compose]] — этап 07b, финальная сборка composed.html с реальными блоками

## Источник

- `skills/block-library-management/SKILL.md`