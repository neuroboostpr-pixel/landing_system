---
type: rule
name: backlog
sources: ["docs/BACKLOG.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-orchestrator", "analytics-engineer", "wp-builder", "wp-cli-deployer", "seo-optimizer", "photo-stylist", "client-assets-collector", "stage-gates"]
tags: ["backlog", "roadmap", "техдолг", "приоритеты"]
---

# Backlog — отложенные задачи системы

## Что делает
Список всех запланированных доработок поверх базового MVP (stage-gates + onboarding). Каждый пункт снабжён обоснованием, объёмом работ и ссылкой на агента/скрипт, который нужно изменить.

## Когда вызывать / в каком этапе
Не привязан к конкретному этапу pipeline. Используется разработчиком системы при выборе следующей задачи. Для запуска работы над любым пунктом используется команда `/brainstorming <id>`, затем `/writing-plans` и `/executing-plans`.

## Что на вход / на выход
**Вход:** решение взять задачу в работу.  
**Выход:** spec в `docs/superpowers/specs/`, план в `docs/superpowers/plans/`, реализованный код и тесты.

---

## Приоритет 1 — функциональные дыры (блокирует прод-запуск)

| ID | Задача | Размер |
|----|--------|--------|
| B1 | Cookie-баннер + 152-ФЗ блок согласия (legal-block.php, cookie-banner.php, policy.html) | ~200 SLOC, 1–2 дня |
| B2 | GTM-вставка в `analytics-engineer` (`GTM_CONTAINER_ID` из .env) | ~30 SLOC, 2–3 часа |
| B3 | Бэкап `wp db export` до деплоя в prod | ~20 SLOC, 1 час |
| B4 | Sitemap.xml в `seo-optimizer` | ~40 SLOC, 2 часа |

## Приоритет 2 — расширение и удобство

| ID | Задача | Размер |
|----|--------|--------|
| B5 | Автоустановка WP-плагинов при деплое (WP Rocket, Wordfence и др.) | ~50 SLOC, 3 часа |
| B6 | Fallback для `photo-stylist` — промпты для ChatGPT если нет HF Token | ~80 SLOC, 1 день |
| B7 | Soft-check фото-стиля в `client-assets-collector` через Pillow | ~120 SLOC, 1 день |
| B8 | `migration-engineer` — 301-редиректы при переносе сайта | ~150 SLOC, 1–2 дня |

## Приоритет 3 — большие фичи

| ID | Задача | Размер |
|----|--------|--------|
| B9 | Multilang (i18n-engineer + Polylang) | ~300 SLOC, 3–4 дня |
| B10 | Staging-окружение (флаг `--env staging/prod`) | ~100 SLOC, 1 день |
| B11 | WP-CLI MCP-сервер (Node.js, 6 инструментов) | ~400 SLOC, 3–5 дней |
| B12 | DNS MCP-серверы (Beget / Cloudflare / Reg.ru) | 3×~250 SLOC, 1 неделя |

## Приоритет 4 — техдолг

| ID | Задача | Размер |
|----|--------|--------|
| B13 | Concurrency-safe `gate-state.sh` через `flock` | ~20 SLOC, 1 час |
| B14 | Single-registry в `aggregate.py` | ~10 SLOC, 30 мин |
| B15 | `pyproject.toml` с `pythonpath = .` | 5 строк, 10 мин |
| B16 | Кэш результатов validate-all в `wizard.sh` | ~10 SLOC, 30 мин |

## Связанные концепты
- [[analytics-engineer]] — B2: GTM-вставка в functions.php
- [[wp-builder]] — B1: legal-block во всех формах
- [[wp-cli-deployer]] — B3: бэкап БД, B5: автоустановка плагинов
- [[seo-optimizer]] — B4: генерация sitemap.xml
- [[photo-stylist]] — B6: fallback-промпты без HF Token
- [[client-assets-collector]] — B7: автооценка фото-стиля
- [[stage-gates]] — B1: soft-check `legal_blocks_present` уже в конфиге

## Источник
- `docs/BACKLOG.md`