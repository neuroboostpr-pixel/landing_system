---
type: agent
name: landing-orchestrator
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-15
triggers:
  - "запустить проект лендинга"
  - "/landing-go"
  - "/landing-build"
  - "/landing-deploy"
  - "/landing-qa"
  - "продолжить работу над лендингом"
  - "следующий этап проекта"
stage: "00–12"
uses:
  - niche-analyst
  - client-assets-collector
  - photo-stylist
  - references-curator
  - moodboard-composer
  - style-extractor
  - brand-architect
  - design-system-generator
  - scene-director
  - stack-planner
  - content-writer
  - wp-builder
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - wp-deployer
  - qa-auditor
  - lifecycle-keeper
  - prototype-importer
  - photo-curator
  - visual-curator
  - block-composer
tags: [orchestrator, workflow, core]
---

# landing-orchestrator (Главный дирижёр)

## Что делает

Ведёт лендинг-проект через все 12 этапов производства: от брифа до деплоя и SEO. На каждом этапе вызывает нужного специализированного агента, показывает результат, ждёт явного одобрения от пользователя и только потом двигается дальше.

## Когда вызывать / в каком этапе

Активируется после создания проекта командами `/landing-new` или `/landing-from-context`. Основная точка входа в текущей реализации — `/landing-go` (PR-D), которая читает `.landing-state.yaml` и автоматически определяет, на каком этапе продолжить. Также активируется при командах `/landing-build`, `/landing-deploy`, `/landing-qa`.

## Что на вход / на выход

**На вход:**
- Инициализированная папка проекта (`~/Lendings/<slug>/`) со структурой template
- `.landing-state.yaml` — состояние 13 этапов (статус каждого: pending / approved / n/a)
- `prototype.pdf` в `07_ПРОТОТИП/source/` (в prototype-first режиме PR-D)
- Ответы пользователя в HARD GATE точках

**На выход:**
- `00_БРИФ/brief.md` — заполненный бриф проекта
- Последовательно: артефакты каждого этапа (мудборд, бренд-кит, DESIGN.md, WP-тема, задеплоенный сайт)
- Обновлённый `.landing-state.yaml` после каждого одобренного этапа

## Ключевые правила

**HARD GATE:** никогда не переходить на этап N+1 без явного «утверждаю», «ok» или «дальше» от пользователя. Gate проверяется скриптом `scripts/gate-check.sh`.

**Auto-fix:** при падении hard_check парсит `fix_hint` из `config/stage-gates.yaml`, предлагает конкретную команду-фикс, ждёт `yes/no`.

**Premium 07b:** этап `07c_composed` не закрывается, пока `scripts/verify-composed-premium.sh` не вернёт exit 0 (13 обязательных фич). Если фичи отсутствуют — делегирует обратно `block-composer`, не просит пользователя «принять как есть».

**Параллельная диспетчеризация:** когда этап 07c одобрен — одновременно запускает `photo-curator` (07d) и `visual-curator` (07e) через `superpowers:dispatching-parallel-agents`.

## Связанные концепты

- [[prototype-importer]] — первый агент в prototype-first потоке (этап 07a)
- [[niche-analyst]] — анализ ниши (этап 01a)
- [[brand-architect]] — сборка бренд-кита (этап 04)
- [[design-system-generator]] — токены и DESIGN.md (этап 05)
- [[wp-builder]] — генерация WP-темы (этап 08)
- [[photo-curator]] — обработка фото клиента (этап 07d)
- [[visual-curator]] — генерация иконок и инфографики (этап 07e)
- [[block-composer]] — финальная сборка composed.html (этап 07b/07f)
- [[qa-auditor]] — проверка живого сайта (этап 10)
- [[lifecycle-keeper]] — rollback и клонирование версий
- [[landing-go]] — slash-команда единой точки входа PR-D

## Источник

- `agents/landing-orchestrator.md`