---
type: agent
name: prototype-importer
sources: ["agents/prototype-importer.md"]
updated: 2026-05-20
triggers:
  - "/landing-prototype"
  - "импортировать прототип"
  - "загрузить prototype.pdf"
  - "распознать прототип"
stage: "07a_prototype"
uses:
  - stage-execution-protocol
  - landing-wireframe
  - validate-prototype
  - md-to-yaml
  - enrich-quiz-funnel
tags: [prototype, import, pdf, yaml, stage-07, quiz-funnel]
---

# Prototype Importer — импорт пользовательского прототипа

## Что делает

Берёт прототип лендинга (PDF или Markdown), извлекает структуру блоков и текстов, нормализует в два файла: `prototype.md` (читаемый) и `prototype.yaml` (машинный). Если в прототипе есть квиз-блоки — автоматически обогащает их в полный Marquiz-фаннел, что даёт +25–40% CR на российском рынке. Если что-то непонятно — агент спрашивает пользователя вместо того, чтобы угадывать.

## Когда вызывать / в каком этапе

Вызывается командой `/landing-prototype` на этапе **07a_prototype**. Активируется только если в `.landing-state.yaml` текущий этап — `07a_prototype`. После завершения передаёт управление этапу `/landing-wireframe`.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/source/prototype.pdf` **или** `source/prototype.md` (один из двух обязателен)

**Выход:**
- `prototype.md` — нормализованный прототип, читаемый человеком
- `prototype.yaml` — машинный формат, валидируется скриптом `validate-prototype.py`
- `import-log.md` — что агент понял, какие вопросы задавал пользователю
- `enrichment-log.md` — отчёт об обогащении квиз-фаннела (создаётся автоматически при наличии квиз-блоков)

**Ключевые ограничения:**
- Если в прототипе нет CTA или других данных — агент пишет пустое поле и фиксирует пропуск в `import-log.md`. Ничего не выдумывает.
- PDF без текстового слоя (сканы) — обрабатываются через OCR-скилл `anthropic-skills:pdf`.

## Связанные концепты

- [[stage-execution-protocol]] — обязательный протокол: проверка gate-check и отображение Mermaid-карты перед любым Write/Edit
- [[landing-wireframe]] — следующий этап после успешного импорта прототипа
- [[landing-prototype]] — slash-команда, запускающая этого агента
- [[enrich-quiz-funnel]] — скрипт обогащения квиз-блоков (шаг 6.5 workflow)
- [[validate-prototype]] — скрипт валидации `prototype.yaml`
- [[md-to-yaml]] — скрипт конвертации `prototype.md` → `prototype.yaml`
- [[photo-curator]] — следующий этап по pipeline (07c), использует тот же `prototype.yaml` для слотов

## Источник

- `agents/prototype-importer.md`