---
slug: design-system-generator
type: agent
name: "Генератор дизайн-системы"
stage: "05"
tags: [design-system, tokens, stage-05, design-preview, traceability]
triggers: [landing-design]
inputs:
  - 04_БРЕНД/brand-kit.md
  - 03b_КОНЦЕПТ/visual-concept.yaml
  - 07_ПРОТОТИП/prototype.yaml
outputs:
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 05_ДИЗАЙН-СИСТЕМА/design-preview.html
pre_reqs: [04-brend, 03-referensy]
related:
  - brand-architect
  - design-tokens-generation
  - landing-design
  - 05-dizayn-sistema
  - brand-kit-build
  - stage-execution-protocol
sources: ["agents/design-system-generator.md"]
updated: 2026-06-19
confidence:
  triggers: low
---

# Генератор дизайн-системы

## Что делает

Агент этапа 05: читает `brand-kit.md` и `visual-concept.yaml`, генерирует полную дизайн-систему с трассируемостью (provenance). Сначала строит HTML-mockup с двумя вариантами дизайна на реальном контенте прототипа — и ждёт выбора менеджера. После одобрения запускает `build-tokens.py` и `render-preview.py`, создаёт единый источник истины `DESIGN.md`, машиночитаемый `tokens.json` и живой `design-preview.html`. Выход к этапу 06 блокируется hard gate до явного «утверждаю» со стороны пользователя.

## Когда вызывается

Вызывается командой `/landing-design` (скилл `landing-design`) в момент когда `.landing-state.yaml` содержит `current_stage == 05_design` и этап 04 закрыт. Оркестратор не пропускает этап, если brand-kit или visual-concept отсутствуют.

## Вход → выход

**Вход:** `04_БРЕНД/brand-kit.md` (цвета, шрифты, иконки, motion), `03b_КОНЦЕПТ/visual-concept.yaml` (визуальная концепция из этапа 03b), `07_ПРОТОТИП/prototype.yaml` (реальный контент для mockup).

**Выход:** `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый YAML-frontmatter источник токенов; `tokens.json` — машиночитаемые токены (цвета, типографика, spacing, grid, radius, shadow, breakpoints, motion); `design-preview.html` — живые компоненты по токенам; `.stage-decisions/05_design.md` — журнал самостоятельных решений (протокол B28).

## Failure modes

- **visual-concept.yaml отсутствует** — агент останавливается с STOP ещё до фазы mockup, без fallback.
- **Stage gate 04 не закрыт** — hook `enforce_stage_gate.py` физически блокирует запись в файлы этапа 05; попытки обойти не работают.
- **Менеджер не даёт ответ на mockup** — агент висит в ожидании; генерация DESIGN.md не начнётся, конвейер стоит.
- **`build-tokens.py` падает** — tokens.json не создан, все последующие этапы (07c, 08) не смогут применить токены.
- **Отклонения не задокументированы** — нарушение протокола B28; дивергенция между `visual-concept.yaml` и реальным DESIGN.md становится необнаруживаемой.

## Related

- [[brand-architect]] — поставляет `brand-kit.md`; должен завершиться до запуска этого агента
- [[design-tokens-generation]] — скилл-владелец; содержит скрипты `build-tokens.py` и `render-preview.py`
- [[landing-design]] — slash-команда, которая диспатчит этот агент
- [[05-dizayn-sistema]] — этап pipeline, который закрывается выходами агента
- [[brand-kit-build]] — скилл, формирующий brand-kit.md на этапе 04
- [[stage-execution-protocol]] — обязательный протокол pre-flight для всех stage-агентов