---
slug: stage-06-stack
type: stage
name: "Стек технологий"
stage: "06"
tags: [stack, auto, wordpress, gutenberg]
triggers: [landing-orchestrator]
inputs: [05_ДИЗАЙН/design-system.md]
outputs: [06_СТЕК/design-stack.yaml]
gates: [stack_confirmed]
pre_reqs: [design-system-generator]
related: [stack-planner, landing-build, landing-orchestrator, wp-builder, wp-gutenberg-block-builder]
sources: ["template/06_СТЕК/README.md"]
updated: 2026-05-26
confidence: {inputs: low, gates: low, pre_reqs: low}
---

# Стек технологий

## Что делает

Этап 06 автоматически формирует технический стек для будущего лендинга. Агент `stack-planner` на основе данных из предыдущих этапов (ниша, бренд, дизайн-система) выбирает набор технологий: WordPress, Gutenberg, Lazy Blocks, аналитику и интеграции. Результат фиксируется в `design-stack.yaml` и задаёт параметры для всех последующих этапов сборки.

## Когда вызывается

Вызывается автоматически оркестратором (`landing-orchestrator`) после подтверждения дизайн-системы (этап 05). Ручного запуска не требует — выполняется без участия пользователя.

## Вход → выход

**Вход:** утверждённые артефакты дизайн-системы из `05_ДИЗАЙН/` (токены, типографика, цвета).

**Выход:** `06_СТЕК/design-stack.yaml` — декларация технического стека с выбранными платформой, плагинами и режимом сборки (`standard` / `cinematic`).

## Чем закрывается этап (gates)

- stack_confirmed — `design-stack.yaml` создан и содержит все обязательные поля (platform, mode, block_builder)

## Failure modes

- `design-stack.yaml` не создан — агент упал без вывода артефакта; оркестратор должен предложить повтор.
- Неверный `mode` — указан невалидный режим сборки; этап 08 не сможет корректно выбрать шаблон.
- Зависимость от несуществующих плагинов — стек ссылается на версию плагина, недоступную на Бегете.
- Пропуск этапа — если оркестратор ошибочно помечает этап как `n/a`, этап 08 запускается без декларации стека.
- Конфликт mode и дизайн-токенов — `cinematic` выбран при минималистичном бренде, что даёт визуальное расхождение.

## Related

- [[stack-planner]] — агент, выполняющий этот этап
- [[landing-build]] — потребляет `design-stack.yaml` для сборки темы
- [[landing-orchestrator]] — вызывает этап и проверяет gate
- [[wp-gutenberg-block-builder]] — использует декларацию стека при генерации блоков
- [[design-system-generator]] — предшествующий этап, результаты которого служат входом