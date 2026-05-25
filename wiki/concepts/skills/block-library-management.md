---
type: skill
name: block-library-management
sources: ["skills/block-library-management/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["ux-composer", "block-library"]
tags: ["block-library", "scaffolding", "validation", "catalog"]
---

# Block Library Management — Управление библиотекой блоков

## Что делает
Скилл предоставляет набор утилит для обслуживания общей библиотеки wireframe-блоков: создаёт новые блоки по шаблону, проверяет корректность каталога и метаданных каждого блока.

## Когда вызывать / в каком этапе
Используется агентом `ux-composer` во время инъекции блоков в wireframe (этап 07a). Вызывается напрямую разработчиком при добавлении нового блока в `block-library/` или при необходимости проверить целостность каталога после изменений.

## Что на вход / на выход

**Вход:**
- Путь к `catalog.yaml` или к папке блока с `meta.yaml` — для валидации.
- Идентификатор нового блока (`--id`) и категория (`--category`) — для скаффолдинга.

**Выход:**
- `scripts/validate-catalog.py` — вывод ошибок валидации `catalog.yaml` или сообщение об успехе.
- `scripts/validate-meta.py` — вывод ошибок схемы `meta.yaml` конкретного блока или сообщение об успехе.
- `scripts/scaffold-block.py` — новая папка блока в `block-library/` с заполненным шаблоном `meta.yaml` и базовой структурой файлов.

## Связанные концепты
- [[ux-composer]] — использует скилл при инъекции блоков; читает `meta.yaml` каждого блока для подбора вариантов
- [[block-library]] — целевой артефакт управления; все 200+ блоков хранятся в этой директории

## Источник
- `skills/block-library-management/SKILL.md`