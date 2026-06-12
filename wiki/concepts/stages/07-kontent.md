---
slug: content-writer-stage
type: stage
name: "07 — Написание контента"
stage: "07"
tags: [content, copywriting, text, auto]
triggers: []
inputs: [prototype-import]
outputs: [final-copy.md]
gates: [final_copy_present]
pre_reqs: [prototype-import]
related: [content-writer, landing-content, block-composer, prototype-importer]
sources: ["template/07_КОНТЕНТ/README.md"]
updated: 2026-05-26
confidence: {gates: low, triggers: low}
---

# 07 — Написание контента

## Что делает

На этом этапе агент `content-writer` формирует финальный текст лендинга: заголовки, подзаголовки, буллеты, CTA и все прочие копирайт-единицы. Основа — структурированный прототип из предыдущего этапа (`prototype.yaml`). Результат — файл `final-copy.md`, разбитый на H2-секции, где каждая секция соответствует одному блоку лендинга.

## Когда вызывается

Запускается автоматически оркестратором (`landing-orchestrator`) после того, как этап импорта прототипа (`prototype-import`) завершён и `prototype.yaml` готов. Ручной запуск — через `/landing-content`.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.yaml` — структурированное описание блоков лендинга с исходным текстом и намерениями.

**Выход:** `07_КОНТЕНТ/final-copy.md` — финальный текст по секциям, готовый к подстановке в `composed.html` на этапе 07b.

## Чем закрывается этап (gates)

- `final_copy_present` — файл `final-copy.md` существует и содержит не менее одной H2-секции с текстом.

## Failure modes

- `prototype.yaml` отсутствует или пуст — агент не может извлечь структуру, этап зависает.
- Блоки в прототипе не имеют текстового содержимого — `final-copy.md` генерируется с пустыми плейсхолдерами вместо реального копирайта.
- Несовпадение количества секций в `prototype.yaml` и `final-copy.md` — блок-композер позднее не найдёт контент для части блоков.
- Файл сохранён не в той папке (вне `07_КОНТЕНТ/`) — гейт `final_copy_present` не срабатывает и этап не закрывается.
- Кодировка или синтаксис Markdown нарушены — downstream-агенты (`block-composer`) читают контент некорректно.

## Related

- [[content-writer]] — агент, непосредственно выполняющий этот этап
- [[landing-content]] — slash-команда для ручного запуска этапа
- [[prototype-import]] — предшествующий этап, поставляет `prototype.yaml`
- [[block-composer]] — потребитель `final-copy.md` на этапе 07b