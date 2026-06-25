---
slug: gen-prototype
type: skill
name: "Генератор прототипа (gen-prototype)"
stage: "07a"
tags: [prototype, parsing, yaml, fidelity, stage-07a]
triggers: [landing-prototype]
inputs: [07-prototip]
outputs: [07-prototip]
gates: [prototype_fidelity]
pre_reqs: [02-materialy-klienta, 07-prototip]
related: [landing-prototype, prototype-importer, prototype-import, landing-compose, 07b-composed, stage-execution-protocol, landing-content]
sources: ["skills/gen-prototype/SKILL.md"]
updated: 2026-06-22
confidence: {triggers: low}
---

# Генератор прототипа (gen-prototype)

## Что делает

Извлекает структуру и тексты из клиентского прототипа (графического или текстового) в типизированный файл `prototype-NN.yaml`. Каждый элемент размечается ролью (`role:`) и группой (`group:`), комментарии клиента разделяются на пожелания (`client_notes`) и инструкции к блокам (`block_instructions`). Ведёт реестр `prototypes-index.md` и проставляет флаг `meta.active: true` ровно на один активный файл. Служит единственным источником истины о структуре и текстах для всего дальнейшего флоу: gen-spec, gen-html, block-composer.

## Когда вызывается

Запускается на этапе 07a — после того как клиент передал прототип (PDF, PNG, DOCX, MD, TXT) в папку `07_ПРОТОТИП/source/`. Обычно инициируется командой `/landing-prototype`. Является обязательным шагом перед генерацией дизайн-системы и composed.html: нельзя закрыть этап 07a без прохождения гейта `prototype_fidelity`.

## Вход → выход

**Вход:** файл прототипа в `07_ПРОТОТИП/source/` — графический (`*.png`, `*.pdf`) или текстовый (`*.docx`, `*.md`, `*.txt`); опционально — комментарии клиента внутри файла или отдельно.

**Выход:**
- `07_ПРОТОТИП/prototype-NN.yaml` — типизированный yaml с полями `meta`, `blocks`, `client_notes`, `block_instructions`, `seo_phrases`.
- `07_ПРОТОТИП/prototypes-index.md` — реестр прототипов с флагом активного и словарём ролей.

## Чем закрывается этап (gates)

- `prototype_fidelity` — скрипт `verify-prototype-fidelity.py` проверяет: покрытие текста из источника ≥ 90%, ноль галлюцинаций (выдуманных элементов), `meta.blocks` совпадает с фактическим числом блоков, ровно один активный yaml в папке. При FAIL этап не закрывается.

## Failure modes

- **Потеря текста при парсинге** — агент усекает длинные заголовки или не вносит таблицы с ценами из DOCX; покрытие падает ниже 90%, гейт возвращает FAIL.
- **Галлюцинации структуры** — агент добавляет блоки, которых нет в прототипе; `no_invented_text` срабатывает.
- **Неверный счётчик блоков** — `meta.blocks` не обновлён после добавления или удаления блока; гейт сигналит расхождение.
- **Два активных yaml** — при создании нового прототипа не снят флаг `active` со старого; гейт падает с «≠1 active».
- **Комментарии клиента попадают в контент** — пожелания записываются в `headline`/`subhead` вместо `client_notes`, что приводит к выдуманному тексту в composed.

## Related

- [[landing-prototype]] — slash-команда, которая вызывает этот скилл
- [[prototype-importer]] — агент-обёртка для выполнения импорта
- [[prototype-import]] — концепт этапа импорта прототипа
- [[07b-composed]] — следующий этап: composed.html строится по данным из yaml
- [[landing-compose]] — скилл генерации composed, потребляет prototype-NN.yaml
- [[landing-content]] — извлекает тексты из prototype.yaml для Gutenberg-блоков
- [[stage-execution-protocol]] — обязательный протокол запуска любого этапа