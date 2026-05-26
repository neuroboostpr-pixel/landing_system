---
type: rule
name: wiki-audit-checklist
sources: ["docs/standards/wiki-audit-checklist.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["premium-07b-checklist", "stage-execution-protocol", "stage-agent-preamble"]
tags: ["wiki", "audit", "quality", "knowledge-base", "code-review"]
---

# Wiki Audit Checklist — стандарт аудита knowledge-layer

## Что делает

Этот стандарт описывает, как аудитор проверяет wiki-слой агентной системы: убеждается, что wiki реально экономит токены, не устарела, доступна агентам как первичный источник и не превратилась в заброшенный архив.

## Когда вызывать / в каком этапе

Применяется при любом ревью состояния `wiki/`, `docs/wiki/`, `kb/` или аналогичных knowledge-layer папок. Вызывается вручную — аудитором или агентом, получившим задачу проверить состояние wiki. Не привязан к конкретному этапу pipeline, но особенно актуален перед merge крупных изменений в `agents/`, `skills/`, `commands/` или `docs/standards/`.

## Что на вход / на выход

**Вход:**
- Папки `wiki/`, `docs/wiki/` или `kb/` в репозитории
- Файлы конфигурации compile-слоя (`compile.py`, `config/*.yaml`)
- Любые инструкции агентам (`CLAUDE.md`, `AGENTS.md`, `agents/`, `commands/`)

**Выход:**
- Итоговый отчёт в `docs/code-review/` по фиксированной структуре: Summary → Critical → Major → Minor → Positive feedback → Questions → Verdict
- Verdict: `Approve` / `Comment` / `Request Changes`

## Структура аудита (10 проверок)

1. **Context** — можно ли в одной фразе описать, для какого агента и зачем существует wiki
2. **Structure: наличие папки** — wiki физически существует
3. **Structure: главный индекс** — есть `index.md` как навигационная точка входа
4. **Structure: wikilinks-граф** — страницы связаны между собой, а не изолированы
5. **Reader instructions** — агенты явно обязаны читать wiki (не факультативно)
6. **Compression benefit** — wiki меньше и компактнее, чем исходники
7. **Compile-слой** — пути в конфиге актуальны, нет битых источников
8. **Freshness** — wiki не старше последних изменений в исходниках; есть sync-механизм
9. **Broken links** — `[[wikilinks]]` ведут в существующие файлы
10. **Orphans и дубли** — нет изолированных страниц и дублирующих концептов

## Severity-модель

| Severity | Когда |
|---|---|
| Critical | Нет reader-инструкций; wiki устарела и используется агентами; compile-конфиг битый; wiki дороже исходников |
| Major | Нет индекса; нет wikilinks; заметные дубли; неполный sync-путь |
| Minor | Непоследовательный нейминг; страницы перегружены; слабые формулировки |

## Режим работы аудитора

Аудит строго **read-only**: можно читать файлы, искать паттерны через `Read`/`Grep`/`Glob`, использовать shell только для инвентаризации. Запрещено редактировать любые файлы системы, запускать compile-скрипты или чинить структуру «заодно».

## Связанные концепты

- [[premium-07b-checklist]] — аналогичный checklist-стандарт для этапа 07b Compose
- [[stage-execution-protocol]] — протокол выполнения этапов, который wiki обязана поддерживать актуальным
- [[stage-agent-preamble]] — инструкция агентам, где должны быть reader-инструкции к wiki

## Источник

- `docs/standards/wiki-audit-checklist.md`