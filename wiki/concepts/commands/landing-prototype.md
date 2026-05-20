---
type: command
name: landing-prototype
sources: ["commands/landing-prototype.md"]
updated: 2026-05-20
triggers:
  - "импортировать прототип"
  - "загрузить PDF прототипа"
  - "начать этап прототипа"
  - "распарсить prototype.pdf"
stage: "07"
uses:
  - prototype-importer
  - landing-wireframe
  - landing-go
  - gate-check
tags:
  - prototype
  - import
  - stage-07
---

# /landing-prototype — Импорт прототипа лендинга

## Что делает
Импортирует пользовательский прототип (PDF или Markdown) из папки проекта, нормализует его в два машиночитаемых формата (`prototype.md` и `prototype.yaml`) и записывает лог импорта. Это стартовый шаг контентного pipeline — без него нельзя запустить wireframe и дальнейшую сборку.

## Когда вызывать / в каком этапе
Этап **07_ПРОТОТИП**. Вызывается когда прототип (PDF или MD) уже лежит в папке `07_ПРОТОТИП/source/` активного проекта-лендинга. Рекомендуемый способ — через `/landing-go`, который сам диспатчит команду в нужный момент. Можно вызвать вручную, если работаете без оркестратора.

## Что на вход / на выход

**На вход:**
- Текущая папка — проект-лендинг (наличие `00_БРИФ/brief.md` или `.landing-state.yaml`)
- Файл `07_ПРОТОТИП/source/prototype.pdf` **или** `07_ПРОТОТИП/source/prototype.md`

**На выход:**
- `07_ПРОТОТИП/prototype.md` — человекочитаемый нормализованный прототип
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемая структура блоков для wireframe-агента
- `07_ПРОТОТИП/import-log.md` — лог импорта с пометками о допущениях и неточностях

**Дополнительно:**
После генерации артефактов команда запускает валидатор:
```bash
python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
```
Если валидация проходит — выводится summary и предложение запустить `/landing-wireframe`.

## Связанные концепты
- [[prototype-importer]] — агент, выполняющий фактический разбор и нормализацию прототипа
- [[landing-wireframe]] — следующий шаг: строит интерактивный wireframe.html из `prototype.yaml`
- [[landing-go]] — главная команда-оркестратор, автоматически вызывает `/landing-prototype` в нужный момент
- [[gate-check]] — скрипт `scripts/gate-check.sh`, проверяет завершённость этапа перед переходом дальше
- [[prototype-import]] — скилл с логикой парсинга и валидации прототипа

## Источник
- `commands/landing-prototype.md`