---
slug: landing-orchestrator
type: agent
name: "Главный дирижёр (Landing Orchestrator)"
tags: [orchestrator, workflow, pipeline, stages, hard-gate]
triggers: [landing-go, landing-new, landing-build, landing-deploy]
inputs: [.landing-state.yaml, 07_ПРОТОТИП/source/prototype.pdf, config/stage-gates.yaml]
outputs: [wiki/pipeline-map.md, 00_БРИФ/brief.md, артефакты каждого этапа]
pre_reqs: [landing-onboarding-wizard]
related:
  - niche-analyst
  - brand-architect
  - content-writer
  - design-system-generator
  - moodboard-composer
  - client-assets-collector
  - photo-curator
  - block-composer
  - integrations-engineer
  - analytics-engineer
  - lifecycle-keeper
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-26
confidence:
  triggers: low
---

# Главный дирижёр (Landing Orchestrator)

## Что делает

Ведёт проект-лендинг через 12 этапов — от брифа до SEO — и обеспечивает соблюдение качества на каждом из них. Перед любым действием читает `.landing-state.yaml`, рисует Mermaid-карту pipeline, формирует TodoWrite со всеми оставшимися этапами и запускает `gate-check.sh`. На каждом этапе диспатчит специализированного агента, ждёт HTML-превью, затем требует явного утверждения пользователя (HARD GATE) перед переходом к следующему шагу. В prototype-first режиме (PR-D) запускается через `/landing-go` и самостоятельно распределяет параллельные этапы 07d (фото) и 07e (визуалы).

## Когда вызывается

Запускается командой `/landing-go` после инициализации проекта (онбординг завершён, папка проекта создана). Также задействуется внутри команд `/landing-new`, `/landing-build`, `/landing-deploy` — всякий раз, когда нужен контроль workflow. Не запускается в обход — пользователь не может попросить «перейти сразу к деплою».

## Вход → выход

**Вход:** инициализированный проект с `.landing-state.yaml`, файл `config/stage-gates.yaml` со списком зависимостей между этапами; в prototype-first режиме — `prototype.pdf` в `07_ПРОТОТИП/source/`.

**Выход:** обновлённый `.landing-state.yaml` с отметками `approved` для каждого пройденного этапа; `wiki/pipeline-map.md` с актуальной Mermaid-картой; все промежуточные артефакты этапов (brief.md, brand-kit.html, composed.html, build-preview.html и т.д.).

## Failure modes

- Пользователь просит пропустить этап — оркестратор отказывает жёстко, ссылаясь на `require_approved` из `stage-gates.yaml`.
- Hard-check на гейте падает, но `fix_hint` не прописан в `stage-gates.yaml` — авто-фикс невозможен, оркестратор сообщает об ошибке и зависает.
- Verify-скрипт (например `verify-composed-premium.sh`) возвращает ненулевой exit-код — оркестратор НЕ объявляет этап завершённым и гоняет `block-composer` в цикле.
- Параллельные субагенты 07d/07e вернули ошибку в одном из потоков — оркестратор не переходит к 07f до тех пор, пока оба гейта не закрыты.
- `.landing-state.yaml` отсутствует или повреждён — весь pipeline недоступен; нужен `migrate-state-for-prd.sh`.

## Related

- [[niche-analyst]] — диспатчится на этапе 01a
- [[brand-architect]] — диспатчится на этапе 04
- [[design-system-generator]] — диспатчится на этапе 05
- [[moodboard-composer]] — диспатчится на этапе 03
- [[content-writer]] — диспатчится на этапе 07
- [[block-composer]] — переделывает composed.html если 07b-гейт упал
- [[photo-curator]] — параллельный субагент этапа 07d
- [[integrations-engineer]] — диспатчится на этапе 08
- [[analytics-engineer]] — диспатчится на этапах 08 и 11
- [[lifecycle-keeper]] — диспатчится на rollback и clone
- [[landing-onboarding-wizard]] — должен завершиться до первого запуска оркестратора