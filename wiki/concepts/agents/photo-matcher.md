---
slug: photo-matcher
type: agent
name: "Photo Matcher — ранжировщик фото по слотам"
stage: "07c"
tags: [photo, ranking, codex, identity-safe, helper-agent]
triggers: []
inputs: [07c-photos]
outputs: [07c-photos]
gates: []
pre_reqs: [photo-classifier, 07-prototip]
related: [photo-curator, photo-curation, 07c-photos, photo-classifier, photo-preview-board]
sources: ["agents/photo-matcher.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Photo Matcher — ранжировщик фото по слотам

## Что делает

Вспомогательный агент, запускаемый `photo-curator` на этапе 07c. Получает список фото-слотов из `prototype.yaml` и каталог загруженных фото (`catalog.yaml`), после чего через codex ранжирует кандидатов для каждого слота. Результат — `selections.draft.yaml` с тремя кандидатами на слот, флагом `ai_fallback_needed` для пустых слотов и флагом `required_user_approval` для identity-safe слотов (testimonial/expert/team).

## Когда вызывается

Не вызывается напрямую пользователем. Диспетчеризуется агентом `photo-curator` в рамках команды `/landing-photos`. Запускается однократно (single-shot) после того, как `photo-classifier` заполнил `catalog.yaml`.

## Вход → выход

**Вход:** директория проекта, в которой уже присутствуют `07c_PHOTOS/catalog.yaml` (выход photo-classifier) и `07_ПРОТОТИП/prototype.yaml` со слотами типа `photo`.

**Выход:** `<project>/07c_PHOTOS/selections.draft.yaml` — YAML со списком слотов; каждый содержит до трёх кандидатов, флаг `ai_fallback_needed: true` если кандидатов нет, и `required_user_approval: true` для слотов с лицами людей.

## Чем закрывается этап (gates)

Этап агент не закрывает самостоятельно — это helper без ownership над стадией. Результаты передаются в `photo-curator`, который ведёт stage 07c.

## Failure modes

- **Invalid YAML от codex** — агент делает две повторные попытки; при третьей неудаче прерывается и просит пользователя проверить лог codex вручную.
- **Пустой список кандидатов для слота** — штатная ситуация: выставляется `ai_fallback_needed: true`, не является ошибкой.
- **Прямой вызов пользователем** — агент не рассчитан на прямой запуск; отсутствие стейта этапа приведёт к падению на pre-flight.
- **Отсутствие `catalog.yaml`** — скрипт `codex-match.sh` упадёт с ошибкой пути; нужно сначала выполнить `/landing-photos` (шаг photo-classifier).
- **Отсутствие identity-safe флага** — если codex вернул неправильную структуру, downstream validator (`selections-validator.py`) заблокирует отображение слота в `photo-board.html`.

## Related

- [[photo-curator]] — родительский агент, диспетчеризует photo-matcher
- [[photo-curation]] — скилл с логикой всего фото-пайплайна, содержит `codex-match.sh`
- [[photo-classifier]] — предшественник: создаёт `catalog.yaml`, который читает этот агент
- [[07c-photos]] — этап, в рамках которого работает агент
- [[photo-preview-board]] — downstream: использует `selections.draft.yaml` для UI preview