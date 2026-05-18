---
type: unknown
name: wizard-check-materials
sources: ["scripts/wizard-check-materials.py", "scripts/wizard-check-materials.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-onboarding-wizard", "landing-start", "landing-onboarding"]
tags: ["script", "wizard", "materials", "validation", "onboarding", "pr-e"]
---

# wizard-check-materials — проверка материалов для мастера онбординга

## Что делает
Python-скрипт проверяет наличие обязательных и опциональных материалов в папке проекта — тех, что пользователь должен загрузить в ходе мастера онбординга (`/landing-start`). По каждому шагу возвращает JSON-отчёт: что найдено, что отсутствует, итоговый статус.

## Когда вызывать / в каком этапе
Используется на этапе **PR-E** (онбординг-мастер) — агент `landing-onboarding-wizard` запускает скрипт после того, как пользователь сообщает о загрузке файлов. Верификация происходит для каждого из 4 шагов мастера отдельно. Также может вызываться напрямую из командной строки для ручной диагностики проекта.

## Что на вход / на выход

**Вход:**
- Путь к папке проекта (аргумент командной строки)
- Опционально: имя конкретного шага для проверки (`prototype`, `photos`, `logos`, `references`)

**Выход:**
- JSON в stdout: `{step, status, found, missing, summary}`
- Exit code `0` — шаг пройден (`pass`) или некритичное предупреждение (`warn`)
- Exit code `1` — обязательный шаг провален (`fail`)

**Проверяемые шаги:**

| Шаг | Статус | Путь | Условие pass |
|---|---|---|---|
| `prototype` | 🔴 обязательный | `07_ПРОТОТИП/source/` | файл `prototype.{pdf,md,html}` |
| `photos` | 🟡 опциональный | `07c_PHOTOS/inbox/` | любые `*.{jpg,jpeg,png,heic}` |
| `logos` | 🟡 опциональный | `04_БРЕНД/logos/` | `logo.*` или любой image |
| `references` | ⚪ опциональный | `03_РЕФЕРЕНСЫ/` | `index.yaml` непустой или `screenshots/` не пуст |

Только `prototype` вызывает exit code `1` при отсутствии — остальные шаги дают `warn`, не блокируя продолжение мастера.

## Связанные концепты
- [[landing-onboarding-wizard]] — агент-мастер, вызывающий скрипт на каждом шаге PR-E
- [[landing-start]] — команда запуска онбординга, в рамках которой происходит проверка материалов
- [[landing-onboarding]] — скилл с описанием полного процесса онбординга

## Источник
- `scripts/wizard-check-materials.py`
- `scripts/wizard-check-materials.py.doc.md`