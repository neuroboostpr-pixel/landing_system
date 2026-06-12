---
slug: prototype-import
type: skill
name: "Импорт прототипа"
stage: "07"
tags: [prototype, import, pdf, yaml, parse, ocr]
triggers: [landing-prototype]
inputs:
  - 07_ПРОТОТИП/source/prototype.pdf
  - 07_ПРОТОТИП/source/prototype.md
outputs:
  - 07_ПРОТОТИП/prototype.md
  - 07_ПРОТОТИП/prototype.yaml
  - 07_ПРОТОТИП/import-log.md
pre_reqs: [client-assets-collection]
related:
  - prototype-importer
  - landing-orchestrator
  - block-composer
  - ux-composer
sources: ["skills/prototype-import/SKILL.md"]
updated: 2026-05-26
confidence: {pre_reqs: low}
---

# Импорт прототипа

## Что делает

Скилл принимает пользовательский прототип в формате PDF или Markdown и преобразует его в два машино-читаемых артефакта: `prototype.md` (читаемый документ со структурой блоков) и `prototype.yaml` (формализованная схема для дальнейшего использования оркестратором и блок-композером). Параллельно ведётся `import-log.md` с протоколом разбора. При PDF-входе используется OCR-fallback через `anthropic-skills:pdf`.

## Когда вызывается

Запускается командой `/landing-prototype`, когда пользователь положил файл прототипа (`prototype.pdf` или `prototype.md`) в папку `<project>/07_ПРОТОТИП/source/`. Вызывается агентом `prototype-importer`. Является обязательным первым шагом цепочки PR-A (Прототип → Wireframe → Compose).

## Вход → выход

**Вход:** файл прототипа в `07_ПРОТОТИП/source/` — либо `prototype.pdf` (текст или сканированный), либо структурированный `prototype.md`.

**Выход:** нормализованные `prototype.md` и `prototype.yaml` в папке `07_ПРОТОТИП/`, а также `import-log.md` с деталями импорта. YAML валидируется скриптом `validate-prototype.py` на соответствие схеме (поля `project`, `blocks[]` с позицией, типом, заголовком, CTA, слотами).

## Failure modes

- PDF содержит только растровые изображения без текстового слоя — OCR-fallback может дать низкое качество или пропустить мелкий текст.
- Пользовательский MD не следует ожидаемой структуре — `md-to-yaml.py` не сможет однозначно распарсить секции; import-log покажет предупреждения, но схема окажется неполной.
- Дублирующиеся значения `position` у блоков — `validate-prototype.py` упадёт с ошибкой схемы; прогон не завершится до ручного исправления.
- Файл не найден в `source/` — скилл сразу завершается с ошибкой, не создавая выходных файлов.
- Неизвестный тип блока (не входит в перечень `hero|features|...`) — валидатор отклонит YAML; нужно либо скорректировать исходник, либо расширить enum в схеме.

## Related

- [[prototype-importer]] — агент, который непосредственно исполняет скрипты этого скилла
- [[landing-orchestrator]] — вызывает prototype-import как первый этап в PR-D workflow
- [[block-composer]] — потребляет `prototype.yaml` на этапе 07b для сборки wireframe и composed.html
- [[ux-composer]] — использует нормализованные данные блоков при генерации wireframe-вариантов