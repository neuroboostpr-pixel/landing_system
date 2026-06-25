---
slug: prototype-importer
type: agent
name: "Импортёр прототипа"
stage: "07a"
tags: [prototype, import, stage-07a, fidelity, docx, pdf, quiz-funnel]
triggers: [landing-prototype, landing-go]
inputs:
  - 07_ПРОТОТИП/source/prototype.pdf
  - 07_ПРОТОТИП/source/prototype.docx
  - 07_ПРОТОТИП/source/prototype.md
outputs:
  - 07_ПРОТОТИП/prototype.md
  - 07_ПРОТОТИП/prototype.yaml
  - 07_ПРОТОТИП/import-log.md
  - 07_ПРОТОТИП/enrichment-log.md
gates: [prototype_fidelity]
pre_reqs: [06-stek]
related:
  - landing-prototype
  - prototype-import
  - 07-prototip
  - landing-go
  - landing-compose
  - 07b-composed
sources: ["agents/prototype-importer.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Импортёр прототипа

## Что делает

Агент принимает пользовательский прототип из папки `07_ПРОТОТИП/source/` (PDF, DOCX или Markdown), извлекает из него весь текст дословно — включая таблицы с ценами и тарифами — и структурирует результат в `prototype.md` (человекочитаемый) и `prototype.yaml` (машиночитаемый). При обнаружении квиз-блоков автоматически расширяет их в полный Marquiz-фаннел (welcome → вопросы → лоадер → скидка → лид-форма → спасибо). Фиксирует вопросы к клиенту в `import-log.md` и отчёт обогащения в `enrichment-log.md`. Строго соблюдает принцип «без потерь и без выдумки»: из прототипа берётся только структура и тексты, визуальный стиль игнорируется полностью.

## Когда вызывается

Запускается командой `/landing-prototype` или оркестратором при выполнении `/landing-go`, когда `.landing-state.yaml` фиксирует `current_stage == 07a_prototype`. Предшественник — закрытый этап 06 (стек). Если этап не активен, агент останавливается без записи файлов.

## Вход → выход

**Вход:** один файл прототипа в `<project>/07_ПРОТОТИП/source/` (`prototype.pdf`, `prototype.docx` или `prototype.md`); закрытый предыдущий этап в `.landing-state.yaml`.

**Выход:** `prototype.md` — дословная нормализация источника; `prototype.yaml` — машиночитаемый разбор блоков; `import-log.md` — зафиксированные уточнения; `enrichment-log.md` — отчёт о квиз-фаннеле. После прохождения hard gate этап переводится в статус `approved`.

## Чем закрывается этап (gates)

- `prototype_fidelity` — покрытие ≥ 90% текста источника в `prototype.yaml` без галлюцинаций; проверяется скриптом `verify-prototype-fidelity.py`; при провале агент обязан доработать `prototype.yaml` перед закрытием

## Failure modes

- Сканированный PDF без текстового слоя — fallback на OCR через `anthropic-skills:pdf`; без него агент падает с exit code 2
- Таблицы цен в DOCX теряются при PDF-конвертации — для `.docx` обязателен `extract-docx-text.py`; иначе тарифы пропадут
- Выдуманные пункты меню, CTA или тарифные опции — hard gate `prototype_fidelity` упадёт; нужна ручная правка и перезапуск
- Покрытие < 90% после конвертации `md-to-yaml.py` — цикл доработки, этап не закрыть до PASS
- Агент вызван при неверном `current_stage` — немедленный STOP, пользователь получает сообщение с объяснением

## Related

- [[landing-prototype]] — slash-команда, которая диспатчит этого агента
- [[prototype-import]] — скилл с библиотекой скриптов (extract-pdf, extract-docx, md-to-yaml, validate, enrich-quiz)
- [[07-prototip]] — этап pipeline, которому принадлежит агент
- [[landing-go]] — оркестратор, который автоматически вызывает агента в нужный момент
- [[landing-compose]] — следующий этап: рисует `composed.html` по `prototype.yaml` и референсу
- [[07b-composed]] — артефакт следующего этапа, зависящий от `prototype.yaml`