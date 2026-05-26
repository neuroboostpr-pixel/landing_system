---
type: skill
name: landing-versioning-and-cloning
sources: ["skills/landing-versioning-and-cloning/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses:
  - wp-multisite
tags:
  - versioning
  - cloning
  - rollback
  - legacy
  - single-site
---

# Landing Versioning and Cloning (устаревший)

## Что делает

Создаёт снимки (snapshots) версий лендинга и позволяет откатиться к любой предыдущей версии. Также умеет клонировать весь проект лендинга как отдельный WordPress-инстанс — для A/B-тестирования или создания дубля сайта.

> ⚠️ **Устарел для multisite-проектов.** Для модели с сегментами целевой аудитории используйте `skills/wp-multisite`.

## Когда вызывать / в каком этапе

Применяется вручную — в любой момент жизненного цикла **single-site** проекта, когда нужно:
- зафиксировать текущее состояние перед рискованными изменениями;
- откатить проект к более ранней рабочей версии;
- создать A/B-копию лендинга как отдельный сайт.

Для **multisite-проектов** (с сегментами ЦА, созданными через `/landing-segment`) этот скилл **не подходит** — используйте `clone-subsite.sh` из `skills/wp-multisite`.

## Что на вход / на выход

**Вход:**
- Путь до папки проекта (`<project-dir>`) — обязателен для обоих скриптов.
- Опциональная метка версии (`version-label`) для `create-version.sh`.
- Новый slug (`<new-slug>`) для `clone-landing.sh`.

**Выход:**
- `create-version.sh` → снимок сохраняется в `<project>/09_ВЕРСИИ/<version>/`.
- `clone-landing.sh` → полная filesystem-копия проекта с новым slug и новым `.env`.

## Связанные концепты

- [[wp-multisite]] — актуальная альтернатива для клонирования сегментов ЦА в multisite-модели; этот скилл явно отсылает к нему как к замене

## Источник

- `skills/landing-versioning-and-cloning/SKILL.md`