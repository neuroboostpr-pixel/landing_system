---
slug: landing-go
type: command
name: "Главная команда оркестратора"
tags: [orchestrator, entry-point, pipeline, prototype-first, auto-fix]
triggers: [landing-go]
inputs: [07-prototip]
outputs: [07b-composed, 08-kod, 09-deploy]
pre_reqs: [landing-start]
related: [landing-orchestrator, landing-prototype, landing-compose, landing-photos, landing-visuals, landing-build, landing-deploy]
sources: ["commands/landing-go.md"]
updated: 2026-06-22
confidence: {stage: low}
---

# /landing-go — Главная команда оркестратора

## Что делает

Единая точка входа в конвейер landing-system. Читает `.landing-state.yaml` проекта через `scripts/landing-go-next-stage.py`, определяет следующий незакрытый этап и диспатчит нужного агента или скилл. На этапе 07d/07e запускает `/landing-photos` и `/landing-visuals` **параллельно**. При падении гейта предлагает авто-фикс по `fix_hint` из `config/stage-gates.yaml` и при согласии перезапускает проверку автоматически. Ведёт проект от прототипа до задеплоенного сайта без ручного переключения между командами.

## Когда вызывается

Запускается вручную маркетологом или агентом один раз в начале сессии — и далее сам продвигает проект по этапам до следующей точки подтверждения. Повторный вызов продолжает с того места, где остановился. В prototype-first флоу обязателен файл `prototype.pdf` или `prototype.md` в `<project>/07_ПРОТОТИП/source/`.

## Вход → выход

**Вход:** папка проекта с заполненным `.landing-state.yaml`; в `07_ПРОТОТИП/source/` лежит прототип (PDF или MD). Флаги: `--project <slug>`, `--auto-fix yes|no`, `--skip-gate <id>`.

**Выход:** команда последовательно закрывает этапы 07a → 03 → 04 → 05 → 06 → 07 → 07c → 07d/07e (параллельно) → 07f → 08 → 09 → 10–12. После каждого этапа обновляет `.landing-state.yaml`. Upstream-этапы 00/01/01a/02 помечаются `n/a` автоматически в prototype-first флоу.

## Failure modes

- **Прототип не найден** — оркестратор не стартует; нужно положить файл в `07_ПРОТОТИП/source/` перед запуском.
- **Гейт падает, fix_hint отсутствует** — авто-фикс невозможен; нужно разбираться вручную, потом `/landing-go` продолжит.
- **`.landing-state.yaml` не синхронизирован** — `landing-go-next-stage.py` вернёт неверный этап; требуется `migrate-state-for-prd.sh` для старых проектов.
- **Параллельные субагенты 07d/07e** завершаются с разным результатом — оркестратор ждёт оба; если один упал, этап 07f не откроется.
- **Upstream-этапы остались в `locked`** — `gate-check.sh` попытается валидировать их hard-checks; нужно явно проставить `n/a` через `gate-state.sh`.

## Related

- [[landing-orchestrator]] — агент, которого диспатчит эта команда; содержит логику обхода этапов
- [[landing-prototype]] — первый авто-этап 07a в prototype-first флоу
- [[landing-compose]] — вызывается на этапах 07c и 07f
- [[landing-photos]] — параллельный субагент этапа 07d
- [[landing-visuals]] — параллельный субагент этапа 07e
- [[landing-build]] — этап 08, авто-генерация WP-темы
- [[landing-deploy]] — этап 09, деплой на Бегет
- [[landing-start]] — предшествует: создаёт папку проекта и структуру материалов