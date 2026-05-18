---
type: unknown
name: pr-h-tests
sources: ["tests/pr-h/README.md", "docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["block-composer", "stage-gates", "landing-compose"]
tags: ["test", "bats", "content-preserve", "hard-gate"]
---

# PR-H Tests — Тесты сохранения контента прототипа

## Что делает

Группа из четырёх bats-тестов проверяет скрипт `scripts/verify-content-preserved.sh`: он сравнивает `composed.html` с `prototype.yaml` и гарантирует, что агент не переписал клиентские тексты молча. Тесты покрывают как «всё хорошо», так и три сценария сбоя.

## Когда вызывать / в каком этапе

Тесты относятся к этапу **07c (Composed)**. Запускаются вручную при разработке и автоматически в CI после любого изменения `scripts/verify-content-preserved.sh` или `scripts/verify_content_preserved.py`. `gate-check.sh` использует скрипт верификации как `hard_check` — этап 07c не закрывается, пока exit-код не равен 0.

## Что на вход / на выход

**Вход:**
- `tests/pr-h/test_pass.bats` — фейковый проект: `prototype.yaml` (2 блока) и `composed.html`, где все строки совпадают
- `tests/pr-h/test_fail_title.bats` — prototype содержит `title: "Original"`, в HTML — `<h1>Changed</h1>`
- `tests/pr-h/test_fail_cta.bats` — prototype `cta: "Запросить тест-драйв"`, в HTML — `<button>Request test drive</button>`
- `tests/pr-h/test_fail_order.bats` — блоки `[hero, features, cta]` в прототипе, в HTML переставлены `[hero, cta, features]`

**Ожидаемый выход:**
- `test_pass` → exit 0, stdout содержит `✅ Контент прототипа сохранён`
- `test_fail_title` → exit 1, stderr содержит `«Original»` в списке пропущенных строк
- `test_fail_cta` → exit 1, stderr содержит `«Запросить тест-драйв»`
- `test_fail_order` → exit 1, stderr содержит `«Порядок блоков»`

**Запуск:**

```bash
bats tests/pr-h/
```

## Связанные концепты

- [[block-composer]] — агент, которому запрещено переписывать текст из prototype.yaml; скрипт ловит его нарушения
- [[stage-gates]] — hard_check `content_preserved` добавляется в секцию `07c_composed` конфига; PR-H тесты верифицируют эту интеграцию
- [[landing-compose]] — команда, запускающая block-composer и создающая composed.html, который и проверяется скриптом
- [[prototype-importer]] — создаёт prototype.yaml — источник правды для верификатора

## Источник

- `tests/pr-h/README.md`
- `docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md`