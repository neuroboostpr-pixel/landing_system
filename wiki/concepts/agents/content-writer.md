---
slug: content-writer
type: agent
name: "Контент-райтер"
stage: "07"
tags: [content, extraction, prototype, stage-07, gutenberg]
triggers: [landing-content]
inputs:
  - 07_ПРОТОТИП/prototype.yaml
  - 07_ПРОТОТИП/prototype.md
  - 01a_АНАЛИЗ_НИШИ/positioning.md
  - 01a_АНАЛИЗ_НИШИ/competitors.yaml
outputs:
  - 07_КОНТЕНТ/content.md
  - 07_КОНТЕНТ/extraction-log.md
gates: [content_md_exists, content_no_lorem, content_sections_match, extraction_log_passed]
pre_reqs: [landing-prototype]
related:
  - landing-content
  - prototype-importer
  - landing-compose
  - block-composer
  - stage-execution-protocol
sources: ["agents/content-writer.md"]
updated: 2026-06-19
---

# Контент-райтер

## Что делает

Извлекает реальные тексты из прототипа лендинга (файл `prototype.md` как канон, `prototype.yaml` как машинный разбор) и структурирует их по секциям и блокам Gutenberg. Агент строго следует правилу «не выдумывать»: весь контент берётся только из файлов прототипа. На выходе — `content.md` с иерархией H2/H3 по секциям/блокам и `extraction-log.md` с логом валидации. Контент без изменений передаётся в следующий этап — `landing-compose`, где агент рисует макет по прототипу и референсу.

## Когда вызывается

Вызывается командой `/landing-content` при активном этапе `07_content` в `.landing-state.yaml`. Перед запуском обязателен закрытый gate предшественника (`landing-prototype`): агент проверяет наличие `prototype.md`, иначе немедленно останавливается с инструкцией пройти импорт прототипа.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.md` (канон, обязателен) + `07_ПРОТОТИП/prototype.yaml` (опционально, машинный разбор). Опционально: `01a_АНАЛИЗ_НИШИ/positioning.md` и `competitors.yaml` для корректировки тональности.

**Выход:** `07_КОНТЕНТ/content.md` — структурированный текстовый контент по секциям прототипа (H2 = секция, H3 = блок, тело = реальный текст). `07_КОНТЕНТ/extraction-log.md` — лог с количеством извлечённых блоков, предупреждениями и результатом валидации.

## Failure modes

- **Изобретение контента** — агент заполняет блоки шаблонными фразами вместо реального текста. Gate `content_no_lorem` блокирует approve.
- **Расхождение количества секций** — если `content.md` содержит меньше секций, чем `prototype.yaml`, gate `content_sections_match` не пройдёт.
- **Потеря блоков при yaml-парсинге** — `prototype.yaml` может терять данные относительно `.md`; агент обязан fallback-ить к `prototype.md` и логировать это предупреждением.
- **Запуск не на том этапе** — если `current_stage != 07_content` в `.landing-state.yaml`, агент обязан остановиться. Harness-хук `enforce_stage_gate.py` физически блокирует Write/Edit.
- **Отсутствие `prototype.md`** — без этого файла агент падает сразу, указывая запустить `/landing-prototype`.

## Related

- [[landing-content]] — slash-команда, которая запускает этого агента
- [[prototype-importer]] — предшественник: импортирует прототип и создаёт prototype.md/yaml
- [[landing-compose]] — следующий этап: использует content.md для сборки composed.html
- [[block-composer]] — рисует макет после того, как контент-райтер передал тексты
- [[stage-execution-protocol]] — обязательный протокол преполётной проверки для всех агентов