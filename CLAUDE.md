# Landing System — CLAUDE Instructions

Это папка мастер-системы для производства WordPress-лендингов через Claude Code.

## Что это

Агентская система для построения production-grade лендингов на WordPress + Бегет.
Полный цикл: бриф → мудборд → бренд-кит → DESIGN.md → код → деплой → QA → SEO.

## Главные команды

- `/landing-new <slug>` — создать новый проект-лендинг с нуля
- `/landing-from-context <slug>` — создать проект из родительской папки агентства
- `/landing-status` — статус системы и текущих проектов
- `/landing-help` — справка по всем командам

## Зависимости

Эта система использует:
- **superpowers** plugin (brainstorming, writing-plans, executing-plans, subagent-driven-development)
- Скиллы из `skills/` (landing-project-init, landing-from-context)
- Агентов из `agents/` (landing-orchestrator)

Перед работой проверь: `scripts/check-deps.sh`.

## Структура

- `template/` — каноничный шаблон проекта-лендинга (13 папок 00–12)
- `skills/` — наши специализированные скиллы
- `agents/` — специализированные агенты
- `.claude/commands/` — slash-команды
- `docs/superpowers/` — спецификации и планы реализации

## Правила работы

1. **TDD строго:** каждое изменение в коде начинается с failing test (через `bats` для bash, `vitest` для JS, `pytest` для Python).
2. **YAGNI:** не реализуем то, чего нет в spec.
3. **Frequent commits:** один commit = одна логическая единица.
4. **HARD GATE между этапами проектов:** агент не идёт на следующий этап workflow без явного утверждения пользователем.

## Для нового проекта-лендинга

При запуске `/landing-new my-project` агенты:
1. Создают `~/Lendings/my-project/` со структурой template/.
2. Запускают `landing-orchestrator`, который ведёт через 12 этапов.
3. На каждом этапе генерируют HTML-preview, ждут подтверждения.
4. Финал — деплой на Бегет, готовый сайт.

## Поддержка

Spec-документ: [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](docs/superpowers/specs/2026-05-03-landing-system-design.md)
Master plan: [`docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)
