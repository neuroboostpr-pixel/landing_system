---
type: rule
name: pr-h-content-preserve
sources: ["docs/superpowers/plans/2026-05-15-pr-h-content-preserve-plan.md"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["block-composer", "stage-gates", "prototype-import", "block-composition"]
tags: ["content", "gate", "verify", "prototype", "07c"]
---

# PR-H — Неприкосновенность текста прототипа

## Что делает

Скрипт `verify-content-preserved.sh` проверяет, что весь текст из `prototype.yaml` (заголовки, CTA, абзацы, пункты списков) дословно присутствует в `composed.html`. Если агент молча переписал хоть одну фразу клиента — HARD GATE блокирует закрытие этапа 07c и выводит список расхождений.

## Когда вызывать / в каком этапе

Автоматически запускается при попытке закрыть этап **07c** (`07c_composed`) через `gate-check.sh`. Также подключён к этапу `07f_composed_final` (после фото-перерендера). Вручную: `bash scripts/verify-content-preserved.sh <project-path>`.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — эталонный текст (titles, cta, body, items)
- `<project>/07b_COMPOSED/composed.html` — финальный HTML для проверки

**Выход:**
- Exit 0 + сообщение `✅ Контент прототипа сохранён (N строк проверено)` — всё в порядке
- Exit 1 + список до 10 пропавших фраз в stderr — найдены расхождения; этап не закрывается
- Exit 2 — один из файлов отсутствует

**Логика:**
1. Substring match по всем строкам из `blocks[]` длиннее 3 символов (whitespace нормализуется)
2. Проверка порядка блоков по атрибуту `data-block` в HTML
3. Placeholder-строки (`____`, `TBD`) пропускаются

**Изменения в системе:**
- `config/stage-gates.yaml` — новый hard_check `content_preserved` в секции `07c_composed`
- `agents/block-composer.md` — добавлен раздел «контент прототипа неприкосновенен» с требованием спрашивать разрешение перед любым изменением текста
- `tests/pr-h/` — 4 bats-теста: pass, fail\_title, fail\_cta, fail\_order

## Связанные концепты

- [[block-composer]] — агент, который рендерит composed.html и обязан дословно переносить текст прототипа
- [[stage-gates]] — механизм HARD GATE, через который подключён verify-скрипт
- [[prototype-import]] — создаёт prototype.yaml, который является эталоном для проверки
- [[block-composition]] — скилл этапа 07b/07c, где применяется данное правило
- [[07c-photos]] — этап, закрытие которого блокируется при расхождении текста

## Источник

- `docs/superpowers/plans/2026-05-15-pr-h-content-preserve-plan.md`