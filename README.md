# Landing System (Neuroboost Agency)

Агентская система внутри Claude Code для производства production-grade лендингов на WordPress. Полный цикл: от референсов до публикации на Бегете.

## Статус

**Версия:** 1.0 (MVP, в разработке)
**Spec-документ:** [docs/superpowers/specs/2026-05-03-landing-system-design.md](docs/superpowers/specs/2026-05-03-landing-system-design.md)

## Быстрый старт

См. раздел **«18. Установка системы — пошагово»** в spec-документе.

## Структура

```
landing-system/
├─ .agents/                      # 18 специализированных агентов
├─ .skills/                      # скиллы (свои + копии нужных)
├─ .claude/
│  ├─ commands/                  # slash-команды (/landing-*)
│  └─ settings.json              # hooks
├─ template/                     # шаблон проекта-лендинга
├─ docs/superpowers/specs/       # этот spec
├─ scripts/                      # bash-скрипты
├─ README.md                     # этот файл
├─ CLAUDE.md                     # инструкции для Claude
├─ .env.local.example            # шаблон глобальных секретов
└─ .gitignore
```

## Документация

Полное техническое задание и инструкции — в [spec-документе](docs/superpowers/specs/2026-05-03-landing-system-design.md):

1. Архитектура и решения
2. Workflow одного лендинга (12 этапов)
3. Карта 18 агентов
4. Скиллы и MCP-серверы
5. Frontend-стек и cinematic-режим
6. Slash-команды
7. Деплой на Бегет (SSH + WP-CLI + rsync)
8. DNS-автоматизация
9. Версионирование и A/B-копии
10. Хранение секретов
11. Установка системы — пошагово
12. **Получение всех API-ключей — где и как**
13. Типовые сценарии использования
14. Roadmap (плагин → SaaS)

## License

Internal use — Neuroboost Agency. Distribution to students under separate agreement.
