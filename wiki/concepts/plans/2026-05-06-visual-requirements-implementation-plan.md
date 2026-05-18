---
type: rule
name: visual-requirements-implementation-plan
sources: ["docs/superpowers/plans/2026-05-06-visual-requirements-implementation-plan.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses:
  - niche-analyst
  - client-assets-collector
  - moodboard-composer
  - references-curator
  - wp-builder
  - stage-gates
  - niche-visual-rules
  - 01a-analiz-nishi
tags: ["visual", "niche", "01a", "plan", "artifacts"]
---

# Визуальные требования: план реализации

## Что делает

Описывает 9-шаговый план добавления четвёртого артефакта `visual-requirements.md` в этап `01a_АНАЛИЗ_НИШИ`. Артефакт фиксирует визуальный язык лендинга — hero focal point, стиль фотографии, product treatment, допустимые фоны и red flags ниши — и передаётся как обязательный input в downstream-агенты: сборщик клиентских ассетов, мудборд, куратор референсов и wp-builder.

## Когда вызывать / в каком этапе

Применяется при разработке landing-system: является планом реализации PR по расширению этапа **01a**. После выполнения всех 9 задач агент `niche-analyst` создаёт `visual-requirements.md` автоматически в шаге 9 своего алгоритма. `gate-check` для этапа 01a начинает требовать наличия файла (hard_check) и прохождения валидатора.

## Что на вход / на выход

**Вход (для нового артефакта в рамках проекта):**
- `00_БРИФ/brief.md` — описание продукта и бренда
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — данные о конкурентах и их визуальных кодах
- `config/niche-visual-rules.yaml` — справочник по категориям ниш (создаётся в Task 1)

**Выход плана (новые файлы в системе):**
- `config/niche-visual-rules.yaml` — справочник с 4 MVP-категориями: `premium_automotive`, `local_services`, `professional_services`, `b2c_consumer` + `default`
- `skills/niche-analysis/scripts/validate-visual-requirements.py` — валидатор: проверяет 7 секций и наличие ≥3 ❌ и ≥3 ✅ в секции 6
- Bats-тесты справочника и pytest-тесты валидатора
- Обновлённые агенты: `niche-analyst.md` (шаг 9), `client-assets-collector.md`, `moodboard-composer.md`, `references-curator.md`, `wp-builder.md` (visual sanity-checks)
- Обновлённый `config/stage-gates.yaml` — два новых hard_check для stage 01a

**Финальный артефакт проекта** (порождается `niche-analyst`):
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — 7 секций: hero focal, photography style, people, product treatment, backgrounds, red flags, источники

## Связанные концепты

- [[niche-analyst]] — получает шаг 9 алгоритма, создаёт visual-requirements.md
- [[client-assets-collector]] — читает visual-requirements.md перед запросом материалов у клиента
- [[moodboard-composer]] — фильтрует референсы через red flags из секции 6
- [[references-curator]] — отвергает референсы, нарушающие визуальные запреты ниши
- [[wp-builder]] — проводит visual sanity-checks перед сборкой WordPress-темы
- [[niche-visual-rules]] — справочник категорий ниш, на который опирается алгоритм
- [[stage-gates]] — добавляются 2 hard_check: file_exists и script-валидация
- [[01a-analiz-nishi]] — этап, в котором появляется четвёртый артефакт

## Источник

- `docs/superpowers/plans/2026-05-06-visual-requirements-implementation-plan.md`