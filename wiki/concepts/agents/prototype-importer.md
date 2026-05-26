---
type: agent
name: prototype-importer
sources: ["agents/prototype-importer.md"]
updated: 2026-05-26
triggers: []
stage: "07a"
uses: ["landing-prototype", "landing-wireframe", "landing-orchestrator", "stage-execution-protocol"]
tags: ["prototype", "import", "stage-07a", "pdf", "yaml"]
---

# Prototype Importer — Агент импорта прототипа

## Что делает

Берёт PDF или Markdown-прототип лендинга от клиента и превращает его в два структурированных файла: читаемый `prototype.md` и машинный `prototype.yaml`. Если в прототипе есть квиз-блоки — автоматически разворачивает их в полный Marquiz-фаннел (+25–40% CR).

## Когда вызывать / в каком этапе

Активируется на этапе **07a (Прототип)**. Запускается командой `/landing-prototype` после того, как клиент положил `prototype.pdf` или `prototype.md` в папку `<project>/07_ПРОТОТИП/source/`. Требует, чтобы `.landing-state.yaml` показывал `current_stage == 07a_prototype`.

Перед началом работы агент обязательно:
1. Проверяет `.landing-state.yaml` и рисует Mermaid-карту pipeline.
2. Запускает `gate-check.sh` — при ошибке останавливается.
3. Создаёт TodoWrite со всеми оставшимися этапами.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/source/prototype.pdf` — сканированный или текстовый PDF
- или `<project>/07_ПРОТОТИП/source/prototype.md` — уже текстовый прототип

**Выход:**
- `prototype.md` — человекочитаемая нормализованная структура блоков
- `prototype.yaml` — машинный формат (валидируется `validate-prototype.py`)
- `import-log.md` — что агент понял, что уточнял, что оставил пустым
- `enrichment-log.md` — отчёт о расширении квиз-фаннела (если были quiz-блоки)

**Ключевое правило:** агент **не выдумывает** недостающие данные. Если CTA не найден — пишет `cta: ""` и фиксирует это в `import-log.md`, затем спрашивает пользователя.

## Связанные концепты

- [[landing-prototype]] — slash-команда, которая вызывает этот агент
- [[landing-wireframe]] — следующий этап после успешного импорта
- [[stage-execution-protocol]] — обязательный протокол предусловий для всех этапов
- [[landing-orchestrator]] — оркестратор, который управляет последовательностью этапов

## Источник

- `agents/prototype-importer.md`