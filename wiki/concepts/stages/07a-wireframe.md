---
slug: 07a-wireframe
type: stage
name: "07a Wireframe — Интерактивный выбор композиций блоков"
stage: "07a"
tags: [wireframe, ux, preview, block-composition, interactive]
triggers: []
inputs: [07-prototip, candidates.yaml]
outputs: [wireframe.html, candidates.yaml, selections.yaml]
gates: [selections_confirmed]
pre_reqs: [07-prototip, 05-dizayn-sistema]
related: [ux-composer, block-composer, block-composition, landing-wireframe, landing-compose, wireframe-rendering]
sources: ["template/07a_WIREFRAME/README.md"]
updated: 2026-05-26
confidence: {gates: low, triggers: low}
---

# 07a Wireframe — Интерактивный выбор композиций блоков

## Что делает

На этом этапе система генерирует интерактивный HTML-файл `wireframe.html`, в котором для каждого блока прототипа предлагаются 2–3 варианта визуальной композиции из block-library. Пользователь открывает файл в браузере, переключает radio-кнопки между кандидатами, видит desktop и mobile preview в реальном времени, затем подтверждает выбор — файл `selections.yaml` сохраняется на диск. Этот файл становится входом для этапа 07b Compose.

## Когда вызывается

Запускается вручную командой `/landing-wireframe` после того, как этап 07 (prototype-import) завершён и этап 05 (design-system) утверждён. В prototype-first workflow оркестратор (через `/landing-go`) диспатчит этап автоматически после прохождения gate 07.

## Вход → выход

**Вход:** `prototype.md` / `prototype.yaml` из этапа 07-прототип; утверждённая дизайн-система (этап 05); block-library с кандидатами, собранными агентом `ux-composer` в `candidates.yaml`.

**Выход:** `wireframe.html` — интерактивный preview; `candidates.yaml` — перечень 2–3 вариантов на каждый блок; `selections.yaml` — финальный выбор пользователя, подтверждённый кнопкой «Confirm selections».

## Чем закрывается этап (gates)

- `selections_confirmed` — файл `selections.yaml` существует в папке `07a_WIREFRAME/` и содержит выбор для каждого блока прототипа; без него этап 07b не запускается.

## Failure modes

- `wireframe.html` открыт через `file://`, но iframe-preview не рендерится — нужно запустить локальный сервер через `skills/wireframe-rendering/scripts/serve-preview.sh`.
- `candidates.yaml` не сгенерирован или пуст — `ux-composer` не получил данные из prototype или block-library; нужно перезапустить генерацию кандидатов.
- Пользователь нажал «Confirm», но `selections.yaml` не сохранился — браузерные ограничения `file://` на запись; решение: использовать serve-preview.sh.
- Выбраны не все блоки — `selections.yaml` неполный, gate `selections_confirmed` не пройдёт; нужно вернуться в wireframe и выбрать оставшиеся варианты.
- Дизайн-токены не подгружены в wireframe — preview выглядит без брендинга; причина: этап 05 не завершён или `tokens.json` отсутствует.

## Related

- [[ux-composer]] — агент, генерирующий `candidates.yaml` с вариантами блоков
- [[block-composer]] — формирует финальную структуру блоков после выбора
- [[block-composition]] — концепция выбора и комбинирования блоков из library
- [[landing-wireframe]] — slash-команда для запуска этого этапа
- [[landing-compose]] — следующий этап (07b), потребляет `selections.yaml`
- [[wireframe-rendering]] — скилл для локального сервера preview