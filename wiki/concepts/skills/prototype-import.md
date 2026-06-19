---
slug: prototype-import
type: skill
name: "Импорт прототипа"
stage: "07a"
tags: [prototype, import, parsing, stage-07a]
triggers: [landing-prototype]
inputs: ["07_ПРОТОТИП/source/"]
outputs: ["07_ПРОТОТИП/prototype.md", "07_ПРОТОТИП/prototype.yaml", "07_ПРОТОТИП/import-log.md"]
gates: []
pre_reqs: [02-materialy-klienta]
related: [prototype-importer, landing-prototype, 07-prototip, landing-compose, landing-content]
sources: ["skills/prototype-import/SKILL.md"]
updated: 2026-06-19
confidence: {pre_reqs: low}
---

# Импорт прототипа

## Что делает

Скилл принимает пользовательский прототип в формате PDF или MD, извлекает из него текст (при необходимости — через OCR), нормализует структуру и записывает два артефакта: человекочитаемый `prototype.md` (канонический источник истины) и машинный `prototype.yaml` (для последующих этапов pipeline). Также формирует `import-log.md` с отчётом о точности парсинга. Скилл используется агентом `prototype-importer`, который вызывается командой `/landing-prototype`.

## Когда вызывается

Запускается командой `/landing-prototype` на этапе 07a, когда пользователь положил файл прототипа (`prototype.pdf` или `prototype.md`) в папку `<project>/07_ПРОТОТИП/source/`. Без этого файла скилл не запускается.

## Вход → выход

**Вход:** файл прототипа в `07_ПРОТОТИП/source/` (PDF с текстовым слоем, DOCX или структурированный MD); утверждённые материалы клиента (этап 02).

**Выход:** `prototype.md` — дословный канон структуры без потерь; `prototype.yaml` — машинная схема с полями `project` (slug, niche, source_file) и `blocks[]` (position, type, headline, subhead, cta, slots, items, mobile_notes); `import-log.md` — отчёт о потерях при парсинге (fidelity-gate не пропустит этап при потере >10% текста или выдуманной структуре).

## Failure modes

- **Плохой PDF без текстового слоя** — OCR даёт неточный результат; скилл выдаёт предупреждение в `fidelity-report.md`, этап остаётся незакрытым.
- **Потеря >10% текста прототипа** — hard-gate `prototype_fidelity` блокирует переход к следующему этапу.
- **Выдуманная структура блоков** — если агент добавил блоки, которых нет в источнике, fidelity-gate тоже упадёт.
- **Файл не в `source/`** — скилл не находит входной файл и завершается с ошибкой до старта парсинга.
- **Некорректная YAML-схема** — `validate-prototype.py` вернёт ошибку; `prototype.yaml` не будет создан, pipeline остановится.

## Related

- [[prototype-importer]] — агент, который вызывает этот скилл и оркеструет шаги парсинга
- [[landing-prototype]] — slash-команда, запускающая прогон скилла
- [[07-prototip]] — этап pipeline, частью которого является этот импорт
- [[landing-compose]] — следующий этап: использует `prototype.yaml` для построения composed.html
- [[landing-content]] — также потребляет `prototype.yaml` для извлечения реальных текстов