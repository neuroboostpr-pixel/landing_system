# Landing System (Neuroboost Agency)

Агентская система внутри Claude Code для производства production-grade лендингов на WordPress + Бегет. Полный цикл: от референсов до публикации.

## Quick Start

1. **Установить зависимости:**
   ```bash
   bash scripts/check-deps.sh
   ```

2. **Заполнить глобальные секреты:**
   ```bash
   cp .env.local.example .env.local
   # Отредактируй .env.local — см. spec раздел 19 для получения ключей
   ```

3. **Установить плагин superpowers (один раз):**
   ```bash
   claude
   > /plugin install superpowers@claude-plugins-official
   ```

4. **Создать первый лендинг:**
   ```bash
   claude
   > /landing-new my-first-landing
   ```

## Структура

```
landing-system/
├─ .agents/              # 1 агент сейчас (landing-orchestrator); ~18 запланировано к Phase 5
├─ .skills/              # наши скиллы (landing-project-init и др.)
├─ .claude/commands/     # slash-команды
├─ template/             # каноничный шаблон проекта-лендинга
├─ docs/superpowers/     # spec и planы реализации
├─ tests/                # bats-тесты (по фазам)
├─ scripts/              # bash-утилиты
├─ CLAUDE.md             # инструкции для Claude в этой папке
├─ README.md             # этот файл
└─ .env.local.example    # шаблон глобальных секретов
```

## Команды

| Команда | Назначение |
|---|---|
| `/landing-new <slug>` | Новый проект с нуля |
| `/landing-from-context <slug>` | Из родительской папки агентства |
| `/landing-clone <src> --as <new>` | A/B-копия независимого лендинга |
| `/landing-status` | Состояние системы и проектов |
| `/landing-help` | Справка по всем командам |

## Документация

- **Полное ТЗ:** [docs/superpowers/specs/2026-05-03-landing-system-design.md](docs/superpowers/specs/2026-05-03-landing-system-design.md)
- **Master plan:** [docs/superpowers/plans/2026-05-03-landing-system-master-plan.md](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)

## Тестирование

```bash
npm test              # все тесты
npm run test:phase-1  # только Phase 1
```

## Статус

**Phase 1 — Skeleton & Infrastructure** ✅ Complete (2026-05-03). Phase 2 — Brainstorming Pipeline (next).

Полный roadmap см. в master plan.

## License

Internal use — Neuroboost Agency. Distribution to students under separate agreement.
