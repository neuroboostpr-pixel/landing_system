---
type: command
name: landing-prototype
sources: ["commands/landing-prototype.md"]
updated: 2026-05-26
triggers:
  - "импортировать прототип"
  - "загрузить PDF прототип"
  - "начать этап прототипа"
  - "обработать prototype.pdf"
stage: "07"
uses:
  - prototype-importer
  - landing-wireframe
  - landing-go
tags:
  - prototype
  - import
  - stage-07
---

# /landing-prototype — Импорт прототипа лендинга

## Что делает
Принимает PDF или Markdown-файл с прототипом лендинга от клиента, нормализует его в машиночитаемый формат (`prototype.md` + `prototype.yaml`) и записывает лог импорта. Это первый шаг визуального пайплайна перед созданием wireframe.

## Когда вызывать / в каком этапе
Этап **07_ПРОТОТИП**. Вызывается когда клиент предоставил прототип (PDF или MD) и он уже лежит в папке `07_ПРОТОТИП/source/`. Запускается вручную или автоматически через `/landing-go`. Перед запуском в папке проекта обязан существовать `brief.md` или `.landing-state.yaml`.

## Что на вход / на выход

**На вход:**
- Файл `07_ПРОТОТИП/source/prototype.pdf` или `07_ПРОТОТИП/source/prototype.md` (обязательно)
- Проект-лендинг с заполненным брифом

**На выход:**
- `07_ПРОТОТИП/prototype.md` — нормализованный прототип в Markdown
- `07_ПРОТОТИП/prototype.yaml` — структурированные данные для следующих этапов
- `07_ПРОТОТИП/import-log.md` — лог импорта с деталями обработки

После завершения автоматически запускается валидатор:
```bash
python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
```

## Связанные концепты
- [[prototype-importer]] — агент, который выполняет фактический импорт и нормализацию
- [[landing-wireframe]] — следующий этап: интерактивный wireframe на основе импортированного прототипа
- [[landing-go]] — главная точка входа, которая запускает эту команду автоматически в нужный момент

## Источник
- `commands/landing-prototype.md`