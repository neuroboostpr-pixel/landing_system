---
slug: landing-onboarding-wizard
type: agent
name: "Мастер онбординга нового лендинга"
stage: "00"
tags: [onboarding, wizard, bootstrap, new-project, materials]
triggers: [landing-start]
inputs: []
outputs: ["~/Lendings/<slug>/", "03_РЕФЕРЕНСЫ/index.yaml", "wiki/project-graph"]
gates: []
pre_reqs: []
related: [landing-start, landing-go, landing-project-init, landing-onboarding, prototype-importer, references-collection, references-curator, landing-orchestrator, landing-new]
sources: ["agents/landing-onboarding-wizard.md"]
updated: 2026-06-19
---

# Мастер онбординга нового лендинга

## Что делает

Агент встречает маркетолога перед началом работы над новым проектом. Объясняет систему тремя короткими параграфами, принимает kebab-case имя проекта и создаёт папку через скилл `landing-project-init`. Затем последовательно проводит через 4 шага укладки материалов: прототип (обязательно), фото клиента, логотип, референсы — с верификацией каждого шага через `wizard-check-materials.py` и явным подтверждением перед переходом. Финалом формирует вики-граф проекта и даёт подсказку `/landing-go`.

## Когда вызывается

Запускается командой `/landing-start`. Рассчитан исключительно на создание новых проектов — не трогает уже существующие папки. Работает до старта основного пайплайна: `landing-orchestrator` принимает управление только после завершения wizard.

## Вход → выход

**Вход:** Маркетолог вводит имя проекта в kebab-case, затем поочерёдно передаёт пути к файлам или URL (прототип PDF/MD, фото в inbox-папки, логотип SVG/PNG, ссылки или скриншоты референсов) либо явно пропускает необязательные шаги.

**Выход:** Папка `~/Lendings/<slug>/` с 18 подпапками и README-подсказками; материалы разложены по нужным подпапкам; `03_РЕФЕРЕНСЫ/index.yaml` с кандидатами; вики-граф проекта в `wiki/`; готовность к запуску `/landing-go`.

## Failure modes

- Прототип не предоставлен — агент блокирует переход на шаг 2, пропуск не принимается.
- Папка `~/Lendings/<slug>/` уже существует — агент уточняет: использовать или назвать иначе.
- Slug не соответствует kebab-case — агент просит переименовать.
- URL референса (Behance, Instagram, Tilda) недоступен без браузера — агент запрашивает скриншоты в чат и сохраняет через `wizard-save-images.py`; если скриншотов нет — URL остаётся в статусе `needs_screenshot`.
- `wizard-check-materials.py` возвращает `fail` — шаг повторяется; `warn` — агент информирует и спрашивает «продолжить?».

## Related

- [[landing-start]] — slash-команда, которая напрямую триггерит этого агента
- [[landing-go]] — следующая точка входа после завершения wizard
- [[landing-project-init]] — скилл создания структуры папки проекта
- [[landing-onboarding]] — связанный гайд по онбордингу системы
- [[prototype-importer]] — агент, который парсит прототип на этапе 07a после wizard
- [[references-collection]] — скилл сбора и валидации референсов
- [[landing-orchestrator]] — оркестратор, принимающий проект после wizard
- [[landing-new]] — альтернативная команда создания проекта без пошагового wizard