---
type: agent
name: landing-orchestrator
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses: ["niche-analyst", "client-assets-collector", "photo-stylist", "references-curator", "moodboard-composer", "style-extractor", "brand-architect", "design-system-generator", "scene-director", "stack-planner", "content-writer", "wp-builder", "integrations-engineer", "analytics-engineer", "seo-optimizer", "wp-deployer", "qa-auditor", "lifecycle-keeper", "prototype-importer", "photo-curator", "visual-curator", "block-composer"]
tags: ["orchestration", "workflow", "pipeline", "hard-gate"]
---

# landing-orchestrator (Главный дирижёр)

## Что делает

Ведёт лендинг-проект через все 12 этапов производства — от брифа до деплоя и SEO. На каждом этапе вызывает нужного специализированного агента, показывает HTML-превью результата и **не двигается дальше без явного утверждения** от пользователя (HARD GATE).

## Когда вызывать / в каком этапе

Запускается через команду `/landing-go` — единственную точку входа для нового проекта в prototype-first режиме. Предполагает, что `landing-project-init` или `landing-from-context` уже выполнен и в папке проекта есть `.landing-state.yaml`.

В legacy-режиме запускается после `/landing-start` или `/landing-new`.

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — текущий статус этапов
- `config/stage-gates.yaml` — правила гейтов
- `07_ПРОТОТИП/source/prototype.pdf` (в prototype-first режиме)
- Ответы пользователя на вопросы брифа (в legacy-режиме)

**Выход:**
- Заполненный `00_БРИФ/brief.md`
- HTML-превью каждого ключевого этапа (moodboard, brand-kit, design-preview, build-preview)
- Обновлённый `.landing-state.yaml` с закрытыми этапами
- Финальный задеплоенный лендинг (этапы 08–12)

## Ключевые механики

**HARD GATE:** агент никогда не переходит к этапу N+1 без явного «утверждаю / ok / дальше» от пользователя. Нельзя пропустить этап даже по просьбе.

**Gate-check:** перед каждым действием выполняет `scripts/gate-check.sh --stage <target> --project <project>`. При падении hard-lock — останавливается и сообщает список незакрытых зависимостей.

**Auto-fix:** при падении hard_check парсит `fix_hint` из stage-gates.yaml и предлагает выполнить исправляющую команду (например `/landing-prototype`).

**Параллельная диспетчеризация:** когда этап 07c утверждён, запускает `photo-curator` и `visual-curator` одновременно через `superpowers:dispatching-parallel-agents`. Переходит к 07f только после того, как оба агента завершились.

**Premium 07b enforcement:** этапы 07c и 07f проверяются скриптом `scripts/verify-composed-premium.sh` на 13 обязательных Premium-фич. Если проверка не пройдена — возвращает задачу агенту `block-composer` и повторяет цикл до exit 0.

## Связанные концепты

- [[niche-analyst]] — диспатчится на этапе 01a для анализа рынка
- [[brand-architect]] — диспатчится на этапе 04 для сборки бренд-кита
- [[design-system-generator]] — диспатчится на этапе 05 для генерации токенов
- [[wp-builder]] — диспатчится на этапе 08 для генерации WordPress-темы
- [[photo-curator]] — диспатчится параллельно на этапе 07d
- [[visual-curator]] — диспатчится параллельно на этапе 07e
- [[block-composer]] — возвращает задачу при не пройденном premium-check
- [[lifecycle-keeper]] — используется при rollback и clone
- [[qa-auditor]] — диспатчится на этапе 10 для проверки живого сайта
- [[landing-go]] — единственная точка входа для запуска оркестратора

## Источник

- `agents/landing-orchestrator.md`