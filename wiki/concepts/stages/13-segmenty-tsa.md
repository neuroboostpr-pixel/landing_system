---
slug: 13-segmenty-tsa
type: stage
name: "13_СЕГМЕНТЫ_ЦА — Сегменты целевой аудитории"
stage: "13"
tags: [multisite, audience-segments, subdomain, wordpress]
triggers: [landing-segment]
inputs: [.landing-state.yaml, 04-brend, 05-dizayn-sistema]
outputs: [13_СЕГМЕНТЫ_ЦА/<slug>/subbrief.yaml, 13_СЕГМЕНТЫ_ЦА/<slug>/.subsite-meta.yaml]
gates: [segment_subsite_created, subdomain_live]
pre_reqs: [landing-setup, wp-multisite]
related: [landing-clone, landing-segment, wp-multisite, landing-go, landing-deploy]
sources: ["template/13_СЕГМЕНТЫ_ЦА/README.md"]
updated: 2026-05-26
confidence: {gates: low, inputs: low}
---

# 13_СЕГМЕНТЫ_ЦА — Сегменты целевой аудитории

## Что делает

Этап 13 описывает структуру и механику создания сегментов целевой аудитории внутри одного лендинг-проекта. Каждый сегмент — самостоятельная версия лендинга под отдельную группу пользователей (например: русскоязычные, семьи, бизнес-туристы). Технически каждый сегмент разворачивается как отдельный WordPress subsite в единой multisite-сети и привязывается к своему поддомену на Бегете. Папка `13_СЕГМЕНТЫ_ЦА/<slug>/` служит рабочей зоной маркетолога: здесь хранятся бриф сегмента, будущий прототип и фото, а машинные метаданные (blog_id, host) фиксируются в `.subsite-meta.yaml`.

## Когда вызывается

Этап активируется командой `/landing-segment <slug>`, когда клиент хочет запустить дополнительную версию лендинга под конкретный сегмент ЦА. Предполагается, что базовый проект уже прошёл этапы бренда (04) и дизайн-системы (05). При первом сегменте система автоматически мигрирует проект из single-site в multisite-режим.

## Вход → выход

**Вход:** действующий лендинг-проект с заполненным `.landing-state.yaml`; slug нового сегмента; настроенные Beget-креды (`BEGET_SITE_ID` и стандартные `BEGET_*`).

**Выход:** поддомен `<slug>.<корневой-домен>` на Бегете; WordPress subsite внутри multisite-сети; папка `13_СЕГМЕНТЫ_ЦА/<slug>/` со скелетом (`subbrief.yaml`, `prototype/`, `photos/`, `.subsite-meta.yaml`); обновлённый `.landing-state.yaml` с флагом `multisite: true` и записью в `audience_segments[]`.

## Чем закрывается этап (gates)

- `segment_subsite_created` — WordPress subsite создан, `blog_id` записан в `.subsite-meta.yaml`
- `subdomain_live` — поддомен зарегистрирован на Бегете и резолвится корректно

## Failure modes

- Beget API не возвращает `site_id` — multisite-миграция падает на шаге создания поддомена; нужно проверить `BEGET_SITE_ID` в `.env`.
- Проект уже в multisite, но `audience_segments[]` в `.landing-state.yaml` пустой — дублирование записей при повторном вызове `/landing-segment`.
- `subbrief.yaml` не заполнен маркетологом — дальнейший pipeline (CD2+) не стартует из-за пустого брифа сегмента.
- Несовпадение `blog_id` в `.subsite-meta.yaml` и реальной WP-сетью — контент деплоится не в тот subsite.
- Папка сегмента уже существует локально при повторном запуске команды — скрипт может перезаписать `.subsite-meta.yaml` без предупреждения.

## Related

- [[landing-clone]] — клонировать готовый сегмент в новый byte-by-byte
- [[wp-multisite]] — скилл миграции и управления WP multisite-сетью
- [[landing-segment]] — команда создания сегмента ЦА
- [[landing-go]] — главная точка входа, диспатчит этапы через оркестратор
- [[landing-deploy]] — деплой основного лендинга (предшествует этапу 13)