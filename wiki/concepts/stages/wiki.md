---
slug: project-wiki
type: catalog
name: "Wiki графа проекта"
tags: [wiki, project-graph, auto-generated, catalog, pipeline]
triggers: []
inputs: [template/wiki/README.md]
outputs: [wiki/index.md, wiki/log.md, wiki/concepts/stage-current.md, wiki/concepts/blocks.md, wiki/concepts/brand.md, wiki/concepts/photos.md]
pre_reqs: []
related: [landing-go, landing-orchestrator, landing-prototype, landing-brand, landing-design, landing-photos, landing-wireframe, landing-compose]
sources: ["template/wiki/README.md"]
updated: 2026-05-26
confidence: {slug: low, triggers: low}
---

# Wiki графа проекта

## Что делает

Папка `wiki/` внутри каждого проекта-лендинга хранит автоматически генерируемый граф состояния проекта. Компайлер `scripts/wiki/compile.py` (режим `project-graph`) наполняет её концептами после закрытия каждого этапа. Папка не редактируется вручную — при следующем запуске компайлера содержимое перезаписывается.

## Когда вызывается

Обновление происходит автоматически при успешном выходе `gate-check.sh` (закрытие этапа), а также вручную командой `python -m scripts.wiki.compile --source-mode=project-graph --project=<slug>`. Папка пуста в начале проекта и наполняется постепенно по мере прохождения этапов pipeline.

## Вход → выход

**Вход:** артефакты закрытых этапов проекта — `brand-kit.md`, `design-tokens.json`, `composed.html`, `07c_PHOTOS/selections.yaml`, `.landing-state.yaml`.

**Выход:** структурированные концепт-файлы в `wiki/concepts/` (текущий этап, выбранные блоки, цвета и шрифты, карта фото-слотов), главный индекс `wiki/index.md` и хронология обновлений `wiki/log.md`.

## Чем закрывается этап (gates)

*(Папка не является самостоятельным этапом pipeline; она сопровождает все этапы как артефакт наблюдения.)*

## Failure modes

- Папка устарела — `gate-check.sh` прошёл, но компайлер не запустился или упал тихо; нужно вызвать вручную.
- Концепт-файл ссылается на данные предыдущей итерации — если этап был пересобран без сброса кэша, wiki может показывать старый результат.
- Редактирование вручную — изменения теряются при следующем прогоне компайлера, что вводит в заблуждение других агентов.
- Компайлер не умеет найти проект — `--project=<slug>` указывает не на реальную папку в `~/Lendings/`; нужно проверить путь.
- Отсутствие нужного модуля Python — `scripts/wiki/compile.py` падает с ImportError если зависимости не установлены (проверить через `scripts/check-deps.sh`).

## Related

- [[landing-go]] — главная точка входа, инициирует этапы, после которых обновляется wiki
- [[landing-orchestrator]] — управляет переходами между этапами и запускает `gate-check.sh`
- [[landing-prototype]] — один из первых этапов, после которого появляется `stage-current.md`
- [[landing-brand]] — формирует данные для `wiki/concepts/brand.md`
- [[landing-photos]] — формирует данные для `wiki/concepts/photos.md`
- [[landing-wireframe]] — формирует данные о выбранных вариантах блоков (`blocks.md`)