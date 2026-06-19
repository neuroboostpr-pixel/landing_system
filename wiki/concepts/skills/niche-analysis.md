---
slug: niche-analysis
type: skill
name: "Анализ ниши"
stage: "01a"
tags: [niche, research, competitors, analysis, automation]
triggers: [landing-niche]
inputs: [00-brif]
outputs: [01a-analiz-nishi]
pre_reqs: [00-brif]
related: [niche-analyst, landing-niche, landing-orchestrator, 01a-analiz-nishi]
sources: ["skills/niche-analysis/SKILL.md"]
updated: 2026-06-19
---

# Анализ ниши

## Что делает

Скилл-обёртка над агентом `niche-analyst`, запускаемая через команду `/landing-niche`. Автоматически исследует нишу клиента и конкурентов без ручных шагов. Перед стартом проверяет готовность проекта: наличие `.landing-state.yaml` и статус `approved` у этапа `00_brief`. Помечает этап `01a_niche_analysis` как `in_progress`, делегирует аналитическую работу агенту, а после его завершения прогоняет валидацию схемы и проверку gate'ов. Результат — три артефакта в папке `01a_АНАЛИЗ_НИШИ/`.

## Когда вызывается

Пользователь запускает `/landing-niche` из папки проекта-лендинга. Скилл активируется только если этап `00_brief` уже утверждён (`approved`). В обратном случае завершается с ошибкой ещё до делегирования агенту.

## Вход → выход

**Вход:** папка проекта с `.landing-state.yaml`, этап `00-brif` в статусе `approved`.

**Выход:** три файла-артефакта в `01a_АНАЛИЗ_НИШИ/` (точный состав определяет агент `niche-analyst`); обновлённый статус этапа в `.landing-state.yaml`; результат проверки `gate-check.sh` по схеме `validate-competitors.py`.

## Failure modes

- Скилл запущен вне папки проекта — `.landing-state.yaml` не найден, завершение с ошибкой.
- Этап `00_brief` не в статусе `approved` — скилл блокирует делегирование агенту.
- Агент `niche-analyst` упал или вернул неполные данные — `validate-competitors.py` отклоняет YAML-схему, gate не проходит.
- `gate-check.sh` завершается с ошибкой — этап остаётся `in_progress`, не переходит в `done`.
- Файл `scripts/validate-competitors.py` отсутствует или сломан — валидация пропускается молча, дефект не фиксируется.

## Related

- [[niche-analyst]] — агент, которому скилл делегирует фактический анализ
- [[landing-niche]] — slash-команда, непосредственно вызывающая этот скилл
- [[01a-analiz-nishi]] — этап шаблона, результат которого закрывает данный скилл
- [[landing-orchestrator]] — оркестратор, в контексте которого живёт этап 01a
- [[00-brif]] — обязательный предшественник: должен быть `approved` до старта