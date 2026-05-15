---
type: stage
name: 03-references
sources: ["template/03_РЕФЕРЕНСЫ/README.md"]
updated: 2026-05-15
triggers: []
stage: "03"
uses:
  - references-curator
  - landing-start
  - landing-references
  - moodboard-composer
tags:
  - references
  - visual
  - stage
---

# 03_РЕФЕРЕНСЫ — Визуальные референсы проекта

## Что делает

Папка хранит список сайтов-образцов, которые нравятся клиенту или подходят по нише. На основе этих URL система строит мудборд и выбирает визуальный стиль лендинга.

## Когда вызывать / в каком этапе

Этап **03** в общем workflow. Маркетолог заполняет папку на старте проекта — либо через wizard `/landing-start` (шаг «Референсы», опциональный), либо вручную. Агент `references-curator` может собирать и тегировать референсы автоматически по команде `/landing-references`. Следующий этап (04 — Бренд) не стартует без хотя бы одного одобренного референса (`status: approved`).

## Что на вход / на выход

**Вход:**
- URL лендингов-образцов — добавляет маркетолог или агент `references-curator`
- Опциональные скриншоты в папку `screenshots/`

**Выход:**
- `index.yaml` — структурированный список референсов с полями `url`, `note`, `status`
- Статусы: `candidate` (кандидат) → `approved` (одобрен) → `rejected` (отклонён)
- Одобренный набор передаётся агенту `moodboard-composer` для построения мудборда

**Формат `index.yaml`:**
```yaml
references:
  - url: https://example.com/landing-1
    note: "Похожая ниша, нравится hero"
    status: approved
  - url: https://example.com/landing-2
    status: candidate
```

## Связанные концепты

- [[references-curator]] — агент, который автоматически собирает, тегирует и ведёт `index.yaml`
- [[landing-references]] — команда для ручного запуска сбора референсов
- [[landing-start]] — wizard на старте проекта, предлагает добавить референсы (опциональный шаг)
- [[moodboard-composer]] — получает одобренные референсы и строит на их основе мудборд
- [[moodboard-creation]] — скилл создания мудборда, использует данные этого этапа

## Источник

- `template/03_РЕФЕРЕНСЫ/README.md`