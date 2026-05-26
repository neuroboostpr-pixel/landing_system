---
slug: prototype-import
type: stage
name: "07 Прототип — импорт источника правды"
stage: "07"
tags: [prototype, import, ux, wireframe, source-of-truth]
triggers: [landing-prototype]
inputs: [07_ПРОТОТИП/source/prototype.pdf, 07_ПРОТОТИП/source/prototype.md]
outputs: [07_ПРОТОТИП/prototype.md, 07_ПРОТОТИП/prototype.yaml, 07_ПРОТОТИП/import-log.md]
gates: [prototype_md_approved]
pre_reqs: []
related: [landing-prototype, ux-composer, wireframe-rendering, landing-compose, block-composition]
sources: ["template/07_ПРОТОТИП/README.md"]
updated: 2026-05-26
confidence: {gates: low, pre_reqs: low}
---

# 07 Прототип — импорт источника правды

## Что делает

Этап принимает исходный прототип от клиента или маркетолога (PDF или Markdown) и нормализует его в два артефакта: человеко-читаемый `prototype.md` и машинно-читаемый `prototype.yaml`. Параллельно агент фиксирует в `import-log.md` всё, что он понял из источника, и отмечает места, где потребовались уточняющие вопросы. Эти файлы становятся источником правды для всех последующих этапов — wireframe, compose и финального билда.

## Когда вызывается

Запускается вручную командой `/landing-prototype` после того как пользователь положил файл `prototype.pdf` или `prototype.md` в папку `07_ПРОТОТИП/source/`. Команда вызывается явно — не через `landing-orchestrator` (интеграция в оркестратор запланирована в PR-D).

## Вход → выход

**Вход:** файл `source/prototype.pdf` или `source/prototype.md` — исходный прототип от клиента или маркетолога.

**Выход:**
- `prototype.md` — нормализованное человеко-читаемое описание структуры лендинга (блоки, тексты, логика).
- `prototype.yaml` — машинно-читаемая версия для `ux-composer`; перегенерируется автоматически при правках в `prototype.md`.
- `import-log.md` — протокол импорта: что агент понял, какие задавал вопросы.

## Чем закрывается этап (gates)

- prototype_md_approved — пользователь проверил и одобрил сгенерированный `prototype.md`; правки внесены напрямую в этот файл, после чего `prototype.yaml` перегенерируется.

## Failure modes

- PDF содержит только изображения без текстового слоя — агент не может извлечь структуру, импорт зависает или даёт пустой результат.
- Прототип слишком абстрактен или неполон — `prototype.yaml` содержит пустые слоты, `ux-composer` падает на следующем этапе.
- Пользователь правит `prototype.yaml` вручную, а не через `prototype.md` — данные расходятся, оркестратор получает рассогласованный вход.
- Файл положен не в `source/`, а в корень `07_ПРОТОТИП/` — агент не находит исходник и завершается ошибкой.
- `import-log.md` не создаётся при сетевых или контекстных ошибках — теряется аудит-след вопросов.

## Related

- [[landing-prototype]] — slash-команда, которая запускает этот этап
- [[ux-composer]] — потребляет `prototype.yaml` на этапе wireframe
- [[wireframe-rendering]] — следующий этап после утверждения прототипа
- [[landing-compose]] — использует нормализованный прототип для сборки composed.html
- [[block-composition]] — логика сборки блоков опирается на структуру из prototype.yaml