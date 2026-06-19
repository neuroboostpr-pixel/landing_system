---
slug: niche-analyst
type: agent
name: "Агент анализа ниши"
stage: "01a"
tags: [niche, analysis, competitors, positioning, market-profile, zero-touch]
triggers: [landing-niche, landing-go]
inputs: [00-brif, 01-kontekst]
outputs: [01a-analiz-nishi]
gates: [competitors_valid, market_profile_valid, positioning_valid, landing_structure_valid, visual_requirements_valid]
pre_reqs: [00-brif, 01-kontekst]
related: [niche-analysis, landing-orchestrator, brand-architect, content-writer, wp-builder, landing-go]
sources: ["agents/niche-analyst.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Агент анализа ниши

## Что делает

Агент автоматически исследует нишу клиента на этапе 01a: классифицирует бренд по типу (1 — глобальный, 2 — региональный, 3 — локальный), собирает 15–25 конкурентов и скрейпит их сайты, рассчитывает accessibility tier через соотношение цены к медианному доходу региона, выбирает один из трёх режимов позиционирования (rational / emotional_aspiration / trust_authority или гибрид) и генерирует карту блоков лендинга. Всё это без единого вопроса пользователю — нехватка данных отмечается как `[ДОПУЩЕНИЕ]`.

## Когда вызывается

Запускается оркестратором (`landing-orchestrator`) при переходе pipeline на этап `01a_niche_analysis`. Предусловие: этап `00-brif` должен быть закрыт и `current_stage` в `.landing-state.yaml` должен совпадать с `01a_niche_analysis`. Если предшественник не закрыт — `PreToolUse` hook блокирует запись файлов физически.

## Вход → выход

**Вход:** `00_БРИФ/brief.md` (обязательно) и `01_КОНТЕКСТ/context.md` (опционально). Дополнительно — WebSearch и mcp__firecrawl__scrape для сбора данных о конкурентах и доходах региона.

**Выход:** 6 артефактов в папке `01a_АНАЛИЗ_НИШИ/`:
- `niche-analysis.md` — обзорный документ 400–800 слов
- `competitors.yaml` — 15–25 записей в 7 ролях
- `market-profile.md` — 8 секций с accessibility tier и predicted mode
- `positioning.md` — заполненный шаблон выбранного режима
- `landing-structure.md` — карта блоков по комбинации Тип × Mode
- `visual-requirements.md` — визуальные требования на основе категории и режима

## Чем закрывается этап (gates)

- `competitors_valid` — валидатор `validate-competitors.py` возвращает exit 0 (≥15 записей, ≥3 роли)
- `market_profile_valid` — валидатор `validate-market-profile.py` проверяет все 8 секций и наличие `Predicted mode`
- `positioning_valid` — валидатор `validate-positioning.py` проверяет заголовок `**Mode:**` и структуру шаблона
- `landing_structure_valid` — валидатор проверяет наличие Hero, CTA, Footer и заголовков-цитат
- `visual_requirements_valid` — валидатор проверяет минимум 3 ❌ и 3 ✅ с обоснованиями

## Failure modes

- **Неверная классификация типа бренда** — английский бриф ошибочно трактуется как глобальный бренд; агент должен проверять Wikipedia, а не язык документа.
- **Неверный accessibility tier** — ratio рассчитывается по категорийной цене из конкурентов, но если у direct-конкурентов нет поля `price_range`, tier ставится с `[ДОПУЩЕНИЕ]` и может быть занижен/завышен.
- **Менее 15 конкурентов** — при узкой нише WebSearch возвращает мало результатов; валидатор заблокирует закрытие этапа.
- **Конфликт brief_indicators** — несколько override-сигналов из брифа указывают в разные режимы; агент выбирает доминирующий, но может ошибиться с гибридом.
- **Блокировка stage gate hook** — если предшественник `01-kontekst` не помечен approved, `enforce_stage_gate.py` блокирует Write и агент не может записать файлы.

## Related

- [[niche-analysis]] — wiki-карточка концепта, который этот агент реализует
- [[landing-orchestrator]] — диспатчит агента и проверяет gates после завершения
- [[brand-architect]] — потребляет `positioning.md` и `market-profile.md` на этапе 04
- [[content-writer]] — использует `landing-structure.md` как карту блоков для контента
- [[wp-builder]] — использует `landing-structure.md` для генерации template-parts
- [[landing-go]] — точка входа в pipeline, через которую запускается этот агент