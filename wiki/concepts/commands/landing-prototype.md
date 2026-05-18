---
type: command
name: landing-prototype
sources: ["commands/landing-prototype.md"]
updated: 2026-05-15
triggers:
  - "импортировать прототип"
  - "загрузить прототип PDF"
  - "запустить этап прототипа"
  - "обработать prototype.pdf"
stage: "07"
uses:
  - prototype-importer
  - landing-wireframe
tags:
  - prototype
  - stage-07
  - import
---

# /landing-prototype — Импорт прототипа

## Что делает

Берёт файл прототипа (`prototype.pdf` или `prototype.md`), который маркетолог положил в папку проекта, и преобразует его в два стандартных формата: человекочитаемый `prototype.md` и машиночитаемый `prototype.yaml`. После этого система готова к построению wireframe.

## Когда вызывать / в каком этапе

Этап **07 — Прототип**. Вызывается вручную командой `/landing-prototype`, когда:
- вы находитесь внутри папки проекта-лендинга (есть `00_БРИФ/brief.md` или `.landing-state.yaml`),
- в папке `07_ПРОТОТИП/source/` лежит файл `prototype.pdf` или `prototype.md`.

После завершения этапа — запускай `/landing-wireframe`.

> **Внимание (PR-A scope):** команда пока не интегрирована с `gate-check.sh` и `.landing-state.yaml`. Порядок этапов контролирует сам пользователь вручную. Интеграция в оркестратор — задача PR-D.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/source/prototype.pdf` **или** `07_ПРОТОТИП/source/prototype.md`

**Выход:**
- `07_ПРОТОТИП/prototype.md` — нормализованный прототип для человека
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемая структура блоков
- `07_ПРОТОТИП/import-log.md` — лог импорта с пометками об уточнениях

**Встроенная проверка:**
После работы агента запускается валидатор:
```bash
python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
```
Команда сообщает итоговый summary и предлагает запустить следующий шаг.

## Связанные концепты

- [[prototype-importer]] — агент, который выполняет парсинг и нормализацию прототипа, задаёт уточняющие вопросы при неоднозначностях
- [[landing-wireframe]] — следующая команда: строит интерактивный wireframe.html на основе `prototype.yaml`
- [[landing-go]] — единая точка входа PR-D, которая в будущем интегрирует эту команду в автоматический оркестратор

## Источник

- `commands/landing-prototype.md`