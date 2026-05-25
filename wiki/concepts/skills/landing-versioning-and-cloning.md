---
type: skill
name: landing-versioning-and-cloning
sources: ["skills/landing-versioning-and-cloning/SKILL.md"]
updated: 2026-05-25
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

# Landing Versioning and Cloning

## Что делает
Создаёт снимки (версии) проекта-лендинга и позволяет откатиться к любой из них. Также умеет клонировать весь проект целиком для A/B-тестирования — но только в устаревшей single-site модели.

## Когда вызывать / в каком этапе
Используется вручную в любой момент жизни **single-site** проекта:
- перед рискованными изменениями — чтобы сохранить рабочую версию;
- после утверждения пользователем очередного этапа — как «точка возврата»;
- при необходимости создать A/B-копию лендинга как отдельный WP-инстанс.

> ⚠️ **Deprecated для multisite-проектов.** Если проект мигрирован на WP Multisite (появился `.landing-state.yaml::multisite: true`), клонирование сегментов делается через [[wp-multisite]] (`clone-subsite.sh`), а не этим скиллом.

## Что на вход / на выход

**Вход:**
- `<project-dir>` — путь к папке проекта (например `~/Lendings/my-project`);
- опциональный `[version-label]` — читаемая метка снимка (например `after-stage-07b`);
- `<new-slug>` — slug нового проекта при клонировании.

**Выход:**
- `create-version.sh` → папка `09_ВЕРСИИ/<version>/` со снимком всего проекта на момент вызова;
- `clone-landing.sh` → новая директория проекта `~/Lendings/<new-slug>/` — полная filesystem-копия с отдельным `.env`.

## Связанные концепты
- [[wp-multisite]] — актуальная альтернатива для клонирования сегментов целевой аудитории в multisite-модели; `clone-subsite.sh` заменяет `clone-landing.sh` для новых проектов
- [[landing-rollback]] — slash-команда для отката проекта к сохранённой версии; использует артефакты, созданные `create-version.sh`
- [[landing-clone]] — slash-команда, которая оборачивает `clone-landing.sh` для пользователя

## Источник
- `skills/landing-versioning-and-cloning/SKILL.md`