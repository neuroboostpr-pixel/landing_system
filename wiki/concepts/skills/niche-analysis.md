---
type: skill
name: niche-analysis
sources: ["skills/niche-analysis/SKILL.md", "agents/niche-analyst.md"]
updated: 2026-05-15
triggers: ["/landing-niche", "анализ ниши", "исследовать конкурентов", "этап 01a"]
stage: "01a"
uses: ["niche-analyst", "landing-orchestrator", "gate-check"]
tags: ["research", "competitors", "positioning", "zero-touch"]
---

# niche-analysis — автоматический анализ ниши и конкурентов

## Что делает

Запускает полностью автоматический ресёрч ниши: ищет конкурентов, классифицирует тип бренда, определяет режим позиционирования и создаёт 6 готовых артефактов для downstream-этапов (бренд-кит, контент, билдер). Никаких вопросов пользователю не задаёт — при нехватке данных ставит пометку `[ДОПУЩЕНИЕ]`.

## Когда вызывать / в каком этапе

Этап **01a** — между `01_КОНТЕКСТ` и `02_МАТЕРИАЛЫ_КЛИЕНТА`.

Вызывается командой `/landing-niche` вручную или через `landing-orchestrator`. Перед запуском skill проверяет два условия:
- в папке есть `.landing-state.yaml` (это проект-лендинг);
- этап `00_brief` имеет статус `approved`.

Если условия не выполнены — выдаёт ошибку и не идёт дальше.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

**Выход (папка `01a_АНАЛИЗ_НИШИ/`):**
1. `niche-analysis.md` — обзор ниши 400–800 слов, тип бренда, список допущений
2. `competitors.yaml` — 15–25 конкурентов в 7 ролях (direct, local_competitor, manufacturer и др.)
3. `market-profile.md` — 8 секций: tier доступности, цикл принятия решения, регулируемость, эмоциональная нагрузка, культурный контекст, рекомендованный режим
4. `positioning.md` — один из 3 режимов: `rational`, `emotional_aspiration`, `trust_authority` (или гибрид)
5. `landing-structure.md` — карта блоков лендинга под выбранный Mode × тип бренда
6. `visual-requirements.md` — визуальные требования с red flags и preferences

После записи всех артефактов skill запускает 5 валидаторов (`validate-competitors.py`, `validate-market-profile.py`, `validate-positioning.py`, `validate-landing-structure.py`, `validate-visual-requirements.py`) и `gate-check.sh`. При успехе `landing-orchestrator` запрашивает у пользователя approve для перехода на этап `02`.

## Связанные концепты

- [[niche-analyst]] — агент, выполняющий фактическую работу (12 шагов, WebSearch + firecrawl scrape)
- [[landing-orchestrator]] — диспатчер этапов; принимает hand-off после gate-check
- [[gate-check]] — скрипт валидации завершения этапа перед переходом к следующему
- [[brand-kit-build]] — downstream-потребитель артефактов этапа 01a
- [[landing-content]] — downstream-потребитель `positioning.md` и `landing-structure.md`

## Источник

- `skills/niche-analysis/SKILL.md`
- `agents/niche-analyst.md`