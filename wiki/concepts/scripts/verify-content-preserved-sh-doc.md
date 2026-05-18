---
type: rule
name: verify-content-preserved
sources: ["scripts/verify-content-preserved.sh", "scripts/verify-content-preserved.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition", "premium-07b-checklist"]
tags: ["verification", "bash", "wrapper", "content", "qa"]
---

# verify-content-preserved.sh

## Что делает
Bash-обёртка над Python-скриптом `verify_content_preserved.py`. Проверяет, что текстовое содержимое прототипа (заголовки, подзаголовки, призывы к действию) действительно попало в итоговый `composed.html` — ничего не потерялось при подстановке токенов и сборке блоков.

## Когда вызывать / в каком этапе
Вызывается на этапе **07b (Block Compose)** — после того как `block-composer` сгенерировал `composed.html`. Является частью HARD GATE этапа 07b: если скрипт возвращает ненулевой exit code, этап не считается пройденным и оркестратор не переходит к следующему шагу.

Типичные сценарии запуска:
- автоматически через `landing-orchestrator` после команды `/landing-compose`;
- вручную разработчиком при отладке шаблонов блоков;
- в CI как часть регрессионного теста.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — собранный HTML-файл с подставленными токенами и текстами прототипа;
- `07_ПРОТОТИП/prototype.yaml` — машинная форма прототипа с исходными текстами.

**Выход:**
- `exit 0` — все тексты прототипа обнаружены в `composed.html`; блок считается валидным.
- `exit 1` — найдены пропуски; в stdout/stderr список конкретных строк, которые не были вставлены.

Фактическая логика проверки реализована в `verify_content_preserved.py`; bash-обёртка передаёт аргументы и возвращает его exit code вызывающему процессу.

## Связанные концепты
- [[block-composer]] — агент, генерирующий `composed.html`; его результат проверяет этот скрипт
- [[block-composition]] — скилл этапа 07b, в котором применяется проверка
- [[premium-07b-checklist]] — полный список HARD GATE требований к этапу 07b, куда входит сохранность контента
- [[ux-composer]] — предшествующий агент (07a wireframe), чьи выборы определяют структуру блоков

## Источник
- `scripts/verify-content-preserved.sh`
- `scripts/verify-content-preserved.sh.doc.md`