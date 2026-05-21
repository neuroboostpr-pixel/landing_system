---
type: agent
name: prototype-importer
sources: ["agents/prototype-importer.md"]
updated: 2026-05-20
triggers: ["импортировать прототип", "загрузить PDF прототип", "/landing-prototype", "этап 07 прототип"]
stage: "07a"
uses: ["landing-orchestrator", "stage-execution-protocol", "wireframe-rendering", "ux-composer", "landing-prototype"]
tags: ["prototype", "import", "pdf", "yaml", "stage-07"]
---

# prototype-importer — Импорт прототипа

## Что делает

Принимает файл прототипа от пользователя (PDF или Markdown), извлекает структуру всех блоков лендинга и сохраняет два нормализованных файла: читаемый `prototype.md` и машинный `prototype.yaml`. Если прототип содержит квиз-блоки — автоматически расширяет их в полноценный Marquiz-фаннел (+25–40% CR).

## Когда вызывать / в каком этапе

Запускается командой `/landing-prototype` на этапе **07a (Прототип)**. Перед запуском агент проверяет, что `.landing-state.yaml` показывает `current_stage == 07a_prototype`. Если предшествующие этапы не закрыты — останавливается с сообщением. После успешного импорта пользователь проверяет `prototype.md` и запускает `/landing-wireframe`.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/source/prototype.pdf` или `source/prototype.md` — один из двух обязателен

**Выход:**
- `prototype.md` — нормализованный human-readable прототип
- `prototype.yaml` — машинный формат (проходит валидацию через `validate-prototype.py`)
- `import-log.md` — что агент понял, какие вопросы задавал пользователю
- `enrichment-log.md` — отчёт об обогащении квиз-фаннела (если были quiz-блоки)

## Ключевые ограничения

- **Не выдумывает**: если в прототипе нет CTA или типа блока — записывает пустое значение и фиксирует пробел в `import-log.md`.
- **Спрашивает при неясности**: ниша, тип неопознанного блока, «Калькулятор — это quiz или pricing?» — всё через явные вопросы пользователю.
- **Harness-гейт**: хук `enforce_stage_gate.py` физически блокирует запись файлов, пока не закрыты предшественники. Обходить не нужно — нужно закрыть предыдущий этап.

## Workflow кратко

1. Находит исходник в `source/`
2. PDF → извлекает текст (`extract-pdf-text.py`), при сканированном PDF — OCR через `anthropic-skills:pdf`
3. Собирает `prototype.md` по формату (block type, headline, cta, слоты)
4. Задаёт уточняющие вопросы при неясностях
5. `md-to-yaml.py` → `prototype.yaml`
6. `enrich-quiz-funnel.py` — расширяет квиз-блоки
7. `validate-prototype.py` — проверяет YAML; при ошибке — исправляет и повторяет

## Связанные концепты

- [[landing-prototype]] — slash-команда, которая вызывает этого агента
- [[ux-composer]] — следующий агент: берёт `prototype.yaml` и строит `wireframe.html`
- [[stage-execution-protocol]] — обязательный протокол перед любым write-действием
- [[prototype-import]] — скилл с набором скриптов (`md-to-yaml.py`, `validate-prototype.py`, `extract-pdf-text.py`)
- [[wireframe-rendering]] — скилл, включающий `enrich-quiz-funnel.py`
- [[landing-wireframe]] — следующая команда после успешного импорта

## Источник

- `agents/prototype-importer.md`