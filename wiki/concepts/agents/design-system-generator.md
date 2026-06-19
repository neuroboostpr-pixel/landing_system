---
slug: design-system-generator
type: agent
name: "Генератор дизайн-системы"
stage: "05"
tags: [design-system, tokens, stage-05, design-preview, mockup]
triggers: [landing-design]
inputs:
  - 04_БРЕНД/brand-kit.md
  - 03b_КОНЦЕПТ/visual-concept.yaml
  - 07_ПРОТОТИП/prototype.yaml
outputs:
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 05_ДИЗАЙН-СИСТЕМА/design-preview.html
  - 05_ДИЗАЙН-СИСТЕМА/mockup-preview.html
  - .stage-decisions/05_design.md
gates: [design_system_approved]
pre_reqs: [04-brend, brand-architect]
related:
  - design-tokens-generation
  - brand-kit-build
  - landing-design
  - 05-dizayn-sistema
  - 04-brend
  - block-composer
sources: ["agents/design-system-generator.md"]
updated: 2026-06-19
confidence:
  gates: low
---

# Генератор дизайн-системы

## Что делает

Читает `04_БРЕНД/brand-kit.md` и `03b_КОНЦЕПТ/visual-concept.yaml`, строит полную дизайн-систему проекта: машиночитаемые токены (`tokens.json`), документ-источник истины (`DESIGN.md`) и живой превью компонентов (`design-preview.html`). До генерации системы обязательно показывает менеджеру два варианта макета (`mockup-preview.html`) с реальным контентом из прототипа и ждёт явного выбора. Все самостоятельные решения (spacing, motion и т.д.) документирует в `.stage-decisions/05_design.md`.

## Когда вызывается

Запускается командой `/landing-design` (скилл `landing-design`) на этапе 05 после того, как `brand-architect` завершил формирование бренд-кита на этапе 04 и `.landing-state.yaml` содержит `current_stage == 05_design`.

## Вход → выход

**Вход:** `04_БРЕНД/brand-kit.md` (цвета, шрифты, иконки, motion, grid), `03b_КОНЦЕПТ/visual-concept.yaml` (выбранный визуальный концепт), `07_ПРОТОТИП/prototype.yaml` (структура и тексты прототипа).

**Выход:** `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — YAML-frontmatter + токены с провенансом; `tokens.json` — машиночитаемая форма токенов; `design-preview.html` — живые компоненты; `mockup-preview.html` — промежуточный макет для согласования; опционально `.stage-decisions/05_design.md` — лог отклонений.

## Чем закрывается этап (gates)

- `design_system_approved` — менеджер явно написал «утверждаю», «ok» или «дальше» после просмотра `design-preview.html`; без этого агент не переходит к этапу 06.

## Failure modes

- `03b_КОНЦЕПТ/visual-concept.yaml` отсутствует — агент останавливается на фазе mockup с STOP-ошибкой.
- Предшественник (этап 04) не закрыт — `enforce_stage_gate.py` физически блокирует Write/Edit к файлам этапа.
- `build-tokens.py` падает из-за некорректного формата `brand-kit.md` — `DESIGN.md` и `tokens.json` не создаются, этап не проходит.
- Менеджер не отвечает на показ mockup — агент не генерирует финальную систему и ждёт бесконечно.
- Токены содержат прямые цвета вне `:root` (нарушение спеки §4.3) — последующий `verify_tokens.py` вернёт ошибку на этапе 07b/08.

## Related

- [[design-tokens-generation]] — скилл-владелец агента; содержит `build-tokens.py` и `render-preview.py`
- [[brand-kit-build]] — предшествующий скилл, формирует `brand-kit.md` на этапе 04
- [[brand-architect]] — агент этапа 04, обязателен как pre-req
- [[landing-design]] — команда-триггер этапа 05
- [[05-dizayn-sistema]] — этап pipeline, который закрывается этим агентом
- [[block-composer]] — потребитель `tokens.json` и `DESIGN.md` на этапе 07b/07c