# Landing System (Neuroboost Agency)

Агентская система для производства production-grade лендингов на WordPress + Бегет внутри Claude Code.
Полный цикл: бриф → мудборд → бренд-кит → DESIGN.md → код → деплой → QA → SEO.

## Quick Start — Установка для команды

### Вариант 1 — Как Claude Code плагин (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/neuroboostpr-pixel/landing_system.git
cd landing_system

# Запустить установщик
bash install.sh
```

Или напрямую через Claude Code CLI:

```bash
claude plugins marketplace add github:neuroboostpr-pixel/landing_system
claude plugins install landing-system
```

### Вариант 2 — Прямое использование из папки

```bash
git clone https://github.com/neuroboostpr-pixel/landing_system.git
cd landing_system
bash scripts/check-deps.sh
```

Открой папку `landing_system/` в Claude Code — команды `/landing-*` будут автоматически доступны.

## Первый запуск

```bash
# 1. Настроить секреты
cp .env.example .env
# Отредактируй .env (Beget SSH, API ключи)

# 2. Установить superpowers plugin (если ещё нет)
# В Claude Code: /plugin install superpowers@claude-plugins-official

# 3. Первый проект
# В Claude Code: /landing-new my-first-landing
```

## Первый запуск (onboarding)

После клонирования репо запусти:

```bash
bash scripts/wizard.sh
# или внутри Claude Code:
/landing-onboarding
```

Onboarding:
- проверяет локальные зависимости (wp-cli, ssh, rsync, python, jq)
- проверяет, что плагин `superpowers` установлен
- проверяет, что Firecrawl MCP настроен
- создаёт `.env` и валидирует все API-ключи
- создаёт флаг `~/.landing-system/setup_complete`

Без пройденного onboarding'а команды `/landing-*` не запускаются.

## Workflow Lock

Каждый проект содержит `.landing-state.yaml`, который фиксирует статус 13 этапов. `/landing-build` не запустится без одобренных 02–07; `/landing-deploy` — без одобренного 08. Этапы перепрыгивать нельзя.

Полный гайд: [`docs/SETUP.md`](docs/SETUP.md)

## Команды

| Команда | Назначение |
|---|---|
| `/landing-new <slug>` | Новый проект с нуля |
| `/landing-from-context <slug>` | Из родительской папки агентства |
| `/landing-niche` | Анализ ниши и конкурентов (этап 01a) |
| `/landing-references` | Референсы и мудборд (этап 03) |
| `/landing-brand` | Бренд-кит из референсов (этап 04) |
| `/landing-design` | Дизайн-система и токены (этап 05) |
| `/landing-stack` | Подбор плагинов и библиотек (этап 06) |
| `/landing-content` | Контент по блокам (этап 07) |
| `/landing-build` | WordPress тема и код (этап 08) |
| `/landing-setup` | Настройка деплоя (один раз) |
| `/landing-deploy` | Деплой на Бегет (этап 09) |
| `/landing-qa` | QA аудит (этап 10) |
| `/landing-rollback <version>` | Откат к версии |
| `/landing-clone <src> --as <new>` | A/B-копия |
| `/landing-status` | Статус системы и проектов |
| `/landing-help` | Справка по всем командам |

## Структура

```
landing-system/
├── agents/              # 19 специализированных агентов
├── skills/              # скиллы (wp-builder, deployer, versioning и др.)
├── commands/            # slash-команды (для плагина)
├── .claude/commands/    # slash-команды (для локального использования)
├── template/            # шаблон проекта-лендинга (папки 00–12)
├── config/              # system.yaml.template, конфигурация
├── tools/               # вспомогательные утилиты (logger, html-templates)
├── tests/               # bats + pytest тесты по фазам
├── scripts/             # bash-утилиты (check-deps, build-zip, deploy)
├── docs/                # spec и planы реализации
├── .claude-plugin/      # метаданные Claude Code плагина
├── CLAUDE.md            # инструкции для Claude
├── install.sh           # установщик для команды
└── .env.example         # шаблон секретов
```

## Зависимости

- **Claude Code** с плагином `superpowers` (`claude plugins install superpowers@claude-plugins-official`)
- **Node.js** ≥ 20
- **Python** 3.10+
- **bats-core** (тесты)
- **wp-cli**, **rsync**, **ssh** (деплой)

Проверь всё: `bash scripts/check-deps.sh`

## Тестирование

```bash
npm test                # все bats-тесты
npm run test:phase-1    # только Phase 1
npm run test:python     # python тесты (Phase 2+)
```

## Документация

- **Полное ТЗ:** [docs/superpowers/specs/2026-05-03-landing-system-design.md](docs/superpowers/specs/2026-05-03-landing-system-design.md)
- **Master plan:** [docs/superpowers/plans/2026-05-03-landing-system-master-plan.md](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)

## Статус

Здесь две разные нумерации, не путать:

- **Stages (этапы 00–12 + 01a)** — пользовательский workflow внутри одного лендинга (бриф → … → деплой → QA → SEO). Зафиксированы в `.landing-state.yaml` каждого проекта, охраняются `gate-check.sh`.
- **Phases (фазы 1–6)** — этапы разработки самой системы (см. [master plan](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)).

Текущее состояние разработки системы:

| Phase | Что входит | Статус |
|---|---|---|
| 1. Skeleton & Infrastructure | каркас, `template/`, `/landing-new` | ✅ |
| 2. Brainstorming Pipeline (stages 00–04) | бриф, материалы, референсы, бренд-кит | ✅ |
| 3. Design Pipeline (stages 05–07) | DESIGN.md, токены, стек, контент | ✅ |
| 4. WP Build Pipeline (stage 08) | Gutenberg-блоки, ACF, тема, аналитика, SEO | ✅ |
| 5. Deploy & Operations (stages 09–12) | `wp-deployer`, `/landing-deploy`, QA, rollback, A/B, DNS | ✅ |
| 6. Packaging & Pilot | `build-zip.sh`, pilot-прогон, student-guide | ⏳ в работе |

Функциональность деплоя реализована в Phase 5. Phase 6 — это упаковка системы для раздачи и пилотный прогон, а не дописывание деплоя. Backlog поверх MVP — в [docs/BACKLOG.md](docs/BACKLOG.md).

## License

Internal use — Neuroboost Agency. Distribution to team members under agency agreement.
