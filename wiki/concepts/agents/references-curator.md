---
slug: references-curator
type: agent
name: "Куратор референсов"
stage: "03"
tags: [references, visual, stage-03, index, curator]
triggers: [landing-references]
inputs: [01a_АНАЛИЗ_НИШИ/competitors.yaml, 01a_АНАЛИЗ_НИШИ/visual-requirements.md]
outputs: [03_РЕФЕРЕНСЫ/index.yaml, 03_РЕФЕРЕНСЫ/refs/]
pre_reqs: [01a-analiz-nishi, 02-materialy-klienta]
related: [moodboard-composer, references-collection, landing-references, niche-analyst, landing-moodboard]
sources: ["agents/references-curator.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Куратор референсов

## Что делает

Собирает и размечает визуальные референсы для лендинга на этапе 03. Принимает от клиента URL-ссылки, файлы Behance/Dribbble и скриншоты, загружает материалы в `03_РЕФЕРЕНСЫ/refs/`, присваивает каждому статус (candidate / approved / rejected) и ведёт индексный файл `index.yaml` через скрипт `index.py`. Обязателен hardcoded минимум: не менее трёх одобренных референсов, после чего управление передаётся `moodboard-composer`.

## Когда вызывается

Вызывается командой `/landing-references` после закрытия этапов 01a (анализ ниши) и 02 (материалы клиента). Агент не стартует, если `.landing-state.yaml` показывает текущий этап, отличный от `03_references`.

## Вход → выход

**Вход:** `01a_АНАЛИЗ_НИШИ/competitors.yaml` (визуальные заметки по конкурентам, поле `visual_notes`) и `visual-requirements.md` (Section 6 — red flags визуала). Дополнительно — URL и скриншоты от клиента.

**Выход:** `03_РЕФЕРЕНСЫ/index.yaml` с размеченными референсами и статусами; скриншоты в `03_РЕФЕРЕНСЫ/refs/`; поле `take: design|layout|both` для каждого блочного референса; `refs-palette.html` с палитрой, снятой с пикселей.

## Failure modes

- Агент пытается получить палитру текстовым пересказом вместо пикселей скриншота — выдаёт неверные цвета (реальный кейс: Mercedes → 403, текстовое описание солгало).
- Ссылка недоступна (бот-защита, 403, геоблок), агент молча пропускает её вместо запроса скриншота у клиента — реферетнс теряется.
- Клонирование визуала конкурентов-лидеров: `competitors.yaml::visual_notes` не проверен перед поиском — нарушение A3-правила.
- Референс попадает под red flag из `visual-requirements.md`, но не отвергается — ошибка проходит в мудборд.
- Hard gate (≥3 approved) не достигнут, но `moodboard-composer` запущен вручную — этап 04 получает неполный набор визуала.

## Related

- [[moodboard-composer]] — принимает управление после одобрения минимального набора референсов
- [[references-collection]] — скилл с инструментами (index.py) для ведения index.yaml
- [[landing-references]] — слеш-команда, запускающая агента
- [[niche-analyst]] — поставляет competitors.yaml и visual-requirements.md как обязательные входы
- [[01a-analiz-nishi]] — этап, закрытие которого обязательно до старта куратора