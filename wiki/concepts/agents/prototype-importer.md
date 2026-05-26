---
slug: prototype-importer
type: agent
name: "Импортёр прототипа"
stage: "07a"
tags: [prototype, import, pdf, yaml, normalization, quiz-funnel]
triggers: [landing-prototype]
inputs:
  - "<project>/07_ПРОТОТИП/source/prototype.pdf"
  - "<project>/07_ПРОТОТИП/source/prototype.md"
outputs:
  - "<project>/07_ПРОТОТИП/prototype.md"
  - "<project>/07_ПРОТОТИП/prototype.yaml"
  - "<project>/07_ПРОТОТИП/import-log.md"
  - "<project>/07_ПРОТОТИП/enrichment-log.md"
gates:
  - prototype_md_verified
  - prototype_yaml_valid
pre_reqs: []
related:
  - block-composer
  - landing-orchestrator
sources: ["agents/prototype-importer.md"]
updated: 2026-05-26
confidence:
  triggers: low
  pre_reqs: low
---

# Импортёр прототипа

## Что делает

Агент принимает пользовательский прототип в формате PDF или Markdown из папки `07_ПРОТОТИП/source/`, извлекает структуру блоков и нормализует её в два артефакта: `prototype.md` (человеко-читаемый) и `prototype.yaml` (машино-читаемый). При обнаружении квиз-блоков автоматически расширяет их в полный Marquiz-фаннел (welcome → вопросы → лоадер → скидка → лид-форма → спасибо), что по данным RU-рынка даёт +25–40% CR. Все решения и заданные уточняющие вопросы фиксируются в `import-log.md`.

## Когда вызывается

Вызывается командой `/landing-prototype` вручную или через `landing-orchestrator` на этапе `07a_prototype`. Обязательное условие: `.landing-state.yaml` должен содержать `current_stage == 07a_prototype`; если нет — агент останавливается и сообщает пользователю.

## Вход → выход

**Вход:** файл `source/prototype.pdf` (с текстовым слоем или сканированный — тогда используется OCR через `anthropic-skills:pdf`) либо `source/prototype.md`. Один из файлов обязан присутствовать.

**Выход:** нормализованный `prototype.md` с разметкой блоков по типам (hero / features / quiz / pricing / …), валидированный `prototype.yaml` пригодный для wireframe-рендеринга, `import-log.md` с фиксацией всех неоднозначностей и ответов пользователя, `enrichment-log.md` с отчётом о расширении квиз-фаннела.

## Чем закрывается этап (gates)

- `prototype_md_verified` — пользователь проверил `prototype.md` и подтвердил корректность извлечения блоков
- `prototype_yaml_valid` — `validate-prototype.py` завершился с exit 0

## Failure modes

- **Сканированный PDF без текстового слоя** — `extract-pdf-text.py` возвращает exit 2; агент должен переключиться на OCR через `anthropic-skills:pdf`, но если скилл недоступен — процесс полностью блокируется.
- **Неоднозначный тип блока** — агент обязан спросить у пользователя вместо угадывания; если вопрос пропущен, `prototype.yaml` содержит некорректные типы и ломает wireframe-рендеринг.
- **Пустые CTA или заголовки** — агент записывает `cta: ""` и логирует в `import-log.md`; если этот сигнал игнорируется, downstream блоки генерируются без текста.
- **Провал `validate-prototype.py`** после конвертации — требует ручной правки `prototype.md` и повторного запуска; цикл может зациклиться, если схема валидатора и формат MD расходятся.
- **PreToolUse hook блокирует запись** — хук `enforce_stage_gate.py` физически не даёт писать файлы, если предшествующий этап не закрыт; обойти нельзя, нужно закрыть предшественника.

## Related

- [[block-composer]] — потребитель `prototype.yaml` на этапе 07b wireframe
- [[landing-orchestrator]] — диспетчер, вызывающий агента в рамках pipeline