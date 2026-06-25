---
slug: landing-compose
type: command
name: "Сборка composed.html (этап 07b)"
stage: "07b"
tags: [compose, html, design-tokens, prototype, collage, moods]
triggers: [landing-go]
inputs: [05-dizayn-sistema, 07-prototip]
outputs: [07b-composed]
pre_reqs: [05-dizayn-sistema, 07-prototip]
related: [block-composer, landing-go, landing-photos, landing-visuals, premium-07b-checklist, landing-design, landing-content]
sources: ["commands/landing-compose.md"]
updated: 2026-06-22
confidence: {triggers: low}
---

# Сборка composed.html (этап 07b)

## Что делает

Запускает этап **07b_COMPOSED**: агент рисует HTML-макет лендинга, собирая три источника правды — дизайн-токены из `tokens.json`, реальные тексты из активного прототипа и, если есть, поблочное ТЗ `build-spec.md`. Результат — `composed.html` с полной коллажной глубиной, токенизированными цветами и переключателем мудов. Визуальные плейсхолдеры (фото, иконки, инфографика) остаются пустыми и заполняются на следующих этапах 07c/07d.

## Когда вызывается

Автоматически через `/landing-go` после того, как утверждены этап 05 (дизайн-система) и этап 07 (прототип). Может быть запущена вручную командой `/landing-compose` из папки проекта. Минимальное условие — наличие `05_ДИЗАЙН-СИСТЕМА/tokens.json`.

## Вход → выход

**Вход:** `05_ДИЗАЙН-СИСТЕМА/tokens.json`, активный `07_ПРОТОТИП/prototype-*.yaml` (`meta.active: true`). Опционально: `07b_COMPOSED/build-spec.md` (ТЗ — главный источник правды при наличии), `05_ДИЗАЙН-СИСТЕМА/moods/*/objects.yaml`, `compositions/hero.yaml`.

**Выход:** `07b_COMPOSED/composed.html` — полный макет с коллажными слоями и обязательной панелью переключения мудов; `07b_COMPOSED/composed-mobile.html`; `07b_COMPOSED/block-injection-log.md` — лог поблочной инъекции.

## Failure modes

- **ТЗ есть, но агент его проигнорировал** — генерация без сверки с `build-spec.md` считается дефектом («ТЗ протекает мимо флоу»); все поблочные требования обязательны.
- **Выдуманный текст** — агент добавляет контент, которого нет в прототипе; нарушение `reference-driven-rules.md §2.1`; ловится `verify_no_invented_text.py`.
- **Отсутствует панель мудов** — `verify-composed-premium.sh` вернёт ненулевой exit; hard-gate 07b не закроется.
- **Прямые цвета вместо токенов** — переключение мудов сломается; ловится `scripts/verify_tokens.py`.
- **Использован неактивный прототип** — при нескольких `prototype-*.yaml` без проверки `active: true` текст будет неверным; см. `07_ПРОТОТИП/prototypes-index.md`.

## Related

- [[block-composer]] — агент, который непосредственно рисует макет по ТЗ и токенам
- [[landing-go]] — оркестратор, вызывающий этот этап автоматически
- [[landing-photos]] — этап 07c, добавляет реальные фото в composed.html после сборки
- [[landing-visuals]] — этап 07d, генерирует иконки и инфографику для плейсхолдеров
- [[premium-07b-checklist]] — обязательный чеклист: токены, clamp, коллажная глубина, панель мудов
- [[landing-design]] — поставляет tokens.json и objects.yaml для этапа 07b