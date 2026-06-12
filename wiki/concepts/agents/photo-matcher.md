---
slug: photo-matcher
type: agent
name: "Агент сопоставления фото со слотами"
stage: "07c"
tags: [photos, matching, codex, identity-safe, helper-agent]
triggers: []
inputs: ["07c_PHOTOS/catalog.yaml", "07_ПРОТОТИП/prototype.yaml", "07a_WIREFRAME/selections.yaml"]
outputs: ["07c_PHOTOS/selections.draft.yaml"]
gates: []
pre_reqs: [photo-curator]
related: [photo-curator]
sources: ["agents/photo-matcher.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# Агент сопоставления фото со слотами

## Что делает

Ранжирует клиентские фото как кандидатов для каждого фото-слота из wireframe. Агент работает в режиме single-shot: читает полный `catalog.yaml` и список активных слотов, затем через codex возвращает топ-3 кандидата на каждый слот. Для слотов, где клиентских фото недостаточно, выставляет флаг `ai_fallback_needed`. Для identity-safe слотов (testimonial, expert, team) устанавливает `required_user_approval: true` согласно правилам `IDENTITY_SAFE.md`.

## Когда вызывается

Вызывается исключительно родительским агентом `photo-curator` на этапе 07c. Не предназначен для прямого вызова пользователем. Stage Execution Protocol контролируется родителем.

## Вход → выход

**Вход:** директория проекта; `07c_PHOTOS/catalog.yaml` с перечнем загруженных фото; `07_ПРОТОТИП/prototype.yaml` со списком слотов; `07a_WIREFRAME/selections.yaml` с выбранными вариантами блоков (фильтрует только актуальные photo-слоты).

**Выход:** `07c_PHOTOS/selections.draft.yaml` — для каждого слота: топ-3 кандидата, флаг `ai_fallback_needed` (если кандидатов нет), флаг `required_user_approval` (для identity-safe слотов).

## Failure modes

- **Невалидный YAML от codex** — агент делает два повторных запроса; после третьего неудачного — прерывает работу и просит пользователя проверить лог codex вручную.
- **Пустой список кандидатов для слота** — штатная ситуация; выставляется `ai_fallback_needed: true`, не является ошибкой.
- **Отсутствие `selections.yaml` из wireframe** — слоты невозможно отфильтровать, агент не запустится корректно.
- **Нарушение identity-safe** — если `required_user_approval` не проставлен в ответе codex, валидатор (`selections-validator.py`) поймает это при последующей проверке.
- **Прямой вызов без родителя** — протокол этапа не выполнен, состояние проекта не проверено.

## Related

- [[photo-curator]] — родительский агент, который диспатчит photo-matcher и владеет этапом 07c целиком