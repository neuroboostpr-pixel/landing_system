---
slug: visual-curator
type: agent
name: "Visual Curator — оркестратор генерации визуалов"
stage: "07"
tags: [visuals, icons, infographics, orchestrator, stage-07d, codex, image-gen]
triggers: [landing-visuals]
inputs: [07b-composed, 05-dizayn-sistema]
outputs: [07d-visuals]
gates: [design_approved, composed_html_exists]
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [icon-generator, infographic-builder, visual-generation, landing-visuals, landing-compose, 07d-visuals, visual-qa, image-pipeline]
sources: ["agents/visual-curator.md"]
updated: 2026-06-19
---

# Visual Curator — оркестратор генерации визуалов

## Что делает

Управляет конвейером генерации AI-визуалов на этапе 07d/07e: сканирует `composed.html` в поисках слотов иконок и инфографики, диспатчит дочерних агентов `icon-generator` и `infographic-builder`, ведёт кэш по хэшу параметров запроса и по завершении вставляет готовые PNG обратно в `composed.html`. Работает идемпотентно — повторный запуск пропускает уже сгенерированные слоты, если не передан флаг `--force`. Не применяет identity-safe ограничения, поскольку визуалы не содержат людей.

## Когда вызывается

Запускается командой `/landing-visuals` после того, как маркетолог утвердил дизайн-систему (этап 05) и в проекте существует `07b_COMPOSED/composed.html`. Если хотя бы одно из предусловий не выполнено — агент завершается с понятным русским сообщением и не трогает файлы.

## Вход → выход

**Вход:** `07b_COMPOSED/composed.html` с незаполненными placeholders вида `[SLOT: feature-1-icon]`; утверждённый `05_ДИЗАЙН/tokens.json`; `market-profile.md` с нишей проекта; опционально кэш предыдущих прогонов в `.cache/`.

**Выход:** `07d_VISUALS/icons/*.png` и `07d_VISUALS/infographics/*.png`; обновлённый `composed.html` с заменёнными `<img class="lp-icon">` вместо placeholders; `07d_VISUALS/STATE.yaml` с итогами каждой фазы (scan / generate / inject).

## Чем закрывается этап (gates)

- `design_approved` — `stages.05_design.status == approved` в `.landing-state.yaml`; без него агент не стартует
- `composed_html_exists` — файл `07b_COMPOSED/composed.html` присутствует на диске; без него агент не стартует

## Failure modes

- **Gate-fail без внятного сообщения** — агент не сообщил, что именно не утверждено; пользователь не понимает, что делать.
- **Кэш-пропуск при изменении бренда** — если `tokens.json` обновился после предыдущего прогона, хэш не меняется (не включал бренд-параметры) → старые иконки не пересоздаются. Исправляется флагом `--force`.
- **Зависание дочернего агента** — `icon-generator` или `infographic-builder` не вернул результат, `STATE.yaml` зависает в `generating`. Нет автоматического таймаута.
- **Инъекция портит HTML** — `rerender-composed.py` заменяет слоты, но не валидирует структуру тега; возможна поломка атрибутов `<img>` при нестандартном формате placeholder.
- **Переполнение codex-квоты** — при большом числе слотов несколько параллельных вызовов могут превысить лимит; в `STATE.yaml` попадут errors, но прогон не прерывается.

## Related

- [[icon-generator]] — дочерний агент для иконок
- [[infographic-builder]] — дочерний агент для инфографики
- [[visual-generation]] — скилл с инструментами генерации
- [[landing-visuals]] — slash-команда, запускающая visual-curator
- [[07b-composed]] — этап создания composed.html (обязательный пре-рек)
- [[05-dizayn-sistema]] — этап дизайн-системы, поставляет tokens.json
- [[visual-qa]] — следующий этап: проверка качества сгенерированных визуалов
- [[image-pipeline]] — стандарт обработки каждого визуального слота (D1)