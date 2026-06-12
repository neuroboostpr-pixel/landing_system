---
slug: landing-wireframe
type: command
name: "/landing-wireframe — Интерактивный Wireframe"
stage: "07a"
tags: [wireframe, ux, prototype, block-library, interactive]
triggers: [landing-wireframe]
inputs: [07_ПРОТОТИП/prototype.yaml]
outputs: [07a_WIREFRAME/wireframe.html, 07a_WIREFRAME/candidates.yaml, 07a_WIREFRAME/selections.yaml]
pre_reqs: [landing-prototype, prototype-import]
related: [ux-composer, wireframe-rendering, landing-compose, landing-go, block-composition, landing-orchestrator]
sources: ["commands/landing-wireframe.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# /landing-wireframe — Интерактивный Wireframe

## Что делает

Запускает этап 07a — генерацию интерактивного wireframe-превью. Для каждого блока из `prototype.yaml` агент `ux-composer` подбирает 2–3 кандидата из библиотеки блоков и рендерит `wireframe.html` с радио-кнопками для выбора. Пользователь открывает файл в браузере, выбирает понравившиеся варианты и нажимает «Confirm» — браузер скачивает `selections.yaml`. Этот файл нужно положить в папку `07a_WIREFRAME/` вручную. После одобрения цепочка продолжается командой `/landing-compose`.

## Когда вызывается

Вызывается вручную командой `/landing-wireframe` либо автоматически оркестратором через `/landing-go`. Предварительное условие — наличие валидного `07_ПРОТОТИП/prototype.yaml`, сгенерированного командой `/landing-prototype`.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.yaml` — распарсенный прототип со списком блоков и их параметрами.

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный HTML с вариантами блоков и радио-кнопками;
- `07a_WIREFRAME/candidates.yaml` — машино-читаемый список кандидатов по каждому блоку;
- `07a_WIREFRAME/selections.yaml` — файл выбора пользователя (создаётся через кнопку Confirm в браузере, затем кладётся вручную).

## Failure modes

- `prototype.yaml` отсутствует или невалиден — команда падает на старте; нужно перезапустить `/landing-prototype`.
- Кандидаты не найдены для какого-то блока — `ux-composer` не может заполнить секцию wireframe; проверь соответствие типов блоков каталогу `block-library/`.
- `selections.yaml` не положен в папку — `/landing-compose` не стартует; пользователь должен вручную переместить скачанный файл.
- Пользователь нажал Confirm, но выбрал не все блоки — `selections.yaml` будет неполным, `block-composer` на этапе 07b может упасть с ошибкой пропущенного слота.
- Файл `wireframe.html` не открывается в браузере локально — проблема прав или кодировки пути; открывай через `file://` или локальный сервер.

## Related

- [[ux-composer]] — агент, выполняющий подбор кандидатов и рендер wireframe.html
- [[wireframe-rendering]] — концепт процесса рендера wireframe
- [[landing-compose]] — следующий этап после одобрения wireframe (07b)
- [[landing-go]] — рекомендуемая точка входа, автоматически диспатчит 07a
- [[block-composition]] — процесс сборки блоков, использующий selections.yaml
- [[landing-orchestrator]] — оркестратор, интегрирующий команду в общий pipeline