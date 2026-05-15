---
type: skill
name: landing-versioning-and-cloning
sources: ["skills/landing-versioning-and-cloning/SKILL.md"]
updated: 2026-05-15
triggers:
  - "сохрани версию лендинга"
  - "откатись к предыдущей версии"
  - "создай A/B клон проекта"
  - "сделай снапшот"
stage: ""
uses:
  - lifecycle-keeper
  - landing-rollback
  - landing-clone
tags:
  - versioning
  - snapshot
  - clone
  - ab-testing
---

# Landing Versioning and Cloning — версионирование и клонирование лендингов

## Что делает

Сохраняет снапшоты (версии) готового лендинга и позволяет откатиться к любой из них. Также создаёт полную копию проекта для A/B-тестирования — чтобы попробовать другой вариант без риска потерять рабочий.

## Когда вызывать / в каком этапе

Вызывается вручную в любой момент работы над проектом:

- **Перед рискованными правками** — сохранить текущее состояние через снапшот.
- **После деплоя** — зафиксировать рабочую версию как контрольную точку.
- **При запуске A/B-теста** — клонировать проект под новый вариант.
- **При откате** — вернуть проект к одной из сохранённых версий.

Активируется через команды `/landing-rollback` и `/landing-clone`, которыми управляет агент [[lifecycle-keeper]].

## Что на вход / на выход

**Вход:**
- Путь к папке проекта (например `~/Lendings/my-project/`)
- Для версии: опциональная метка (`version-label`), например `v1-before-redesign`
- Для клона: новый слаг (`new-slug`), например `my-project-ab`

**Выход:**
- **Снапшот:** папка `09_ВЕРСИИ/<version>/` внутри проекта — полная копия состояния на момент сохранения
- **Клон:** новая папка проекта `~/Lendings/<new-slug>/` — независимая копия всего лендинга для параллельной работы

## Скрипты

```bash
# Сохранить снапшот
bash skills/landing-versioning-and-cloning/scripts/create-version.sh <project-dir> [version-label]

# Клонировать проект
bash skills/landing-versioning-and-cloning/scripts/clone-landing.sh <project-dir> <new-slug>
```

## Связанные концепты

- [[lifecycle-keeper]] — агент-оркестратор, который управляет этим скиллом через `/landing-rollback` и `/landing-clone`
- [[landing-rollback]] — команда для отката к сохранённой версии
- [[landing-clone]] — команда для создания A/B-копии проекта

## Источник

- `skills/landing-versioning-and-cloning/SKILL.md`