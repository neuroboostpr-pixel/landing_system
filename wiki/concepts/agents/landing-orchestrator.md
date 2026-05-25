---
type: agent
name: landing-orchestrator
sources: ["agents/landing-orchestrator.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses:
  - landing-go
  - landing-prototype
  - landing-wireframe
  - landing-compose
  - landing-photos
  - landing-visuals
  - landing-build
  - landing-deploy
  - landing-qa
  - niche-analyst
  - brand-architect
  - design-system-generator
  - content-writer
  - wp-builder
  - wp-deployer
  - qa-auditor
  - references-curator
  - moodboard-composer
  - style-extractor
  - stack-planner
tags: [orchestrator, pipeline, workflow, core]
---

# landing-orchestrator (Главный дирижёр)

## Что делает

Управляет полным производственным циклом лендинга — от брифа до деплоя. Читает состояние проекта, диспатчит специализированных агентов на каждый этап, принудительно контролирует HARD GATE между шагами и не даёт пропустить ни один этап без явного утверждения пользователем.

## Когда вызывать / в каком этапе

Запускается командой `/landing-go` (основной режим, prototype-first) или исторически — `/landing-new`. Активируется сразу после инициализации проекта и ведёт через все 12+ этапов (00→12 для full flow, 03→12 для prototype-first). В prototype-first режиме этапы 00–02 помечены `n/a`, стартовая точка — `07a_prototype`.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` проекта — текущее состояние этапов
- `config/stage-gates.yaml` — список hard/soft проверок для каждого этапа
- Пользовательские материалы: `prototype.pdf`, клиентские фото, логотип

**Выход:**
- Последовательно — артефакты каждого этапа: `brief.md`, `moodboard.html`, `brand-kit.md`, `DESIGN.md`, `composed.html`, WordPress-тема, задеплоенный сайт
- Обновлённый `.landing-state.yaml` после каждого `--approve`

## Обязательный протокол перед каждым действием (Stage Execution Protocol)

1. Прочитать `.landing-state.yaml`, запустить `render-pipeline-map.sh` — показать Mermaid-карту пользователю
2. Создать TodoWrite со всеми оставшимися этапами
3. Запустить `gate-check.sh --stage <id>`, прочитать чек-лист `stage-<id>-checklist.md` если есть
4. После verify → `gate-check.sh --approve` → переход к следующему этапу

## Параллельная диспетчеризация (этапы 07d + 07e)

Когда `07c_composed` одобрен, оркестратор запускает **одновременно** `photo-curator` и `visual-curator` через `superpowers:dispatching-parallel-agents`. Переход к `07f` только после завершения обоих агентов и прохождения обоих гейтов.

## Контроль качества 07b

HARD GATE `composed_premium_standard` — скрипт `verify-composed-premium.sh` проверяет 13 обязательных премиум-фич. Если падает — оркестратор возвращает задачу `block-composer`, цикл до `exit 0`. «И так сойдёт» — недопустимо.

## Связанные концепты

- [[landing-go]] — главная точка входа, вызывает оркестратор
- [[landing-prototype]] — этап 07a, парсинг PDF-прототипа
- [[landing-wireframe]] — этап 07b, выбор вариантов блоков
- [[landing-compose]] — этапы 07c и 07f, сборка composed.html
- [[landing-photos]] — этап 07d, обработка фото клиента
- [[landing-visuals]] — этап 07e, AI-генерация иконок
- [[landing-build]] — этап 08, генерация WordPress-темы
- [[landing-deploy]] — этап 09, деплой на Бегет
- [[niche-analyst]] — агент этапа 01a, анализ ниши
- [[brand-architect]] — агент этапа 04, создание бренд-кита
- [[wp-builder]] — агент этапа 08, сборка блоков
- [[qa-auditor]] — агент этапа 10, QA-отчёт

## Источник

- `agents/landing-orchestrator.md`