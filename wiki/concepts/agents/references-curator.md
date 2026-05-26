---
slug: references-curator
type: agent
name: "Куратор референсов"
stage: "03"
tags: [references, visual, stage-03, curator]
triggers: [landing-orchestrator]
inputs:
  - 01a_АНАЛИЗ_НИШИ/competitors.yaml
  - 01a_АНАЛИЗ_НИШИ/visual-requirements.md
outputs:
  - 03_РЕФЕРЕНСЫ/index.yaml
  - 03_РЕФЕРЕНСЫ/refs/
gates:
  - min_3_approved_refs
pre_reqs: [niche-analyst]
related: [moodboard-composer, landing-orchestrator, niche-analyst]
sources: ["agents/references-curator.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Куратор референсов

## Что делает

Первая половина этапа 03. Принимает от пользователя ссылки на сайты, файлы Behance/Dribbble и скриншоты, складывает их в `03_РЕФЕРЕНСЫ/refs/`, присваивает каждому статус (candidate / approved / rejected) и ведёт реестр через `index.yaml`. Перед оценкой любого референса сверяется с `visual-requirements.md` конкурентного анализа: визуальные паттерны лидеров ниши и «красные флаги» раздела 6 служат фильтром — клонировать визуал конкурентов нельзя, нужно искать незанятые ниши. После накопления минимум трёх approved-референсов передаёт управление `moodboard-composer`.

## Когда вызывается

Запускается `landing-orchestrator` при переходе проекта в состояние `current_stage == 03_references`. До запуска агент проверяет это состояние в `.landing-state.yaml` и отказывается работать, если этап не совпадает. `PreToolUse`-хук физически блокирует Write/Edit к файлам этапа, если предшественники не закрыты.

## Вход → выход

**Вход:** `01a_АНАЛИЗ_НИШИ/competitors.yaml` (поле `visual_notes` каждого конкурента) и `01a_АНАЛИЗ_НИШИ/visual-requirements.md` (секция 6 с запретами); пользовательские ссылки и скриншоты.

**Выход:** заполненный `03_РЕФЕРЕНСЫ/index.yaml` — реестр референсов со статусами; сохранённые файлы в `03_РЕФЕРЕНСЫ/refs/`. При наборе ≥3 approved записей — готовность к передаче в `moodboard-composer`.

## Чем закрывается этап (gates)

- min_3_approved_refs — в `index.yaml` должно быть не менее трёх записей со статусом `approved`; иначе мудборд не стартует.

## Failure modes

- Пользователь предоставляет менее трёх ссылок — агент зависает на HARD GATE и не может передать управление `moodboard-composer`.
- Референс попадает под «красный флаг» из `visual-requirements.md`, но агент не сверился с файлом — в мудборд проходит запрещённый визуальный паттерн.
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` отсутствует или не содержит `visual_notes` — агент работает без контекста конкурентов и рискует рекомендовать клонирование.
- `scripts/hooks/enforce_stage_gate.py` блокирует запись, если предшественник (нише-анализ) не закрыт — пользователь видит ошибку «Stage gate enforcement» и не понимает причину.
- `index.py` завершается с ошибкой (Python-окружение не настроено) — индекс не обновляется, состояние этапа рассинхронизируется.

## Related

- [[moodboard-composer]] — принимает управление после набора ≥3 approved референсов
- [[landing-orchestrator]] — вызывает агента и отслеживает закрытие этапа
- [[niche-analyst]] — производит обязательные входные артефакты этапа 01a