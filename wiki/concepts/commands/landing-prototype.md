---
type: command
name: landing-prototype
sources: ["commands/landing-prototype.md"]
updated: 2026-05-20
triggers:
  - "импортировать прототип"
  - "загрузить прототип PDF"
  - "разобрать прототип"
  - "начать этап прототипа"
  - "запустить 07 этап"
stage: "07"
uses:
  - prototype-importer
  - landing-wireframe
  - landing-go
  - gate-check
tags: [prototype, import, pdf, yaml, stage-07]
---

# /landing-prototype — Импорт прототипа лендинга

## Что делает

Импортирует пользовательский прототип (PDF или Markdown) из папки проекта, разбирает его структуру и создаёт два нормализованных файла: читаемый `prototype.md` и машинный `prototype.yaml`. Это стартовая точка перед сборкой wireframe.

## Когда вызывать / в каком этапе

**Этап 07_ПРОТОТИП.** Вызывается вручную командой `/landing-prototype` или автоматически через `/landing-go`. Перед запуском необходимо:
- находиться в папке проекта-лендинга (должен быть `00_БРИФ/brief.md` или `.landing-state.yaml`);
- положить `prototype.pdf` или `prototype.md` в папку `07_ПРОТОТИП/source/`.

После выполнения и проверки результата — запускать `/landing-wireframe`.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/source/prototype.pdf` **или** `07_ПРОТОТИП/source/prototype.md` — исходный прототип от клиента или маркетолога.

**Выход:**
- `07_ПРОТОТИП/prototype.md` — человекочитаемая версия прототипа.
- `07_ПРОТОТИП/prototype.yaml` — машинная структура для дальнейших этапов (wireframe, compose).
- `07_ПРОТОТИП/import-log.md` — лог импорта с замечаниями и предположениями.

**Валидация:** после агента автоматически запускается `validate-prototype.py` — если есть ошибки структуры, они будут указаны до продолжения.

## Как работает внутри

1. Проверяет наличие проекта и исходника.
2. Передаёт управление агенту [[prototype-importer]].
3. Запускает валидатор `skills/prototype-import/scripts/validate-prototype.py`.
4. Выводит summary и предлагает `/landing-wireframe`.

Порядок этапов контролируется `landing-orchestrator` и `scripts/gate-check.sh` — пропустить или переставить этапы нельзя.

## Связанные концепты

- [[prototype-importer]] — агент, выполняющий непосредственный разбор PDF/MD и генерацию артефактов
- [[landing-wireframe]] — следующий шаг после одобрения прототипа
- [[landing-go]] — главная точка входа, вызывает этот этап автоматически в правильном порядке
- [[prototype-import]] — скилл с логикой импорта и валидации

## Источник

- `commands/landing-prototype.md`