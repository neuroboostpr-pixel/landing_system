---
type: skill
name: block-library-management
sources: ["skills/block-library-management/SKILL.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses: ["ux-composer", "block-library"]
tags: ["block-library", "scaffold", "validation", "catalog"]
---

# Block Library Management — Управление библиотекой блоков

## Что делает
Предоставляет утилиты для обслуживания общей библиотеки wireframe-блоков: создаёт новые блоки по шаблону, проверяет корректность каталога и метаданных каждого блока.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** агентом `ux-composer` при инъекции блоков в wireframe. Также вызывается вручную разработчиком, когда нужно добавить новый блок в библиотеку или убедиться, что существующие блоки соответствуют схемам.

## Что на вход / на выход

**Вход:**
- Путь к `block-library/catalog.yaml` — для валидации каталога
- Путь к `block-library/<block>/meta.yaml` — для валидации метаданных блока
- Параметры `--id` и `--category` — для создания нового блока

**Выход:**
- Отчёт валидации (exit 0 / ошибки) от `validate-catalog.py` и `validate-meta.py`
- Новый блок-папка со всеми обязательными файлами — от `scaffold-block.py`

**Скрипты:**
| Команда | Назначение |
|---|---|
| `scripts/validate-catalog.py <path>` | Проверить `catalog.yaml` по схеме |
| `scripts/validate-meta.py <path>` | Проверить `meta.yaml` отдельного блока |
| `scripts/scaffold-block.py --id <id> --category <cat>` | Создать новый блок из шаблона |

## Связанные концепты
- [[ux-composer]] — использует библиотеку при инъекции блоков в wireframe.html на этапе 07a
- block-library — сам каталог блоков, который этот скилл обслуживает
- [[wireframe-rendering]] — потребитель блоков на этапе 07a

## Источник
- `skills/block-library-management/SKILL.md`