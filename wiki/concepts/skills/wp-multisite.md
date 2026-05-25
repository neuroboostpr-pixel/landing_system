---
type: skill
name: wp-multisite
sources: ["skills/wp-multisite/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-segment", "landing-clone", "landing-orchestrator"]
tags: ["multisite", "wordpress", "beget", "сегменты", "поддомены"]
---

# wp-multisite — управление WordPress Multisite на Beget

## Что делает

Позволяет запустить несколько лендингов под одним клиентским доменом: превращает обычный WordPress-сайт в мультисетевой, создаёт поддомены для разных аудиторий и копирует готовые сегменты без ручной настройки.

## Когда вызывать / в каком этапе

Вызывается командами `/landing-segment <slug>` и `/landing-clone <source> <dest>` когда проекту нужно больше одного лендинга под одним доменом клиента. Скилл входит в стадию `13_СЕГМЕНТЫ_ЦА`. Если проект ещё не переведён в multisite-режим, скрипт `landing-segment.sh` запускает миграцию автоматически перед созданием первого сегмента.

## Что на вход / на выход

**Вход:**
- `<project-dir>` — путь к папке проекта (`~/Lendings/<slug>/`)
- `.landing-state.yaml` — читается флаг `multisite` и список `audience_segments`
- `BEGET_*` переменные окружения (SSH, API-ключи)
- `BEGET_SITE_ID` — integer id сайта на Бегете (получить через `beget_api site/getList`)

**Выход:**
- Поддомен создан на Бегете
- WP subsite добавлен в сеть (wp-cli)
- Директория `<project>/13_СЕГМЕНТЫ_ЦА/<slug>/` с `subbrief.yaml` и `.subsite-meta.yaml`
- `.landing-state.yaml` обновлён: `multisite: true`, новый элемент в `audience_segments[]`

**При клонировании:**
- Все страницы и опции скопированы из source-сегмента в dest-сегмент
- `siteurl` / `home` переписаны на новый поддомен

## Ключевые скрипты

| Скрипт | Назначение |
|---|---|
| `migrate-to-multisite.sh` | Single-site → multisite (идемпотентен, no-op если уже multisite) |
| `landing-segment.sh` | Создать сегмент ЦА: поддомен + WP subsite + папки |
| `clone-subsite.sh` | Byte-by-byte копия сегмента в новый slug |

**Lib:**
- `lib/beget-api.sh` — обёртка Beget API
- `lib/ssh-helpers.sh` — SSH + wp-cli обёртки
- `lib/state.sh` — read/write `.landing-state.yaml`

## Связанные концепты

- [[landing-segment]] — slash-команда, вызывает `landing-segment.sh` из этого скилла
- [[landing-clone]] — slash-команда, вызывает `clone-subsite.sh` из этого скилла
- [[landing-orchestrator]] — оркестратор pipeline, к которому привязан этап 13 сегментов
- [[landing-go]] — главная точка входа, диспатчит этапы в т.ч. создание сегментов

## Источник

- `skills/wp-multisite/SKILL.md`