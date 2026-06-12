---
slug: niche-analyst
type: agent
name: "Аналитик ниши (Stage 01a)"
stage: "01a"
tags: [niche, analysis, competitors, positioning, market-profile, zero-touch]
triggers: [landing-orchestrator]
inputs:
  - 00_БРИФ/brief.md
  - 01_КОНТЕКСТ/context.md
outputs:
  - 01a_АНАЛИЗ_НИШИ/niche-analysis.md
  - 01a_АНАЛИЗ_НИШИ/competitors.yaml
  - 01a_АНАЛИЗ_НИШИ/market-profile.md
  - 01a_АНАЛИЗ_НИШИ/positioning.md
  - 01a_АНАЛИЗ_НИШИ/landing-structure.md
  - 01a_АНАЛИЗ_НИШИ/visual-requirements.md
gates: [gate-check-01a-niche-analysis]
pre_reqs: []
related:
  - landing-orchestrator
  - brand-architect
  - content-writer
  - wp-builder
sources: ["agents/niche-analyst.md"]
updated: 2026-05-26
confidence:
  triggers: low
  pre_reqs: low
---

# Аналитик ниши (Stage 01a)

## Что делает

Автоматически исследует нишу клиента и формирует **6 артефактов** для downstream-этапов (бренд, контент, вёрстка). Классифицирует бренд по типу (1 — глобальный, 2 — региональный, 3 — локальный), рассчитывает доступность продукта по доходам региона, собирает 15–25 конкурентов в 7 ролях, выбирает один из трёх режимов позиционирования (rational / emotional_aspiration / trust_authority или гибрид) и прописывает карту блоков лендинга под конкретный тип × режим. Работает полностью без вопросов к пользователю — пробелы помечает `[ДОПУЩЕНИЕ]`.

## Когда вызывается

Запускается `landing-orchestrator`-ом автоматически, когда `.landing-state.yaml` переходит в `current_stage == 01a_niche_analysis`. Условие — `00_БРИФ/brief.md` существует и gate-check предыдущего этапа вернул exit 0.

## Вход → выход

**Вход:** `00_БРИФ/brief.md` (обязательно) и `01_КОНТЕКСТ/context.md` (если есть). Из брифа извлекаются: название, категория, регион, целевой рынок, цена/чек.

**Выход:** шесть файлов в `01a_АНАЛИЗ_НИШИ/` — обзорный `niche-analysis.md`, `competitors.yaml` (15–25 записей, схема валидируется), `market-profile.md` (8 секций с tier-расчётом), `positioning.md` (шаблон по режиму), `landing-structure.md` (таблица блоков лендинга с контрактом для wp-builder), `visual-requirements.md` (правила из `config/niche-visual-rules.yaml` + дериваты из конкурентов). Все четыре Python-валидатора должны вернуть exit 0.

## Чем закрывается этап (gates)

- `gate-check-01a-niche-analysis` — все 6 артефактов записаны, все валидаторы (`validate-competitors.py`, `validate-market-profile.py`, `validate-positioning.py`, `validate-landing-structure.py`, `validate-visual-requirements.py`) возвращают exit 0, обязательные блоки Hero/CTA/Footer присутствуют в landing-structure.

## Failure modes

- **Недостаточно конкурентов** — WebSearch или Firecrawl не нашли 15 записей; агент вынужден дублировать роли, валидатор падает по `min_competitors`.
- **Неверный tier** — медианный доход региона недоступен, расчёт ratio делается по ВВП-прокси; реальный tier может быть завышен/занижен; confidence: low не проставлен.
- **Конфликт brief_indicators** — бриф содержит смешанные сигналы, агент выбирает dominant-маркер без уточнения, что ведёт к неверному режиму позиционирования.
- **Отсутствие `context.md`** — агент пропускает конкурентный анализ выше уровня поиска и опирается только на бриф; итоговый список конкурентов беднее.
- **Harness-блокировка** — `enforce_stage_gate.py` не даёт записать файлы, если предшественник не закрыт; агент STOP'ится и ожидает закрытия предыдущего gate.

## Related

- [[landing-orchestrator]] — диспатчит агента и принимает hand-off после gate-check
- [[brand-architect]] — потребляет `positioning.md` и `market-profile.md` на этапе 04
- [[content-writer]] — опирается на `landing-structure.md` при написании текстов (этап 07)
- [[wp-builder]] — использует контракт template-parts из `landing-structure.md` на этапе 08