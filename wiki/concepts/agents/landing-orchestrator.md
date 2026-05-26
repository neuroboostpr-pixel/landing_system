---
slug: landing-orchestrator
type: agent
name: "Landing Orchestrator — Главный дирижёр"
tags: [orchestrator, pipeline, workflow, stages, dispatch]
triggers: [landing-go, landing-build, landing-deploy, landing-qa, landing-rollback, landing-clone]
inputs: [.landing-state.yaml, config/stage-gates.yaml]
outputs: [.landing-state.yaml, 00_БРИФ/brief.md, wiki/pipeline-map.md]
pre_reqs: [landing-start, landing-new]
related: [landing-go, landing-build, landing-deploy, landing-prototype, landing-wireframe, landing-compose, landing-photos, landing-visuals, landing-qa, landing-status]
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-26
---

# Landing Orchestrator — Главный дирижёр

## Что делает

Ведёт проект-лендинг через полный цикл из 12 этапов: от брифа до SEO-оптимизации. Читает `.landing-state.yaml`, определяет текущий этап, диспатчит нужного специализированного агента (brand-architect, wp-builder, wp-deployer и др.) и принудительно блокирует переход к следующему этапу без явного утверждения пользователя. В prototype-first режиме (PR-D) работает через команду `/landing-go` как единую точку входа с auto-resume по state-файлу.

## Когда вызывается

Основной триггер — `/landing-go` (prototype-first flow). Также активируется через `/landing-build`, `/landing-deploy`, `/landing-qa`, `/landing-rollback`, `/landing-clone`. Запускается после того, как проект инициализирован через `/landing-start` или `/landing-new` и в папке `07_ПРОТОТИП/source/` лежит `prototype.pdf`.

## Вход → выход

**Вход:** инициализированная папка проекта, `.landing-state.yaml` с текущим статусом этапов, `config/stage-gates.yaml` с определениями гейтов, артефакты предыдущих этапов (прототип, бренд-кит, tokens.json и т.д.).

**Выход:** последовательно закрытые этапы 00–12 в `.landing-state.yaml`, HTML-превью каждого этапа для утверждения пользователем, задиспатченные агенты с их артефактами, итоговый задеплоенный WordPress-сайт.

## Failure modes

- **Прыжок через этап** — оркестратор отказывает, если `require_approved` в stage-gates.yaml содержит незакрытый этап; пользователь получает явное сообщение с инструкцией.
- **Падение hard_check** — оркестратор не переходит дальше; парсит `fix_hint`, предлагает авто-фикс (один раз на check_id для защиты от циклов).
- **Premium 07b не прошёл** — `verify-composed-premium.sh` вернул exit ≠ 0; оркестратор возвращает задачу `block-composer` и не принимает approve.
- **Параллельные субагенты (07d+07e)** — если один из двух завис или упал, оркестратор ждёт оба и не переходит к 07f, пока не пройдут оба гейта.
- **Отсутствует `.landing-state.yaml`** — оркестратор не стартует; нужен `/landing-new` или `/landing-start`.

## Related

- [[landing-go]] — команда-точка входа, которая запускает оркестратор
- [[landing-build]] — команда этапа 08, диспатчится оркестратором для сборки WordPress-темы
- [[landing-deploy]] — команда этапа 09, деплой на Бегет через wp-deployer
- [[landing-prototype]] — парсинг prototype.pdf, первый авто-этап в PR-D потоке
- [[landing-wireframe]] — интерактивный выбор вариантов блоков (этап 07b)
- [[landing-compose]] — сборка composed.html (этапы 07c и 07f)
- [[landing-photos]] — обработка клиентских фото (этап 07d, параллельно с 07e)
- [[landing-visuals]] — AI-генерация иконок и инфографики (этап 07e)
- [[landing-qa]] — аудит задеплоенного сайта (этапы 10–12)
- [[landing-status]] — просмотр текущего состояния pipeline без запуска действий