---
type: rule
name: content-preserve
sources: ["docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses:
  - block-composer
  - stage-gates
  - prototype-importer
  - premium-07b-checklist
tags: ["content-integrity", "hard-gate", "07c", "prototype", "verify"]
---

# Content Preserve — текст прототипа неприкосновенен (PR-H)

## Что делает

Автоматически проверяет, что все заголовки, кнопки и тексты из `prototype.yaml` перенесены в `composed.html` **дословно и в том же порядке**. Если агент что-то переписал «в улучшенном виде» — этап 07c не закрывается.

## Когда вызывать / в каком этапе

Запускается автоматически через `gate-check.sh` при попытке закрыть этап **07c_composed** (и повторно — 07f_composed_final). Пользователь видит результат при выполнении `/landing-go` или `bash scripts/gate-check.sh --stage 07c_composed --project <project>`.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — источник правды (структурированный YAML с блоками, заголовками, CTA, абзацами)
- `<project>/07b_COMPOSED/composed.html` — рендеренный HTML для проверки

**Выход:**
- `exit 0` — все строки прототипа найдены, порядок блоков совпадает; печатает `✅ Контент прототипа сохранён (N строк проверено)`
- `exit 1` — найдены расхождения; в stderr — список конкретных пропавших строк и/или сообщение о неправильном порядке блоков
- `exit 2` — один из файлов отсутствует

**Механика:**
1. Bash-враппер `scripts/verify-content-preserved.sh` вызывает Python-скрипт `scripts/verify_content_preserved.py`.
2. Python рекурсивно обходит все строковые поля YAML (кроме служебных: `id`, `type`, `block_id`, `class`, `tag`).
3. Сравнение substring с whitespace-нормализацией, case-sensitive.
4. Плейсхолдеры `____` и строки начинающиеся на `TBD` пропускаются.
5. Порядок секций `data-block="<id>"` в HTML должен совпадать с порядком `blocks[]` в YAML.

**Интеграция в `stage-gates.yaml`:**
```yaml
"07c_composed":
  hard_checks:
    - id: content_preserved
      type: script
      script: "scripts/verify-content-preserved.sh"
      required: true
```

**Усиление агента:** в `agents/block-composer.md` добавлен раздел «СТРОГО: контент прототипа неприкосновенен» — агент обязан спрашивать явное разрешение перед любым изменением текста клиента.

**Тесты:** 4 bats-теста (`pass`, `fail_title`, `fail_cta`, `fail_order`) с изолированными фикстурами.

## Связанные концепты

- [[block-composer]] — агент-составитель HTML, получивший запрет на молчаливое переписывание текста
- [[stage-gates]] — фреймворк hard_checks, куда добавляется новый чек `content_preserved`
- [[prototype-importer]] — создаёт `prototype.yaml` — источник правды для этой проверки
- [[premium-07b-checklist]] — параллельный hard_check на CSS-фичи в 07b, не конфликтует

## Источник

- `docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md`